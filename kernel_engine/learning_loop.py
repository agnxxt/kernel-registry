from typing import Dict, Any, List
from datetime import datetime
import uuid
from persistence.db import SessionLocal
from persistence.models.learning import FeedbackEvent, ImprovementProposal

class LearningLoop:
    """
    Captures feedback and generates Improvement Proposals.
    The 'Self-Improving' engine of the kernel.
    Backed by Postgres persistence.
    """
    def __init__(self, tracker=None):
        self.tracker = tracker # MLflow tracker

    def capture_feedback(self, action_id: str, feedback: Dict[str, Any]):
        """
        Registers human or peer feedback and persists to DB.
        """
        score = feedback.get("score", 1.0)
        
        with SessionLocal() as session:
            # Register feedback event
            event = FeedbackEvent(
                feedback_id=str(uuid.uuid4()),
                tenant_id=feedback.get("tenant_id", "default"),
                agent_id=feedback.get("agent_id", "unknown"),
                task_id=feedback.get("task_id", "unknown"),
                run_id=feedback.get("run_id", action_id), # Fallback to action_id
                source="user",
                score=int(score * 100), # Normalize to 0-100
                comment=feedback.get("comment", ""),
                rubric=feedback.get("rubric", {})
            )
            session.add(event)
            
            # If score is low, generate an Improvement Proposal autonomously
            proposal_id = None
            if score < 0.5:
                proposal = self._generate_proposal(action_id, feedback)
                db_proposal = ImprovementProposal(
                    proposal_id=proposal["id"],
                    tenant_id=event.tenant_id,
                    agent_id=event.agent_id,
                    task_id=event.task_id,
                    run_id=event.run_id,
                    target=proposal["target_artifact"],
                    change_set=str(proposal["patch_delta"]),
                    rationale=proposal["rationale"],
                    confidence=0.85,
                    status="PROPOSED",
                    evidence=feedback
                )
                session.add(db_proposal)
                proposal_id = proposal["id"]
            
            session.commit()
            
            if proposal_id:
                return {"status": "Feedback-Received", "proposal_id": proposal_id}

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
