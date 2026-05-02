from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.db import Base


class CanonicalIdentity(Base):
    __tablename__ = "canonical_identity"

    canonical_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # Multi-tenant isolation
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False) # Human, Agent, Organization
    subject_ref: Mapped[str] = mapped_column(String(128), nullable=False)
    issuer: Mapped[str] = mapped_column(String(128), nullable=False)
    did: Mapped[str | None] = mapped_column(String(256))
    
    # Federated Sponsorship Model
    domain: Mapped[str] = mapped_column(String(32), default="INTERNAL", nullable=False) # INTERNAL, EXTERNAL, VENDOR, CUSTOMER, PROJECT
    sponsor_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("canonical_identity.canonical_id"))
    
    # CIAM & Time-Bound Federated Grants
    grant_type: Mapped[str] = mapped_column(String(32), default="PERMANENT") # PERMANENT, TIME_BOUND, EPHEMERAL
    grant_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    grant_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    consent_metadata: Mapped[dict | None] = mapped_column(JSON) # Scopes, data sharing agreements
    
    key_id: Mapped[str | None] = mapped_column(String(256))
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Self-referential relationship for sponsorship
    sponsor = relationship("CanonicalIdentity", remote_side=[canonical_id])

class VerifiableCredential(Base):
    __tablename__ = "verifiable_credential"

    vc_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    holder_canonical_id: Mapped[str] = mapped_column(ForeignKey("canonical_identity.canonical_id"), nullable=False)
    vc_type: Mapped[str] = mapped_column(String(128), nullable=False)
    issuer: Mapped[str] = mapped_column(String(128), nullable=False)
    proof_type: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    credential_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    claims: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class Wallet(Base):
    __tablename__ = "wallet"

    wallet_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    holder_canonical_id: Mapped[str] = mapped_column(ForeignKey("canonical_identity.canonical_id"), nullable=False)
    chain: Mapped[str] = mapped_column(String(64), nullable=False)
    network: Mapped[str] = mapped_column(String(64), nullable=False)
    address: Mapped[str] = mapped_column(String(256), nullable=False)
    public_key: Mapped[str | None] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TrustScore(Base):
    __tablename__ = "trust_score"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_canonical_id: Mapped[str] = mapped_column(ForeignKey("canonical_identity.canonical_id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    tier: Mapped[str] = mapped_column(String(32), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    factors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RegistryRecord(Base):
    __tablename__ = "registry_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_id: Mapped[str] = mapped_column(ForeignKey("canonical_identity.canonical_id"), nullable=False)
    record_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(256))
    attributes: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
