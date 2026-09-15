import os
from typing import Generator

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./rippleproof.db",
)


# ---------------------------------------------------------
# PostgreSQL URL normalization
# ---------------------------------------------------------
#
# Railway commonly provides:
#
#   postgresql://user:password@host:port/database
#
# Plain "postgresql://" makes SQLAlchemy use the psycopg2
# dialect by default.
#
# RippleProof uses Psycopg 3, whose SQLAlchemy dialect is:
#
#   postgresql+psycopg://
#
# This conversion keeps Railway configuration simple while
# ensuring SQLAlchemy always uses Psycopg 3.
# ---------------------------------------------------------

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )


# ---------------------------------------------------------
# SQLAlchemy engine configuration
# ---------------------------------------------------------

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
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

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------
# Database initialization
# ---------------------------------------------------------

def init_db() -> None:
    """
    Import RippleProof SQLAlchemy models and create any
    database tables that do not already exist.

    For the hackathon MVP this is used instead of a full
    database migration framework.
    """

    from app import models  # noqa: F401

    Base.metadata.create_all(
        bind=engine
    )


# ---------------------------------------------------------
# FastAPI database dependency
# ---------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Provide one SQLAlchemy database session per request.
    """

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
    Check whether RippleProof can communicate with the
    configured database without exposing credentials.
    """

    backend = engine.url.get_backend_name()

    result = {
        "configured": True,
        "connected": False,
        "backend": backend,
        "database": engine.url.database,
        "host": (
            engine.url.host
            if backend != "sqlite"
            else "local-file"
        ),
        "port": engine.url.port,
    }

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        result["connected"] = True

        result["message"] = (
            "Database connection successful."
        )

    except Exception as exc:
        result["message"] = (
            f"{type(exc).__name__}: {exc}"
        )

    return result