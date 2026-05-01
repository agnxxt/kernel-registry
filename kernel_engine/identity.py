from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity, TrustScore
from kernel_engine.did_manager import AgentDidManager

class IdentityTrustManager:
    """
    Manages the Dynamic Epistemic Trust Ledger and Federated Sponsorship.
    Backed by Postgres persistence.
    """
    def __init__(self):
        self.did_manager = AgentDidManager()

    def get_trust_score(self, entity_id: str) -> float:
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.canonical_id == entity_id) | 
                (CanonicalIdentity.subject_ref == entity_id)
            ).first()
            if not identity:
                return 0.5
            score_record = session.query(TrustScore).filter(
                TrustScore.subject_canonical_id == identity.canonical_id
            ).order_by(TrustScore.id.desc()).first()
            return score_record.score if score_record else 0.5

    def register_identity(self, spec: Dict[str, Any]) -> CanonicalIdentity:
        """
        Registers a new identity with Domain and Sponsor metadata.
        Supports Internal, External, Vendor, Customer, and Project agents.
        """
        entity_id = spec.get("id")
        domain = spec.get("domain", "INTERNAL")
        sponsor_id = spec.get("sponsor_id")
        
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter_by(canonical_id=entity_id).first()
            if not identity:
                did = self.did_manager.generate_did(entity_id)
                identity = CanonicalIdentity(
                    canonical_id=entity_id,
                    subject_type=spec.get("type", "Agent"),
                    subject_ref=spec.get("name", entity_id),
                    issuer="kernel:identity:manager",
                    did=did,
                    domain=domain,
                    sponsor_id=sponsor_id,
                    metadata_json=spec.get("metadata", {})
                )
                session.add(identity)
                session.commit()
                session.refresh(identity)
            return identity

    def update_trust(self, entity_id: str, outcome: str, impact: float = 0.1):
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.canonical_id == entity_id) | 
                (CanonicalIdentity.subject_ref == entity_id)
            ).first()
            
            if not identity:
                identity = self.register_identity({"id": entity_id, "name": entity_id})

            current_score = self.get_trust_score(identity.canonical_id)
            if outcome == "success":
                new_score = min(1.0, current_score + (impact * 0.5))
            elif outcome == "betrayal":
                new_score = max(0.0, current_score - impact)
            else:
                new_score = current_score

            new_record = TrustScore(
                subject_canonical_id=identity.canonical_id,
                score=new_score,
                tier="Cognitive",
                model_version="v1",
                factors=["interaction_outcome"],
                evidence={"outcome": outcome, "impact": impact, "timestamp": datetime.utcnow().isoformat()}
            )
            session.add(new_record)
            session.commit()

    def generate_identity_signature(self, agent_id: str) -> str:
        score = self.get_trust_score(agent_id)
        return f"identity_v1_{agent_id}_{score:.2f}"
