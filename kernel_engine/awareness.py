"""
Awareness - First-Class Entity (Python)

Awareness is the agent's knowledge of:
- Self (capabilities, limits, state)
- Environment (context, resources)
- Others (agents, users, tools)
- Task (goals, progress, history)
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import time


# ============================================================
# Self-Awareness
# ============================================================

@dataclass
class SelfAwareness:
    """Self-awareness - knowledge of self"""
    agent_id: str
    agent_name: str = ""
    agent_type: str = "general"
    
    # Capabilities
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    
    # State
    status: str = "idle"  # idle, busy, waiting, error
    load: int = 0  # 0-100
    available_memory: int = 100
    available_compute: int = 100
    
    # Preferences
    preferences: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "limitations": self.limitations,
            "tools": self.tools,
            "skills": self.skills,
            "status": self.status,
            "load": self.load,
            "available_resources": {
                "memory": self.available_memory,
                "compute": self.available_compute,
            },
            "preferences": self.preferences,
        }


# ============================================================
# EnvironmentAwareness
# ============================================================

@dataclass
class EnvironmentAwareness:
    """Environment awareness - knowledge of context"""
    session_id: str = ""
    tenant_id: str = ""
    user_id: str = ""
    
    # Time
    current_time: str = ""
    timezone: str = "UTC"
    
    # Location
    location_type: str = "cloud"
    region: str = ""
    
    # Resources
    api_calls_remaining: int = 1000
    tokens_remaining: int = 100000
    memory_available: int = 1000
    
    # Security
    auth_level: str = "standard"
    restrictions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "current_time": self.current_time,
            "timezone": self.timezone,
            "location": {
                "type": self.location_type,
                "region": self.region,
            },
            "resources": {
                "api_calls_remaining": self.api_calls_remaining,
                "tokens_remaining": self.tokens_remaining,
                "memory_available": self.memory_available,
            },
            "security": {
                "auth_level": self.auth_level,
                "restrictions": self.restrictions,
            },
        }


# ============================================================
# SocialAwareness
# ============================================================

@dataclass
class SocialAwareness:
    """Social awareness - knowledge of others"""
    user_id: str = ""
    user_name: str = ""
    user_role: str = ""
    
    # Team members
    team_members: List[Dict] = field(default_factory=list)
    
    # Other agents
    other_agents: List[Dict] = field(default_factory=list)
    
    # Tools
    tools: List[Dict] = field(default_factory=list)
    
    def set_user(self, user_id: str, name: str = "", role: str = ""):
        """Set current user"""
        self.user_id = user_id
        self.user_name = name
        self.user_role = role
    
    def add_team_member(self, member_id: str, name: str, role: str):
        """Add team member"""
        self.team_members.append({
            "id": member_id,
            "name": name,
            "role": role,
            "online": False,
        })
    
    def add_agent(self, agent_id: str, agent_type: str, capabilities: List[str]):
        """Add other agent"""
        self.other_agents.append({
            "id": agent_id,
            "type": agent_type,
            "status": "idle",
            "capabilities": capabilities,
        })
    
    def add_tool(self, name: str, description: str = ""):
        """Add tool"""
        self.tools.append({
            "name": name,
            "description": description,
            "available": True,
        })
    
    def to_dict(self) -> Dict:
        return {
            "user": {
                "id": self.user_id,
                "name": self.user_name,
                "role": self.user_role,
            } if self.user_id else None,
            "team_members": self.team_members,
            "other_agents": self.other_agents,
            "tools": self.tools,
        }


# ============================================================
# TaskAwareness
# ============================================================

@dataclass
class TaskAwareness:
    """Task awareness - knowledge of current work"""
    task_id: str = ""
    task_name: str = ""
    task_description: str = ""
    task_priority: str = "medium"
    task_progress: int = 0
    
    # Goal
    goal: str = ""
    goal_progress: int = 0
    
    # History
    recent_actions: List[Dict] = field(default_factory=list)
    
    # Pending decisions
    pending_decisions: List[Dict] = field(default_factory=list)
    
    # Blockers
    blockers: List[str] = field(default_factory=list)
    
    def set_task(self, task_id: str, name: str, description: str = "",
              priority: str = "medium"):
        """Set current task"""
        self.task_id = task_id
        self.task_name = name
        self.task_description = description
        self.task_priority = priority
    
    def add_action(self, action: str, result: str):
        """Add recent action"""
        self.recent_actions.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self.recent_actions) > 20:
            self.recent_actions.pop(0)
    
    def add_decision(self, decision_id: str, description: str,
                   options: List[str]):
        """Add pending decision"""
        self.pending_decisions.append({
            "id": decision_id,
            "description": description,
            "options": options,
        })
    
    def add_blocker(self, blocker: str):
        """Add blocker"""
        if blocker not in self.blockers:
            self.blockers.append(blocker)
    
    def remove_blocker(self, blocker: str):
        """Remove blocker"""
        if blocker in self.blockers:
            self.blockers.remove(blocker)
    
    def to_dict(self) -> Dict:
        return {
            "current_task": {
                "id": self.task_id,
                "name": self.task_name,
                "description": self.task_description,
                "priority": self.task_priority,
                "progress": self.task_progress,
            } if self.task_id else None,
            "goal": self.goal,
            "goal_progress": self.goal_progress,
            "recent_actions": self.recent_actions,
            "pending_decisions": self.pending_decisions,
            "blockers": self.blockers,
        }


# ============================================================
# Full Awareness
# ============================================================

@dataclass
class Awareness:
    """Full awareness - all four pillars combined"""
    id: str
    agent_id: str
    
    # Four pillars
    self_awareness: SelfAwareness
    environment_awareness: EnvironmentAwareness
    social_awareness: SocialAwareness
    task_awareness: TaskAwareness
    
    # Meta
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update_self(self):
        """Mark updated"""
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "self": self.self_awareness.to_dict(),
            "environment": self.environment_awareness.to_dict(),
            "social": self.social_awareness.to_dict(),
            "task": self.task_awareness.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ============================================================
# Awareness Update
# ============================================================

@dataclass
class AwarenessUpdate:
    """Awareness update event"""
    awareness_id: str
    update_type: str  # self, environment, social, task
    field: str
    old_value: Any = None
    new_value: Any = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "awareness_id": self.awareness_id,
            "type": self.update_type,
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp,
        }


# ============================================================
# Factory
# ============================================================

def create_awareness(agent_id: str) -> Awareness:
    """Create awareness for agent"""
    now = datetime.now().isoformat()
    
    return Awareness(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        self_awareness=SelfAwareness(agent_id=agent_id),
        environment_awareness=EnvironmentAwareness(current_time=now),
        social_awareness=SocialAwareness(),
        task_awareness=TaskAwareness(),
        created_at=now,
        updated_at=now,
    )


__all__ = [
    'SelfAwareness', 'EnvironmentAwareness', 
    'SocialAwareness', 'TaskAwareness',
    'Awareness', 'AwarenessUpdate',
    'create_awareness'
]