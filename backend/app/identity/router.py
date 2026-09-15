from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.identity.models import Team, TeamMember, User
from app.identity.security import (
    create_access_token,
    get_current_user,
    get_db,
    hash_password,
    verify_password,
)


router = APIRouter(prefix="/api", tags=["Identity"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CreateTeamRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)


class AddTeamMemberRequest(BaseModel):
    email: EmailStr
    role: Literal["reviewer", "viewer"] = "viewer"


def user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }


def require_team_owner(
    db: Session,
    team_id: str,
    user_id: str,
) -> TeamMember:
    membership = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    )

    if membership is None or membership.role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Only the team owner can perform this action.",
        )

    return membership


@router.post("/auth/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = request.email.lower().strip()

    existing = db.scalar(
        select(User).where(User.email == email)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    try:
        password_hash = hash_password(request.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    user = User(
        name=request.name.strip(),
        email=email,
        password_hash=password_hash,
    )

    db.add(user)
    db.flush()

    team = Team(
        name=f"{request.name.strip()}'s Workspace",
    )

    db.add(team)
    db.flush()

    membership = TeamMember(
        user_id=user.id,
        team_id=team.id,
        role="owner",
    )

    db.add(membership)
    db.commit()

    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user_payload(user),
        "team": {
            "id": team.id,
            "name": team.name,
            "role": "owner",
        },
    }


@router.post("/auth/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    email = request.email.lower().strip()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user_payload(user),
    }


@router.get("/auth/me")
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Team, TeamMember)
        .join(
            TeamMember,
            TeamMember.team_id == Team.id,
        )
        .where(
            TeamMember.user_id == current_user.id
        )
    ).all()

    teams = [
        {
            "id": team.id,
            "name": team.name,
            "role": membership.role,
        }
        for team, membership in rows
    ]

    return {
        "user": user_payload(current_user),
        "teams": teams,
    }


@router.post("/teams")
def create_team(
    request: CreateTeamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team = Team(
        name=request.name.strip(),
    )

    db.add(team)
    db.flush()

    db.add(
        TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role="owner",
        )
    )

    db.commit()

    return {
        "id": team.id,
        "name": team.name,
        "role": "owner",
    }


@router.get("/teams")
def list_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Team, TeamMember)
        .join(
            TeamMember,
            TeamMember.team_id == Team.id,
        )
        .where(
            TeamMember.user_id == current_user.id
        )
    ).all()

    return [
        {
            "id": team.id,
            "name": team.name,
            "role": membership.role,
        }
        for team, membership in rows
    ]


@router.get("/teams/{team_id}/members")
def team_members(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this team.",
        )

    rows = db.execute(
        select(User, TeamMember)
        .join(
            TeamMember,
            TeamMember.user_id == User.id,
        )
        .where(
            TeamMember.team_id == team_id
        )
    ).all()

    return [
        {
            **user_payload(user),
            "role": member.role,
        }
        for user, member in rows
    ]


@router.post("/teams/{team_id}/members")
def add_team_member(
    team_id: str,
    request: AddTeamMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_team_owner(
        db,
        team_id,
        current_user.id,
    )

    target = db.scalar(
        select(User).where(
            User.email == request.email.lower().strip()
        )
    )

    if target is None:
        raise HTTPException(
            status_code=404,
            detail="This user must create a RippleProof account first.",
        )

    existing = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == target.id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="User is already a member of this team.",
        )

    member = TeamMember(
        team_id=team_id,
        user_id=target.id,
        role=request.role,
    )

    db.add(member)
    db.commit()

    return {
        "user": user_payload(target),
        "role": request.role,
    }