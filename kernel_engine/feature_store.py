from typing import Dict, Any, List
import os
from persistence.db import SessionLocal
from persistence.models.identity import RegistryRecord, CanonicalIdentity

# Optional import for prod
try:
    from feast import FeatureStore
except ImportError:
    FeatureStore = None

class CognitiveFeatureStore:
    """
    Stores and retrieves pre-calculated cognitive features.
    Backed by Feast for production-grade online serving.
    """
    def __init__(self):
        repo_path = os.getenv("FEAST_REPO_PATH", "feature_repo")
        try:
            self.store = FeatureStore(repo_path=repo_path) if FeatureStore else None
        except Exception:
            self.store = None

    def get_agent_features(self, agent_id: str) -> Dict[str, Any]:
        """
        Retrieves the feature vector for a specific agent via Feast online store.
        """
        if self.store:
            try:
                # 1. Fetch from Feast Online Store
                entity_rows = [{"agent_id": agent_id}]
                features = [
                    "agent_cognitive_metrics:avg_latency_ms",
                    "agent_cognitive_metrics:historical_hallucination_rate"
                ]
                response = self.store.get_online_features(
                    feature_refs=features,
                    entity_rows=entity_rows
                ).to_dict()
                
                # Cleanup Feast response
                return {
                    "avg_latency_ms": response.get("avg_latency_ms", [0])[0],
                    "historical_hallucination_rate": response.get("historical_hallucination_rate", [0])[0],
                    "source": "Feast"
                }
            except Exception as e:
                print(f"Feast Fetch Error: {e}")

        # 2. Fallback to RegistryRecords (Legacy/Local-Dev)
        with SessionLocal() as session:
            record = session.query(RegistryRecord).join(CanonicalIdentity).filter(
                (CanonicalIdentity.subject_ref == agent_id) | 
                (CanonicalIdentity.canonical_id == agent_id),
                RegistryRecord.record_type == "cognitive_features"
            ).order_by(RegistryRecord.id.desc()).first()
            
            if record:
                return record.attributes
            
            return {
                "avg_latency_ms": 0,
                "historical_hallucination_rate": 0,
                "common_biases": [],
                "skill_scores": {},
                "source": "Fallback"
            }

    def update_skill_score(self, agent_id: str, skill: str, delta: float):
        """
        Updates an agent's skill competency and persists to RegistryRecord.
        Note: Writing back to Feast typically happens via an offline batch process.
        """
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.subject_ref == agent_id) | 
                (CanonicalIdentity.canonical_id == agent_id)
            ).first()
            
            if not identity:
                 return

            features = self.get_agent_features(agent_id)
            scores = features.setdefault("skill_scores", {})
            scores[skill] = max(0, min(1, scores.get(skill, 0.5) + delta))
            
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
