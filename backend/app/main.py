from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session

from app.core.api_errors import install_error_handlers
from app.db import (
    database_status,
    get_db,
    init_db,
)
from app.identity.models import init_identity_tables
from app.identity.router import router as identity_router
from app.middleware import ProductionMiddleware
from app.schemas.contracts import PolicyChangeRequest
from app.services.custom_run_service import create_custom_run
from app.services.dashboard_service import dashboard_summary
from app.services.demo_service import (
    analyze_demo,
    run_demo,
    verify_demo,
)
from app.services.evaluation_service import (
    deterministic_benchmark,
    evaluation_summary,
)
from app.services.llm_service import LLMService
from app.services.persistence_service import (
    approve_run,
    create_demo_run,
    get_run,
    list_runs,
    verify_run,
)
from app.services.policy_engine import PolicyEngine
from app.services.upload_service import (
    MAX_UPLOAD_FILES,
    UploadService,
)


# ============================================================
# Environment
# ============================================================

load_dotenv()


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper(),
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)

logger = logging.getLogger("rippleproof")


# ============================================================
# CORS
# ============================================================

def cors_origins() -> list[str]:
    """
    Local development origins plus production frontend origins.

    Supported env examples:

    CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

    or

    FRONTEND_ORIGIN=https://rippleproof.vercel.app
    """

    origins = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }

    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "",
    )

    for value in raw_origins.split(","):
        value = value.strip()

        if value:
            origins.add(
                value.rstrip("/")
            )

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "",
    ).strip()

    if frontend_origin:
        origins.add(
            frontend_origin.rstrip("/")
        )

    return sorted(origins)


# ============================================================
# Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    # --------------------------------------------------------
    # Main RippleProof database
    # --------------------------------------------------------

    try:
        init_db()

    except Exception:
        logger.exception(
            "RippleProof database initialization failed."
        )

    # --------------------------------------------------------
    # Authentication / team tables
    # --------------------------------------------------------

    try:
        init_identity_tables()

        logger.info(
            "RippleProof identity/team tables ready."
        )

    except Exception:
        logger.exception(
            "RippleProof identity/team initialization failed."
        )

    # --------------------------------------------------------
    # Startup status
    # --------------------------------------------------------

    db_state = database_status()

    llm_state = (
        LLMService()
        .status()
    )

    logger.info(
        "RippleProof startup "
        "version=%s "
        "database=%s "
        "db_connected=%s "
        "llm_provider=%s "
        "llm_mode=%s "
        "llm_configured=%s",
        app.version,
        db_state.get("backend"),
        db_state.get("connected"),
        llm_state.get("provider"),
        llm_state.get("mode"),
        llm_state.get("configured"),
    )

    yield

    logger.info(
        "RippleProof API shutdown complete."
    )


# ============================================================
# FastAPI app
# ============================================================

app = FastAPI(
    title="RippleProof API",
    version="0.7.0",
    description=(
        "Production-ready semantic policy change propagation "
        "with real artifact ingestion, Groq intelligence, "
        "PostgreSQL audit persistence, human approval, "
        "deterministic executable proof, identity, teams "
        "and operational evaluation."
    ),
    lifespan=lifespan,
)


# ============================================================
# Clean API error handling
# ============================================================

install_error_handlers(app)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ],
    expose_headers=[
        "X-Request-ID",
        "X-Response-Time",
    ],
)


# ============================================================
# Compression
# ============================================================

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# ============================================================
# Existing production middleware
# ============================================================

app.add_middleware(
    ProductionMiddleware
)


# ============================================================
# Authentication / Teams
# ============================================================

app.include_router(
    identity_router
)


# ============================================================
# Root
# ============================================================

@app.get(
    "/",
    tags=["System"],
    include_in_schema=False,
)
def root():
    return {
        "product": "RippleProof",
        "status": "operational",
        "version": app.version,
        "description": (
            "Semantic policy change intelligence "
            "with executable proof."
        ),
        "documentation": "/docs",
        "openapi": "/openapi.json",
    }


# ============================================================
# System
# ============================================================

@app.get(
    "/health",
    tags=[
        "System"
    ],
)
def health():
    return {
        "status": "ok",
        "service": "rippleproof-api",
        "version": app.version,
    }


@app.get(
    "/api/system/readiness",
    tags=[
        "System"
    ],
)
def readiness():
    database = database_status()

    llm = (
        LLMService()
        .status()
    )

    db_ready = bool(
        database.get(
            "connected"
        )
    )

    llm_ready = bool(
        llm.get(
            "configured"
        )
    )

    ready = (
        db_ready
        and
        llm_ready
    )

    return {
        "status": (
            "ready"
            if ready
            else "degraded"
        ),
        "database": {
            "ready": db_ready,
            "backend": database.get(
                "backend"
            ),
        },
        "llm": {
            "ready": llm_ready,
            "provider": llm.get(
                "provider"
            ),
            "mode": llm.get(
                "mode"
            ),
            "model": llm.get(
                "model"
            ),
        },
    }


