"""federated identity and sponsorship

Revision ID: 0005_federated_sponsorship
Revises: 0004_unified_lifecycle
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_federated_sponsorship"
down_revision = "0004_unified_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("canonical_identity", sa.Column("domain", sa.String(length=32), nullable=False, server_default="INTERNAL"))
    op.add_column("canonical_identity", sa.Column("sponsor_id", sa.String(length=128), nullable=True))
    op.create_foreign_key("fk_identity_sponsor", "canonical_identity", "canonical_identity", ["sponsor_id"], ["canonical_id"])


def downgrade() -> None:
    op.drop_constraint("fk_identity_sponsor", "canonical_identity", type_="foreignkey")
    op.drop_column("canonical_identity", "sponsor_id")
    op.drop_column("canonical_identity", "domain")
