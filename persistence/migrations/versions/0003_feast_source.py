"""add feast source table

Revision ID: 0003_feast_source
Revises: 0002_extended_schema
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_feast_source"
down_revision = "0002_extended_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cognitive_metrics",
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("avg_latency_ms", sa.Integer(), nullable=False),
        sa.Column("historical_hallucination_rate", sa.Float(), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_metrics_agent_timestamp", "cognitive_metrics", ["agent_id", "event_timestamp"])


def downgrade() -> None:
    op.drop_table("cognitive_metrics")
