"""extended kernel persistence schema

Revision ID: 0002_extended_schema
Revises: 0001_initial
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_extended_schema"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Identity Extended
    op.create_table(
        "trust_score",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_canonical_id", sa.String(length=128), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("tier", sa.String(length=32), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("factors", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["subject_canonical_id"], ["canonical_identity.canonical_id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "registry_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("canonical_id", sa.String(length=128), nullable=False),
        sa.Column("record_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("checksum", sa.String(length=256), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["canonical_id"], ["canonical_identity.canonical_id"]),
        sa.PrimaryKeyConstraint("id")
    )

    # 2. Decisions
    op.create_table(
        "decision",
        sa.Column("decision_id", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=True),
        sa.Column("step_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("effective_verdict", sa.String(length=32), nullable=False),
        sa.Column("required_approvals", sa.Integer(), nullable=False),
        sa.Column("allowed_rejections", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("decision_id")
    )

    # 3. Learning
    op.create_table(
        "feedback_event",
        sa.Column("feedback_id", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("rubric", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("feedback_id")
    )
    op.create_table(
        "improvement_proposal",
        sa.Column("proposal_id", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("target", sa.String(length=64), nullable=False),
        sa.Column("change_set", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("proposal_id")
    )

    # 4. Artifacts
    op.create_table(
        "runtime_artifact",
        sa.Column("artifact_id", sa.String(length=128), nullable=False),
        sa.Column("schema_org_type", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=32), nullable=False),
        sa.Column("semantic_extension", sa.JSON(), nullable=False),
        sa.Column("owner_ref", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("artifact_id")
    )


def downgrade() -> None:
    op.drop_table("runtime_artifact")
    op.drop_table("improvement_proposal")
    op.drop_table("feedback_event")
    op.drop_table("decision")
    op.drop_table("registry_record")
    op.drop_table("trust_score")
