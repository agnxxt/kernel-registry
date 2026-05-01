from typing import Dict, Any, List
import json
from datetime import datetime
from persistence.db import SessionLocal
from persistence.models.artifact import RuntimeArtifact

class GraphAdapter:
    """
    Simulates the interface to the Agent Knowledge Graph.
    Ingests Schema.org actions and translates them into relational edges.
    Backed by Postgres persistence.
    """
    def __init__(self):
        pass

    def ingest_action(self, action_payload: Dict[str, Any]):
        """
        Maps an action to the graph ontology and persists it.
        """
        agent_id = action_payload.get("agent", {}).get("name", "unknown")
        action_id = action_payload.get("id", "temp_id")
        
        with SessionLocal() as session:
            # Map Action to RuntimeArtifact
            artifact = RuntimeArtifact(
                artifact_id=action_id,
                schema_org_type=action_payload.get("@type", "Action"),
                kind="governed_action",
                name=action_payload.get("name", f"Action {action_id[:8]}"),
                version="1.0.0",
                lifecycle_state="active",
                owner_ref=agent_id,
                semantic_extension=action_payload.get("semantic_extension", {})
            )
            session.add(artifact)
            session.commit()

    def query_facts(self, subject_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all facts asserted by or about a subject.
        In this relational mapping, we query the semantic_extension of the artifacts.
        """
        with SessionLocal() as session:
            artifact = session.query(RuntimeArtifact).filter(
                RuntimeArtifact.artifact_id == subject_id
            ).first()
            
            if not artifact:
                return []
            
            # Reconstruct the edges from the semantic extension
            ext = artifact.semantic_extension
            relations = ext.get("ontology", {}).get("relations", [])
            
            edges = []
            for rel in relations:
                edges.append({
                    "subject": rel.get("subject"),
                    "predicate": rel.get("predicate"),
                    "object": rel.get("object")
                })
            
            # Lineage
            lineage = ext.get("lineage", {})
            for source in lineage.get("source_artifacts", []):
                edges.append({
                    "subject": subject_id,
                    "predicate": "DERIVES_FROM",
                    "object": source
                })
                
            return edges
