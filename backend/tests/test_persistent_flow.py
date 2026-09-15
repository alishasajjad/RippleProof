import os
from pathlib import Path


# ---------------------------------------------------------
# Test database configuration
# ---------------------------------------------------------

TEST_DB = (
    Path(__file__).parent
    / "phase3_test.db"
)


# IMPORTANT:
# Environment variables must be set BEFORE importing app.db
os.environ["DATABASE_URL"] = (
    f"sqlite:///{TEST_DB.as_posix()}"
)

# Tests must never call a real LLM
os.environ["LLM_MODE"] = "off"


# ---------------------------------------------------------
# App imports
# ---------------------------------------------------------

from app.db import (  # noqa: E402
    Base,
    SessionLocal,
    engine,
)

from app.services.persistence_service import (  # noqa: E402
    approve_run,
    create_demo_run,
    get_run,
    list_runs,
    verify_run,
)


# ---------------------------------------------------------
# Test setup
# ---------------------------------------------------------

def setup_function():
    """
    Reset the SQLite test database before every test.

    engine.dispose() is important on Windows because SQLite
    database files can stay locked by pooled connections.
    """

    engine.dispose()

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )


# ---------------------------------------------------------
# Test cleanup
# ---------------------------------------------------------

def teardown_module():
    """
    Completely close SQLAlchemy connections before deleting
    the SQLite test database.

    Without engine.dispose(), Windows may raise:
    PermissionError: [WinError 32]
    """

    Base.metadata.drop_all(
        bind=engine
    )

    # Close all pooled SQLite connections
    engine.dispose()

    # Now Windows can safely delete the DB file
    if TEST_DB.exists():
        TEST_DB.unlink()


# ---------------------------------------------------------
# Full Phase 3 persistence lifecycle test
# ---------------------------------------------------------

def test_persistent_run_lifecycle():

    with SessionLocal() as db:

        # -------------------------------------------------
        # 1. Create persistent analysis run
        # -------------------------------------------------

        analysis = create_demo_run(
            db
        )

        run_id = analysis[
            "run_id"
        ]


        assert run_id is not None

        assert (
            analysis["engine"][
                "database"
            ]
            == "persistent"
        )

        assert (
            analysis["engine"][
                "semantic_mode"
            ]
            == "deterministic_fallback"
        )


        # -------------------------------------------------
        # 2. Confirm policy contract
        # -------------------------------------------------

        contract = analysis[
            "contract"
        ]

        assert (
            contract.new_rule.value
            == 14
        )

        assert (
            contract.old_rule.value
            == 30
        )


        # -------------------------------------------------
        # 3. Confirm artifacts
        # -------------------------------------------------

        assert (
            len(
                analysis[
                    "artifacts"
                ]
            )
            == 5
        )


        # -------------------------------------------------
        # 4. Confirm impact findings
        # -------------------------------------------------

        findings = analysis[
            "findings"
        ]

        assert (
            len(findings)
            == 5
        )


        stale_findings = [
            finding
            for finding
            in findings
            if finding.status
            == "stale"
        ]

        assert (
            len(
                stale_findings
            )
            == 4
        )


        critical_findings = [
            finding
            for finding
            in findings
            if (
                finding.status
                == "stale"
                and
                finding.severity
                == "critical"
            )
        ]

        assert (
            len(
                critical_findings
            )
            == 1
        )


        # -------------------------------------------------
        # 5. Confirm patch proposals
        # -------------------------------------------------

        patches = analysis[
            "patches"
        ]

        assert (
            len(patches)
            == 4
        )


        # -------------------------------------------------
        # 6. Confirm before-fix verification fails
        # -------------------------------------------------

        before = analysis[
            "verification_before_fix"
        ]

        assert (
            before.verified
            is False
        )


        # -------------------------------------------------
        # 7. Confirm run persisted in database
        # -------------------------------------------------

        rows = list_runs(
            db
        )

        assert (
            len(rows)
            >= 1
        )

        assert (
            rows[0]["id"]
            == run_id
        )

        assert (
            rows[0][
                "status"
            ]
            == "IMPACT_READY"
        )


        # -------------------------------------------------
        # 8. Human approval
        # -------------------------------------------------

        approved = approve_run(
            db,
            run_id,
        )


        assert (
            approved
            is not None
        )

        assert (
            approved[
                "approved_patches"
            ]
            == 4
        )

        assert (
            approved[
                "status"
            ]
            == "PATCH_APPROVED"
        )


        # -------------------------------------------------
        # 9. Verify patched implementation
        # -------------------------------------------------

        verified = verify_run(
            db,
            run_id,
        )


        assert (
            verified
            is not None
        )


        verification_report = (
            verified[
                "verification_after_fix"
            ]
        )


        assert (
            verification_report
            .verified
            is True
        )

        assert (
            verification_report
            .total
            == 6
        )

        assert (
            verification_report
            .passed
            == 6
        )

        assert (
            verification_report
            .failed
            == 0
        )


        # -------------------------------------------------
        # 10. Verify proof receipt
        # -------------------------------------------------

        receipt = verified[
            "receipt"
        ]


        assert (
            receipt
            .behavior_verification
            == "PASSED"
        )

        assert (
            receipt
            .verification_tests
            == 6
        )

        assert (
            receipt
            .tests_passed
            == 6
        )

        assert (
            receipt
            .tests_failed
            == 0
        )

        assert (
            receipt
            .policy_coverage_percent
            == 100.0
        )

        assert (
            len(
                receipt
                .evidence_hash
            )
            == 64
        )


        # -------------------------------------------------
        # 11. Reload run from database
        # -------------------------------------------------

        detail = get_run(
            db,
            run_id,
        )


        assert (
            detail
            is not None
        )

        assert (
            detail[
                "status"
            ]
            == "VERIFIED"
        )

        assert (
            detail[
                "risk_score"
            ]
            > 0
        )


        # -------------------------------------------------
        # 12. Verification tests persisted
        # -------------------------------------------------

        assert (
            len(
                detail[
                    "verification_tests"
                ]
            )
            == 6
        )


        assert all(
            test[
                "passed"
            ]
            is True
            for test
            in detail[
                "verification_tests"
            ]
        )


        # -------------------------------------------------
        # 13. Audit trail persisted
        # -------------------------------------------------

        event_types = {
            event[
                "event_type"
            ]
            for event
            in detail[
                "events"
            ]
        }


        assert (
            "RUN_CREATED"
            in event_types
        )

        assert (
            "IMPACT_ANALYZED"
            in event_types
        )

        assert (
            "PATCHES_APPROVED"
            in event_types
        )

        assert (
            "VERIFICATION_COMPLETED"
            in event_types
        )