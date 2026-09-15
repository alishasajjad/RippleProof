from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.identity.models import User


# ============================================================
# Environment
# ============================================================

load_dotenv()


JWT_SECRET_KEY = (
    os.getenv("JWT_SECRET_KEY")
    or os.getenv("AUTH_SECRET_KEY")
    or "rippleproof-development-secret-change-before-production"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

JWT_ISSUER = os.getenv(
    "JWT_ISSUER",
    "rippleproof",
)

JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "720",
    )
)


# ============================================================
# Password hashing
# ============================================================

PBKDF2_ITERATIONS = 600_000


def hash_password(
    password: str,
) -> str:
    """
    Securely hash a password with PBKDF2-HMAC-SHA256.
    """

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    salt = secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()

    return (
        f"pbkdf2_sha256"
        f"${PBKDF2_ITERATIONS}"
        f"${salt}"
        f"${digest}"
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    """
    Verify a password against a RippleProof PBKDF2 hash.
    """

    if not password or not stored_hash:
        return False

    try:
        (
            algorithm,
            iterations_text,
            salt,
            expected_digest,
        ) = stored_hash.split(
            "$",
            3,
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(
            iterations_text
        )

        actual_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()

        return hmac.compare_digest(
            actual_digest,
            expected_digest,
        )

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):
        return False


# ============================================================
# JWT helper
# ============================================================

def _extract_identity(
    value: Any,
) -> tuple[str | None, str | None]:
    """
    Accept all identity formats RippleProof currently uses:

    - SQLAlchemy User object
    - dict
    - raw user-id string
    """

    if value is None:
        return None, None

    # --------------------------------------------------------
    # SQLAlchemy User / ORM object
    # --------------------------------------------------------

    if hasattr(value, "id"):
        raw_id = getattr(
            value,
            "id",
            None,
        )

        raw_email = getattr(
            value,
            "email",
            None,
        )

        user_id = (
            str(raw_id).strip()
            if raw_id is not None
            else None
        )

        email = (
            str(raw_email).strip().lower()
            if raw_email
            else None
        )

        return user_id, email

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(
        value,
        dict,
    ):
        raw_id = (
            value.get("sub")
            or value.get("user_id")
            or value.get("id")
        )

        raw_email = value.get(
            "email"
        )

        user_id = (
            str(raw_id).strip()
            if raw_id is not None
            else None
        )

        email = (
            str(raw_email).strip().lower()
            if raw_email
            else None
        )

        return user_id, email

    # --------------------------------------------------------
    # Raw ID
    # --------------------------------------------------------

    if isinstance(
        value,
        str,
    ):
        cleaned = value.strip()

        return (
            cleaned or None,
            None,
        )

    return None, None


# ============================================================
# JWT creation
# ============================================================

def create_access_token(
    user: Any = None,
    email: str | None = None,
    *,
    user_id: str | None = None,
    subject: str | None = None,
    expires_minutes: int | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a RippleProof JWT.

    Supports:

        create_access_token(user)

    where user is a SQLAlchemy User object.

    Also supports:

        create_access_token({
            "sub": "...",
            "email": "..."
        })

        create_access_token("USER_ID")

        create_access_token(
            user_id="USER_ID",
            email="..."
        )
    """

    extracted_id, extracted_email = (
        _extract_identity(
            user
        )
    )

    final_user_id = (
        subject
        or user_id
        or extracted_id
    )

    final_email = (
        email
        or extracted_email
    )

    if final_user_id is None:
        raise ValueError(
            "JWT subject/user ID is required."
        )

    final_user_id = str(
        final_user_id
    ).strip()

    if not final_user_id:
        raise ValueError(
            "JWT subject/user ID cannot be empty."
        )

    claims: dict[str, Any] = {
        "sub": final_user_id,
    }

    if final_email:
        claims["email"] = (
            str(final_email)
            .strip()
            .lower()
        )

    if additional_claims:
        claims.update(
            additional_claims
        )

    now = datetime.now(
        timezone.utc
    )

    expiry = now + timedelta(
        minutes=(
            expires_minutes
            if expires_minutes is not None
            else JWT_EXPIRE_MINUTES
        )
    )

    claims["iat"] = int(
        now.timestamp()
    )

    claims["exp"] = int(
        expiry.timestamp()
    )

    claims["iss"] = JWT_ISSUER

    return jwt.encode(
        claims,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


# ============================================================
# JWT decoding
# ============================================================

def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """
    Decode and validate a RippleProof JWT.
    """

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing.",
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[
                JWT_ALGORITHM
            ],
            issuer=JWT_ISSUER,
        )

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Authentication token "
                "has expired."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        ) from exc

    except jwt.InvalidIssuerError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Authentication token "
                "has an invalid issuer."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        ) from exc

    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid authentication token."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        ) from exc

    raw_subject = payload.get(
        "sub"
    )

    if raw_subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Authentication token "
                "does not contain a user ID."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    payload["sub"] = str(
        raw_subject
    ).strip()

    if payload.get(
        "email"
    ):
        payload["email"] = (
            str(
                payload["email"]
            )
            .strip()
            .lower()
        )

    return payload


# ============================================================
# Swagger Bearer authentication
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    description=(
        "RippleProof access token. "
        "Paste only the JWT token here. "
        "Swagger automatically adds "
        "the Bearer prefix."
    ),
)


# Backward-compatible alias
security = bearer_scheme


# ============================================================
# User lookup
# ============================================================

def find_user_from_token(
    db: Session,
    payload: dict[str, Any],
) -> User | None:
    """
    Match the JWT to the real database user.

    Primary:
        JWT sub -> User.id

    Secondary safety fallback:
        JWT email -> User.email
    """

    user_id = str(
        payload.get(
            "sub",
            "",
        )
    ).strip()

    email = str(
        payload.get(
            "email",
            "",
        )
    ).strip().lower()

    conditions = []

    if user_id:
        conditions.append(
            cast(
                User.id,
                String,
            )
            == user_id
        )

    if email:
        conditions.append(
            func.lower(
                User.email
            )
            == email
        )

    if not conditions:
        return None

    statement = (
        select(User)
        .where(
            or_(
                *conditions
            )
        )
    )

    return (
        db.execute(
            statement
        )
        .scalars()
        .first()
    )


# ============================================================
# Current authenticated user
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials
    | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(
        get_db
    ),
) -> User:
    """
    Resolve the authenticated RippleProof user.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    if (
        credentials.scheme.lower()
        != "bearer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Bearer authentication "
                "is required."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    payload = decode_access_token(
        credentials.credentials
    )

    user = find_user_from_token(
        db,
        payload,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "User account was not found."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    return user


def get_current_user_id(
    current_user: User = Depends(
        get_current_user
    ),
) -> str:
    """
    Return authenticated user's database ID.
    """

    return str(
        current_user.id
    )