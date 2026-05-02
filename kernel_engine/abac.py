"""
ABAC - Attribute-Based Access Control
Dynamic authorization based on subject, resource, and environment attributes.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class AttributeOperator(Enum):
    EQ = "eq"           # Equal
    NE = "ne"           # Not Equal
    GT = "gt"           # Greater Than
    GTE = "gte"         # Greater Than or Equal
    LT = "lt"           # Less Than
    LTE = "lte"         # Less Than or Equal
    IN = "in"           # In list
    NOT_IN = "not_in"   # Not in list
    CONTAINS = "contains"  # Contains
    STARTS_WITH = "startsWith"
    ENDS_WITH = "endsWith"
    MATCHES = "matches"  # Regex match


class AttributeType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DATETIME = "datetime"


@dataclass
class Attribute:
    """Attribute definition"""
    name: str
    attr_type: AttributeType
    value: Any
    operator: AttributeOperator = AttributeOperator.EQ
    
    def evaluate(self, actual_value: Any) -> bool:
        """Evaluate attribute against actual value"""
        try:
            if self.operator == AttributeOperator.EQ:
                return self.value == actual_value
            elif self.operator == AttributeOperator.NE:
                return self.value != actual_value
            elif self.operator == AttributeOperator.GT:
                return actual_value > self.value
            elif self.operator == AttributeOperator.GTE:
                return actual_value >= self.value
            elif self.operator == AttributeOperator.LT:
                return actual_value < self.value
            elif self.operator == AttributeOperator.LTE:
                return actual_value <= self.value
            elif self.operator == AttributeOperator.IN:
                return actual_value in self.value
            elif self.operator == AttributeOperator.NOT_IN:
                return actual_value not in self.value
            elif self.operator == AttributeOperator.CONTAINS:
                return self.value in actual_value
            elif self.operator == AttributeOperator.STARTS_WITH:
                return str(actual_value).startswith(str(self.value))
            elif self.operator == AttributeOperator.ENDS_WITH:
                return str(actual_value).endswith(str(self.value))
            elif self.operator == AttributeOperator.MATCHES:
                import re
                return bool(re.match(self.value, str(actual_value)))
            return False
        except Exception:
            return False


class ConditionType(Enum):
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class Condition:
    """Boolean condition"""
    condition_type: ConditionType
    conditions: List["Condition"] = field(default_factory=list)
    attribute: Optional[Attribute] = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context"""
        if self.attribute:
            # Get value from context
            path = self.attribute.name.split(".")
            value = context
            for p in path:
                if isinstance(value, dict):
                    value = value.get(p)
                else:
                    break
            return self.attribute.evaluate(value)
        
        if self.condition_type == ConditionType.AND:
            return all(c.evaluate(context) for c in self.conditions)
        elif self.condition_type == ConditionType.OR:
            return any(c.evaluate(context) for c in self.conditions)
        elif self.condition_type == ConditionType.NOT:
            return not self.conditions[0].evaluate(context)
        return False


