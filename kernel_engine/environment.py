"""
Environment - First-Class Entity

Environment as a core entity for agent context:
- Physical Environment
- Digital Environment
- Social Environment
- Task Environment
- Resources
- Constraints
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Environment Core
# ============================================================

class EnvironmentType:
    PHYSICAL = "physical"
    DIGITAL = "digital"
    SOCIAL = "social"
    TASK = "task"
    HYBRID = "hybrid"


@dataclass
class Environment:
    """Environment (First-Class Entity)"""
    id: str
    name: str
    description: str = ""
    
    environment_type: str = "digital"
    
    properties: Dict = field(default_factory=dict)
    
    status: str = "active"
    
    is_accessible: bool = True
    
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "environment_type": self.environment_type,
            "status": self.status,
            "is_accessible": self.is_accessible,
        }


# ============================================================
# Physical Environment
# ============================================================

@dataclass
class PhysicalLocation:
    """Physical location"""
    id: str
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    
    address: str = ""
    building: str = ""
    room: str = ""
    
    location_type: str = "indoor"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "location_type": self.location_type,
        }


# ============================================================
# Digital Environment
# ============================================================

class NetworkType:
    LOCAL = "local"
    CLOUD = "cloud"
    EDGE = "edge"
    HYBRID = "hybrid"


@dataclass
class DigitalEnvironment:
    """Digital environment"""
    id: str
    
    network_type: str = "cloud"
    ip_address: str = ""
    hostname: str = ""
    
    compute: Dict = field(default_factory=dict)
    
    services: List[str] = field(default_factory=list)
    
    security_level: str = "internal"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "network_type": self.network_type,
            "hostname": self.hostname,
            "security_level": self.security_level,
        }


# ============================================================
# Social Environment
# ============================================================

@dataclass
class SocialContext:
    """Social context"""
    id: str
    
    people: List[str] = field(default_factory=list)
    roles: Dict[str, str] = field(default_factory=dict)
    relationships: Dict[str, float] = field(default_factory=dict)
    
    group_id: str = ""
    group_type: str = "team"
    
    culture: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "people": self.people,
            "group_type": self.group_type,
            "culture": self.culture,
        }


# ============================================================
# Task Environment
# ============================================================

class TaskStatus:
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class TaskEnvironment:
    """Task environment"""
    id: str
    
    task_id: str = ""
    task_name: str = ""
    
    goals: List[str] = field(default_factory=list)
    
    progress: float = 0
    
    status: str = "idle"
    
    constraints: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "task_name": self.task_name,
            "progress": self.progress,
            "status": self.status,
        }


# ============================================================
# Resources
# ============================================================

class ResourceType:
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    HUMAN = "human"
    FINANCIAL = "financial"
    TIME = "time"
    INFORMATION = "information"


@dataclass
class Resource:
    """Resource"""
    id: str
    name: str
    
    resource_type: str = "compute"
    
    capacity: float = 0
    available: float = 0
    
    cost_per_unit: Optional[float] = None
    
    status: str = "available"
    
    def allocate(self, amount: float) -> bool:
        """Allocate resource"""
        if amount <= self.available:
            self.available -= amount
            if self.available <= 0:
                self.status = "exhausted"
            return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "resource_type": self.resource_type,
            "capacity": self.capacity,
            "available": self.available,
            "status": self.status,
        }


# ============================================================
# Constraints
# ============================================================

class ConstraintType:
    TIME = "time"
    BUDGET = "budget"
    RESOURCE = "resource"
    POLICY = "policy"
    LEGAL = "legal"
    ETHICAL = "ethical"
    PHYSICAL = "physical"


@dataclass
class Constraint:
    """Constraint"""
    id: str
    
    constraint_type: str = "resource"
    
    description: str = ""
    
    limit: float = 0
    unit: str = ""
    
    is_hard: bool = True
    
    context: str = ""
    
    def is_violated(self, value: float) -> bool:
        """Check if violated"""
        return value > self.limit
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "constraint_type": self.constraint_type,
            "description": self.description,
            "limit": self.limit,
            "is_hard": self.is_hard,
        }


# ============================================================
# Environment State
# ============================================================

@dataclass
class EnvironmentState:
    """Environment state"""
    environment: Environment
    
    location: Optional[PhysicalLocation] = None
    digital: Optional[DigitalEnvironment] = None
    social: Optional[SocialContext] = None
    task: Optional[TaskEnvironment] = None
    
    resources: List[Resource] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_resource(self, resource: Resource):
        """Add resource"""
        self.resources.append(resource)
    
    def add_constraint(self, constraint: Constraint):
        """Add constraint"""
        self.constraints.append(constraint)
    
    def check_constraints(self) -> List[str]:
        """Check all constraints"""
        violations = []
        for c in self.constraints:
            # Simplified check
            violations.append(c.description)
        return violations
    
    def to_dict(self) -> Dict:
        return {
            "environment": self.environment.to_dict(),
            "resource_count": len(self.resources),
            "constraint_count": len(self.constraints),
            "timestamp": self.timestamp,
        }


# ============================================================
# Factory
# ============================================================

def create_environment(name: str, env_type: str = "digital") -> Environment:
    """Create environment"""
    return Environment(
        id=str(uuid.uuid4()),
        name=name,
        environment_type=env_type,
    )


def create_resource(name: str, resource_type: str, 
                  capacity: float) -> Resource:
    """Create resource"""
    return Resource(
        id=str(uuid.uuid4()),
        name=name,
        resource_type=resource_type,
        capacity=capacity,
        available=capacity,
    )


def create_constraint(description: str, constraint_type: str,
                   limit: float) -> Constraint:
    """Create constraint"""
    return Constraint(
        id=str(uuid.uuid4()),
        description=description,
        constraint_type=constraint_type,
        limit=limit,
    )


__all__ = [
    'EnvironmentType', 'Environment',
    'PhysicalLocation',
    'NetworkType', 'DigitalEnvironment',
    'SocialContext',
    'TaskStatus', 'TaskEnvironment',
    'ResourceType', 'Resource',
    'ConstraintType', 'Constraint',
    'EnvironmentState',
    'create_environment', 'create_resource', 'create_constraint'
]