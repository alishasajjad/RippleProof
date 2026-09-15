from __future__ import annotations

import hashlib
import json
import re

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models import (
    ArtifactRecord,
    AuditEvent,
    ChangeRun,
    ImpactRecord,
    PatchRecord,
    Policy,
    PolicyVersion,
    VerificationTestRecord,
)


from app.schemas.contracts import (
    Artifact,
    ImpactFinding,
    PatchProposal,
    PolicyContract,
    ProofReceipt,
)


from app.services.demo_service import (
    demo_artifacts,
    demo_policy_change,
)


from app.services.impact_engine import (
    ImpactEngine,
)


from app.services.llm_service import (
    LLMService,
)


from app.services.patch_engine import (
    PatchEngine,
)


from app.services.verification_engine import (
    VerificationEngine,
)


from app.services.email_alerts import (
    send_verified_alert,
)



# =====================================================
# COMMON HELPERS
# =====================================================


def _utcnow():

    return datetime.now(
        timezone.utc
    )



def _audit(
    db: Session,
    run_id: str,
    event_type: str,
    payload: dict,
    actor: str = "system",
):

    db.add(
        AuditEvent(
            run_id=run_id,
            event_type=event_type,
            actor=actor,
            payload=payload,
        )
    )



def _risk_score(
    findings: list[ImpactFinding],
) -> float:


    weights = {

        "low": 1,
        "medium": 3,
        "high": 6,
        "critical": 10,

    }


    stale = [

        finding

        for finding in findings

        if finding.status == "stale"

    ]


    if not stale:

        return 0.0



    raw = sum(

        weights.get(
            finding.severity,
            1,
        )
        *
        finding.confidence

        for finding in stale

    )


    maximum = len(stale) * 10



    return round(

        min(
            100.0,
            (raw / maximum) * 100
        ),

        1

    )



# =====================================================
# CREATE DEMO RUN
# =====================================================


def _analysis_payload(
    run: ChangeRun,
    contract: PolicyContract,
    artifacts: list[Artifact],
    findings: list[ImpactFinding],
    patches: list[PatchProposal],
    before,
):

    return {

        "run_id":
        run.id,


        "engine": {

            "semantic_mode":
            run.semantic_mode,


            "llm_model":
            run.llm_model,


            "database":
            "persistent",


            "risk_score":
            run.risk_score,

        },


        "request":
        demo_policy_change(),


        "contract":
        contract,


        "artifacts":
        artifacts,


        "findings":
        findings,


        "patches":
        patches,


        "verification_before_fix":
        before,

    }





