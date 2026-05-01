"""unified lifecycle and caas blocks

Revision ID: 0004_unified_lifecycle
Revises: 0003_feast_source
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_unified_lifecycle"
down_revision = "0003_feast_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("runtime_artifact", sa.Column("version_snapshot", sa.JSON(), nullable=True))
    op.add_column("runtime_artifact", sa.Column("checksum", sa.String(length=256), nullable=True))
    op.add_column("runtime_artifact", sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("runtime_artifact", sa.Column("decommissioned_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("runtime_artifact", "decommissioned_at")
    op.drop_column("runtime_artifact", "activated_at")
    op.drop_column("runtime_artifact", "checksum")
    op.drop_column("runtime_artifact", "version_snapshot")