@dataclass
class ABACPolicy:
    """ABAC Policy"""
    policy_id: str = field(default_factory=lambda: f"abac_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    subjects: List[Dict[str, Any]] = field(default_factory=list)  # Subject filters
    resources: List[Dict[str, Any]] = field(default_factory=list)  # Resource filters
    environments: List[Dict[str, Any]] = field(default_factory=list)  # Env filters
    actions: List[str] = field(default_factory=list)  # Allowed actions
    conditions: List[Condition] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True
    
    def evaluate(self, subject: Dict[str, Any], resource: Dict[str, Any],
                  action: str, environment: Dict[str, Any]) -> bool:
        """Evaluate policy"""
        if not self.enabled:
            return False
        
        # Check action
        if self.actions and action not in self.actions:
            return False
        
        # Check subject attributes
        for subj_filter in self.subjects:
            match = True
            for k, v in subj_filter.items():
                if subject.get(k) != v:
                    match = False
                    break
            if not match and self.subjects:
                continue
        
        # Check resource attributes
        for res_filter in self.resources:
            match = True
            for k, v in res_filter.items():
                if resource.get(k) != v:
                    match = False
                    break
            if not match and self.resources:
                continue
        
        # Check conditions
        context = {**subject, **resource, **environment, "action": action}
        if self.conditions:
            return all(c.evaluate(context) for c in self.conditions)
        
        return True


class ABACEngine:
    """ABAC Authorization Engine"""
    
    def __init__(self):
        self.policies: Dict[str, ABACPolicy] = {}
        self.cache: Dict[str, bool] = {}
    
    def add_policy(self, policy: ABACPolicy):
        """Add policy"""
        self.policies[policy.policy_id] = policy
        self.cache.clear()
    
    def remove_policy(self, policy_id: str):
        """Remove policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
        self.cache.clear()
    
    def get_policy(self, policy_id: str) -> Optional[ABACPolicy]:
        """Get policy"""
        return self.policies.get(policy_id)
    
    def list_policies(self) -> List[ABACPolicy]:
        """List all policies"""
        return sorted(self.policies.values(), key=lambda p: p.priority)
    
    def authorize(self, subject: Dict[str, Any], resource: Dict[str, Any],
                 action: str, environment: Dict[str, Any] = None) -> bool:
        """Authorize action"""
        env = environment or {}
        
        # Build cache key
        cache_key = f"{subject.get('id', 'anon')}:{resource.get('id', 'anon')}:{action}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Evaluate policies by priority
        for policy in self.policies.values():
            if policy.evaluate(subject, resource, action, env):
                self.cache[cache_key] = True
                return True
        
        self.cache[cache_key] = False
        return False
    
    def evaluate_all(self, subject: Dict[str, Any], resource: Dict[str, Any],
                   action: str, environment: Dict[str, Any] = None) -> Dict[str, bool]:
        """Evaluate all policies, return results"""
        env = environment or {}
        results = {}
        
        for policy_id, policy in self.policies.items():
            results[policy_id] = policy.evaluate(subject, resource, action, env)
        
        return results
    
    def clear_cache(self):
        """Clear cache"""
        self.cache.clear()


# ============================================================
# Subject/Resource Attribute Extractors
# ============================================================

class AttributeExtractor:
    """Extract attributes from various sources"""
    
    @staticmethod
    def from_user(user: Dict[str, Any]) -> Dict[str, Any]:
        """Extract subject attributes from user"""
        return {
            "id": user.get("id"),
            "type": user.get("type", "user"),
            "role": user.get("role"),
            "department": user.get("department"),
            "location": user.get("location"),
            "clearance_level": user.get("clearance_level", 0),
            "tenant_id": user.get("tenant_id"),
            "auth_time": user.get("auth_time"),
        }
    
    @staticmethod
    def from_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource attributes"""
        return {
            "id": resource.get("id"),
            "type": resource.get("type"),
            "owner": resource.get("owner"),
            "owner_id": resource.get("owner_id"),
            "tenant_id": resource.get("tenant_id"),
            "sensitivity": resource.get("sensitivity", "public"),
            "classification": resource.get("classification", "internal"),
            "created_at": resource.get("created_at"),
            "cost_center": resource.get("cost_center"),
        }
    
    @staticmethod
    def from_environment(env: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract environment attributes"""
        return {
            "time": datetime.now().isoformat(),
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "ip_address": env.get("ip_address") if env else None,
            "user_agent": env.get("user_agent") if env else None,
            "geo_location": env.get("geo_location") if env else None,
            "risk_level": env.get("risk_level", "low"),
        }


__all__ = [
    'ABACEngine', 'ABACPolicy', 'Attribute', 'AttributeType', 
    'AttributeOperator', 'Condition', 'ConditionType', 'AttributeExtractor'
]