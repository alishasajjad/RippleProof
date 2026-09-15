from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.contracts import (
    PolicyContract,
)

from app.services.dashboard_service import (
    dashboard_summary,
)

from app.services.verification_engine import (
    VerificationEngine,
)


BENCHMARK_SCENARIOS = [
    {
        "name":
            "Customer refund window",

        "domain":
            "financial",

        "field":
            "refund_period_days",

        "old":
            30,

        "new":
            14,

        "unit":
            "days",
    },

    {
        "name":
            "Manual approval threshold",

        "domain":
            "financial",

        "field":
            "approval_limit",

        "old":
            10000,

        "new":
            5000,

        "unit":
            "USD",
    },

    {
        "name":
            "Free trial period",

        "domain":
            "commercial",

        "field":
            "trial_period_days",

        "old":
            30,

        "new":
            14,

        "unit":
            "days",
    },

    {
        "name":
            "Authentication retry limit",

        "domain":
            "security",

        "field":
            "retry_limit",

        "old":
            5,

        "new":
            3,

        "unit":
            "attempts",
    },

    {
        "name":
            "Payment grace period",

        "domain":
            "financial",

        "field":
            "grace_period_days",

        "old":
            10,

        "new":
            5,

        "unit":
            "days",
    },
]


def _contract(
    scenario: dict,
) -> PolicyContract:

    return (
        PolicyContract
        .model_validate(
            {
                "policy_name":
                    scenario[
                        "name"
                    ],

                "subject":
                    "business rule",

                "attribute":
                    scenario[
                        "field"
                    ],

                "old_rule": {
                    "field":
                        scenario[
                            "field"
                        ],

                    "operator":
                        "<=",

                    "value":
                        scenario[
                            "old"
                        ],

                    "unit":
                        scenario[
                            "unit"
                        ],
                },

                "new_rule": {
                    "field":
                        scenario[
                            "field"
                        ],

                    "operator":
                        "<=",

                    "value":
                        scenario[
                            "new"
                        ],

                    "unit":
                        scenario[
                            "unit"
                        ],
                },

                "change_type":
                    "tightening",

                "risk_domain":
                    scenario[
                        "domain"
                    ],

                "boundary_values":
                    [],
            }
        )
    )


def deterministic_benchmark() -> dict:

    engine = (
        VerificationEngine()
    )

    results = []

    total_before_tests = 0
    total_before_passed = 0

    total_after_tests = 0
    total_after_passed = 0

    for scenario in (
        BENCHMARK_SCENARIOS
    ):

        contract = (
            _contract(
                scenario
            )
        )

        before = (
            engine.run(
                contract,
                implemented_threshold=float(
                    scenario[
                        "old"
                    ]
                ),
            )
        )

        after = (
            engine.run(
                contract,
                implemented_threshold=float(
                    scenario[
                        "new"
                    ]
                ),
            )
        )

        total_before_tests += (
            before.total
        )

        total_before_passed += (
            before.passed
        )

        total_after_tests += (
            after.total
        )

        total_after_passed += (
            after.passed
        )

        results.append(
            {
                "name":
                    scenario[
                        "name"
                    ],

                "domain":
                    scenario[
                        "domain"
                    ],

                "old_value":
                    scenario[
                        "old"
                    ],

                "new_value":
                    scenario[
                        "new"
                    ],

                "unit":
                    scenario[
                        "unit"
                    ],

                "before": {
                    "passed":
                        before.passed,

                    "failed":
                        before.failed,

                    "total":
                        before.total,

                    "verified":
                        before.verified,
                },

                "after": {
                    "passed":
                        after.passed,

                    "failed":
                        after.failed,

                    "total":
                        after.total,

                    "verified":
                        after.verified,
                },
            }
        )

    before_rate = (
        round(
            total_before_passed
            / total_before_tests
            * 100,
            1,
        )
        if total_before_tests
        else 0.0
    )

    after_rate = (
        round(
            total_after_passed
            / total_after_tests
            * 100,
            1,
        )
        if total_after_tests
        else 0.0
    )

    return {
        "benchmark_name":
            "RippleProof Deterministic Proof Benchmark",

        "uses_llm":
            False,

        "scenarios":
            len(results),

        "before": {
            "tests":
                total_before_tests,

            "passed":
                total_before_passed,

            "pass_rate":
                before_rate,
        },

        "after": {
            "tests":
                total_after_tests,

            "passed":
                total_after_passed,

            "pass_rate":
                after_rate,
        },

        "improvement_points":
            round(
                after_rate
                - before_rate,
                1,
            ),

        "results":
            results,
    }


def evaluation_summary(
    db: Session,
) -> dict:

    operational = (
        dashboard_summary(
            db
        )
    )

    benchmark = (
        deterministic_benchmark()
    )

    return {
        "operational":
            operational[
                "metrics"
            ],

        "benchmark":
            {
                "name":
                    benchmark[
                        "benchmark_name"
                    ],

                "scenarios":
                    benchmark[
                        "scenarios"
                    ],

                "before_pass_rate":
                    benchmark[
                        "before"
                    ][
                        "pass_rate"
                    ],

                "after_pass_rate":
                    benchmark[
                        "after"
                    ][
                        "pass_rate"
                    ],

                "improvement_points":
                    benchmark[
                        "improvement_points"
                    ],

                "uses_llm":
                    False,
            },
    }