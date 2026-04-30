from typing import Dict, Any, List
import uuid
from datetime import datetime

class AgentBuilder:
    """
    Assembles a deployable Agent Artifact based on discovered profiles and admin policy.
    Implements the 'Targeted User Provisioning' phase.
    """
    def __init__(self, validator=None):
        self.validator = validator

    def assemble_agent(self, user_profile: Dict[str, Any], cognitive_config: Dict[str, Any], admin_policy: List[str]) -> Dict[str, Any]:
        """
        Creates a complete RuntimeArtifact for a new user agent.
        """
        agent_id = f"agent-{user_profile.get('name', 'user').lower()}-{str(uuid.uuid4())[:8]}"
        
        artifact = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "artifact_id": agent_id,
            "kind": "worker",
            "name": f"Assistant for {user_profile.get('name')}",
            "version": "1.0.0",
            "lifecycle_state": "active",
            "owner_ref": user_profile.get("name"),
            "environment": "prod",
            "runtime": {
                "provider_topology": { "primary_provider": "hybrid", "is_multi_cloud": True },
                "framework_signature": { "name": "PydanticAI", "language": "Python" },
                "model_signature": {
                    "primary_model": "gemini-1.5-pro",
                    "provider": "google",
                    "fallback_models": ["gpt-4o"]
                }
            },
            "spec": {
                "objectives": cognitive_config.get("objectives", []),
                "deontic_guardrails": admin_policy
            },
            "semantic_extension": {
                "taxonomy": { "labels": ["provisioned_agent", "user_assistant"] },
                "attributes": cognitive_config.get("personality", {}),
                "lineage": {
                    "source_artifacts": ["urn:agnxxt:onboarding:approval-01"],
                    "transformation_logic": "Assembled via AgentBuilder from approved user profile."
                },
                "audit_tracking": {
                    "created_by": "System-Agent-Builder",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
        }
        
        return artifact

