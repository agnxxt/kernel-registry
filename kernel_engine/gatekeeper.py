from typing import Dict, Any
from kernel_engine.adapters.github_adapter import GitHubAdapter
from kernel_engine.secret_kernel import SecretKernel

class ToolGatekeeper:
    """
    Implements Intelligent Runtime Authentication for Tool-Specific Copilots.
    Now integrates with real GitHub API via GitHubAdapter.
    """
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.secrets = SecretKernel() # Using our secure kernel for tokens

    def authenticate_request(self, agent_id: str, action_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs cognitive validation and real-world availability checks.
        """
        # 1. Retrieve real token from Secret Kernel
        token = self.secrets.get_secret("urn:agnxxt:secret:github-token")
        if not token:
            return {"authenticated": False, "reason": "System Error: Tool credentials missing from Secret Kernel."}

        # 2. Extract targets from payload
        target_obj = action_payload.get("object", {})
        repo_name = target_obj.get("name")
        branch = action_payload.get("payload", {}).get("branch", "main")

        if self.tool_name == "GitHub" and repo_name:
            adapter = GitHubAdapter(token)
            # Intelligent Check: Validate intent against repo state
            validation = adapter.validate_intent(repo_name, branch, "")
            
            if not validation.get("exists"):
                return {"authenticated": False, "reason": f"GitHub Gatekeeper: Target repository '{repo_name}' not found."}
            
            if validation.get("protected") and "force" in str(action_payload).lower():
                return {"authenticated": False, "reason": f"Deontic Violation: Force-pushing to protected branch '{branch}' is constitutionally forbidden."}

            return {
                "authenticated": True, 
                "gatekeeper_signature": f"sig-{self.tool_name}-live-valid",
                "permissions_verified": validation.get("permissions")
            }

        return {"authenticated": True, "gatekeeper_signature": f"sig-{self.tool_name}-mock-valid"}