@app.get(
    "/api/system/status",
    tags=[
        "System"
    ],
)
def system_status():
    llm = LLMService()

    return {
        "api": {
            "status": "ok",
            "version": app.version,
        },
        "database": database_status(),
        "llm": llm.status(),
    }


@app.post(
    "/api/system/llm-test",
    tags=[
        "System"
    ],
)
def llm_test():
    """
    IMPORTANT:
    This endpoint makes an external LLM request.

    Do not call it during normal local testing if you
    want to preserve Groq quota.
    """

    return (
        LLMService()
        .test_connection()
    )


# ============================================================
# Dashboard
# ============================================================

@app.get(
    "/api/dashboard/summary",
    tags=[
        "Dashboard"
    ],
)
def dashboard(
    db: Session = Depends(
        get_db
    ),
):
    return dashboard_summary(
        db
    )


# ============================================================
# Evaluation
# ============================================================

@app.get(
    "/api/evaluation/summary",
    tags=[
        "Evaluation"
    ],
)
def evaluation(
    db: Session = Depends(
        get_db
    ),
):
    return evaluation_summary(
        db
    )


@app.get(
    "/api/evaluation/benchmark",
    tags=[
        "Evaluation"
    ],
)
def benchmark():
    """
    Offline deterministic benchmark.

    No Groq request is required here.
    """

    return deterministic_benchmark()


# ============================================================
# Policy
# ============================================================

@app.post(
    "/api/policy-contract",
    tags=[
        "Policy"
    ],
)
def create_policy_contract(
    payload: PolicyChangeRequest,
):
    try:
        return (
            PolicyEngine()
            .parse_change(
                payload
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


# ============================================================
# Custom production workflow
# ============================================================

@app.post(
    "/api/runs/custom",
    tags=[
        "Analysis"
    ],
)
async def custom_analysis(
    policy_name: str = Form(...),
    old_text: str = Form(...),
    new_text: str = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(
        get_db
    ),
):
    if not policy_name.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Policy name is required."
            ),
        )

    if not old_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Previous policy text is required."
            ),
        )

    if not new_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Updated policy text is required."
            ),
        )

    if not files:
        raise HTTPException(
            status_code=422,
            detail=(
                "Upload at least one artifact."
            ),
        )

    if len(files) > MAX_UPLOAD_FILES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Maximum {MAX_UPLOAD_FILES} "
                "artifacts are allowed."
            ),
        )

    try:
        artifacts = (
            await UploadService()
            .parse_files(
                files
            )
        )

        request = PolicyChangeRequest(
            policy_name=(
                policy_name.strip()
            ),
            old_text=(
                old_text.strip()
            ),
            new_text=(
                new_text.strip()
            ),
        )

        return create_custom_run(
            db=db,
            request=request,
            artifacts=artifacts,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Custom analysis failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "RippleProof could not complete "
                "the analysis. Please try again."
            ),
        )


# ============================================================
# Persistent flagship workflow
# ============================================================

@app.post(
    "/api/runs/demo",
    tags=[
        "Analysis"
    ],
)
def create_persistent_demo(
    db: Session = Depends(
        get_db
    ),
):
    try:
        return create_demo_run(
            db
        )

    except Exception:
        logger.exception(
            "Flagship analysis failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "RippleProof could not start "
                "the flagship analysis."
            ),
        )


@app.get(
    "/api/runs",
    tags=[
        "Runs"
    ],
)
def recent_runs(
    db: Session = Depends(
        get_db
    ),
):
    return list_runs(
        db
    )


@app.get(
    "/api/runs/{run_id}",
    tags=[
        "Runs"
    ],
)
def run_detail(
    run_id: str,
    db: Session = Depends(
        get_db
    ),
):
    result = get_run(
        db,
        run_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=(
                "Run not found."
            ),
        )

    return result


@app.post(
    "/api/runs/{run_id}/approve",
    tags=[
        "Runs"
    ],
)
def approve(
    run_id: str,
    db: Session = Depends(
        get_db
    ),
):
    result = approve_run(
        db,
        run_id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=(
                "Run not found."
            ),
        )

    return result


@app.post(
    "/api/runs/{run_id}/verify",
    tags=[
        "Runs"
    ],
)
def verify(
    run_id: str,
    db: Session = Depends(
        get_db
    ),
):
    try:
        result = verify_run(
            db,
            run_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    if not result:
        raise HTTPException(
            status_code=404,
            detail=(
                "Run not found."
            ),
        )

    return result


# ============================================================
# Hidden backwards compatibility
# ============================================================

@app.post(
    "/api/demo/analyze",
    include_in_schema=False,
)
def demo_analyze():
    return analyze_demo()


@app.post(
    "/api/demo/verify",
    include_in_schema=False,
)
def demo_verify():
    return verify_demo()


@app.post(
    "/api/demo/run",
    include_in_schema=False,
)
def demo_run():
    return run_demo()