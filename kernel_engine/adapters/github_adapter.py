from github import Github, GithubException
from typing import Dict, Any, List
import os

class GitHubAdapter:
    """
    Real-world adapter for GitHub. 
    Handles Intelligent Authentication and Action Execution.
    """
    def __init__(self, token: str):
        self.client = Github(token)

    def validate_intent(self, repo_name: str, branch: str, file_path: str) -> Dict[str, Any]:
        """
        Intelligent Check: Does the target exist and is it protected?
        """
        try:
            repo = self.client.get_repo(repo_name)
            # Verify branch protection as a Deontic check
            branch_info = repo.get_branch(branch)
            return {
                "exists": True,
                "protected": branch_info.protected,
                "permissions": repo.permissions.push
            }
        except GithubException as e:
            return {"exists": False, "error": str(e)}

    def execute_code_change(self, repo_name: str, branch: str, file_path: str, content: str, message: str):
        """
        Performs the actual GitHub commit/update.
        """
        repo = self.client.get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path, ref=branch)
            return repo.update_file(
                contents.path, 
                message, 
                content, 
                contents.sha, 
                branch=branch
            )
        except GithubException:
            # Create if it doesn't exist
            return repo.create_file(file_path, message, content, branch=branch)

