from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import User, Scan
from app.utils.schemas import DashboardStats, ScanResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardStats)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_filter = (Scan.uploader_id == user.id)
    if user.team_id:
        user_filter = (Scan.uploader_id == user.id) | (Scan.team_id == user.team_id)

    total_scans = await db.execute(select(func.count()).where(user_filter))
    total_scans = total_scans.scalar()

    total_open = await db.execute(
        select(func.coalesce(func.sum(Scan.open_ports), 0)).where(user_filter)
    )
    total_open = total_open.scalar()

    avg_risk = await db.execute(
        select(func.coalesce(func.avg(Scan.risk_score), 0)).where(user_filter)
    )
    avg_risk = round(float(avg_risk.scalar()), 1)

    critical = await db.execute(
        select(func.count()).where(user_filter & (Scan.risk_score >= 80))
    )
    critical = critical.scalar()

    recent = await db.execute(
        select(Scan).where(user_filter).order_by(desc(Scan.created_at)).limit(10)
    )
    recent_scans = [
        ScanResponse(
            id=str(s.id), title=s.title, target=s.target, scan_type=s.scan_type,
            file_type=s.file_type, risk_score=s.risk_score, total_ports=s.total_ports,
            open_ports=s.open_ports, closed_ports=s.closed_ports, filtered_ports=s.filtered_ports,
            outdated_services=s.outdated_services or [], ai_summary=s.ai_summary,
            ai_recommendations=s.ai_recommendations or [], status=s.status,
            uploader_id=str(s.uploader_id), team_id=str(s.team_id) if s.team_id else None,
            scan_date=s.scan_date, created_at=s.created_at,
        )
        for s in recent
    ]

    risk_trend = []
    for i in range(30, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        day_scans = await db.execute(
            select(func.coalesce(func.avg(Scan.risk_score), 0)).where(
                user_filter & (Scan.created_at >= day_start) & (Scan.created_at < day_end)
            )
        )
        risk_trend.append({
            "date": day_start.strftime("%m/%d"),
            "score": round(float(day_scans.scalar()), 1),
        })

    port_distribution = []
    for level in ["critical", "high", "medium", "low"]:
        count = await db.execute(
            select(func.count()).where(
                user_filter & (Scan.risk_score >= _get_min(level)) & (Scan.risk_score < _get_max(level))
            )
        )
        port_distribution.append({"level": level, "count": count.scalar()})

    scan_types = []
    for stype in ["quick", "full", "stealth", "custom"]:
        count = await db.execute(
            select(func.count()).where(user_filter & (Scan.scan_type == stype))
        )
        val = count.scalar()
        if val > 0:
            scan_types.append({"type": stype, "count": val})

    return DashboardStats(
        total_scans=total_scans,
        total_open_ports=total_open,
        avg_risk_score=avg_risk,
        critical_findings=critical,
        recent_scans=recent_scans,
        risk_trend=risk_trend,
        port_distribution=port_distribution,
        scan_type_distribution=scan_types,
    )


def _get_min(level: str) -> int:
    return {"critical": 80, "high": 60, "medium": 40, "low": 0}.get(level, 0)


def _get_max(level: str) -> int:
    return {"critical": 101, "high": 80, "medium": 60, "low": 40}.get(level, 101)
