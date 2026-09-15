from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def uid() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    domain: Mapped[str] = mapped_column(
        String(80),
        default="business",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    policy_id: Mapped[str] = mapped_column(
        ForeignKey("policies.id"),
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    structured_rule: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class ChangeRun(Base):
    __tablename__ = "change_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    policy_id: Mapped[str] = mapped_column(
        ForeignKey("policies.id"),
        index=True,
    )

    old_version_id: Mapped[str] = mapped_column(
        ForeignKey("policy_versions.id"),
    )

    new_version_id: Mapped[str] = mapped_column(
        ForeignKey("policy_versions.id"),
    )

    status: Mapped[str] = mapped_column(
        String(60),
        default="IMPACT_READY",
        index=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    semantic_mode: Mapped[str] = mapped_column(
        String(60),
        default="deterministic_fallback",
    )

    llm_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contract_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )


class ArtifactRecord(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    run_id: Mapped[str] = mapped_column(
        ForeignKey("change_runs.id"),
        index=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    artifact_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    relationship: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    source_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    original_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    current_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class ImpactRecord(Base):
    __tablename__ = "impacts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    run_id: Mapped[str] = mapped_column(
        ForeignKey("change_runs.id"),
        index=True,
    )

    artifact_external_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    affected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    relationship: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    evidence: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class PatchRecord(Base):
    __tablename__ = "patches"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    run_id: Mapped[str] = mapped_column(
        ForeignKey("change_runs.id"),
        index=True,
    )

    artifact_external_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    original_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    proposed_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    diff: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="proposed",
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class VerificationTestRecord(Base):
    __tablename__ = "verification_tests"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    run_id: Mapped[str] = mapped_column(
        ForeignKey("change_runs.id"),
        index=True,
    )

    test_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    input_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    expected_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    actual_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uid,
    )

    run_id: Mapped[str] = mapped_column(
        ForeignKey("change_runs.id"),
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    actor: Mapped[str] = mapped_column(
        String(100),
        default="system",
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )