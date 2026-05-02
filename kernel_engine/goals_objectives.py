"""
Goals and Objectives - Goal-Oriented Behavior

Goal hierarchy, objectives, timelines, and motivation:
- Goals
- Objectives
- Key Results (OKR)
- Timeline
- Milestones
- Motivation
- Rewards
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Goals
# ============================================================

class GoalType:
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    TEAM = "team"
    ORGANIZATIONAL = "organizational"
    SOCIAL = "social"


class GoalScope:
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    LIFETIME = "lifetime"


@dataclass
class Goal:
    """Goal"""
    id: str
    title: str
    description: str = ""
    
    goal_type: str = "personal"
    
    parent_goal_id: str = ""
    child_goal_ids: List[str] = field(default_factory=list)
    
    scope: str = "short_term"
    
    priority: int = 5  # 1-10
    is_stretch: bool = False
    
    status: str = "draft"  # draft, active, completed, abandoned, on_hold
    
    start_date: str = ""
    target_date: str = ""
    completed_date: str = ""
    
    progress: float = 0  # 0-100
    
    motivation_ids: List[str] = field(default_factory=list)
    
    def complete(self):
        """Mark as completed"""
        self.status = "completed"
        self.completed_date = datetime.now().isoformat()
        self.progress = 100
    
    def update_progress(self, progress: float):
        """Update progress"""
        self.progress = min(100, max(0, progress))
        if self.progress >= 100:
            self.complete()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "goal_type": self.goal_type,
            "scope": self.scope,
            "priority": self.priority,
            "status": self.status,
            "progress": self.progress,
        }


# ============================================================
# Objectives
# ============================================================

@dataclass
class Objective:
    """Objective"""
    id: str
    title: str
    description: str = ""
    
    goal_id: str = ""
    
    key_results: List[str] = field(default_factory=list)
    
    weight: float = 1.0
    
    status: str = "draft"
    
    start_date: str = ""
    target_date: str = ""
    
    progress: float = 0
    
    def complete(self):
        """Mark as completed"""
        self.status = "completed"
        self.progress = 100
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "goal_id": self.goal_id,
            "weight": self.weight,
            "status": self.status,
            "progress": self.progress,
        }


@dataclass
class KeyResult:
    """Key Result (OKR)"""
    id: str
    title: str
    
    objective_id: str = ""
    
    target_value: float = 0
    current_value: float = 0
    
    unit: str = "count"
    
    status: str = "on_track"  # on_track, at_risk, behind, completed
    
    start_date: str = ""
    target_date: str = ""
    
    def progress(self) -> float:
        """Calculate progress"""
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "progress": self.progress(),
            "status": self.status,
        }


# ============================================================
# Timeline
# ============================================================

class EventType:
    MILESTONE = "milestone"
    DEADLINE = "deadline"
    REVIEW = "review"
    CHECKPOINT = "checkpoint"


@dataclass
class Timeline:
    """Timeline"""
    id: str
    name: str = ""
    
    events: List[Dict] = field(default_factory=list)
    
    start_date: str = ""
    end_date: str = ""
    
    progress: float = 0
    
    def add_event(self, name: str, date: str, event_type: str = "milestone"):
        """Add event"""
        self.events.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "date": date,
            "type": event_type,
            "status": "upcoming",
        })
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "event_count": len(self.events),
            "progress": self.progress,
        }


@dataclass
class Milestone:
    """Milestone"""
    id: str
    title: str
    description: str = ""
    
    target_date: str = ""
    
    status: str = "pending"  # pending, achieved, missed, rescheduled
    
    criteria: List[str] = field(default_factory=list)
    
    linked_goal_ids: List[str] = field(default_factory=list)
    linked_objective_ids: List[str] = field(default_factory=list)
    
    def achieve(self):
        """Mark as achieved"""
        self.status = "achieved"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "target_date": self.target_date,
            "status": self.status,
        }


# ============================================================
# Motivation
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


@dataclass
class Motivation:
    """Motivation"""
    id: str
    
    motivation_type: str = "intrinsic"
    
    description: str = ""
    
    strength: float = 0.5  # 0-1
    
    source: str = "self"  # self, peer, leader, organization, society
    
    goal_ids: List[str] = field(default_factory=list)
    
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "motivation_type": self.motivation_type,
            "description": self.description,
            "strength": self.strength,
            "source": self.source,
            "is_active": self.is_active,
        }


class RewardType:
    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    SOCIAL = "social"
    FINANCIAL = "financial"
    RECOGNITION = "recognition"
    GROWTH = "growth"


@dataclass
class Reward:
    """Reward"""
    id: str
    name: str
    
    reward_type: str = "extrinsic"
    
    value: float = 0
    
    criteria: str = ""
    goal_id: str = ""
    
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
# Cost
# ============================================================

class CostType:
    TIME = "time"
    MONEY = "money"
    EFFORT = "effort"
    OPPORTUNITY = "opportunity"
    RESOURCE = "resource"
    EMOTIONAL = "emotional"


@dataclass
class Cost:
    """Cost"""
    id: str
    name: str
    
    cost_type: str = "effort"
    
    amount: float = 0
    currency: str = "USD"
    
    goal_id: str = ""
    objective_id: str = ""
    
    status: str = "estimated"  # estimated, actual, budgeted
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "cost_type": self.cost_type,
            "amount": self.amount,
            "currency": self.currency,
        }


@dataclass
class Budget:
    """Budget"""
    id: str
    name: str = ""
    
    total: float = 0
    currency: str = "USD"
    
    allocated: float = 0
    spent: float = 0
    
    items: List[Cost] = field(default_factory=list)
    
    period: str = ""
    
    def remaining(self) -> float:
        """Get remaining"""
        return self.total - self.spent
    
    def add_cost(self, cost: Cost):
        """Add cost"""
        self.items.append(cost)
        self.spent += cost.amount
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "total": self.total,
            "spent": self.spent,
            "remaining": self.remaining(),
            "period": self.period,
        }


@dataclass
class ROI:
    """Return on Investment"""
    investment: float = 0
    return_value: float = 0
    
    roi: Optional[float] = None
    
    period: str = ""
    goal_id: str = ""
    
    def calculate(self):
        """Calculate ROI"""
        if self.investment > 0:
            self.roi = ((self.return_value - self.investment) / self.investment) * 100
    
    def to_dict(self) -> Dict:
        return {
            "investment": self.investment,
            "return": self.return_value,
            "roi": self.roi,
        }


# ============================================================
# Progress
# ============================================================

@dataclass
class Progress:
    """Progress tracking"""
    entity_type: str  # goal, objective, milestone, project
    entity_id: str
    
    progress: float = 0
    
    metrics: Dict[str, float] = field(default_factory=dict)
    
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_by: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "progress": self.progress,
            "metrics": self.metrics,
            "updated_at": self.updated_at,
        }


# ============================================================
# Factory
# ============================================================

def create_goal(title: str, goal_type: str = "personal", 
               scope: str = "short_term") -> Goal:
    """Create goal"""
    return Goal(
        id=str(uuid.uuid4()),
        title=title,
        goal_type=goal_type,
        scope=scope,
    )


def create_okr(objective_title: str, key_results: List[tuple]) -> tuple:
    """Create OKR (Objective + Key Results)"""
    objective = Objective(
        id=str(uuid.uuid4()),
        title=objective_title,
    )
    
    results = []
    for title, target in key_results:
        kr = KeyResult(
            id=str(uuid.uuid4()),
            title=title,
            objective_id=objective.id,
            target_value=target,
        )
        results.append(kr)
    
    return objective, results


__all__ = [
    'GoalType', 'GoalScope', 'Goal',
    'Objective', 'KeyResult',
    'EventType', 'Timeline', 'Milestone',
    'MotivationType', 'Motivation',
    'RewardType', 'Reward',
    'CostType', 'Cost', 'Budget', 'ROI',
    'Progress',
    'create_goal', 'create_okr'
]