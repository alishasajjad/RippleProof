from __future__ import annotations

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ============================================================
# Environment
# ============================================================

load_dotenv()

_raw_database_url = os.getenv("DATABASE_URL", "").strip()

if not _raw_database_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is not configured."
    )


# ============================================================
# SQLAlchemy Base
#
# IMPORTANT:
# app.models imports Base from app.db, therefore Base MUST
# be defined here. Do not import Base from app.models.
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# PostgreSQL URL normalization
#
# Railway normally supplies:
#
# postgresql://user:password@host:port/database
#
# SQLAlchemy interprets plain postgresql:// using psycopg2.
# RippleProof uses psycopg v3, therefore explicitly use:
#
# postgresql+psycopg://
# ============================================================

if _raw_database_url.startswith("postgresql+psycopg://"):
    DATABASE_URL = _raw_database_url

elif _raw_database_url.startswith("postgresql://"):
    DATABASE_URL = _raw_database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

elif _raw_database_url.startswith("postgres://"):
    DATABASE_URL = _raw_database_url.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )

else:
    DATABASE_URL = _raw_database_url


# ============================================================
# SQLAlchemy Engine
# ============================================================

engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)


# ============================================================
# Session Factory
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# FastAPI Database Dependency
# ============================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# Initialize Database
#
# Import app.models INSIDE the function.
# This registers all SQLAlchemy models with Base.metadata
# without causing the circular import:
#
# app.models -> app.db -> app.models
# ============================================================

def init_db() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


# ============================================================
# Database Health / Status
# ============================================================

def database_status() -> dict:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "configured": True,
            "connected": True,
            "backend": engine.url.get_backend_name(),
            "database": engine.url.database,
            "host": engine.url.host,
            "port": engine.url.port,
            "message": "Database connection successful.",
        }

    except Exception as exc:
        return {
            "configured": True,
            "connected": False,
            "backend": engine.url.get_backend_name(),
            "database": engine.url.database,
            "host": engine.url.host,
            "port": engine.url.port,
            "message": f"Database connection failed: {exc}",
        }


# ============================================================
# Optional Compatibility Helpers
# ============================================================

def get_engine() -> Engine:
    return engine


def get_session() -> Session:
    return SessionLocal()