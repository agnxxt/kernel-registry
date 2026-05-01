from typing import Dict, Any
import os
from jira import JIRA

class JiraAdapter:
    def __init__(self, api_key: str, server: str = "https://your-domain.atlassian.net"):
        # Expecting JIRA_EMAIL env for basic auth with API Key
        email = os.getenv("JIRA_EMAIL", "admin@example.com")
        self.client = JIRA(server=server, basic_auth=(email, api_key))

    def update_issue(self, issue_id: str, comment: str) -> Dict[str, Any]:
        try:
            self.client.add_comment(issue_id, comment)
            return {"status": "updated", "issue": issue_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
