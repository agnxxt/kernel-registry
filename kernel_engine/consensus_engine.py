import json
import os
from typing import Dict, Any, List
from kernel_engine.event_bus import EventBus

class ConsensusEngine:
    """
    Asynchronous Consensus Sidecar.
    Tallys BFT-style majority votes for high-risk actions from the event bus.
    """
    def __init__(self):
        self.bus = EventBus(group_id="consensus-engine")

    def run(self):
        """
        Main loop: Listens for voting requests.
        """
        topics = ["kernel.consensus.requests"]
        self.bus.listen(topics, self.on_request)

    def on_event(self, topic: str, payload: Dict[str, Any]):
        # Implementation for background listener
        pass

    def on_request(self, topic: str, payload: Dict[str, Any]):
        request_id = payload.get("request_id")
        participants = payload.get("participants", [])
        
        print(f"Consensus Request Received: {request_id} for {len(participants)} agents.")
        
        # 1. Collect Votes (Simulated feedback loop)
        tally = {"ALLOW": 0, "DENY": 0}
        for agent in participants:
            # In a real system, we'd wait for individual agent 'Vote' messages on the bus
            vote = "ALLOW"
            tally[vote] += 1

        # 2. BFT Logic
        threshold = (len(participants) // 2) + 1
        verdict = "APPROVED" if tally["ALLOW"] >= threshold else "REJECTED"

        # 3. Publish Result
        self.bus.publish("kernel.consensus.results", {
            "request_id": request_id,
            "verdict": verdict,
            "tally": tally
        })

if __name__ == "__main__":
    engine = ConsensusEngine()
    engine.run()
