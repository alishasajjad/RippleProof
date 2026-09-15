from __future__ import annotations

import logging
import os
from typing import TypedDict

import httpx


logger = logging.getLogger("rippleproof")


class ProviderConfig(TypedDict):
    name: str
    api_key: str
    base_url: str
    model: str


class LLMUnavailableError(RuntimeError):
    """Raised when no configured LLM provider can complete the request."""


def provider_config(prefix: str) -> ProviderConfig | None:
    """
    Read one OpenAI-compatible provider from environment variables.

    Example:
        GROQ_API_KEY
        GROQ_BASE_URL
        GROQ_MODEL

    Or:
        LLM_FALLBACK_API_KEY
        LLM_FALLBACK_BASE_URL
        LLM_FALLBACK_MODEL
    """

    api_key = os.getenv(f"{prefix}_API_KEY")
    base_url = os.getenv(f"{prefix}_BASE_URL")
    model = os.getenv(f"{prefix}_MODEL")

    # Explicit checks are intentional.
    # Pylance now knows these values are str below this block.
    if not api_key:
        return None

    if not base_url:
        return None

    if not model:
        return None

    return {
        "name": prefix.lower(),
        "api_key": api_key,
        "base_url": base_url.rstrip("/"),
        "model": model,
    }


async def call_openai_compatible(
    provider: ProviderConfig,
    *,
    messages: list[dict[str, object]],
    temperature: float = 0.0,
) -> dict:
    """
    Call an OpenAI-compatible /chat/completions endpoint.
    """

    endpoint = f"{provider['base_url']}/chat/completions"

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=10.0,
            read=45.0,
            write=20.0,
            pool=10.0,
        )
    ) as client:
        response = await client.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": provider["model"],
                "messages": messages,
                "temperature": temperature,
            },
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise LLMUnavailableError(
                f"{provider['name']} returned an invalid response."
            )

        return payload


async def call_llm_with_fallback(
    *,
    messages: list[dict[str, object]],
    temperature: float = 0.0,
) -> tuple[dict, str]:
    """
    Try Groq first.

    If Groq fails because of rate limiting, timeout,
    network failure or an upstream server error,
    try the optional secondary provider.

    Returns:
        (response_payload, provider_name)
    """

    providers: list[ProviderConfig] = []

    groq = provider_config("GROQ")

    fallback = provider_config("LLM_FALLBACK")

    if groq is not None:
        providers.append(groq)

    if fallback is not None:
        providers.append(fallback)

    if not providers:
        raise LLMUnavailableError(
            "No AI provider is configured."
        )

    failures: list[str] = []

    for index, provider in enumerate(providers):
        try:
            logger.info(
                "Attempting semantic analysis provider=%s model=%s",
                provider["name"],
                provider["model"],
            )

            payload = await call_openai_compatible(
                provider,
                messages=messages,
                temperature=temperature,
            )

            if index > 0:
                logger.warning(
                    "RippleProof successfully used fallback provider=%s",
                    provider["name"],
                )

            return payload, provider["name"]

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            failures.append(
                f"{provider['name']}: HTTP {status_code}"
            )

            logger.warning(
                "LLM provider failed provider=%s status=%s",
                provider["name"],
                status_code,
            )

            # Authentication / malformed-request failures usually
            # should not be retried repeatedly.
            if status_code in {400, 401, 403, 404}:
                continue

        except httpx.TimeoutException:
            failures.append(
                f"{provider['name']}: timeout"
            )

            logger.warning(
                "LLM provider timeout provider=%s",
                provider["name"],
            )

        except httpx.NetworkError:
            failures.append(
                f"{provider['name']}: network error"
            )

            logger.warning(
                "LLM provider network failure provider=%s",
                provider["name"],
            )

        except Exception as exc:
            failures.append(
                f"{provider['name']}: {type(exc).__name__}"
            )

            logger.exception(
                "Unexpected LLM provider error provider=%s",
                provider["name"],
            )

    logger.error(
        "All configured LLM providers failed: %s",
        "; ".join(failures),
    )

    raise LLMUnavailableError(
        "AI semantic analysis is temporarily unavailable. "
        "Your uploaded artifacts were not modified. "
        "Please try again later."
    )


def get_llm_provider_status() -> dict:
    """
    Token-free provider configuration status.
    Does NOT call Groq.
    """

    groq = provider_config("GROQ")
    fallback = provider_config("LLM_FALLBACK")

    return {
        "primary": {
            "provider": "groq",
            "configured": groq is not None,
            "model": (
                groq["model"]
                if groq is not None
                else None
            ),
        },
        "fallback": {
            "provider": "llm_fallback",
            "configured": fallback is not None,
            "model": (
                fallback["model"]
                if fallback is not None
                else None
            ),
        },
    }