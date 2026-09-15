from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


# ============================================================
# Database Configuration
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://rippleproof:rippleproof@127.0.0.1:5435/rippleproof",
).strip()


# Railway normally provides:
# postgresql://user:password@host:port/database
#
# SQLAlchemy may interpret plain "postgresql://" as psycopg2.
# RippleProof uses psycopg v3, so force the correct driver.

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


# ============================================================
# SQLAlchemy Base
# ============================================================

class IdentityBase(DeclarativeBase):
    pass


# ============================================================
# User Model
# ============================================================

class User(IdentityBase):
    __tablename__ = "rp_users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ============================================================
# Team Model
# ============================================================

class Team(IdentityBase):
    __tablename__ = "rp_teams"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ============================================================
# Team Member Model
# ============================================================

class TeamMember(IdentityBase):
    __tablename__ = "rp_team_members"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    team_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "rp_teams.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "rp_users.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="viewer",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "user_id",
            name="uq_rp_team_member",
        ),
    )


# ============================================================
# Database Engine
# ============================================================

identity_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ============================================================
# Database Session
# ============================================================

IdentitySession = sessionmaker(
    bind=identity_engine,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# Database Initialization
# ============================================================

def init_identity_tables() -> None:
    """
    Create RippleProof identity/team tables if they do not exist.
    """
    IdentityBase.metadata.create_all(bind=identity_engine)