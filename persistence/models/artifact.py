from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from persistence.db import Base

class RuntimeArtifact(Base):
    """
    Unified Schema.org storage for all Kernel Artifacts.
    Implements the 'One Universal Schema' principle.
    """
    __tablename__ = "runtime_artifact"

    artifact_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    schema_org_type: Mapped[str] = mapped_column(String(128), nullable=False) # e.g. AssessAction
    kind: Mapped[str] = mapped_column(String(128), nullable=False) # e.g. epistemic_trust
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(32), default="active")
    
    # The Universal Semantic Extension block
    semantic_extension: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Audit fields extracted for indexing
    owner_ref: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RuntimeArtifact(id={self.artifact_id}, kind={self.kind}, version={self.version})>"
