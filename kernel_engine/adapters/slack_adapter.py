from typing import Dict, Any
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackAdapter:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def send_message(self, channel: str, text: str) -> Dict[str, Any]:
        try:
            response = self.client.chat_postMessage(channel=channel, text=text)
            return {"status": "ok", "channel": channel, "ts": response["ts"]}
        except SlackApiError as e:
            return {"status": "error", "message": str(e)}

