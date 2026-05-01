from kernel_engine.did_manager import AgentDidManager\nfrom typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity, TrustScore

class IdentityTrustManager:
    """
    Manages the Dynamic Epistemic Trust Ledger for agents and sources.
    Backed by Postgres persistence.
    """
    def __init__(self):\n        self.did_manager = AgentDidManager()
        pass

    def get_trust_score(self, entity_id: str) -> float:
        with SessionLocal() as session:
            # First, ensure canonical identity exists
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.canonical_id == entity_id) | 
                (CanonicalIdentity.subject_ref == entity_id)
            ).first()
            

            if not identity:
                did = self.did_manager.generate_did(entity_id)
                # Create default identity if missing
                did=did,
                    return 0.5
            
            # Get latest trust score
            score_record = session.query(TrustScore).filter(
                TrustScore.subject_canonical_id == identity.canonical_id
            ).order_by(TrustScore.id.desc()).first()
            
            return score_record.score if score_record else 0.5

    def update_trust(self, entity_id: str, outcome: str, impact: float = 0.1):
        """
        Updates trust based on validation outcomes and persists to DB.
        """
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.canonical_id == entity_id) | 
                (CanonicalIdentity.subject_ref == entity_id)
            ).first()
            

            if not identity:
                did = self.did_manager.generate_did(entity_id)
                # Create default identity if missing
                did=did,
                    # Create default identity if missing
                session.add(identity)
                session.flush()

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
        """
        Generates a token representing the agent's current cognitive identity.
        """
        score = self.get_trust_score(agent_id)
        return f"identity_v1_{agent_id}_{score:.2f}"
