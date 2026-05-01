from kernel_engine.telemetry import tracer
import os
import asyncio
from typing import Dict, Any, Optional
from kernel_engine.adapters.slack_adapter import SlackAdapter
from kernel_engine.adapters.jira_adapter import JiraAdapter
from kernel_engine.adapters.github_adapter import GitHubAdapter
from kernel_engine.secret_kernel import SecretKernel

class ActionExecutor:
    """
    Dispatches approved tasks to physical APIs or tool copilots.
    Implements POST-ACCESS Auditing to detect data leaks or policy drift.
    """
    def __init__(self, caas_gateway: Optional[Any] = None):
        self.secrets = SecretKernel()
        self.caas = caas_gateway

    async def execute(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with tracer.start_as_current_span("kernel.physical_execution") as span:
            span.set_attribute("action_id", action_id)
            tool_name = str(payload.get("object", {}).get("name", "unknown"))
            span.set_attribute("tool", tool_name)

            # 1. Execution Logic (Physical Adapters)
            result = await self._dispatch_physical_call(action_id, payload)

            # 2. Post-Access Audit (Fine-Grained Governance)
            if self.caas:
                agent_id = payload.get("agent", {}).get("name", "unknown")
                post_audit = self.caas.post_access_audit(agent_id, payload, result, {})
                if not post_audit["authorized"]:
                    # Violation detected after the fact (e.g. data leak)
                    # We return the violation result and flag it for the responder
                    result["execution_metadata"]["status"] = "PostAuditViolation"
                    result["execution_metadata"]["violation_reason"] = post_audit["reason"]
                    # Optionally: Wipe sensitive value from result before returning to agent
                    result["value"] = "[REDACTED: POST-ACCESS POLICY VIOLATION]"
            
            return result

    async def _dispatch_physical_call(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        action_type = payload.get("@type", "Action")
        target_obj = payload.get("object", {})
        repo_name = target_obj.get("name")
        
        # 1. GitHub Execution
        if action_type == "UpdateAction" and repo_name:
            token = self.secrets.get_secret("urn:agnxxt:secret:github-token")
            adapter = GitHubAdapter(token)
            p = payload.get("payload", {})
            try:
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

        # Fallback
        if os.getenv("MOCK_INFERENCE", "true").lower() == "false":
            raise NotImplementedError(f"Action type {action_type} lacks a physical execution adapter.")
            
        await asyncio.sleep(0.1) 
        return {
            "@type": "PropertyValue",
            "name": f"{action_type} Result",
            "value": "Execution completed (Simulated)",
            "execution_metadata": {"action_id": action_id, "status": "CompletedActionStatus"}
        }
