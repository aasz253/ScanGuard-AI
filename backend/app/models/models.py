import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")  # admin, manager, analyst, viewer
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)
    dark_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="members")
    scans = relationship("Scan", back_populates="uploader")


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    invite_code = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = relationship("User", back_populates="team")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    target = Column(String(500), nullable=False)
    scan_type = Column(String(50), nullable=False)  # quick, full, stealth, custom
    file_type = Column(String(20), nullable=False)  # xml, gnmap, nmap
    file_path = Column(String(1024), nullable=False)
    risk_score = Column(Integer, default=0)
    total_ports = Column(Integer, default=0)
    open_ports = Column(Integer, default=0)
    closed_ports = Column(Integer, default=0)
    filtered_ports = Column(Integer, default=0)
    outdated_services = Column(JSON, default=list)
    ai_summary = Column(Text, nullable=True)
    ai_recommendations = Column(JSON, default=list)
    raw_stats = Column(JSON, default=dict)
    status = Column(String(50), default="processing")  # processing, completed, failed
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    scan_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploader = relationship("User", back_populates="scans")
    ports = relationship("ScanPort", back_populates="scan", cascade="all, delete-orphan")


class ScanPort(Base):
    __tablename__ = "scan_ports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    port_number = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False)
    state = Column(String(50), nullable=False)
    service = Column(String(255), nullable=True)
    version = Column(String(255), nullable=True)
    product = Column(String(255), nullable=True)
    extra_info = Column(Text, nullable=True)
    is_outdated = Column(Boolean, default=False)
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    ai_explanation = Column(Text, nullable=True)
    banner = Column(Text, nullable=True)

    scan = relationship("Scan", back_populates="ports")


class ScanComment(Base):
    __tablename__ = "scan_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