def create_demo_run(
    db: Session,
) -> dict:


    request = demo_policy_change()


    llm_service = LLMService()



    semantic = (

        llm_service
        .interpret_policy_change(
            request
        )

    )


    contract = semantic.contract


    artifacts = demo_artifacts()



    deterministic_findings = (

        ImpactEngine()
        .analyze(
            contract,
            artifacts,
        )

    )



    findings = (

        llm_service
        .analyze_artifacts(
            contract,
            artifacts,
            deterministic_findings,
        )

    )



    patches = (

        PatchEngine()
        .propose(
            contract,
            artifacts,
            findings,
        )

    )



    before = (

        VerificationEngine()
        .run(
            contract,

            implemented_threshold=float(
                contract.old_rule.value
            ),

        )

    )



    policy = Policy(

        name=request.policy_name,

        domain=contract.risk_domain,

    )


    db.add(policy)

    db.flush()



    old_version = PolicyVersion(

        policy_id=policy.id,

        version=1,

        raw_text=request.old_text,

        structured_rule=
        contract.old_rule.model_dump(),

    )



    new_version = PolicyVersion(

        policy_id=policy.id,

        version=2,

        raw_text=request.new_text,

        structured_rule=
        contract.new_rule.model_dump(),

    )



    db.add_all(
        [
            old_version,
            new_version,
        ]
    )


    db.flush()



    run = ChangeRun(

        policy_id=policy.id,

        old_version_id=old_version.id,

        new_version_id=new_version.id,

        status="IMPACT_READY",

        semantic_mode=semantic.mode,

        llm_model=semantic.model,

        contract_json=
        contract.model_dump(),

        risk_score=
        _risk_score(findings),

    )


    db.add(run)

    db.flush()
    
    for artifact in artifacts:

        db.add(

            ArtifactRecord(

                run_id=run.id,

                external_id=artifact.id,

                name=artifact.name,

                artifact_type=(
                    artifact.artifact_type
                ),

                relationship=(
                    artifact.relationship
                ),

                source_path=(
                    artifact.source_path
                ),

                original_content=(
                    artifact.content
                ),

                current_content=(
                    artifact.content
                ),

            )

        )



    for finding in findings:


        db.add(

            ImpactRecord(

                run_id=run.id,

                artifact_external_id=(
                    finding.artifact_id
                ),

                affected=(
                    finding.affected
                ),

                severity=(
                    finding.severity
                ),

                confidence=(
                    finding.confidence
                ),

                relationship=(
                    finding.relationship
                ),

                evidence=(
                    finding.evidence
                ),

                reason=(
                    finding.reason
                ),

                status=(
                    finding.status
                ),

            )

        )



    for patch in patches:


        db.add(

            PatchRecord(

                run_id=run.id,

                artifact_external_id=(
                    patch.artifact_id
                ),

                original_content=(
                    patch.original_content
                ),

                proposed_content=(
                    patch.proposed_content
                ),

                diff=patch.diff,

                rationale=(
                    patch.rationale
                ),

                status="proposed",

            )

        )



    _audit(

        db,

        run.id,

        "RUN_CREATED",

        {

            "semantic_mode":
            semantic.mode,


            "llm_model":
            semantic.model,


        },

    )



    _audit(

        db,

        run.id,

        "IMPACT_ANALYZED",

        {

            "findings":
            len(findings),


            "patches":
            len(patches),


            "risk_score":
            run.risk_score,


        },

    )



    db.commit()

    db.refresh(run)



    return _analysis_payload(

        run,

        contract,

        artifacts,

        findings,

        patches,

        before,

    )





# =====================================================
# LIST RUNS
# =====================================================


def list_runs(
    db: Session,
) -> list[dict]:


    rows = db.scalars(

        select(ChangeRun)

        .order_by(
            ChangeRun.created_at.desc()
        )

        .limit(20)

    ).all()



    result = []



    for run in rows:


        policy = db.get(

            Policy,

            run.policy_id,

        )



        result.append(

            {

                "id":
                run.id,


                "policy_name":
                (

                    policy.name

                    if policy

                    else

                    "Unknown policy"

                ),


                "status":
                run.status,


                "risk_score":
                run.risk_score,


                "semantic_mode":
                run.semantic_mode,


                "llm_model":
                run.llm_model,


                "created_at":
                run.created_at,


                "updated_at":
                run.updated_at,

            }

        )



    return result





# =====================================================
# GET SINGLE RUN
# =====================================================


