import asyncio
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

        # 2. Default/Simulated Execution for other types
        await asyncio.sleep(0.1) 
        return {
            "@type": "PropertyValue",
            "name": f"{action_type} Result",
            "value": "Execution completed (Simulated)",
            "execution_metadata": {"action_id": action_id, "status": "CompletedActionStatus"}
        }

