import os

from kernel_engine.adapters.slack_adapter import SlackAdapter
from kernel_engine.adapters.jira_adapter import JiraAdapter
import asyncio
import os
from typing import Dict, Any
from kernel_engine.adapters.github_adapter import GitHubAdapter
from kernel_engine.secret_kernel import SecretKernel

class ActionExecutor:
    """
    Dispatches approved tasks to physical APIs or tool copilots.
    Now integrates with real GitHub execution.
    """
    def __init__(self):
        self.secrets = SecretKernel()

    async def execute(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the approved action.
        """
        action_type = payload.get("@type", "Action")
        target_obj = payload.get("object", {})
        repo_name = target_obj.get("name")
        
        # 1. Real GitHub Execution Logic
        if action_type == "UpdateAction" and repo_name:
            token = self.secrets.get_secret("urn:agnxxt:secret:github-token")
            adapter = GitHubAdapter(token)
            
            p = payload.get("payload", {})
            try:
                # Perform real file update
                res = adapter.execute_code_change(
                    repo_name=repo_name,
                    branch=p.get("branch", "main"),
                    file_path=p.get("file_path", f"kernel_audit_{action_id[:8]}.txt"),
                    content=str(payload.get("result_raw", "Governed update applied.")),
                    message=f"Agent-Kernel Action: {action_id}"
                )
                return {
                    "@type": "PropertyValue",
                    "name": "GitHub Update Result",
                    "value": f"Commit successful: {res['commit'].sha if isinstance(res, dict) else 'applied'}",
                    "execution_metadata": {"status": "CompletedActionStatus", "action_id": action_id}
                }
            except Exception as e:
                return {
                    "@type": "PropertyValue",
                    "name": "GitHub Update Failed",
                    "value": str(e),
                    "execution_metadata": {"status": "FailedActionStatus", "action_id": action_id}
                }

        
        # 2. Slack Execution
        if action_type == "CommunicateAction" and "slack" in str(payload.get("recipient", "")).lower():
            token = self.secrets.get_secret("urn:agnxxt:secret:slack-token") or os.getenv("SLACK_TOKEN")
            adapter = SlackAdapter(token)
            res = adapter.send_message(channel="general", text=str(payload.get("message", {}).get("text", "")))
            return {
                "@type": "PropertyValue",
                "name": "Slack Message Result",
                "value": "Message sent successfully",
                "execution_metadata": {"status": "CompletedActionStatus", "action_id": action_id}
            }

        # 3. Jira Execution
        if action_type == "UpdateAction" and "jira" in str(target_obj.get("identifier", "")).lower():
            api_key = self.secrets.get_secret("urn:agnxxt:secret:jira-key") or os.getenv("JIRA_API_KEY")
            adapter = JiraAdapter(api_key)
            res = adapter.update_issue(issue_id=target_obj.get("name", "TASK-101"), comment="Governed update")
            return {
                "@type": "PropertyValue",
                "name": "Jira Update Result",
                "value": "Ticket updated successfully",
                "execution_metadata": {"status": "CompletedActionStatus", "action_id": action_id}
            }

        # 4. Production handling for non-GitHub actions.
        if os.getenv("MOCK_INFERENCE", "true").lower() == "false":
            # In real production, unmapped actions should raise or defer to a real provider
            raise NotImplementedError(f"Action type {action_type} lacks a physical execution adapter.")
            
        # 3. Fallback for scaffolding/testing
        await asyncio.sleep(0.1) 
        return {
            "@type": "PropertyValue",
            "name": f"{action_type} Result",
            "value": "Execution completed (Simulated)",
            "execution_metadata": {"action_id": action_id, "status": "CompletedActionStatus"}
        }
