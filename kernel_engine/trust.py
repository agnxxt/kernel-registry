"""
Trust - First-Class Entity

Trust as a core entity for agent relationships:
- Trust Dimensions
- Trust Score
- Trust Factors
- Trust History
- Trust Networks
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Trust Core
# ============================================================

class TrustType:
    PERSONAL = "personal"
    INSTITUTIONAL = "institutional"
    SYSTEM = "system"
    TECHNOLOGICAL = "technological"
    COMPETENCE = "competence"
    BENEVOLENCE = "benevolence"
    INTEGRITY = "integrity"
    PREDICTABILITY = "predictability"


@dataclass
class Trust:
    """Trust (First-Class Entity)"""
    id: str
    
    trustor_id: str  # Who trusts
    trustee_id: str  # Who is trusted
    
    trust_type: str = "personal"
    
    score: float = 0.5  # 0-1
    
    competence: float = 0.5
    benevolence: float = 0.5
    integrity: float = 0.5
    predictability: float = 0.5
    
    context: str = ""
    domain: str = ""
    
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    is_trusted: bool = False
    verified: bool = False
    
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_score(self):
        """Calculate trust score from components"""
        self.score = (
            self.competence * 0.3 +
            self.benevolence * 0.3 +
            self.integrity * 0.25 +
            self.predictability * 0.15
        )
        self.is_trusted = self.score >= 0.5
    
    def update(self, delta: float):
        """Update trust score"""
        self.score = max(0, min(1, self.score + delta))
        self.last_updated = datetime.now().isoformat()
        self.calculate_score()
    
    def positive_interaction(self):
        """Record positive interaction"""
        self.positive_interactions += 1
        self.update(0.05)
    
    def negative_interaction(self):
        """Record negative interaction"""
        self.negative_interactions += 1
        self.update(-0.1)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trustor_id": self.trustor_id,
            "trustee_id": self.trustee_id,
            "trust_type": self.trust_type,
            "score": self.score,
            "is_trusted": self.is_trusted,
        }


# ============================================================
# Trust Factors
# ============================================================

class TrustFactorType:
    REPUTATION = "reputation"
    EXPERIENCE = "experience"
    RECOMMENDATION = "recommendation"
    CREDENTIAL = "credential"
    TRANSPARENCY = "transparency"
    COMMUNICATION = "communication"
    CONSISTENCY = "consistency"
    TRACK_RECORD = "track_record"


@dataclass
class TrustFactor:
    """Trust factor"""
    id: str
    
    factor_type: str = "reputation"
    
    impact: float = 0  # -1 to 1
    
    weight: float = 0.5  # 0-1
    
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "factor_type": self.factor_type,
            "impact": self.impact,
            "weight": self.weight,
        }


# ============================================================
# Trust Dynamics
# ============================================================

class TrustCause:
    POSITIVE_INTERACTION = "positive_interaction"
    NEGATIVE_INTERACTION = "negative_interaction"
    RECOMMENDATION = "recommendation"
    EVIDENCE = "evidence"
    TIME = "time"
    VERIFICATION = "verification"


@dataclass
class TrustChange:
    """Trust change"""
    id: str
    
    trust_id: str
    
    old_score: float
    new_score: float
    delta: float
    
    cause: str = "positive_interaction"
    
    description: str = ""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trust_id": self.trust_id,
            "old_score": self.old_score,
            "new_score": self.new_score,
            "delta": self.delta,
            "cause": self.cause,
        }


# ============================================================
# Trust Network
# ============================================================

@dataclass
class TrustNetwork:
    """Trust network"""
    id: str
    
    owner_id: str
    
    trusts: List[str] = field(default_factory=list)
    trusted_by: List[str] = field(default_factory=list)
    
    avg_trust_score: Optional[float] = None
    trust_worthiness: Optional[float] = None
    
    centrality: Optional[float] = None
    
    def calculate_avg(self, trust_scores: Dict[str, float]):
        """Calculate average trust score"""
        if not self.trusts:
            self.avg_trust_score = 0
            return
        
        scores = [trust_scores.get(t, 0) for t in self.trusts]
        self.avg_trust_score = sum(scores) / len(scores) if scores else 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "trust_count": len(self.trusts),
            "trusted_by_count": len(self.trusted_by),
            "avg_trust_score": self.avg_trust_score,
        }


# ============================================================
# Trust Profile
# ============================================================

@dataclass
class TrustProfile:
    """Trust profile"""
    id: str
    entity_id: str
    
    trusts: List[Trust] = field(default_factory=list)
    
    history: List[TrustChange] = field(default_factory=list)
    
    network: Optional[TrustNetwork] = None
    
    default_score: float = 0.5
    
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_trust(self, trust: Trust):
        """Add trust relationship"""
        self.trusts.append(trust)
    
    def get_trust(self, trustee_id: str) -> Optional[Trust]:
        """Get trust for entity"""
        for trust in self.trusts:
            if trust.trustee_id == trustee_id:
                return trust
        return None
    
    def update_trust(self, trustee_id: str, delta: float):
        """Update trust score"""
        trust = self.get_trust(trustee_id)
        if trust:
            old_score = trust.score
            trust.update(delta)
            
            # Record change
            change = TrustChange(
                id=str(uuid.uuid4()),
                trust_id=trust.id,
                old_score=old_score,
                new_score=trust.score,
                delta=trust.score - old_score,
            )
            self.history.append(change)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "trust_count": len(self.trusts),
            "default_score": self.default_score,
        }


# ============================================================
# Factory
# ============================================================

def create_trust(trustor_id: str, trustee_id: str, 
                trust_type: str = "personal") -> Trust:
    """Create trust"""
    return Trust(
        id=str(uuid.uuid4()),
        trustor_id=trustor_id,
        trustee_id=trustee_id,
        trust_type=trust_type,
    )


def create_trust_network(owner_id: str) -> TrustNetwork:
    """Create trust network"""
    return TrustNetwork(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
    )


__all__ = [
    'TrustType',
    'Trust',
    'TrustFactorType', 'TrustFactor',
    'TrustCause', 'TrustChange',
    'TrustNetwork',
    'TrustProfile',
    'create_trust', 'create_trust_network'
]