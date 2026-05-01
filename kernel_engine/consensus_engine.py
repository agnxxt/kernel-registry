import json
import os
import time
from typing import Dict, Any, List
from kernel_engine.event_bus import EventBus

class ConsensusEngine:
    """
    Independent Consensus Sidecar.
    Handles BFT-style voting for high-risk kernel actions.
    Listens to 'kernel.consensus.requests' and publishes to 'kernel.consensus.results'.
    """
    def __init__(self):
        self.bus = EventBus()
        self.votes = {} # In-memory vote tracking for this demo

    def run(self):
        """
        Main loop: In a real system, this would be a Kafka consumer.
        For this prototype, we simulate the voting logic.
        """
        print("Consensus Engine Online. Waiting for voting requests...")
        while True:
            # Simulation: Check for pending votes (e.g. from a shared state or queue)
            # In production, use confluent_kafka Consumer
            time.sleep(10)

    def process_vote_request(self, request_id: str, action_payload: Dict[str, Any], participants: List[str]):
        """
        Triggers a new voting round among a group of agents.
        """
        print(f"Starting consensus round {request_id} for action {action_payload.get('@type')}")
        
        # 1. Broadast Vote Request to the bus
        self.bus.publish("kernel.consensus.requests", {
            "request_id": request_id,
            "payload": action_payload,
            "participants": participants,
            "expires_at": time.time() + 30
        })

        # 2. Heuristic: Auto-generate votes from participant agents 
        # (Simulating real agent feedback)
        tally = {"ALLOW": 0, "DENY": 0}
        for agent in participants:
            # Simulate high-trust agents always voting ALLOW
            vote = "ALLOW" 
            tally[vote] += 1

        # 3. Determine Result (BFT Majority)
        threshold = (len(participants) // 2) + 1
        verdict = "APPROVED" if tally["ALLOW"] >= threshold else "REJECTED"
        
        # 4. Publish Final Result
        self.bus.publish("kernel.consensus.results", {
            "request_id": request_id,
            "verdict": verdict,
            "tally": tally
        })
        
        return verdict

if __name__ == "__main__":
    engine = ConsensusEngine()
    engine.run()
