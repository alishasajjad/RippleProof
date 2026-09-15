from __future__ import annotations

import hashlib
import json
import re

from datetime import datetime, timezone
from typing import Sequence

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
    PolicyChangeRequest,
    PolicyContract,
    ProofReceipt,
)

from app.services.impact_engine import ImpactEngine
from app.services.llm_service import LLMService
from app.services.patch_engine import PatchEngine
from app.services.verification_engine import VerificationEngine
from app.services.email_alerts import send_verified_alert



def utcnow():
    return datetime.now(timezone.utc)



def calculate_risk_score(
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

    score = sum(
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
            (score / maximum) * 100,
        ),
        1,
    )



def create_custom_run(
    db: Session,
    request: PolicyChangeRequest,
    artifacts: list[Artifact],
) -> dict:

    if not artifacts:
        raise ValueError(
            "At least one artifact required."
        )


    llm = LLMService()


    semantic = (
        llm
        .interpret_policy_change(
            request
        )
    )


    contract = semantic.contract


    if not isinstance(
        contract.old_rule.value,
        (int, float),
    ):
        raise ValueError(
            "Only numeric policies supported."
        )


    if not isinstance(
        contract.new_rule.value,
        (int, float),
    ):
        raise ValueError(
            "Only numeric policies supported."
        )


    fallback_findings = (
        ImpactEngine()
        .analyze(
            contract,
            artifacts,
        )
    )


    findings = (
        llm
        .analyze_artifacts(
            contract,
            artifacts,
            fallback_findings,
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


    verification_before = (
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
        description="RippleProof policy analysis",
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


    risk_score = calculate_risk_score(
        findings
    )


    run = ChangeRun(
        policy_id=policy.id,
        old_version_id=old_version.id,
        new_version_id=new_version.id,
        status="IMPACT_READY",
        risk_score=risk_score,
        semantic_mode=semantic.mode,
        llm_model=semantic.model,
        contract_json=contract.model_dump(),
    )


    db.add(run)
    db.flush()



    for artifact in artifacts:

        db.add(
            ArtifactRecord(
                run_id=run.id,
                external_id=artifact.id,
                name=artifact.name,
                artifact_type=artifact.artifact_type,
                relationship=artifact.relationship,
                source_path=artifact.source_path,
                original_content=artifact.content,
                current_content=artifact.content,
            )
        )



    for finding in findings:

        db.add(
            ImpactRecord(
                run_id=run.id,
                artifact_external_id=finding.artifact_id,
                affected=finding.affected,
                severity=finding.severity,
                confidence=finding.confidence,
                relationship=finding.relationship,
                evidence=finding.evidence,
                reason=finding.reason,
                status=finding.status,
            )
        )



    for patch in patches:

        db.add(
            PatchRecord(
                run_id=run.id,
                artifact_external_id=patch.artifact_id,
                original_content=patch.original_content,
                proposed_content=patch.proposed_content,
                diff=patch.diff,
                rationale=patch.rationale,
                status="proposed",
            )
        )



    db.add(
        AuditEvent(
            run_id=run.id,
            event_type="CUSTOM_RUN_CREATED",
            actor="user",
            payload={
                "policy_name": request.policy_name,
                "uploaded_artifacts": len(artifacts),
                "semantic_mode": semantic.mode,
                "llm_model": semantic.model,
            },
        )
    )


    db.commit()
    db.refresh(run)


    return {
        "run_id": run.id,
        "engine": {
            "semantic_mode": semantic.mode,
            "llm_model": semantic.model,
            "database": "postgresql",
            "risk_score": run.risk_score,
        },
        "request": request,
        "contract": contract,
        "artifacts": artifacts,
        "findings": findings,
        "patches": patches,
        "verification_before_fix":
            verification_before,
    }




def _implemented_threshold(
    artifacts: Sequence[ArtifactRecord],
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




def verify_run(
    db: Session,
    run_id: str,
) -> dict | None:
    
    print("VERIFY_RUN STARTED", run_id)


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
            "Approve patches first."
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
            VerificationTestRecord.run_id == run_id
        )
    ).all()



    for old in old_tests:
        db.delete(old)


    db.flush()



    for case in report.cases:

        db.add(
            VerificationTestRecord(
                run_id=run_id,
                test_name=case.name,
                input_json=case.input,
                expected_json={
                    "value": case.expected
                },
                actual_json={
                    "value": case.actual
                },
                passed=case.passed,
            )
        )



    impacts = db.scalars(
        select(ImpactRecord)
        .where(
            ImpactRecord.run_id == run_id
        )
    ).all()



    stale = sum(
        impact.status == "stale"
        for impact in impacts
    )


    critical = sum(
        impact.status == "stale"
        and impact.severity == "critical"
        for impact in impacts
    )


    affected = sum(
        impact.affected
        for impact in impacts
    )



    evidence_payload = json.dumps(
        {
            "run_id": run_id,
            "implemented": implemented,
            "verification": report.model_dump(),
        },
        sort_keys=True,
        default=str,
    )


    evidence_hash = hashlib.sha256(
        evidence_payload.encode()
    ).hexdigest()



    receipt = ProofReceipt(

        policy_name=contract.policy_name,

        change_summary=(
            f"{contract.old_rule.value} days → "
            f"{contract.new_rule.value} days"
        ),

        artifacts_examined=len(artifacts),

        affected_artifacts=affected,

        confirmed_inconsistencies=stale,

        critical_inconsistencies=critical,

        approved_fixes=len(patches),

        verification_tests=report.total,

        tests_passed=report.passed,

        tests_failed=report.failed,

        policy_coverage_percent=(
            100.0
            if report.verified
            else round(
                report.passed /
                max(
                    1,
                    report.total,
                )
                * 100,
                1,
            )
        ),

        behavior_verification=(
            "PASSED"
            if report.verified
            else "FAILED"
        ),

        evidence_hash=evidence_hash,
    )



    run.status = (
        "VERIFIED"
        if report.verified
        else "VERIFICATION_FAILED"
    )



    db.add(
        AuditEvent(
            run_id=run_id,
            event_type="VERIFICATION_COMPLETED",
            actor="system",
            payload={
                "implemented_threshold": implemented,
                "passed": report.passed,
                "failed": report.failed,
                "evidence_hash": evidence_hash,
            },
        )
    )



    db.commit()
    
    print("SENDING VERIFIED EMAIL")
    
    send_verified_alert(
    to_email="dev.alishasajjad@gmail.com",
    policy_name=contract.policy_name,
    run_id=run_id,
    receipt_hash=evidence_hash,
    )


    return {

        "run_id":run_id,

        "verification_after_fix":
        report,

        "receipt":
        receipt

    }