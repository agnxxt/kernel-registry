from typing import Dict, Any, List
import uuid
from kernel_engine.adapters.github_adapter import GitHubAdapter
from kernel_engine.secret_kernel import SecretKernel
from persistence.db import SessionLocal
from persistence.models.identity import CanonicalIdentity, RegistryRecord

class DiscoveryEngine:
    """
    Autonomously discovers Users, Repositories, and Permissions from connected apps.
    Now integrates with real GitHub crawling and Postgres persistence.
    """
    def __init__(self):
        self.secrets = SecretKernel()

    def crawl_github_org(self, org_name: str) -> List[Dict[str, Any]]:
        """
        Crawls a real GitHub Organization to discover entities and persists them.
        """
        token = self.secrets.get_secret("urn:agnxxt:secret:github-token")
        if not token:
            return []
            
        adapter = GitHubAdapter(token)
        discovered = []

        try:
            org = adapter.client.get_organization(org_name)
            
            with SessionLocal() as session:
                # 1. Discover Repositories as SoftwareApplications
                for repo in org.get_repos():
                    entity = {
                        "@type": "SoftwareApplication",
                        "name": repo.full_name,
                        "identifier": f"urn:agnxxt:artifact:github:{repo.id}",
                        "semantic_extension": {
                            "taxonomy": {"labels": ["repository", "source_code"]},
                            "attributes": {
                                "stars": repo.stargazers_count,
                                "is_private": repo.private,
                                "default_branch": repo.default_branch
                            }
                        }
                    }
                    discovered.append(entity)
                    self._persist_entity(session, entity, "github_discovery")

                # 2. Discover Users as Persons
                for member in org.get_members():
                    entity = {
                        "@type": "Person",
                        "name": member.login,
                        "identifier": f"urn:agnxxt:user:github:{member.id}",
                        "semantic_extension": {
                            "taxonomy": {"labels": ["user", "org_member"]},
                            "attributes": {"github_profile": member.html_url}
                        }
                    }
                    discovered.append(entity)
                    self._persist_entity(session, entity, "github_discovery")
                
                session.commit()
        except Exception as e:
            print(f"Discovery Error: {e}")

        return discovered

    def _persist_entity(self, session, entity: Dict[str, Any], source: str):
        """
        Helper to persist discovered entities to the Registry.
        """
        canonical_id = entity["identifier"]
        
        # Check if identity exists
        identity = session.query(CanonicalIdentity).filter_by(canonical_id=canonical_id).first()
        if not identity:
            identity = CanonicalIdentity(
                canonical_id=canonical_id,
                subject_type=entity["@type"],
                subject_ref=entity["name"],
                issuer=f"kernel:discovery:{source}",
                metadata_json=entity.get("semantic_extension", {})
            )
            session.add(identity)
            session.flush()

        # Update or create registry record
        record = session.query(RegistryRecord).filter_by(
            canonical_id=canonical_id,
            record_type="discovery_artifact"
        ).first()
        
        if record:
            record.attributes = entity
        else:
            record = RegistryRecord(
                canonical_id=canonical_id,
                record_type="discovery_artifact",
                status="active",
                source=source,
                attributes=entity
            )
            session.add(record)

    def generate_provisioning_request(self, user_id: str) -> Dict[str, Any]:
        """
        Generates the Schema.org outreach action for targeted provisioning.
        """
        return {
            "@context": "https://schema.org",
            "@type": "CommunicateAction",
            "name": "Provisioning Outreach",
            "recipient": {"@type": "Person", "name": user_id},
            "payload": {
                "text": f"Hello {user_id}, your GitHub organization is connected. Let's set up your agent."
            }
        }
