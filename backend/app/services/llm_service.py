from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.schemas.contracts import (
    Artifact,
    ImpactFinding,
    PolicyChangeRequest,
    PolicyContract,
)

from app.services.policy_engine import (
    PolicyEngine,
)


# =========================================================
# Result object
# =========================================================

@dataclass
class SemanticResult:
    contract: PolicyContract
    mode: str
    model: str | None


# =========================================================
# LLM service
# =========================================================

class LLMService:
    """
    Provider-neutral semantic intelligence layer.

    RippleProof currently uses Groq through its
    OpenAI-compatible REST API.

    AI responsibilities:
    - Understand policy meaning
    - Convert policy change into structured contract
    - Detect semantic artifact dependencies

    AI does NOT establish final proof.
    Final behaviour verification remains deterministic.
    """

    def __init__(
        self,
    ) -> None:

        self.provider = os.getenv(
            "LLM_PROVIDER",
            "groq",
        )

        self.base_url = os.getenv(
            "LLM_BASE_URL",
            "",
        ).rstrip("/")

        self.api_key = (
            os.getenv(
                "GROQ_API_KEY",
                "",
            )
            or
            os.getenv(
                "LLM_API_KEY",
                "",
            )
        )

        self.model = os.getenv(
            "LLM_MODEL",
            "",
        )

        self.mode = os.getenv(
            "LLM_MODE",
            "auto",
        ).lower()


    # -----------------------------------------------------
    # Configuration
    # -----------------------------------------------------

    @property
    def configured(
        self,
    ) -> bool:

        return bool(
            self.base_url
            and
            self.api_key
            and
            self.model
            and
            self.mode
            != "off"
        )


    def status(
        self,
    ) -> dict:

        return {
            "provider": (
                self.provider
            ),
            "configured": (
                self.configured
            ),
            "mode": (
                self.mode
            ),
            "model": (
                self.model
                or None
            ),
            "base_url": (
                self.base_url
                or None
            ),
            "api_key_present": (
                bool(
                    self.api_key
                )
            ),
        }


    # -----------------------------------------------------
    # Connection test
    # -----------------------------------------------------

    def test_connection(
        self,
    ) -> dict:

        base = self.status()

        if not self.configured:

            return {
                **base,
                "reachable": False,
                "model_available": False,
                "message": (
                    "LLM is not fully configured."
                ),
            }

        try:

            with httpx.Client(
                timeout=20.0
            ) as client:

                response = client.get(
                    (
                        f"{self.base_url}"
                        "/models"
                    ),
                    headers={
                        "Authorization":
                            (
                                f"Bearer "
                                f"{self.api_key}"
                            ),

                        "Content-Type":
                            "application/json",
                    },
                )

                response.raise_for_status()

                payload = (
                    response.json()
                )


            model_ids = {
                item.get(
                    "id"
                )
                for item
                in payload.get(
                    "data",
                    [],
                )
            }


            model_available = (
                self.model
                in model_ids
            )


            return {
                **base,

                "reachable": True,

                "model_available":
                    model_available,

                "available_models_count":
                    len(
                        model_ids
                    ),

                "message": (
                    "Groq connection successful."
                    if model_available
                    else (
                        "Groq connection works, "
                        "but configured model "
                        "was not found."
                    )
                ),
            }

        except Exception as exc:

            return {
                **base,

                "reachable": False,

                "model_available": False,

                "message": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            }


    # =====================================================
    # Policy interpretation
    # =====================================================

    def interpret_policy_change(
        self,
        request: PolicyChangeRequest,
    ) -> SemanticResult:

        if not self.configured:

            return (
                self
                ._deterministic_result(
                    request
                )
            )


        try:

            payload = self._chat_json(

                system=(
                    "You are RippleProof's "
                    "policy semantics engine. "

                    "Convert the supplied old "
                    "and new business-policy "
                    "statements into a precise "
                    "machine-verifiable policy "
                    "contract. "

                    "Return ONLY valid JSON. "

                    "Do not add markdown. "
                    "Do not explain outside JSON. "
                    "Do not invent facts. "

                    "Identify the subject, business "
                    "attribute, old and new rules, "
                    "comparison operators, values, "
                    "units, change type, risk domain "
                    "and useful numeric boundary "
                    "values for verification."
                ),

                user=json.dumps(
                    {
                        "policy_name":
                            request.policy_name,

                        "old_text":
                            request.old_text,

                        "new_text":
                            request.new_text,

                        "required_json_shape": {
                            "policy_name":
                                "string",

                            "subject":
                                "string",

                            "attribute":
                                "string",

                            "old_rule": {
                                "field":
                                    "string",

                                "operator":
                                    "<=|<|>=|>|==|!=",

                                "value":
                                    "number or string",

                                "unit":
                                    "string or null",
                            },

                            "new_rule": {
                                "field":
                                    "string",

                                "operator":
                                    "<=|<|>=|>|==|!=",

                                "value":
                                    "number or string",

                                "unit":
                                    "string or null",
                            },

                            "change_type":
                                "string",

                            "risk_domain":
                                "string",

                            "boundary_values":
                                [
                                    "number"
                                ],
                        },
                    },
                    default=str,
                ),
            )


            contract = (
                PolicyContract
                .model_validate(
                    payload
                )
            )


            contract = (
                self
                ._ensure_boundaries(
                    contract
                )
            )


            return SemanticResult(
                contract=contract,
                mode="llm",
                model=self.model,
            )


        except Exception:

            if (
                self.mode
                == "required"
            ):
                raise


            return (
                self
                ._deterministic_result(
                    request
                )
            )


    # =====================================================
    # Artifact semantic analysis
    # =====================================================

    def analyze_artifacts(
        self,
        contract: PolicyContract,
        artifacts: list[
            Artifact
        ],
        fallback_findings: list[
            ImpactFinding
        ],
    ) -> list[
        ImpactFinding
    ]:

        if not self.configured:

            return (
                fallback_findings
            )


        try:

            payload = self._chat_json(

                system=(
                    "You are RippleProof's "
                    "semantic dependency analyzer. "

                    "You receive one structured "
                    "policy contract and a set of "
                    "heterogeneous organizational "
                    "artifacts. "

                    "Determine whether each artifact "
                    "describes, references, depends on "
                    "or enforces the changed rule. "

                    "Return ONLY JSON. "
                    "No markdown. "

                    "Return exactly one finding for "
                    "every supplied artifact. "

                    "status must be one of: "
                    "compliant, stale, unknown. "

                    "severity must be one of: "
                    "low, medium, high, critical. "

                    "Executable API/backend enforcement "
                    "that contradicts the official "
                    "policy should normally be critical. "

                    "Forms or chatbots that produce "
                    "incorrect decisions should normally "
                    "be high. "

                    "Documentation wording is normally "
                    "medium or low depending on impact. "

                    "Evidence must come directly from "
                    "the supplied artifact. "
                    "Never invent evidence."
                ),

                user=json.dumps(
                    {
                        "policy_contract":
                            contract.model_dump(),

                        "artifacts": [
                            artifact
                            .model_dump()

                            for artifact
                            in artifacts
                        ],

                        "required_json_shape": {
                            "findings": [
                                {
                                    "artifact_id":
                                        (
                                            "exact "
                                            "supplied id"
                                        ),

                                    "artifact_name":
                                        "string",

                                    "affected":
                                        "boolean",

                                    "severity":
                                        (
                                            "low|medium|"
                                            "high|critical"
                                        ),

                                    "confidence":
                                        (
                                            "number "
                                            "between 0 and 1"
                                        ),

                                    "relationship":
                                        "string",

                                    "evidence":
                                        "string",

                                    "reason":
                                        "string",

                                    "status":
                                        (
                                            "compliant|"
                                            "stale|unknown"
                                        ),
                                }
                            ]
                        },
                    },
                    default=str,
                ),
            )


            raw_findings = (
                payload.get(
                    "findings",
                    []
                )
            )


            findings = [
                ImpactFinding
                .model_validate(
                    item
                )

                for item
                in raw_findings
            ]


            supplied_ids = {
                artifact.id
                for artifact
                in artifacts
            }


            returned_ids = {
                finding.artifact_id
                for finding
                in findings
            }


            if (
                supplied_ids
                != returned_ids
            ):

                raise ValueError(
                    "LLM must return "
                    "exactly one finding "
                    "for every artifact."
                )


            return findings


        except Exception:

            if (
                self.mode
                == "required"
            ):
                raise


            return (
                fallback_findings
            )


    # =====================================================
    # Internal API call
    # =====================================================

    def _chat_json(
        self,
        system: str,
        user: str,
    ) -> dict[
        str,
        Any
    ]:

        last_error: Exception | None = None


        for attempt in range(
            2
        ):

            try:

                with httpx.Client(
                    timeout=60.0
                ) as client:

                    response = (
                        client.post(
                            (
                                f"{self.base_url}"
                                "/chat/completions"
                            ),

                            headers={
                                "Authorization":
                                    (
                                        "Bearer "
                                        f"{self.api_key}"
                                    ),

                                "Content-Type":
                                    "application/json",
                            },

                            json={
                                "model":
                                    self.model,

                                "temperature":
                                    0,

                                "response_format": {
                                    "type":
                                        "json_object"
                                },

                                "messages": [
                                    {
                                        "role":
                                            "system",

                                        "content":
                                            system,
                                    },
                                    {
                                        "role":
                                            "user",

                                        "content":
                                            user,
                                    },
                                ],
                            },
                        )
                    )


                    response.raise_for_status()


                    body = (
                        response.json()
                    )


                    content = (
                        body[
                            "choices"
                        ][0][
                            "message"
                        ][
                            "content"
                        ]
                    )


                return (
                    self
                    ._extract_json(
                        content
                    )
                )


            except Exception as exc:

                last_error = exc


                if attempt == 0:
                    continue


        if last_error:
            raise last_error


        raise RuntimeError(
            "Unknown LLM error."
        )


    # =====================================================
    # Helpers
    # =====================================================

    @staticmethod
    def _extract_json(
        text: str,
    ) -> dict[
        str,
        Any
    ]:

        text = (
            text.strip()
        )


        if text.startswith(
            "```"
        ):

            text = re.sub(
                r"^```(?:json)?\s*",
                "",
                text,
            )

            text = re.sub(
                r"\s*```$",
                "",
                text,
            )


        try:

            value = (
                json.loads(
                    text
                )
            )


            if not isinstance(
                value,
                dict,
            ):
                raise ValueError(
                    "Expected JSON object."
                )


            return value


        except (
            json.JSONDecodeError,
            ValueError,
        ):

            start = (
                text.find(
                    "{"
                )
            )

            end = (
                text.rfind(
                    "}"
                )
            )


            if (
                start == -1
                or
                end == -1
                or
                end <= start
            ):

                raise ValueError(
                    "Model did not "
                    "return valid JSON."
                )


            value = json.loads(
                text[
                    start:
                    end + 1
                ]
            )


            if not isinstance(
                value,
                dict,
            ):
                raise ValueError(
                    "Expected JSON object."
                )


            return value


    @staticmethod
    def _ensure_boundaries(
        contract:
            PolicyContract,
    ) -> PolicyContract:

        if (
            contract
            .boundary_values
        ):
            return contract


        new_value = (
            contract
            .new_rule
            .value
        )

        old_value = (
            contract
            .old_rule
            .value
        )


        if (
            isinstance(
                new_value,
                (int, float),
            )
            and
            isinstance(
                old_value,
                (int, float),
            )
        ):

            contract.boundary_values = (
                sorted(
                    set(
                        [
                            0,
                            max(
                                0,
                                new_value
                                - 1,
                            ),
                            new_value,
                            new_value
                            + 1,
                            old_value,
                            old_value
                            + 1,
                        ]
                    )
                )
            )


        return contract


    @staticmethod
    def _deterministic_result(
        request:
            PolicyChangeRequest,
    ) -> SemanticResult:

        contract = (
            PolicyEngine()
            .parse_change(
                request
            )
        )


        return SemanticResult(
            contract=contract,
            mode=(
                "deterministic_fallback"
            ),
            model=None,
        )