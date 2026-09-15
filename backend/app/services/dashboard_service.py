from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    ArtifactRecord,
    ChangeRun,
    ImpactRecord,
    PatchRecord,
)

from app.services.persistence_service import (
    list_runs,
)


def _count(
    db: Session,
    statement,
) -> int:
    value = db.scalar(
        statement
    )

    return int(
        value or 0
    )


def dashboard_summary(
    db: Session,
) -> dict:

    total_runs = _count(
        db,
        select(
            func.count()
        ).select_from(
            ChangeRun
        ),
    )

    verified_runs = _count(
        db,
        select(
            func.count()
        )
        .select_from(
            ChangeRun
        )
        .where(
            ChangeRun.status
            == "VERIFIED"
        ),
    )

    impact_ready_runs = _count(
        db,
        select(
            func.count()
        )
        .select_from(
            ChangeRun
        )
        .where(
            ChangeRun.status
            == "IMPACT_READY"
        ),
    )

    approved_runs = _count(
        db,
        select(
            func.count()
        )
        .select_from(
            ChangeRun
        )
        .where(
            ChangeRun.status
            == "PATCH_APPROVED"
        ),
    )

    artifacts = _count(
        db,
        select(
            func.count()
        ).select_from(
            ArtifactRecord
        ),
    )

    stale_findings = _count(
        db,
        select(
            func.count()
        )
        .select_from(
            ImpactRecord
        )
        .where(
            ImpactRecord.status
            == "stale"
        ),
    )

    critical_findings = _count(
        db,
        select(
            func.count()
        )
        .select_from(
            ImpactRecord
        )
        .where(
            ImpactRecord.status
            == "stale",
            ImpactRecord.severity
            == "critical",
        ),
    )

    patches = _count(
        db,
        select(
            func.count()
        ).select_from(
            PatchRecord
        ),
    )

    approved_patches = _count(
        db,
        select(
            func.count()
        )
        .select_from(
            PatchRecord
        )
        .where(
            PatchRecord.status
            == "approved"
        ),
    )

    average_risk_raw = db.scalar(
        select(
            func.avg(
                ChangeRun.risk_score
            )
        )
    )

    average_risk = round(
        float(
            average_risk_raw
            or 0
        ),
        1,
    )

    verification_success_rate = (
        round(
            verified_runs
            / total_runs
            * 100,
            1,
        )
        if total_runs
        else 0.0
    )

    patch_approval_rate = (
        round(
            approved_patches
            / patches
            * 100,
            1,
        )
        if patches
        else 0.0
    )

    recent_runs = (
        list_runs(
            db
        )
        [:8]
    )

    return {
        "metrics": {
            "total_runs":
                total_runs,

            "verified_runs":
                verified_runs,

            "impact_ready_runs":
                impact_ready_runs,

            "approved_runs":
                approved_runs,

            "artifacts_examined":
                artifacts,

            "stale_findings":
                stale_findings,

            "critical_findings":
                critical_findings,

            "patches_generated":
                patches,

            "approved_patches":
                approved_patches,

            "average_risk":
                average_risk,

            "verification_success_rate":
                verification_success_rate,

            "patch_approval_rate":
                patch_approval_rate,
        },

        "recent_runs":
            recent_runs,
    }