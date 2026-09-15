import os
from typing import Generator

from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    text,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rippleproof.db",
)


# ---------------------------------------------------------
# SQLAlchemy engine
# ---------------------------------------------------------

connect_args = {}

if DATABASE_URL.startswith(
    "sqlite"
):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# Declarative base
# ---------------------------------------------------------

class Base(
    DeclarativeBase
):
    pass


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------

def init_db() -> None:
    """
    Import SQLAlchemy models and create
    any missing database tables.

    For the hackathon MVP this replaces
    a full migration framework.
    """

    from app import models  # noqa: F401

    Base.metadata.create_all(
        bind=engine
    )


# ---------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------

def get_db() -> Generator[
    Session,
    None,
    None,
]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ---------------------------------------------------------
# Database diagnostics
# ---------------------------------------------------------

def database_status() -> dict:
    """
    Check whether RippleProof can
    communicate with its database.

    Does not expose credentials.
    """

    backend = (
        engine.url
        .get_backend_name()
    )

    result = {
        "configured": True,
        "connected": False,
        "backend": backend,
        "database": (
            engine.url.database
        ),
        "host": (
            engine.url.host
            if backend
            != "sqlite"
            else "local-file"
        ),
        "port": (
            engine.url.port
        ),
    }

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        result[
            "connected"
        ] = True

        result[
            "message"
        ] = (
            "Database connection successful."
        )

    except Exception as exc:

        result[
            "message"
        ] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result