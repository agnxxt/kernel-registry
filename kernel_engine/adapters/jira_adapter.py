from typing import Dict, Any
from jira import JIRA
import os
from kernel_engine.adapters.base import BaseAdapter

class JiraAdapter(BaseAdapter):
    def __init__(self, api_key: str):
        email = os.getenv("JIRA_EMAIL", "admin@example.com")
        server = os.getenv("JIRA_SERVER", "https://your-domain.atlassian.net")
        self.client = JIRA(server=server, basic_auth=(email, api_key))

    def get_supported_actions(self) -> list[str]:
        return ["UpdateAction"]

    def execute(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            issue_id = payload.get("object", {}).get("name", "TASK-101")
            comment = "Governed kernel update"
            self.client.add_comment(issue_id, comment)
            return {
                "@type": "PropertyValue",
                "name": "Jira Result",
                "value": "Comment added",
                "execution_metadata": {"status": "CompletedActionStatus", "action_id": action_id}
            }
        except Exception as e:
            return {
                "@type": "PropertyValue",
                "name": "Jira Error",
                "value": str(e),
                "execution_metadata": {"status": "FailedActionStatus", "action_id": action_id}
            }
