from __future__ import annotations

from typing import Any

from app.schemas.contracts import (
    PolicyContract,
    VerificationCase,
    VerificationReport,
)


class VerificationEngine:
    """
    Deterministic executable verification.

    LLM interprets policy meaning.
    This engine proves whether actual behaviour
    satisfies the structured policy contract.
    """

    def run(
        self,
        contract: PolicyContract,
        implemented_threshold: float,
    ) -> VerificationReport:

        new_value = contract.new_rule.value
        old_value = contract.old_rule.value


        if not isinstance(
            new_value,
            (int, float),
        ):
            raise ValueError(
                "Verification requires numeric new policy value."
            )


        if not isinstance(
            old_value,
            (int, float),
        ):
            raise ValueError(
                "Verification requires numeric old policy value."
            )


        boundary_values = (
            self._build_boundary_suite(
                new_value=float(new_value),
                old_value=float(old_value),
                supplied=contract.boundary_values,
            )
        )


        cases: list[VerificationCase] = []


        field_name = (
            contract.new_rule.field
            or "policy_value"
        )


        operator = (
            contract.new_rule.operator
        )


        for raw_value in boundary_values:


            expected = self._evaluate(
                actual=raw_value,
                operator=operator,
                threshold=float(new_value),
            )


            actual = self._evaluate(
                actual=raw_value,
                operator=operator,
                threshold=float(
                    implemented_threshold
                ),
            )


            passed = (
                expected == actual
            )


            display_value: Any = (
                int(raw_value)
                if float(raw_value).is_integer()
                else raw_value
            )


            cases.append(
                VerificationCase(
                    name=(
                        f"{field_name}="
                        f"{display_value}"
                    ),

                    input={
                        field_name:
                            display_value
                    },

                    expected=expected,

                    actual=actual,

                    passed=passed,
                )
            )


        passed_count = sum(
            case.passed
            for case in cases
        )


        failed_count = (
            len(cases)
            -
            passed_count
        )


        return VerificationReport(
            total=len(cases),

            passed=passed_count,

            failed=failed_count,

            cases=cases,

            verified=(
                failed_count == 0
            ),
        )



    @staticmethod
    def _build_boundary_suite(
        new_value: float,
        old_value: float,
        supplied: list[
            float | int
        ],
    ) -> list[float]:
        """
        Creates regression boundary cases.

        Example:

        old = 30
        new = 14

        Result:

        0,
        13,
        14,
        15,
        30,
        31
        """


        candidates: set[float] = {

            0.0,

            max(
                0.0,
                new_value - 1,
            ),

            new_value,

            new_value + 1,

            old_value,

            old_value + 1,

        }



        for value in supplied:

            if isinstance(
                value,
                (int, float),
            ):

                candidates.add(
                    float(value)
                )


        return sorted(
            candidates
        )



    @staticmethod
    def _evaluate(
        actual: float,
        operator: str,
        threshold: float,
    ) -> bool:


        if operator == "<=":
            return actual <= threshold


        if operator == "<":
            return actual < threshold


        if operator == ">=":
            return actual >= threshold


        if operator == ">":
            return actual > threshold


        if operator == "==":
            return actual == threshold


        if operator == "!=":
            return actual != threshold


        raise ValueError(
            f"Unsupported operator: {operator}"
        )