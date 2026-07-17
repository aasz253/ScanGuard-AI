"""initial tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "teams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("invite_code", sa.String(100), unique=True, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), server_default="analyst"),
        sa.Column("team_id", UUID(as_uuid=True), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("dark_mode", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "scans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("target", sa.String(500), nullable=False),
        sa.Column("scan_type", sa.String(50), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("risk_score", sa.Integer, server_default=sa.text("0")),
        sa.Column("total_ports", sa.Integer, server_default=sa.text("0")),
        sa.Column("open_ports", sa.Integer, server_default=sa.text("0")),
        sa.Column("closed_ports", sa.Integer, server_default=sa.text("0")),
        sa.Column("filtered_ports", sa.Integer, server_default=sa.text("0")),
        sa.Column("outdated_services", sa.JSON, server_default=sa.text("'[]'")),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("ai_recommendations", sa.JSON, server_default=sa.text("'[]'")),
        sa.Column("raw_stats", sa.JSON, server_default=sa.text("'{}'")),
        sa.Column("status", sa.String(50), server_default="processing"),
        sa.Column("uploader_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", UUID(as_uuid=True), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("scan_date", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "scan_ports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("scan_id", UUID(as_uuid=True), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("port_number", sa.Integer, nullable=False),
        sa.Column("protocol", sa.String(10), nullable=False),
        sa.Column("state", sa.String(50), nullable=False),
        sa.Column("service", sa.String(255), nullable=True),
        sa.Column("version", sa.String(255), nullable=True),
        sa.Column("product", sa.String(255), nullable=True),
        sa.Column("extra_info", sa.Text, nullable=True),
        sa.Column("is_outdated", sa.Boolean, server_default=sa.text("false")),
        sa.Column("risk_level", sa.String(20), server_default="low"),
        sa.Column("ai_explanation", sa.Text, nullable=True),
        sa.Column("banner", sa.Text, nullable=True),
    )

    op.create_table(
        "scan_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("scan_id", UUID(as_uuid=True), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("scan_comments")
    op.drop_table("scan_ports")
    op.drop_table("scans")
    op.drop_table("users")
    op.drop_table("teams")
