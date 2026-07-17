import uuid
import os
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User, Scan, ScanPort, ScanComment
from app.utils.schemas import (
    ScanResponse, ScanDetailResponse, ScanPortResponse,
    CommentCreate, CommentResponse
)
from app.utils.auth import get_current_user
from app.services.nmap_parser import parse_nmap_xml, calculate_risk_score, get_risk_label
from app.services.ai_service import analyze_port_with_ai, generate_scan_summary, generate_recommendations
from app.services.pdf_service import generate_pdf_report

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("/upload", response_model=ScanResponse)
async def upload_scan(
    file: UploadFile = File(...),
    title: str = Form(...),
    target: str = Form(...),
    scan_type: str = Form("full"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    allowed_ext = {".xml", ".nmap", ".gnmap"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(allowed_ext)}")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    with open(file_path, "wb") as f:
        f.write(content)

    scan = Scan(
        id=uuid.uuid4(),
        title=title,
        target=target,
        scan_type=scan_type,
        file_type=ext.lstrip("."),
        file_path=file_path,
        uploader_id=user.id,
        team_id=user.team_id,
        status="processing",
        scan_date=datetime.utcnow(),
    )
    db.add(scan)
    await db.commit()

    try:
        parsed = parse_nmap_xml(file_path)

        ports = parsed.get("ports", [])
        risk_score = calculate_risk_score(ports)

        scan.risk_score = risk_score
        scan.total_ports = parsed["stats"]["total_unique_ports"]
        scan.open_ports = len([p for p in ports if p["state"] == "open"])
        scan.closed_ports = len([p for p in ports if p["state"] == "closed"])
        scan.filtered_ports = len([p for p in ports if p["state"] == "filtered"])
        scan.outdated_services = [
            {"port": p["port_number"], "service": p.get("service"), "product": p.get("product"), "version": p.get("version")}
            for p in ports if p.get("is_outdated")
        ]
        scan.raw_stats = parsed["stats"]
        scan.status = "processing"

        for p in ports:
            scan_port = ScanPort(
                id=uuid.uuid4(),
                scan_id=scan.id,
                port_number=p["port_number"],
                protocol=p["protocol"],
                state=p["state"],
                service=p.get("service"),
                version=p.get("version"),
                product=p.get("product"),
                extra_info=p.get("extra_info"),
                is_outdated=p.get("is_outdated", False),
                risk_level=p.get("risk_level", "low"),
                banner=p.get("banner"),
            )
            db.add(scan_port)

        await db.commit()

        open_ports_data = [p for p in ports if p["state"] == "open"]
        for p in open_ports_data:
            db_port = await db.execute(
                select(ScanPort).where(
                    ScanPort.scan_id == scan.id,
                    ScanPort.port_number == p["port_number"],
                    ScanPort.protocol == p["protocol"],
                )
            )
            port_record = db_port.scalar_one_or_none()
            if port_record:
                explanation = await analyze_port_with_ai(p, f"Scan target: {target}")
                port_record.ai_explanation = explanation
        await db.commit()

        ai_summary = await generate_scan_summary(parsed, ports, risk_score)
        scan.ai_summary = ai_summary

        recommendations = await generate_recommendations(ports, risk_score)
        scan.ai_recommendations = recommendations
        scan.status = "completed"
        await db.commit()

    except Exception as e:
        scan.status = "failed"
        scan.ai_summary = f"Processing error: {str(e)}"
        await db.commit()

    await db.refresh(scan)
    return ScanResponse(
        id=str(scan.id),
        title=scan.title,
        target=scan.target,
        scan_type=scan.scan_type,
        file_type=scan.file_type,
        risk_score=scan.risk_score,
        total_ports=scan.total_ports,
        open_ports=scan.open_ports,
        closed_ports=scan.closed_ports,
        filtered_ports=scan.filtered_ports,
        outdated_services=scan.outdated_services or [],
        ai_summary=scan.ai_summary,
        ai_recommendations=scan.ai_recommendations or [],
        status=scan.status,
        uploader_id=str(scan.uploader_id),
        team_id=str(scan.team_id) if scan.team_id else None,
        scan_date=scan.scan_date,
        created_at=scan.created_at,
    )


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Scan).where(Scan.uploader_id == user.id).order_by(desc(Scan.created_at))
    if user.team_id:
        query = select(Scan).where(
            (Scan.uploader_id == user.id) | (Scan.team_id == user.team_id)
        ).order_by(desc(Scan.created_at))

    result = await db.execute(query)
    scans = result.scalars().all()

    return [
        ScanResponse(
            id=str(s.id), title=s.title, target=s.target, scan_type=s.scan_type,
            file_type=s.file_type, risk_score=s.risk_score, total_ports=s.total_ports,
            open_ports=s.open_ports, closed_ports=s.closed_ports, filtered_ports=s.filtered_ports,
            outdated_services=s.outdated_services or [], ai_summary=s.ai_summary,
            ai_recommendations=s.ai_recommendations or [], status=s.status,
            uploader_id=str(s.uploader_id), team_id=str(s.team_id) if s.team_id else None,
            scan_date=s.scan_date, created_at=s.created_at,
        )
        for s in scans
    ]


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan).options(selectinload(Scan.ports)).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    port_responses = [
        ScanPortResponse(
            id=str(p.id), port_number=p.port_number, protocol=p.protocol,
            state=p.state, service=p.service, version=p.version,
            product=p.product, extra_info=p.extra_info, is_outdated=p.is_outdated,
            risk_level=p.risk_level, ai_explanation=p.ai_explanation, banner=p.banner,
        )
        for p in sorted(scan.ports, key=lambda x: x.port_number)
    ]

    return ScanDetailResponse(
        id=str(scan.id), title=scan.title, target=scan.target, scan_type=scan.scan_type,
        file_type=scan.file_type, risk_score=scan.risk_score, total_ports=scan.total_ports,
        open_ports=scan.open_ports, closed_ports=scan.closed_ports, filtered_ports=scan.filtered_ports,
        outdated_services=scan.outdated_services or [], ai_summary=scan.ai_summary,
        ai_recommendations=scan.ai_recommendations or [], status=scan.status,
        uploader_id=str(scan.uploader_id), team_id=str(scan.team_id) if scan.team_id else None,
        scan_date=scan.scan_date, created_at=scan.created_at, ports=port_responses,
    )


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if str(scan.uploader_id) != str(user.id) and user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Not authorized")

    if scan.file_path and os.path.exists(scan.file_path):
        os.remove(scan.file_path)
    await db.delete(scan)
    await db.commit()
    return {"detail": "Scan deleted"}


