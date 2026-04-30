from typing import Dict, Any, List
from persistence.db import SessionLocal
from persistence.models.identity import RegistryRecord, CanonicalIdentity

class CognitiveFeatureStore:
    """
    Stores and retrieves pre-calculated cognitive features.
    Backed by RegistryRecords in the Postgres database.
    """
    def __init__(self):
        pass

    def get_agent_features(self, agent_id: str) -> Dict[str, Any]:
        """
        Retrieves the feature vector for a specific agent from RegistryRecords.
        """
        with SessionLocal() as session:
            # Try to find a registry record for the agent
            record = session.query(RegistryRecord).join(CanonicalIdentity).filter(
                (CanonicalIdentity.subject_ref == agent_id) | 
                (CanonicalIdentity.canonical_id == agent_id),
                RegistryRecord.record_type == "cognitive_features"
            ).order_by(RegistryRecord.id.desc()).first()
            
            if record:
                return record.attributes
            
            # Default features
            return {
                "avg_latency_ms": 0,
                "historical_hallucination_rate": 0,
                "common_biases": [],
                "skill_scores": {}
            }

    def update_skill_score(self, agent_id: str, skill: str, delta: float):
        """
        Updates an agent's skill competency and persists to RegistryRecord.
        """
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.subject_ref == agent_id) | 
                (CanonicalIdentity.canonical_id == agent_id)
            ).first()
            
            if not identity:
                 return # Cannot update features for unknown agent

            features = self.get_agent_features(agent_id)
            scores = features.setdefault("skill_scores", {})
            scores[skill] = max(0, min(1, scores.get(skill, 0.5) + delta))
            
            # Upsert registry record
            record = session.query(RegistryRecord).filter(
                RegistryRecord.canonical_id == identity.canonical_id,
                RegistryRecord.record_type == "cognitive_features"
            ).first()
            
            if record:
                record.attributes = features
            else:
                record = RegistryRecord(
                    canonical_id=identity.canonical_id,
                    record_type="cognitive_features",
                    status="active",
                    source="kernel:feature_store",
                    attributes=features
                )
                session.add(record)
            
            session.commit()
