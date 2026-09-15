from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger("rippleproof")


def install_error_handlers(
    app: FastAPI,
) -> None:

    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next,
    ):
        request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = (
            request_id
        )

        return response

    @app.exception_handler(
        RequestValidationError
    )
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": (
                        "Some submitted values are invalid. "
                        "Please review the form and try again."
                    ),
                    "request_id": request.state.request_id,
                }
            },
        )

    @app.exception_handler(
        HTTPException
    )
    async def http_error_handler(
        request: Request,
        exc: HTTPException,
    ):
        if exc.status_code >= 500:
            message = (
                "RippleProof could not complete this request. "
                "Please try again shortly."
            )
        else:
            message = str(exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": (
                        f"HTTP_{exc.status_code}"
                    ),
                    "message": message,
                    "request_id": (
                        request.state.request_id
                    ),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "Unhandled RippleProof error "
            "request_id=%s",
            request.state.request_id,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": (
                        "Something went wrong while processing "
                        "the request. No data was changed. "
                        "Please try again."
                    ),
                    "request_id": (
                        request.state.request_id
                    ),
                }
            },
        )