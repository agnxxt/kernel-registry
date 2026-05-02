"""
Intention - First-Class Entity

Intention as a core entity driving agent behavior:
- Intention Types
- Intention State
- Plans
- Commitment
- Volition
- Willpower
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Intention Core
# ============================================================

class IntentionType:
    DESIRE = "desire"
    GOAL = "goal"
    PLAN = "plan"
    COMMITMENT = "commitment"
    RESOLUTION = "resolution"
    WISH = "wish"
    HOPE = "hope"
    DREAM = "dream"
    AMBITION = "ambition"
    PURPOSE = "purpose"


class IntentionSource:
    REASONING = "reasoning"
    EMOTION = "emotion"
    INSTINCT = "instinct"
    CULTURE = "culture"
    AUTHORITY = "authority"
    SELF = "self"


class IntentionStatus:
    LATENT = "latent"
    ACTIVATED = "activated"
    FORMING = "forming"
    FORMED = "formed"
    ACTING = "acting"
    SUSPENDED = "suspended"
    FULFILLED = "fulfilled"
    ABANDONED = "abandoned"
    FAILED = "failed"


@dataclass
class Intention:
    """Intention (First-Class Entity)"""
    id: str
    content: str
    description: str = ""
    
    intention_type: str = "desire"
    
    source: str = "reasoning"
    
    strength: float = 0.5  # 0-1
    urgency: float = 0.5
    importance: float = 0.5
    
    status: str = "latent"
    
    target_id: str = ""
    target_type: str = ""
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    activated_at: str = ""
    fulfilled_at: str = ""
    abandoned_at: str = ""
    
    def activate(self):
        """Activate intention"""
        self.status = IntentionStatus.ACTIVATED
        self.activated_at = datetime.now().isoformat()
    
    def fulfill(self):
        """Fulfill intention"""
        self.status = IntentionStatus.FULFILLED
        self.fulfilled_at = datetime.now().isoformat()
    
    def abandon(self):
        """Abandon intention"""
        self.status = IntentionStatus.ABANDONED
        self.abandoned_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "intention_type": self.intention_type,
            "strength": self.strength,
            "urgency": self.urgency,
            "importance": self.importance,
            "status": self.status,
        }


# ============================================================
# Intention Components
# ============================================================

@dataclass
class Volition:
    """Volition (willpower)"""
    id: str
    
    capacity: float = 0.5  # Max willpower
    current: float = 0.5   # Current level
    
    depletion_rate: float = 0.1
    recovery_rate: float = 0.05
    
    is_depleted: bool = False
    
    intention_ids: List[str] = field(default_factory=list)
    
    def deplete(self, amount: float):
        """Deplete willpower"""
        self.current = max(0, self.current - amount)
        if self.current < 0.1:
            self.is_depleted = True
    
    def recover(self):
        """Recover willpower"""
        self.current = min(self.capacity, self.current + self.recovery_rate)
        if self.current > 0.2:
            self.is_depleted = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "capacity": self.capacity,
            "current": self.current,
            "is_depleted": self.is_depleted,
        }


class CommitmentLevel:
    CASUAL = "casual"
    SERIOUS = "serious"
    DEEP = "deep"
    SACRED = "sacred"


@dataclass
class Commitment:
    """Commitment"""
    id: str
    
    intention_id: str
    
    level: str = "serious"
    
    made_to: str = ""
    
    is_public: bool = False
    
    breaking_cost: float = 1
    
    status: str = "pending"
    
    made_at: str = field(default_factory=lambda: datetime.now().isoformat())
    fulfilled_at: str = ""
    broken_at: str = ""
    
    def fulfill(self):
        """Fulfill commitment"""
        self.status = "fulfilled"
        self.fulfilled_at = datetime.now().isoformat()
    
    def break_commitment(self):
        """Break commitment"""
        self.status = "broken"
        self.broken_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intention_id": self.intention_id,
            "level": self.level,
            "status": self.status,
        }


@dataclass
class ActionStep:
    """Action in a plan"""
    id: str
    action: str
    order: int = 0
    
    dependencies: List[str] = field(default_factory=list)
    
    status: str = "pending"  # pending, ready, executing, completed, failed


@dataclass
class Plan:
    """Plan (intention + action sequence)"""
    id: str
    
    intention_id: str
    
    actions: List[ActionStep] = field(default_factory=list)
    
    status: str = "planning"
    
    confidence: float = 0.5
    flexibility: float = 0.5
    
    start_by: str = ""
    complete_by: str = ""
    
    def add_action(self, action: str, order: int = 0):
        """Add action"""
        step = ActionStep(
            id=str(uuid.uuid4()),
            action=action,
            order=order,
        )
        self.actions.append(step)
        self.actions.sort(key=lambda a: a.order)
    
    def next_action(self) -> Optional[ActionStep]:
        """Get next ready action"""
        for action in self.actions:
            if action.status == "ready":
                return action
            if action.status == "pending":
                # Check dependencies
                deps_ready = all(
                    self._get_action(a).status == "completed" 
                    for a in action.dependencies
                )
                if deps_ready:
                    action.status = "ready"
                    return action
        return None
    
    def _get_action(self, action_id: str) -> ActionStep:
        """Get action by ID"""
        for a in self.actions:
            if a.id == action_id:
                return a
        return ActionStep(id="", action="")
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intention_id": self.intention_id,
            "action_count": len(self.actions),
            "status": self.status,
            "confidence": self.confidence,
        }


# ============================================================
# Intention State
# ============================================================

@dataclass
class IntentionState:
    """Intention state"""
    active: List[str] = field(default_factory=list)  # Intention IDs
    
    pending: List[str] = field(default_factory=list)
    suspended: List[str] = field(default_factory=list)
    fulfilled: List[str] = field(default_factory=list)
    abandoned: List[str] = field(default_factory=list)
    
    primary: str = ""
    secondary: List[str] = field(default_factory=list)
    
    def activate(self, intention_id: str):
        """Activate intention"""
        if intention_id not in self.active:
            self.active.append(intention_id)
            if intention_id in self.pending:
                self.pending.remove(intention_id)
    
    def fulfill(self, intention_id: str):
        """Fulfill intention"""
        if intention_id in self.active:
            self.active.remove(intention_id)
        if intention_id in self.pending:
            self.pending.remove(intention_id)
        self.fulfilled.append(intention_id)
    
    def abandon(self, intention_id: str):
        """Abandon intention"""
        if intention_id in self.active:
            self.active.remove(intention_id)
        self.abandoned.append(intention_id)
    
    def to_dict(self) -> Dict:
        return {
            "active_count": len(self.active),
            "pending_count": len(self.pending),
            "fulfilled_count": len(self.fulfilled),
            "primary": self.primary,
        }


# ============================================================
# Intention Dynamics
# ============================================================

@dataclass
class IntentionFormation:
    """Intention formation"""
    trigger: str = ""
    
    antecedents: List[str] = field(default_factory=list)
    
    intention_id: str = ""
    
    deliberation: str = ""
    reasoning: str = ""
    
    formed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "trigger": self.trigger,
            "intention_id": self.intention_id,
            "formed_at": self.formed_at,
        }


@dataclass
class IntentionConflict:
    """Intention conflict"""
    id: str
    
    intention_ids: List[str] = field(default_factory=list)
    
    resolution: str = "priority"  # priority, bundle, sequence, choose, abandon
    
    winner_id: str = ""
    
    method: str = "deliberation"
    
    def resolve(self, winner_id: str):
        """Resolve conflict"""
        self.winner_id = winner_id
        self.resolution = "priority"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intention_ids": self.intention_ids,
            "winner_id": self.winner_id,
            "resolution": self.resolution,
        }


@dataclass
class IntentionExecution:
    """Intention execution"""
    id: str
    
    intention_id: str
    
    plan_id: str = ""
    
    progress: float = 0
    
    blocks: List[str] = field(default_factory=list)
    
    resumed_at: str = ""
    completed_at: str = ""
    
    result: str = "pending"  # success, failure, abandoned, pending
    
    def execute_action(self):
        """Execute next action"""
        self.progress = min(1.0, self.progress + 0.1)
    
    def complete(self, success: bool = True):
        """Complete execution"""
        self.completed_at = datetime.now().isoformat()
        self.result = "success" if success else "failure"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intention_id": self.intention_id,
            "progress": self.progress,
            "result": self.result,
        }


# ============================================================
# Intention Profile
# ============================================================

@dataclass
class IntentionProfile:
    """Intention profile"""
    id: str
    entity_id: str  # Agent or user
    
    intentions: List[Intention] = field(default_factory=list)
    
    volition: Volition = field(default_factory=Volition)
    
    commitments: List[Commitment] = field(default_factory=list)
    
    plans: List[Plan] = field(default_factory=list)
    
    state: IntentionState = field(default_factory=IntentionState)
    
    conflict_ids: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_intention(self, intention: Intention):
        """Add intention"""
        self.intentions.append(intention)
    
    def get_intention(self, intention_id: str) -> Optional[Intention]:
        """Get intention"""
        for i in self.intentions:
            if i.id == intention_id:
                return i
        return None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "intention_count": len(self.intentions),
            "commitment_count": len(self.commitments),
            "plan_count": len(self.plans),
        }


# ============================================================
# Factory
# ============================================================

def create_intention(content: str, intention_type: str = "desire",
                    strength: float = 0.5) -> Intention:
    """Create intention"""
    return Intention(
        id=str(uuid.uuid4()),
        content=content,
        intention_type=intention_type,
        strength=strength,
    )


def create_commitment(intention_id: str, level: str = "serious") -> Commitment:
    """Create commitment"""
    return Commitment(
        id=str(uuid.uuid4()),
        intention_id=intention_id,
        level=level,
    )


__all__ = [
    'IntentionType', 'IntentionSource', 'IntentionStatus',
    'Intention', 'Volition', 'CommitmentLevel', 'Commitment',
    'ActionStep', 'Plan',
    'IntentionState',
    'IntentionFormation', 'IntentionConflict', 'IntentionExecution',
    'IntentionProfile',
    'create_intention', 'create_commitment'
]