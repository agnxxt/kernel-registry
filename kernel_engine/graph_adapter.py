from typing import Dict, Any, List
import json

class GraphAdapter:
    """
    Simulates the interface to the Agent Knowledge Graph.
    Ingests Schema.org actions and translates them into relational edges.
    """
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def ingest_action(self, action_payload: Dict[str, Any]):
        """
        Maps an action to the graph ontology.
        """
        agent_id = action_payload.get("agent", {}).get("name", "unknown")
        action_id = action_payload.get("id", "temp_id")
        
        # 1. Register Action Node
        self.nodes[action_id] = {
            "type": action_payload.get("@type"),
            "name": action_payload.get("name")
        }

        # 2. Extract Relational Edges from semantic_extension
        ext = action_payload.get("semantic_extension", {})
        relations = ext.get("ontology", {}).get("relations", [])
        
        for rel in relations:
            self.edges.append({
                "subject": rel.get("subject"),
                "predicate": rel.get("predicate"),
                "object": rel.get("object")
            })

        # 3. Automatic Lineage Edge
        lineage = ext.get("lineage", {})
        for source in lineage.get("source_artifacts", []):
            self.edges.append({
                "subject": action_id,
                "predicate": "DERIVES_FROM",
                "object": source
            })

    def query_facts(self, subject_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all facts asserted by or about a subject.
        """
        return [e for e in self.edges if e["subject"] == subject_id]

