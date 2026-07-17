from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


# Auth
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    dark_mode: bool
    team_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Team
class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    invite_code: Optional[str]
    member_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TeamJoin(BaseModel):
    invite_code: str


# Scan
class ScanResponse(BaseModel):
    id: str
    title: str
    target: str
    scan_type: str
    file_type: str
    risk_score: int
    total_ports: int
    open_ports: int
    closed_ports: int
    filtered_ports: int
    outdated_services: list
    ai_summary: Optional[str]
    ai_recommendations: list
    status: str
    uploader_id: str
    team_id: Optional[str]
    scan_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ScanPortResponse(BaseModel):
    id: str
    port_number: int
    protocol: str
    state: str
    service: Optional[str]
    version: Optional[str]
    product: Optional[str]
    extra_info: Optional[str]
    is_outdated: bool
    risk_level: str
    ai_explanation: Optional[str]
    banner: Optional[str]

    class Config:
        from_attributes = True


class ScanDetailResponse(ScanResponse):
    ports: List[ScanPortResponse] = []


class DashboardStats(BaseModel):
    total_scans: int
    total_open_ports: int
    avg_risk_score: float
    critical_findings: int
    recent_scans: List[ScanResponse]
    risk_trend: list
    port_distribution: list
    scan_type_distribution: list


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: str
    scan_id: str
    user_id: str
    content: str
    user_name: str
    created_at: datetime
