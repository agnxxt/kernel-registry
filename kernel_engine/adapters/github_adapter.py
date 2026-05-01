from typing import Dict, Any
from github import Github
from kernel_engine.adapters.base import BaseAdapter

class GitHubAdapter(BaseAdapter):
    def __init__(self, token: str):
        self.client = Github(token)

    def get_supported_actions(self) -> list[str]:
        return ["UpdateAction"]

    def execute(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_obj = payload.get("object", {})
        repo_name = target_obj.get("name")
        p = payload.get("payload", {})
        
        try:
            repo = self.client.get_repo(repo_name)
            res = repo.create_file(
                path=p.get("file_path", f"audit_{action_id[:8]}.txt"),
                message=f"Agent-Kernel: {action_id}",
                content=str(payload.get("result_raw", "Update applied.")),
                branch=p.get("branch", "main")
            )
            return {
                "@type": "PropertyValue",
                "name": "GitHub Result",
                "value": f"Commit: {res['commit'].sha}",
                "execution_metadata": {"status": "CompletedActionStatus", "action_id": action_id}
            }
        except Exception as e:
            return {
                "@type": "PropertyValue",
                "name": "GitHub Error",
                "value": str(e),
                "execution_metadata": {"status": "FailedActionStatus", "action_id": action_id}
            }

    def validate_intent(self, repo_name: str, branch: str, file_path: str) -> Dict[str, Any]:
        try:
            repo = self.client.get_repo(repo_name)
            return {"exists": True, "protected": branch == repo.default_branch, "permissions": True}
        except:
            return {"exists": False}
