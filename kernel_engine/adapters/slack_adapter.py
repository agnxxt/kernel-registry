from typing import Dict, Any
from slack_sdk import WebClient
from kernel_engine.adapters.base import BaseAdapter

class SlackAdapter(BaseAdapter):
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def get_supported_actions(self) -> list[str]:
        return ["CommunicateAction"]

    def execute(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            recipient = str(payload.get("recipient", "general"))
            text = str(payload.get("message", {}).get("text", ""))
            response = self.client.chat_postMessage(channel=recipient, text=text)
            return {
                "@type": "PropertyValue",
                "name": "Slack Result",
                "value": "Message sent",
                "execution_metadata": {"status": "CompletedActionStatus", "action_id": action_id}
            }
        except Exception as e:
            return {
                "@type": "PropertyValue",
                "name": "Slack Error",
                "value": str(e),
                "execution_metadata": {"status": "FailedActionStatus", "action_id": action_id}
            }
