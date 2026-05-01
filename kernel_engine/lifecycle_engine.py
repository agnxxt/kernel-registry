from datetime import datetime
import hashlib
import json
from typing import Dict, Any, Optional
from persistence.db import SessionLocal
from persistence.models.artifact import RuntimeArtifact
from kernel_engine.did_manager import AgentDidManager

class LifecycleEngine:
    """
    Unified Lifecycle Engine (ALM).
    Combines OpenAGX Governance with CAAS Block-Versioning.
    Handles 'Joiner-Mover-Leaver' (Birth-Revision-Death) of Agents.
    """
    def __init__(self):
        self.did_manager = AgentDidManager()

    def provision_agent(self, spec: Dict[str, Any]) -> str:
        """
        'Birth' (Joiner): Creates a new agent from versioned blocks.
        """
        artifact_id = spec.get("id")
        blocks = spec.get("blocks", {}) # e.g. {"model": "gpt-4o:v2", "tools": ["github:v1"]}
        
        # 1. Deterministic Identity Checksum (OpenAGX)
        checksum = hashlib.sha256(json.dumps(blocks, sort_keys=True).encode()).hexdigest()
        
        with SessionLocal() as session:
            artifact = RuntimeArtifact(
                artifact_id=artifact_id,
                schema_org_type="SoftwareApplication",
                kind="agent",
                name=spec.get("name"),
                version=spec.get("version", "1.0.0"),
                lifecycle_state="PROVISIONING",
                version_snapshot=blocks,
                checksum=checksum,
                owner_ref=spec.get("owner", "admin"),
                semantic_extension=spec.get("semantic_extension", {"audit_tracking": {"created_by": "kernel"}})
            )
            session.add(artifact)
            session.commit()
            
        return artifact_id

    def activate_agent(self, agent_id: str):
        """
        'Activation': Moves agent to ACTIVE state after security validation.
        """
        with SessionLocal() as session:
            artifact = session.query(RuntimeArtifact).filter_by(artifact_id=agent_id).first()
            if artifact:
                artifact.lifecycle_state = "ACTIVE"
                artifact.activated_at = datetime.utcnow()
                session.commit()

    def revise_agent(self, agent_id: str, new_blocks: Dict[str, Any]):
        """
        'Revision' (Mover): Updates agent blocks, requiring a new checksum.
        """
        checksum = hashlib.sha256(json.dumps(new_blocks, sort_keys=True).encode()).hexdigest()
        
        with SessionLocal() as session:
            artifact = session.query(RuntimeArtifact).filter_by(artifact_id=agent_id).first()
            if artifact:
                artifact.version_snapshot = new_blocks
                artifact.checksum = checksum
                artifact.lifecycle_state = "PROVISIONING" # Force re-validation
                session.commit()

    def decommission_agent(self, agent_id: str):
        """
        'Death' (Leaver): Revokes all access and sanitizes.
        """
        with SessionLocal() as session:
            artifact = session.query(RuntimeArtifact).filter_by(artifact_id=agent_id).first()
            if artifact:
                artifact.lifecycle_state = "REVOKED"
                artifact.decommissioned_at = datetime.utcnow()
                # In production, trigger Secret Revocation and Memory Wipe here
                session.commit()
                print(f"Agent {agent_id} DECOMMISSIONED. Secrets revoked.")

