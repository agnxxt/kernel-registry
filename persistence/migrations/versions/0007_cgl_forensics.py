"""cgl forensics and behavioral audit tables

Revision ID: 0007_cgl_forensics
Revises: 0006_timebound_grants
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0007_cgl_forensics"
down_revision = "0006_timebound_grants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. CGL Tasks & Lifecycle
    op.create_table(
        "cgl_tasks",
        sa.Column("task_id", sa.String(length=128), primary_key=True),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("declared_intent", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 2. Reasoning & CoT Audit
    op.create_table(
        "cgl_reasoning",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("raw_cot", sa.Text(), nullable=False),
        sa.Column("audit_verdict", sa.String(length=32), nullable=False),
        sa.Column("violations", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 3. Drift & Sycophancy Scores
    op.create_table(
        "cgl_drift_scores",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False), # 0-1000
        sa.Column("signals", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    op.create_table(
        "cgl_sycophancy",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("pattern_type", sa.String(length=64), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 4. Memory Boundaries & Session Keys
    op.create_table(
        "cgl_session_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("key_name", sa.String(length=256), nullable=False),
        sa.Column("storage_provider", sa.String(length=64), nullable=False),
    )

    # 5. Planner Iterations (Microsoft SK/AutoGen pattern)
    op.create_table(
        "cgl_planner_iterations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("iteration_count", sa.Integer(), nullable=False),
        sa.Column("selected_tool", sa.String(length=128), nullable=True),
        sa.Column("directive", sa.String(length=32), nullable=False), # CONTINUE, TERMINATE, etc.
    )


def downgrade() -> None:
    op.drop_table("cgl_planner_iterations")
    op.drop_table("cgl_session_keys")
    op.drop_table("cgl_sycophancy")
    op.drop_table("cgl_drift_scores")
    op.drop_table("cgl_reasoning")
    op.drop_table("cgl_tasks")
