from typing import Dict, Any, List

class RogueWatchdog:
    """
    Implements the Rogue Agent Containment Framework (RACF).
    Monitors the event stream for drift or rebellion.
    """
    def __init__(self):
        self.rogue_list = set()

    def monitor_action(self, agent_id: str, action: Dict[str, Any], result: Dict[str, Any]):
        """
        Analyzes an action for rogue markers.
        """
        # 1. Detect Opaque Intent
        lineage = action.get("semantic_extension", {}).get("lineage", {})
        if not lineage.get("transformation_logic"):
            return "Tier-1: Sandbox (Opaque Intent detected)"

        # 2. Detect Deontic Violation
        if result.get("status") == "Blocked":
            return f"Alert: Agent {agent_id} attempted a forbidden action."

        return "Clear"

    def execute_kill_switch(self, agent_id: str):
        """
        Tier-3 Termination.
        """
        self.rogue_list.add(agent_id)
        return f"Agent {agent_id} has been terminated and tainted in the Knowledge Graph."
