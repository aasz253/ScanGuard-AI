import uuid
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.models import User, Team
from app.utils.schemas import TeamCreate, TeamResponse, TeamJoin
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse)
async def create_team(
    data: TeamCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.team_id:
        raise HTTPException(status_code=400, detail="Already in a team")

    team = Team(
        id=uuid.uuid4(),
        name=data.name,
        description=data.description,
        invite_code=secrets.token_urlsafe(16),
    )
    db.add(team)
    await db.flush()

    user.team_id = team.id
    user.role = "admin"
    await db.commit()

    count = await db.execute(select(func.count()).where(User.team_id == team.id))
    return TeamResponse(
        id=str(team.id), name=team.name, description=team.description,
        invite_code=team.invite_code, member_count=count.scalar(),
        created_at=team.created_at,
    )


@router.post("/join", response_model=TeamResponse)
async def join_team(
    data: TeamJoin,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.team_id:
        raise HTTPException(status_code=400, detail="Already in a team")

    result = await db.execute(select(Team).where(Team.invite_code == data.invite_code))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    user.team_id = team.id
    user.role = "analyst"
    await db.commit()

    count = await db.execute(select(func.count()).where(User.team_id == team.id))
    return TeamResponse(
        id=str(team.id), name=team.name, description=team.description,
        invite_code=team.invite_code, member_count=count.scalar(),
        created_at=team.created_at,
    )


@router.get("/me", response_model=TeamResponse)
async def get_my_team(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.team_id:
        raise HTTPException(status_code=404, detail="Not in a team")

    result = await db.execute(select(Team).where(Team.id == user.team_id))
    team = result.scalar_one_or_none()
    count = await db.execute(select(func.count()).where(User.team_id == team.id))

    return TeamResponse(
        id=str(team.id), name=team.name, description=team.description,
        invite_code=team.invite_code, member_count=count.scalar(),
        created_at=team.created_at,
    )


@router.get("/members")
async def list_members(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.team_id:
        raise HTTPException(status_code=404, detail="Not in a team")

    result = await db.execute(select(User).where(User.team_id == user.team_id))
    members = result.scalars().all()

    return [
        {
            "id": str(m.id), "full_name": m.full_name,
            "email": m.email, "role": m.role,
            "is_active": m.is_active, "created_at": m.created_at.isoformat(),
        }
        for m in members
    ]


@router.delete("/leave")
async def leave_team(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.team_id = None
    user.role = "analyst"
    await db.commit()
    return {"detail": "Left team"}