def get_run(

    db: Session,

    run_id: str,

) -> dict | None:


    run = db.get(

        ChangeRun,

        run_id,

    )



    if not run:

        return None



    policy = db.get(

        Policy,

        run.policy_id,

    )



    artifacts = db.scalars(

        select(ArtifactRecord)

        .where(
            ArtifactRecord.run_id == run_id
        )

    ).all()



    impacts = db.scalars(

        select(ImpactRecord)

        .where(
            ImpactRecord.run_id == run_id
        )

    ).all()



    patches = db.scalars(

        select(PatchRecord)

        .where(
            PatchRecord.run_id == run_id
        )

    ).all()



    tests = db.scalars(

        select(
            VerificationTestRecord
        )

        .where(
            VerificationTestRecord.run_id
            ==
            run_id
        )

    ).all()



    events = db.scalars(

        select(AuditEvent)

        .where(
            AuditEvent.run_id == run_id
        )

        .order_by(
            AuditEvent.created_at
        )

    ).all()



    artifact_names = {

        artifact.external_id:
        artifact.name

        for artifact in artifacts

    }



    return {


        "id":
        run.id,


        "policy_name":

        (
            policy.name

            if policy

            else

            "Unknown policy"

        ),


        "status":
        run.status,


        "risk_score":
        run.risk_score,


        "semantic_mode":
        run.semantic_mode,


        "llm_model":
        run.llm_model,


        "contract":
        run.contract_json,


        "artifacts":

        [

            {

                "id":
                artifact.external_id,


                "name":
                artifact.name,


                "artifact_type":
                artifact.artifact_type,


                "relationship":
                artifact.relationship,


                "source_path":
                artifact.source_path,


                "content":
                artifact.current_content,


                "original_content":
                artifact.original_content,


                "current_content":
                artifact.current_content,

            }

            for artifact in artifacts

        ],


        "impacts":

        [

            {

                "artifact_id":
                impact.artifact_external_id,


                "artifact_name":

                artifact_names.get(

                    impact.artifact_external_id,

                    impact.artifact_external_id,

                ),


                "affected":
                impact.affected,


                "severity":
                impact.severity,


                "confidence":
                impact.confidence,


                "relationship":
                impact.relationship,


                "evidence":
                impact.evidence,


                "reason":
                impact.reason,


                "status":
                impact.status,


            }

            for impact in impacts

        ],


        "patches":

        [

            {

                "id":
                patch.id,


                "artifact_id":
                patch.artifact_external_id,


                "status":
                patch.status,


                "diff":
                patch.diff,


                "rationale":
                patch.rationale,


            }

            for patch in patches

        ],


        "verification_tests":

        [

            {

                "name":
                test.test_name,


                "input":
                test.input_json,


                "expected":
                test.expected_json,


                "actual":
                test.actual_json,


                "passed":
                test.passed,


            }

            for test in tests

        ],


        "events":

        [

            {

                "event_type":
                event.event_type,


                "actor":
                event.actor,


                "payload":
                event.payload,


                "created_at":
                event.created_at,


            }

            for event in events

        ],


        "created_at":
        run.created_at,


        "updated_at":
        run.updated_at,

    }

# =====================================================
# APPROVE PATCHES
# =====================================================


def approve_run(
    db: Session,
    run_id: str,
    actor: str = "reviewer",
) -> dict | None:


    run = db.get(
        ChangeRun,
        run_id,
    )


    if not run:

        return None



    patches = db.scalars(

        select(PatchRecord)

        .where(
            PatchRecord.run_id == run_id
        )

    ).all()



    artifacts = db.scalars(

        select(ArtifactRecord)

        .where(
            ArtifactRecord.run_id == run_id
        )

    ).all()



    artifact_map = {

        artifact.external_id:
        artifact

        for artifact in artifacts

    }



    for patch in patches:


        patch.status = "approved"


        patch.approved_at = _utcnow()



        artifact = artifact_map.get(

            patch.artifact_external_id

        )


        if artifact:

            artifact.current_content = (

                patch.proposed_content

            )



    run.status = "PATCH_APPROVED"



    _audit(

        db,

        run_id,

        "PATCHES_APPROVED",

        {

            "count":
            len(patches)

        },

        actor=actor,

    )



    db.commit()



    return {


        "run_id":
        run_id,


        "status":
        run.status,


        "approved_patches":
        len(patches),

    }





# =====================================================
# DETECT IMPLEMENTED VALUE
# =====================================================


def _implemented_threshold(

    artifacts: list[ArtifactRecord],

    fallback: float,

) -> float:


    patterns = [

        r"purchase_age_days\s*<=\s*(\d+(?:\.\d+)?)",

        r"refund.*?within\s*(\d+(?:\.\d+)?)\s*(?:calendar\s*)?days",

        r"(\d+(?:\.\d+)?)\s*(?:calendar\s*)?days",

    ]



    for artifact in artifacts:


        content = (

            artifact.current_content

            or ""

        )



        for pattern in patterns:


            match = re.search(

                pattern,

                content,

                re.IGNORECASE,

            )


            if match:


                return float(

                    match.group(1)

                )



    return fallback