@router.get("/{scan_id}/pdf")
async def download_pdf(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan).options(selectinload(Scan.ports)).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    pdf_dir = os.path.join(settings.UPLOAD_DIR, "reports")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{scan_id}_report.pdf")

    if not os.path.exists(pdf_path):
        ports_data = [
            {
                "port_number": p.port_number, "protocol": p.protocol, "state": p.state,
                "service": p.service, "version": p.version, "product": p.product,
                "extra_info": p.extra_info, "is_outdated": p.is_outdated,
                "risk_level": p.risk_level, "ai_explanation": p.ai_explanation or "",
                "banner": p.banner,
            }
            for p in sorted(scan.ports, key=lambda x: x.port_number)
        ]

        result_path = generate_pdf_report(
            scan_data={
                "target": scan.target,
                "scan_date": scan.scan_date.isoformat() if scan.scan_date else "",
                "scan_type": scan.scan_type,
                "risk_score": scan.risk_score,
            },
            ports=ports_data,
            ai_summary=scan.ai_summary or "",
            recommendations=scan.ai_recommendations or [],
            output_path=pdf_path,
        )
        if result_path.endswith(".html"):
            return FileResponse(result_path, media_type="text/html", filename="report.html")

    return FileResponse(pdf_path, media_type="application/pdf", filename="scanguard_report.pdf")


@router.post("/{scan_id}/comments", response_model=CommentResponse)
async def add_comment(
    scan_id: str,
    data: CommentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Scan not found")

    comment = ScanComment(
        id=uuid.uuid4(), scan_id=uuid.UUID(scan_id),
        user_id=user.id, content=data.content,
    )
    db.add(comment)
    await db.commit()

    return CommentResponse(
        id=str(comment.id), scan_id=str(comment.scan_id),
        user_id=str(comment.user_id), content=comment.content,
        user_name=user.full_name, created_at=comment.created_at,
    )


@router.get("/{scan_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanComment).where(ScanComment.scan_id == scan_id).order_by(ScanComment.created_at)
    )
    comments = result.scalars().all()
    return [
        CommentResponse(
            id=str(c.id), scan_id=str(c.scan_id), user_id=str(c.user_id),
            content=c.content, user_name=c.user.full_name, created_at=c.created_at,
        )
        for c in comments
    ]
