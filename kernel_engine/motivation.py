"""
Motivation - First-Class Entity

Motivation as a core entity driving all agent behavior:
- Motivation Types (intrinsic, extrinsic)
- Drivers (psychological needs)
- Values
- Incentives
- Rewards
- Goals alignment
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Motivation Core
# ============================================================

class MotivationType:
    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    ACHIEVEMENT = "achievement"
    POWER = "power"
    AFFILIATION = "affiliation"
    SECURITY = "security"
    GROWTH = "growth"
    PURPOSE = "purpose"
    AUTONOMY = "autonomy"
    COMPETENCE = "competence"
    RELATEDNESS = "relatedness"


class MotivationSource:
    SELF_DETERMINATION = "self_determination"
    BIOLOGICAL = "biological"
    SOCIAL = "social"
    CULTURAL = "cultural"
    ORGANIZATIONAL = "organizational"
    ENVIRONMENTAL = "environmental"


@dataclass
class Motivation:
    """Motivation (First-Class Entity)"""
    id: str
    name: str
    description: str = ""
    
    motivation_type: str = "intrinsic"
    
    source: str = "self_determination"
    
    strength: float = 0.5  # 0-1
    
    activation_threshold: float = 0.3
    
    decay_rate: float = 0.1
    
    is_active: bool = True
    
    satisfies_need_ids: List[str] = field(default_factory=list)
    
    def activate(self, current_level: float) -> bool:
        """Check if motivation is activated"""
        return self.is_active and current_level >= self.activation_threshold
    
    def decay(self):
        """Apply decay"""
        self.strength = max(0, self.strength * (1 - self.decay_rate))
    
    def strengthen(self, amount: float):
        """Strengthen motivation"""
        self.strength = min(1, self.strength + amount)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "motivation_type": self.motivation_type,
            "source": self.source,
            "strength": self.strength,
            "is_active": self.is_active,
        }


# ============================================================
# Psychological Needs
# ============================================================

class NeedType:
    PHYSIOLOGICAL = "physiological"
    SAFETY = "safety"
    LOVE_BELONGING = "love_belonging"
    ESTEEM = "esteem"
    SELF_ACTUALIZATION = "self_actualization"
    AUTONOMY = "autonomy"
    COMPETENCE = "competence"
    RELATEDNESS = "relatedness"
    MEANING = "meaning"
    CERTAINTY = "certainty"
    SIGNIFICANCE = "significance"
    CONNECTION = "connection"
    GROWTH = "growth"


@dataclass
class PsychologicalNeed:
    """Psychological need"""
    id: str
    name: str
    description: str = ""
    
    need_type: str = "autonomy"
    
    maslow_level: Optional[int] = None
    
    satisfaction: float = 0.5  # 0-1
    
    importance: float = 0.5  # 0-1
    
    deficiency_or_growth: str = "deficiency"  # D or G
    
    def is_deficient(self) -> bool:
        """Check if deficient"""
        return self.deficiency_or_growth == "deficiency" and self.satisfaction < 0.7
    
    def satisfy(self, amount: float):
        """Increase satisfaction"""
        self.satisfaction = min(1, self.satisfaction + amount)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "need_type": self.need_type,
            "satisfaction": self.satisfaction,
            "importance": self.importance,
        }


# ============================================================
# Values
# ============================================================

class ValueType:
    TERMINAL = "terminal"  # End states
    INSTRUMENTAL = "instrumental"  # Modes of conduct
    PERSONAL = "personal"
    SOCIAL = "social"
    MORAL = "moral"
    COMPETENCE = "competence"
    HEDONIC = "hedonic"


@dataclass
class Value:
    """Value"""
    id: str
    name: str
    description: str = ""
    
    value_type: str = "personal"
    
    importance: float = 0.5  # 0-1
    
    guides_behavior: bool = True
    
    rank: Optional[int] = None
    
    cultural_origin: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "value_type": self.value_type,
            "importance": self.importance,
            "guides_behavior": self.guides_behavior,
        }


# ============================================================
# Incentives
# ============================================================

class IncentiveType:
    TANGIBLE = "tangible"  # Money, goods
    INTANGIBLE = "intangible"  # Recognition, praise
    SOCIAL = "social"  # Approval
    INTRINSIC = "intrinsic"  # Enjoyment
    AVERSIVE = "aversive"  # Avoidance


@dataclass
class Incentive:
    """Incentive"""
    id: str
    name: str
    description: str = ""
    
    incentive_type: str = "tangible"
    
    value: float = 0
    
    motivates_ids: List[str] = field(default_factory=list)
    
    duration: Optional[float] = None  # seconds
    
    frequency: str = "one_time"
    
    is_available: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "incentive_type": self.incentive_type,
            "value": self.value,
            "is_available": self.is_available,
        }


# ============================================================
# Rewards
# ============================================================

class RewardType:
    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    SOCIAL = "social"
    FINANCIAL = "financial"
    RECOGNITION = "recognition"
    GROWTH = "growth"
    AUTONOMY = "autonomy"
    COMPETENCE = "competence"


@dataclass
class RewardEntity:
    """Reward"""
    id: str
    name: str
    description: str = ""
    
    reward_type: str = "extrinsic"
    
    value: float = 0
    cost: float = 0
    
    probability: float = 1.0
    
    timing: str = "immediate"
    
    goal_ids: List[str] = field(default_factory=list)
    
    given_at: str = ""
    given_to: str = ""
    
    def give(self, to: str):
        """Give reward"""
        self.given_to = to
        self.given_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "reward_type": self.reward_type,
            "value": self.value,
            "given_to": self.given_to,
        }


# ============================================================
# Motivation State
# ============================================================

@dataclass
class MotivationState:
    """Motivation state"""
    active_motivations: List[str] = field(default_factory=list)  # Motivation IDs
    
    satisfied_needs: Dict[str, float] = field(default_factory=dict)  # Need ID -> satisfaction
    
    active_values: List[str] = field(default_factory=list)  # Value IDs
    
    available_incentives: List[str] = field(default_factory=list)
    
    pending_rewards: List[str] = field(default_factory=list)
    
    energy_level: float = 0.5  # 0-1
    focus_level: float = 0.5  # 0-1
    
    def activate_motivation(self, motivation_id: str):
        """Activate motivation"""
        if motivation_id not in self.active_motivations:
            self.active_motivations.append(motivation_id)
    
    def to_dict(self) -> Dict:
        return {
            "active_motivations": self.active_motivations,
            "satisfied_needs": self.satisfied_needs,
            "energy_level": self.energy_level,
            "focus_level": self.focus_level,
        }


# ============================================================
# Motivation Dynamics
# ============================================================

@dataclass
class MotivationConflict:
    """Motivation conflict"""
    id: str
    
    motivation_ids: List[str] = field(default_factory=list)
    
    resolution: str = "contextual"  # satisfaction, suppression, compromise, contextual
    
    winner_id: str = ""
    
    impact_score: float = 0
    
    def resolve(self, winner_id: str):
        """Resolve conflict"""
        self.winner_id = winner_id
        self.resolution = "satisfaction"


@dataclass
class MotivationChain:
    """Motivation chain"""
    id: str
    
    chain: List[str] = field(default_factory=list)  # Motivation IDs
    
    goal_id: str = ""
    
    chain_strength: float = 0.5
    
    is_complete: bool = False
    
    def add_link(self, motivation_id: str):
        """Add to chain"""
        self.chain.append(motivation_id)
    
    def complete(self):
        """Mark complete"""
        self.is_complete = True


# ============================================================
# Motivation Profile
# ============================================================

@dataclass
class MotivationProfile:
    """Motivation profile"""
    id: str
    entity_id: str  # Agent or user
    
    motivations: List[Motivation] = field(default_factory=list)
    needs: List[PsychologicalNeed] = field(default_factory=list)
    values: List[Value] = field(default_factory=list)
    incentives: List[Incentive] = field(default_factory=list)
    rewards: List[RewardEntity] = field(default_factory=list)
    
    state: MotivationState = field(default_factory=MotivationState)
    
    conflict_ids: List[str] = field(default_factory=list)
    chain_ids: List[str] = field(default_factory=list)
    
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_motivation(self, motivation: Motivation):
        """Add motivation"""
        self.motivations.append(motivation)
    
    def get_motivation(self, motivation_id: str) -> Optional[Motivation]:
        """Get motivation"""
        for m in self.motivations:
            if m.id == motivation_id:
                return m
        return None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "motivation_count": len(self.motivations),
            "need_count": len(self.needs),
            "value_count": len(self.values),
        }


# ============================================================
# Factory
# ============================================================

def create_motivation(name: str, motivation_type: str = "intrinsic",
                    strength: float = 0.5) -> Motivation:
    """Create motivation"""
    return Motivation(
        id=str(uuid.uuid4()),
        name=name,
        motivation_type=motivation_type,
        strength=strength,
    )


def create_need(name: str, need_type: str = "autonomy") -> PsychologicalNeed:
    """Create need"""
    return PsychologicalNeed(
        id=str(uuid.uuid4()),
        name=name,
        need_type=need_type,
    )


def create_value(name: str, value_type: str = "personal") -> Value:
    """Create value"""
    return Value(
        id=str(uuid.uuid4()),
        name=name,
        value_type=value_type,
    )


__all__ = [
    'MotivationType', 'MotivationSource', 'Motivation',
    'NeedType', 'PsychologicalNeed',
    'ValueType', 'Value',
    'IncentiveType', 'Incentive',
    'RewardType', 'RewardEntity',
    'MotivationState',
    'MotivationConflict', 'MotivationChain',
    'MotivationProfile',
    'create_motivation', 'create_need', 'create_value'
]