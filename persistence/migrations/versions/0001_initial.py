"""initial kernel persistence schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_identity",
        sa.Column("canonical_id", sa.String(length=128), primary_key=True),
        sa.Column("subject_type", sa.String(length=32), nullable=False),
        sa.Column("subject_ref", sa.String(length=128), nullable=False),
        sa.Column("issuer", sa.String(length=128), nullable=False),
        sa.Column("did", sa.String(length=256), nullable=True),
        sa.Column("key_id", sa.String(length=256), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "verifiable_credential",
        sa.Column("vc_id", sa.String(length=256), primary_key=True),
        sa.Column("holder_canonical_id", sa.String(length=128), sa.ForeignKey("canonical_identity.canonical_id"), nullable=False),
        sa.Column("vc_type", sa.String(length=128), nullable=False),
        sa.Column("issuer", sa.String(length=128), nullable=False),
        sa.Column("proof_type", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("credential_hash", sa.String(length=256), nullable=False),
        sa.Column("claims", sa.JSON(), nullable=False),
    )

    op.create_table(
        "wallet",
        sa.Column("wallet_id", sa.String(length=128), primary_key=True),
        sa.Column("holder_canonical_id", sa.String(length=128), sa.ForeignKey("canonical_identity.canonical_id"), nullable=False),
        sa.Column("chain", sa.String(length=64), nullable=False),
        sa.Column("network", sa.String(length=64), nullable=False),
        sa.Column("address", sa.String(length=256), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("wallet")
    op.drop_table("verifiable_credential")
    op.drop_table("canonical_identity")
