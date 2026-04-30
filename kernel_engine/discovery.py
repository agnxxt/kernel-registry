from typing import Dict, Any, List
import uuid
from kernel_engine.adapters.github_adapter import GitHubAdapter
from kernel_engine.secret_kernel import SecretKernel

class DiscoveryEngine:
    """
    Autonomously discovers Users, Repositories, and Permissions from connected apps.
    Now integrates with real GitHub crawling.
    """
    def __init__(self):
        self.secrets = SecretKernel()

    def crawl_github_org(self, org_name: str) -> List[Dict[str, Any]]:
        """
        Crawls a real GitHub Organization to discover entities.
        """
        token = self.secrets.get_secret("urn:agnxxt:secret:github-token")
        if not token:
            return []
            
        adapter = GitHubAdapter(token)
        discovered = []

        try:
            org = adapter.client.get_organization(org_name)
            
            # 1. Discover Repositories as SoftwareApplications
            for repo in org.get_repos():
                discovered.append({
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
                })

            # 2. Discover Users as Persons
            for member in org.get_members():
                discovered.append({
                    "@type": "Person",
                    "name": member.login,
                    "identifier": f"urn:agnxxt:user:github:{member.id}",
                    "semantic_extension": {
                        "taxonomy": {"labels": ["user", "org_member"]},
                        "attributes": {"github_profile": member.html_url}
                    }
                })
        except Exception as e:
            print(f"Discovery Error: {e}")

        return discovered

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