# =====================================================
# VERIFY RUN
# =====================================================


def verify_run(

    db: Session,

    run_id: str,

) -> dict | None:



    run = db.get(

        ChangeRun,

        run_id,

    )



    if not run:

        return None




    patches = db.scalars(

        select(PatchRecord)

        .where(
            PatchRecord.run_id == run_id
        )

    ).all()



    if any(

        patch.status != "approved"

        for patch in patches

    ):

        raise ValueError(

            "All patches must be approved first."

        )



    contract = PolicyContract.model_validate(

        run.contract_json

    )



    artifacts = db.scalars(

        select(ArtifactRecord)

        .where(
            ArtifactRecord.run_id == run_id
        )

    ).all()



    implemented = _implemented_threshold(

        artifacts,

        fallback=float(

            contract.old_rule.value

        ),

    )



    report = VerificationEngine().run(

        contract,

        implemented_threshold=implemented,

    )



    old_tests = db.scalars(

        select(
            VerificationTestRecord
        )

        .where(
            VerificationTestRecord.run_id
            ==
            run_id
        )

    ).all()



    for test in old_tests:

        db.delete(test)



    db.flush()




    for case in report.cases:


        db.add(

            VerificationTestRecord(

                run_id=run_id,

                test_name=case.name,

                input_json=case.input,

                expected_json={

                    "value":
                    case.expected

                },

                actual_json={

                    "value":
                    case.actual

                },

                passed=case.passed,

            )

        )




    evidence = json.dumps(

        {

            "run_id":
            run_id,


            "implemented":
            implemented,


            "verification":
            report.model_dump(),

        },

        sort_keys=True,

        default=str,

    )



    evidence_hash = hashlib.sha256(

        evidence.encode()

    ).hexdigest()




    receipt = ProofReceipt(

        policy_name=
        contract.policy_name,


        change_summary=(

            f"{contract.old_rule.value} days → "

            f"{contract.new_rule.value} days"

        ),


        artifacts_examined=
        len(artifacts),


        affected_artifacts=
        len(artifacts),


        confirmed_inconsistencies=0,


        critical_inconsistencies=0,


        approved_fixes=
        len(patches),


        verification_tests=
        report.total,


        tests_passed=
        report.passed,


        tests_failed=
        report.failed,


        policy_coverage_percent=(

            100.0

            if report.verified

            else

            round(

                report.passed /
                max(
                    1,
                    report.total
                )
                *
                100,

                1,

            )

        ),


        behavior_verification=(

            "PASSED"

            if report.verified

            else

            "FAILED"

        ),


        evidence_hash=evidence_hash,

    )




    run.status = (

        "VERIFIED"

        if report.verified

        else

        "VERIFICATION_FAILED"

    )



    _audit(

        db,

        run_id,

        "VERIFICATION_COMPLETED",

        {

            "implemented_threshold":
            implemented,


            "passed":
            report.passed,


            "failed":
            report.failed,


            "evidence_hash":
            evidence_hash,

        },

    )



    db.commit()




    # =================================================
    # EMAIL ALERT
    # =================================================


    try:


        print(
            "SENDING VERIFIED EMAIL"
        )



        send_verified_alert(

            to_email=
            "dev.alishasajjad@gmail.com",


            policy_name=
            contract.policy_name,


            run_id=
            run_id,


            receipt_hash=
            evidence_hash,

        )



        print(
            "VERIFIED EMAIL SENT"
        )



    except Exception as e:


        print(

            f"EMAIL ERROR: {e}"

        )




    return {


        "run_id":
        run_id,


        "verification_after_fix":
        report,


        "receipt":
        receipt,

    }