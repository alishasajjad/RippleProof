from __future__ import annotations

import hashlib
import json

from app.schemas.contracts import (
    Artifact,
    PolicyChangeRequest,
    ProofReceipt,
)

from app.services.policy_engine import (
    PolicyEngine,
)

from app.services.impact_engine import (
    ImpactEngine,
)

from app.services.patch_engine import (
    PatchEngine,
)

from app.services.verification_engine import (
    VerificationEngine,
)



def demo_policy_change() -> PolicyChangeRequest:

    return PolicyChangeRequest(

        policy_name=
        "Customer Refund Policy",

        old_text=
        "Customers may request a full refund within 30 calendar days of purchase.",

        new_text=
        "Customers may request a full refund within 14 calendar days of purchase.",

    )




def demo_artifacts() -> list[Artifact]:

    return [

        Artifact(

            id="policy-doc",

            name="refund_policy.md",

            artifact_type="DOCUMENT",

            relationship="DESCRIBES",

            content=
            "Customers may request a full refund within 14 calendar days of purchase.",

        ),



        Artifact(

            id="faq",

            name="Website FAQ",

            artifact_type="WEBSITE",

            relationship="DESCRIBES",

            content=
            """
            Q: Can I get a refund?

            A: Yes, refunds are available within 30 days of purchase.
            """,

        ),



        Artifact(

            id="bot",

            name="Support Chatbot",

            artifact_type="CHATBOT",

            relationship="DESCRIBES",

            content=
            """
            If asked about refunds,
            tell customers they are eligible within 30 days of purchase.
            """,

        ),



        Artifact(

            id="form",

            name="Refund Form",

            artifact_type="FORM",

            relationship="DEPENDS_ON",

            content=
            "Refund request form available for purchases made in the last 30 days.",

        ),



        Artifact(

            id="api",

            name="Refund Eligibility API",

            artifact_type="API",

            relationship="ENFORCES",

            source_path=
            "refund_service.py:42",

            content=
            """
            def is_refund_eligible(purchase_age_days):

                return purchase_age_days <= 30
            """,

        ),

    ]





def analyze_demo() -> dict:


    request = demo_policy_change()


    contract = (
        PolicyEngine()
        .parse_change(
            request
        )
    )


    artifacts = demo_artifacts()



    findings = (
        ImpactEngine()
        .analyze(
            contract,
            artifacts,
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



    return {

        "request":
        request,


        "contract":
        contract,


        "artifacts":
        artifacts,


        "findings":
        findings,


        "patches":
        patches,


        "verification_before_fix":
        verification_before,

    }






def verify_demo() -> dict:


    analyzed = analyze_demo()


    contract = analyzed["contract"]

    artifacts = analyzed["artifacts"]

    findings = analyzed["findings"]

    patches = analyzed["patches"]



    verification_after = (
        VerificationEngine()
        .run(
            contract,
            implemented_threshold=float(
                contract.new_rule.value
            ),
        )
    )



    stale = sum(
        finding.status == "stale"
        for finding in findings
    )



    critical = sum(
        finding.status == "stale"
        and finding.severity == "critical"
        for finding in findings
    )



    affected = sum(
        finding.affected
        for finding in findings
    )



    evidence = json.dumps(

        {

            "policy":
            contract.model_dump(),

            "verification":
            verification_after.model_dump(),

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


        change_summary=
        (
            f"{contract.old_rule.value} days → "
            f"{contract.new_rule.value} days"
        ),


        artifacts_examined=
        len(artifacts),


        affected_artifacts=
        affected,


        confirmed_inconsistencies=
        stale,


        critical_inconsistencies=
        critical,


        approved_fixes=
        len(patches),


        verification_tests=
        verification_after.total,


        tests_passed=
        verification_after.passed,


        tests_failed=
        verification_after.failed,


        policy_coverage_percent=
        100.0
        if verification_after.verified
        else 0.0,


        behavior_verification=
        "PASSED"
        if verification_after.verified
        else "FAILED",


        evidence_hash=
        evidence_hash,

    )



    return {

        "verification_after_fix":
        verification_after,


        "receipt":
        receipt,

    }





def run_demo()->dict:

    return {

        **analyze_demo(),

        **verify_demo(),

    }