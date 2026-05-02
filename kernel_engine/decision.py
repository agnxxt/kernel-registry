"""
Decision Engine - Decision Chaining from Decide

Supports decision alternatives, evidence, criteria, scoring, and approval workflows.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json


class DecisionStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CLOSED = "closed"


class DecisionPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# Decision Models
# ============================================================

@dataclass
class Decision:
    """Main decision entity"""
    id: str
    tenant_id: str
    title: str
    description: str = ""
    status: str = DecisionStatus.DRAFT.value
    priority: str = DecisionPriority.MEDIUM.value
    created_by: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    decided_at: Optional[float] = None
    implemented_at: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class DecisionAlternative:
    """Alternative for a decision"""
    id: str
    decision_id: str
    name: str
    description: str = ""
    pros: str = ""
    cons: str = ""
    cost_estimate: float = 0.0
    benefit_estimate: float = 0.0
    risk_level: str = "medium"
    is_recommended: bool = False
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "name": self.name,
            "description": self.description,
            "pros": self.pros,
            "cons": self.cons,
            "cost_estimate": self.cost_estimate,
            "benefit_estimate": self.benefit_estimate,
            "risk_level": self.risk_level,
            "is_recommended": self.is_recommended,
        }


@dataclass
class DecisionEvidence:
    """Evidence supporting a decision"""
    id: str
    alternative_id: str
    evidence_type: str  # data, research, expert_opinion, Anecdote
    description: str
    source: str = ""
    url: str = ""
    credibility: str = "medium"  # low, medium, high
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "alternative_id": self.alternative_id,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "source": self.source,
            "url": self.url,
            "credibility": self.credibility,
        }


@dataclass
class DecisionCriterion:
    """Criterion for evaluating alternatives"""
    id: str
    decision_id: str
    name: str
    description: str = ""
    weight: float = 1.0  # 0-1
    is_mandatory: bool = False
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "is_mandatory": self.is_mandatory,
        }


@dataclass
class DecisionScore:
    """Score for alternative against criterion"""
    id: str
    alternative_id: str
    criterion_id: str
    score: float  # 0-10
    reasoning: str = ""
    scored_by: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "alternative_id": self.alternative_id,
            "criterion_id": self.criterion_id,
            "score": self.score,
            "reasoning": self.reasoning,
            "scored_by": self.scored_by,
        }


@dataclass
class DecisionRecommendation:
    """Recommendation with rationale"""
    id: str
    decision_id: str
    alternative_id: str
    rationale: str
    conditions: str = ""
    recommended_by: str = ""
    recommended_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "alternative_id": self.alternative_id,
            "rationale": self.rationale,
            "conditions": self.conditions,
            "recommended_by": self.recommended_by,
        }


@dataclass
class DecisionApprovalStep:
    """Approval workflow step"""
    id: str
    decision_id: str
    step_order: int
    approver_role: str
    status: str = "pending"
    approved_by: str = ""
    approved_at: Optional[float] = None
    comments: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "step_order": self.step_order,
            "approver_role": self.approver_role,
            "status": self.status,
            "approved_by": self.approved_by,
            "comments": self.comments,
        }


@dataclass
class DecisionOutcome:
    """Outcome review"""
    id: str
    decision_id: str
    alternative_id: str
    outcome: str = ""  # successful, partially_successful, failed
    lessons_learned: str = ""
    reviewed_by: str = ""
    reviewed_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "alternative_id": self.alternative_id,
            "outcome": self.outcome,
            "lessons_learned": self.lessons_learned,
            "reviewed_by": self.reviewed_by,
        }


# ============================================================
# Decision Engine
# ============================================================

class DecisionEngine:
    """Decision chain execution engine"""
    
    def __init__(self):
        self.decisions: Dict[str, Decision] = {}
        self.alternatives: Dict[str, DecisionAlternative] = {}
        self.evidences: Dict[str, DecisionEvidence] = {}
        self.criteria: Dict[str, DecisionCriterion] = {}
        self.scores: Dict[str, DecisionScore] = {}
        self.recommendations: Dict[str, DecisionRecommendation] = {}
        self.approval_steps: Dict[str, DecisionApprovalStep] = {}
        self.outcomes: Dict[str, DecisionOutcome] = {}
    
    # --- CRUD ---
    
    def create_decision(self, tenant_id: str, title: str, 
                       description: str = "", created_by: str = "") -> Decision:
        """Create new decision"""
        decision = Decision(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            title=title,
            description=description,
            created_by=created_by,
        )
        self.decisions[decision.id] = decision
        return decision
    
    def add_alternative(self, decision_id: str, name: str,
                     description: str = "") -> DecisionAlternative:
        """Add alternative to decision"""
        alt = DecisionAlternative(
            id=str(uuid.uuid4()),
            decision_id=decision_id,
            name=name,
            description=description,
        )
        self.alternatives[alt.id] = alt
        return alt
    
    def add_evidence(self, alternative_id: str, evidence_type: str,
                   description: str, source: str = "") -> DecisionEvidence:
        """Add evidence to alternative"""
        ev = DecisionEvidence(
            id=str(uuid.uuid4()),
            alternative_id=alternative_id,
            evidence_type=evidence_type,
            description=description,
            source=source,
        )
        self.evidences[ev.id] = ev
        return ev
    
    def add_criterion(self, decision_id: str, name: str, 
                   weight: float = 1.0) -> DecisionCriterion:
        """Add criterion"""
        crit = DecisionCriterion(
            id=str(uuid.uuid4()),
            decision_id=decision_id,
            name=name,
            weight=weight,
        )
        self.criteria[crit.id] = crit
        return crit
    
    def add_score(self, alternative_id: str, criterion_id: str,
                 score: float, reasoning: str = "") -> DecisionScore:
        """Score alternative against criterion"""
        sc = DecisionScore(
            id=str(uuid.uuid4()),
            alternative_id=alternative_id,
            criterion_id=criterion_id,
            score=score,
            reasoning=reasoning,
        )
        self.scores[sc.id] = sc
        return sc
    
    def recommend(self, decision_id: str, alternative_id: str,
               rationale: str) -> DecisionRecommendation:
        """Add recommendation"""
        rec = DecisionRecommendation(
            id=str(uuid.uuid4()),
            decision_id=decision_id,
            alternative_id=alternative_id,
            rationale=rationale,
        )
        self.recommendations[rec.id] = rec
        return rec
    
    def add_approval_step(self, decision_id: str, step_order: int,
                       approver_role: str) -> DecisionApprovalStep:
        """Add approval step"""
        step = DecisionApprovalStep(
            id=str(uuid.uuid4()),
            decision_id=decision_id,
            step_order=step_order,
            approver_role=approver_role,
        )
        self.approval_steps[step.id] = step
        return step
    
    def record_outcome(self, decision_id: str, alternative_id: str,
                    outcome: str, lessons_learned: str = "") -> DecisionOutcome:
        """Record outcome"""
        out = DecisionOutcome(
            id=str(uuid.uuid4()),
            decision_id=decision_id,
            alternative_id=alternative_id,
            outcome=outcome,
            lessons_learned=lessons_learned,
        )
        self.outcomes[out.id] = out
        return out
    
    # --- Query ---
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get decision"""
        return self.decisions.get(decision_id)
    
    def get_alternatives(self, decision_id: str) -> List[DecisionAlternative]:
        """Get alternatives for decision"""
        return [a for a in self.alternatives.values() 
                if a.decision_id == decision_id]
    
    def get_evidence(self, alternative_id: str) -> List[DecisionEvidence]:
        """Get evidence for alternative"""
        return [e for e in self.evidences.values()
                if e.alternative_id == alternative_id]
    
    def get_criteria(self, decision_id: str) -> List[DecisionCriterion]:
        """Get criteria for decision"""
        return [c for c in self.criteria.values()
                if c.decision_id == decision_id]
    
    def calculate_scores(self, decision_id: str) -> Dict[str, float]:
        """Calculate weighted scores for alternatives"""
        criteria = self.get_criteria(decision_id)
        alternatives = self.get_alternatives(decision_id)
        
        scores = {}
        for alt in alternatives:
            total = 0
            total_weight = 0
            
            for crit in criteria:
                # Find score
                score = next((s for s in self.scores.values()
                          if s.alternative_id == alt.id
                          and s.criterion_id == crit.id), None)
                if score:
                    total += score.score * crit.weight
                    total_weight += crit.weight
            
            scores[alt.id] = total / total_weight if total_weight > 0 else 0
        
        return scores
    
    def get_recommendation(self, decision_id: str) -> Optional[DecisionRecommendation]:
        """Get recommendation for decision"""
        return next((r for r in self.recommendations.values()
                  if r.decision_id == decision_id), None)
    
    def get_approval_status(self, decision_id: str) -> Dict:
        """Get approval status"""
        steps = [s for s in self.approval_steps.values()
                if s.decision_id == decision_id]
        
        return {
            "total": len(steps),
            "approved": len([s for s in steps if s.status == "approved"]),
            "pending": len([s for s in steps if s.status == "pending"]),
        }
    
    # --- Export ---
    
    def export_decision(self, decision_id: str) -> Dict:
        """Export full decision"""
        decision = self.get_decision(decision_id)
        if not decision:
            return {}
        
        return {
            "decision": decision.to_dict(),
            "alternatives": [a.to_dict() for a in self.get_alternatives(decision_id)],
            "criteria": [c.to_dict() for c in self.get_criteria(decision_id)],
            "scores": self.calculate_scores(decision_id),
            "recommendation": self.get_recommendation(decision_id).to_dict() if self.get_recommendation(decision_id) else None,
            "approval_status": self.get_approval_status(decision_id),
        }


__all__ = [
    'DecisionStatus', 'DecisionPriority',
    'Decision', 'DecisionAlternative', 'DecisionEvidence',
    'DecisionCriterion', 'DecisionScore', 'DecisionRecommendation',
    'DecisionApprovalStep', 'DecisionOutcome', 'DecisionEngine'
]