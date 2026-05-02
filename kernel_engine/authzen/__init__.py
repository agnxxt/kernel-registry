"""Authzen - Authorization Framework"""
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

class AuthzDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ABSTAIN = "abstain"

class AuthzEffect(Enum):
    PERMIT = "permit"
    FORBID = "forbid"

@dataclass
class AuthzRequest:
    subject: str
    action: str
    resource: str
    context: Dict = field(default_factory=dict)
    
    def to_key(self) -> str:
        return f"{self.subject}:{self.action}:{self.resource}"

@dataclass
class AuthzResponse:
    decision: AuthzDecision
    effect: AuthzEffect
    policy_ids: List[str] = field(default_factory=list)
    
    def is_allowed(self) -> bool:
        return self.decision == AuthzDecision.ALLOW and self.effect == AuthzEffect.PERMIT

class AuthzPolicy:
    """Authorization policy"""
    def __init__(self, policy_id: str):
        self.policy_id = policy_id
        self.rules: List[Dict] = []
        
    def add_rule(self, subject: str = "*", action: str = "*", 
              resource: str = "*", effect: str = "permit"):
        self.rules.append({'subject': subject, 'action': action,
                       'resource': resource, 'effect': effect})
        
    def evaluate(self, request: AuthzRequest) -> AuthzResponse:
        for rule in self.rules:
            if rule['subject'] != "*" and rule['subject'] != request.subject:
                continue
            if rule['action'] != "*" and rule['action'] != request.action:
                continue
            if rule['resource'] != "*" and not request.resource.startswith(rule['resource']):
                continue
            effect = AuthzEffect.PERMIT if rule['effect'] == 'permit' else AuthzEffect.FORBID
            decision = AuthzDecision.ALLOW if effect == AuthzEffect.PERMIT else AuthzDecision.DENY
            return AuthzResponse(decision, effect, [self.policy_id])
        return AuthzResponse(AuthzDecision.ALLOW, AuthzEffect.PERMIT)

class AuthzenEngine:
    """Authorization engine"""
    def __init__(self):
        self.policies: Dict[str, AuthzPolicy] = {}
        self.identity_cache: Dict[str, Dict] = {}
        self.decision_cache: Dict[str, Tuple[AuthzResponse, datetime]] = {}
        
    def add_policy(self, policy: AuthzPolicy):
        self.policies[policy.policy_id] = policy
        
    def authorize(self, request: AuthzRequest) -> AuthzResponse:
        cache_key = request.to_key()
        if cache_key in self.decision_cache:
            resp, expiry = self.decision_cache[cache_key]
            if datetime.now() < expiry:
                return resp
        for policy in self.policies.values():
            resp = policy.evaluate(request)
            if resp.decision != AuthzDecision.ABSTAIN:
                self.decision_cache[cache_key] = (resp, datetime.now() + timedelta(minutes=5))
                return resp
        return AuthzResponse(AuthzDecision.ALLOW, AuthzEffect.PERMIT)

class RBACBackend:
    """Role-Based Access Control"""
    def __init__(self):
        self.roles: Dict[str, Set[str]] = {}
        self.permissions: Dict[str, Set[tuple]] = {}
        
    def create_role(self, role_id: str):
        self.roles[role_id] = set()
        self.permissions[role_id] = set()
        
    def grant_permission(self, role_id: str, action: str, resource: str):
        if role_id not in self.roles:
            self.create_role(role_id)
        self.permissions[role_id].add((action, resource))
        
    def assign_role(self, role_id: str, agent_id: str):
        if role_id not in self.roles:
            self.create_role(role_id)
        self.roles[role_id].add(agent_id)
        
    def has_permission(self, agent_id: str, action: str, resource: str) -> bool:
        for role_id, members in self.roles.items():
            if agent_id not in members:
                continue
            perms = self.permissions.get(role_id, set())
            for p in perms:
                if p == (action, resource) or p == (action, '*') or p == ('*', resource) or p == ('*', '*'):
                    return True
        return False

__all__ = ['AuthzenEngine', 'AuthzPolicy', 'AuthzRequest', 'AuthzResponse', 'RBACBackend']