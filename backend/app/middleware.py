from __future__ import annotations

import os
import threading
import time
import uuid

from collections import (
    defaultdict,
    deque,
)

from fastapi import Request

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

from starlette.responses import (
    JSONResponse,
)


class ProductionMiddleware(
    BaseHTTPMiddleware
):
    """
    Production safety middleware.

    Features:
    - Request IDs
    - API processing time
    - Security headers
    - No-store API caching
    - Lightweight in-memory rate limiting
      for expensive AI endpoints
    """

    def __init__(
        self,
        app,
    ):
        super().__init__(
            app
        )

        self.limit = int(
            os.getenv(
                "ANALYSIS_RATE_LIMIT_PER_MINUTE",
                "8",
            )
        )

        self.window_seconds = 60

        self.requests = defaultdict(
            deque
        )

        self.lock = (
            threading.Lock()
        )


    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        started = (
            time.perf_counter()
        )

        request_id = (
            request.headers.get(
                "X-Request-ID"
            )
            or
            str(
                uuid.uuid4()
            )
        )

        request.state.request_id = (
            request_id
        )


        if self._is_expensive(
            request
        ):

            allowed, retry_after = (
                self._allow_request(
                    request
                )
            )

            if not allowed:

                return JSONResponse(
                    status_code=429,

                    content={
                        "detail":
                            (
                                "Analysis rate "
                                "limit exceeded."
                            ),

                        "request_id":
                            request_id,

                        "retry_after_seconds":
                            retry_after,
                    },

                    headers={
                        "Retry-After":
                            str(
                                retry_after
                            ),

                        "X-Request-ID":
                            request_id,
                    },
                )


        response = await call_next(
            request
        )


        elapsed = (
            time.perf_counter()
            - started
        )


        response.headers[
            "X-Request-ID"
        ] = request_id


        response.headers[
            "X-Process-Time-Ms"
        ] = str(
            round(
                elapsed
                * 1000,
                2,
            )
        )


        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"


        response.headers[
            "X-Frame-Options"
        ] = "DENY"


        response.headers[
            "Referrer-Policy"
        ] = "no-referrer"


        response.headers[
            "Permissions-Policy"
        ] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )


        if (
            request.url.path
            .startswith(
                "/api/"
            )
        ):
            response.headers[
                "Cache-Control"
            ] = (
                "no-store, "
                "max-age=0"
            )


        return response


    @staticmethod
    def _is_expensive(
        request: Request,
    ) -> bool:

        if request.method != "POST":
            return False


        expensive_paths = {
            "/api/runs/custom",
            "/api/runs/demo",
            "/api/system/llm-test",
        }


        return (
            request.url.path
            in expensive_paths
        )


    def _allow_request(
        self,
        request: Request,
    ) -> tuple[
        bool,
        int,
    ]:

        host = (
            request.client.host
            if request.client
            else "unknown"
        )

        key = (
            f"{host}:"
            f"{request.url.path}"
        )

        now = time.time()

        cutoff = (
            now
            - self.window_seconds
        )


        with self.lock:

            bucket = (
                self.requests[
                    key
                ]
            )


            while (
                bucket
                and
                bucket[0]
                < cutoff
            ):
                bucket.popleft()


            if (
                len(bucket)
                >= self.limit
            ):

                oldest = (
                    bucket[0]
                )

                retry_after = max(
                    1,
                    int(
                        self.window_seconds
                        - (
                            now
                            - oldest
                        )
                    ),
                )

                return (
                    False,
                    retry_after,
                )


            bucket.append(
                now
            )


        return (
            True,
            0,
        )