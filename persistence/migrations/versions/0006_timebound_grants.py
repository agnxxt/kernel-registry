"""timebound grants and ciam

Revision ID: 0006_timebound_grants
Revises: 0005_federated_sponsorship
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0006_timebound_grants"
down_revision = "0005_federated_sponsorship"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("canonical_identity", sa.Column("grant_type", sa.String(length=32), nullable=False, server_default="PERMANENT"))
    op.add_column("canonical_identity", sa.Column("grant_start_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("canonical_identity", sa.Column("grant_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("canonical_identity", sa.Column("consent_metadata", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("canonical_identity", "consent_metadata")
    op.drop_column("canonical_identity", "grant_expires_at")
    op.drop_column("canonical_identity", "grant_start_at")
    op.drop_column("canonical_identity", "grant_type")
