"""
Trust Score - First-Class Entity

Trust Score as a core entity for reputation and reliability:
- Trust Score Components
- Trust Calculation
- Trust History
- Trust Verification
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Trust Score Core
# ============================================================

@dataclass
class TrustScore:
    """Trust Score (First-Class Entity)"""
    id: str
    
    subject_id: str
    subject_type: str = "agent"
    
    # Components
    competence: float = 0.5
    reliability: float = 0.5
    integrity: float = 0.5
    benevolence: float = 0.5
    capability: float = 0.5
    
    # Overall score
    score: float = 0.5
    
    # Confidence
    confidence: float = 0.5
    
    # Level
    level: str = "medium"
    
    # Verifications
    verified: bool = False
    verified_by: List[str] = field(default_factory=list)
    
    # History
    total_interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    # Weights
    weight_competence: float = 0.2
    weight_reliability: float = 0.25
    weight_integrity: float = 0.25
    weight_benevolence: float = 0.15
    weight_capability: float = 0.15
    
    # Timestamps
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_score(self):
        """Calculate overall score"""
        self.score = (
            self.competence * self.weight_competence +
            self.reliability * self.weight_reliability +
            self.integrity * self.weight_integrity +
            self.benevolence * self.weight_benevolence +
            self.capability * self.weight_capability
        )
        self._update_level()
        self.last_updated = datetime.now().isoformat()
    
    def _update_level(self):
        """Update trust level"""
        if self.score >= 0.8:
            self.level = "trusted"
        elif self.score >= 0.6:
            self.level = "high"
        elif self.score >= 0.4:
            self.level = "medium"
        elif self.score >= 0.2:
            self.level = "low"
        else:
            self.level = "untrusted"
    
    def update_from_interaction(self, interaction_type: str, impact: float = 0.5):
        """Update from interaction"""
        self.total_interactions += 1
        
        delta = impact * 0.1  # 10% max change per interaction
        
        if interaction_type == "success":
            self.positive_interactions += 1
            self.competence = min(1, self.competence + delta)
            self.reliability = min(1, self.reliability + delta)
        elif interaction_type == "failure":
            self.negative_interactions += 1
            self.competence = max(0, self.competence - delta)
            self.reliability = max(0, self.reliability - delta)
        
        self.calculate_score()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "score": self.score,
            "level": self.level,
            "confidence": self.confidence,
            "total_interactions": self.total_interactions,
            "positive_ratio": self.positive_interactions / max(1, self.total_interactions),
        }


# ============================================================
# Trust Calculation
# ============================================================

@dataclass
class TrustCalculationInput:
    """Trust calculation input"""
    interaction_type: str = "success"
    impact: float = 0.5
    category: str = "performance"
    evidence: List[str] = field(default_factory=list)
    source: str = ""


# ============================================================
# Trust History
# ============================================================

class TrustEventType:
    INTERACTION = "interaction"
    VERIFICATION = "verification"
    RECOMMENDATION = "recommendation"
    REVIEW = "review"
    PENALTY = "penalty"
    REWARD = "reward"


@dataclass
class TrustEvent:
    """Trust event"""
    id: str
    
    trust_score_id: str
    
    event_type: str = "interaction"
    
    description: str = ""
    
    score_delta: float = 0
    
    # Component changes
    competence_delta: float = 0
    reliability_delta: float = 0
    integrity_delta: float = 0
    benevolence_delta: float = 0
    capability_delta: float = 0
    
    metadata: Dict = field(default_factory=dict)
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trust_score_id": self.trust_score_id,
            "event_type": self.event_type,
            "description": self.description,
            "score_delta": self.score_delta,
            "timestamp": self.timestamp,
        }


# ============================================================
# Trust Verification
# ============================================================

@dataclass
class TrustVerification:
    """Trust verification"""
    id: str
    
    trust_score_id: str
    
    verifier_id: str
    
    method: str = "manual_review"
    
    is_verified: bool = False
    verification_level: float = 0
    
    evidence: List[str] = field(default_factory=list)
    
    valid_until: str = ""
    
    verified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trust_score_id": self.trust_score_id,
            "verifier_id": self.verifier_id,
            "is_verified": self.is_verified,
            "verification_level": self.verification_level,
        }


# ============================================================
# Factory
# ============================================================

def create_trust_score(subject_id: str, subject_type: str = "agent") -> TrustScore:
    """Create trust score"""
    return TrustScore(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        subject_type=subject_type,
    )


__all__ = [
    'TrustScore',
    'TrustCalculationInput',
    'TrustEventType', 'TrustEvent',
    'TrustVerification',
    'create_trust_score'
]