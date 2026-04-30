from typing import Dict, Any, List
from datetime import datetime
import uuid

class LearningLoop:
    """
    Captures feedback and generates Improvement Proposals.
    The 'Self-Improving' engine of the kernel.
    """
    def __init__(self, tracker=None):
        self.tracker = tracker # MLflow tracker
        self.proposals = []

    def capture_feedback(self, action_id: str, feedback: Dict[str, Any]):
        """
        Registers human or peer feedback for a completed action.
        """
        score = feedback.get("score", 1.0)
        comment = feedback.get("comment", "")
        
        # 1. If score is low, generate an Improvement Proposal autonomously
        if score < 0.5:
            proposal = self._generate_proposal(action_id, feedback)
            self.proposals.append(proposal)
            return {"status": "Feedback-Received", "proposal_id": proposal["id"]}

        return {"status": "Feedback-Received"}

    def _generate_proposal(self, action_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new version of a cognitive artifact to fix a failure.
        """
        return {
            "id": str(uuid.uuid4()),
            "target_artifact": "dual_process_theory",
            "change_type": "patch",
            "patch_delta": {"add_engagement_trigger": "low_confidence_feedback"},
            "rationale": f"Action {action_id} failed due to: {feedback.get('comment')}",
            "created_at": datetime.utcnow().isoformat()
        }

