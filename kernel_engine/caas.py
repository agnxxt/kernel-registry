"""
OpenAGX / CAAS - Agent Authorization Service

OAuth2-based protocol for agent-to-agent and agent-to-resource authorization.
Extends OAuth2 with agent-specific grants and scopes.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import hashlib
from datetime import datetime, timedelta


class GrantType(Enum):
    AGENT_CREDENTIAL = "urn:openagx:grant:agent_credential"
    DELEGATED_AGENT = "urn:openagx:grant:delegated_agent"
    AGENT_IMPERSONATION = "urn:openagx:grant:agent_impersonation"
    DEVICE_FLOW = "urn:openagx:grant:device_flow"


class Scope(Enum):
    AGENT_READ = "agent:read"
    AGENT_EXECUTE = "agent:execute"
    AGENT_ADMIN = "agent:admin"
    AGENT_DELEGATE = "agent:delegate"
    AGENT_IMPERSONATE = "agent:impersonate"
    RESOURCE_READ = "resource:read"
    RESOURCE_WRITE = "resource:write"
    RESOURCE_ADMIN = "resource:admin"


class AgentGrant:
    """Agent authorization grant"""
    grant_id: str = ""
    agent_id: str = ""
    resource_owner: str = ""
    scope: List[str] = field(default_factory=list)
    expires_at: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CAASClient:
    """CAAS - Cloud Agent Authorization Service"""
    
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Authorization grants
        self.grants: Dict[str, AgentGrant] = {}
        self.tokens: Dict[str, Dict] = {}
        
        # Policy engine
        self.policies: Dict[str, Dict] = {}
        
        # Delegation chain
        self.delegations: Dict[str, List[str]] = {}
    
    # ============ Authorization ============
    
    def authorize(self, agent_id: str, resource_owner: str,
               scope: List[str], max_age: int = 3600) -> AgentGrant:
        """Issue authorization grant"""
        grant_id = f"grant_{uuid.uuid4().hex[:16]}"
        
        grant = AgentGrant(
            grant_id=grant_id,
            agent_id=agent_id,
            resource_owner=resource_owner,
            scope=scope,
            expires_at=int(time.time()) + max_age,
        )
        
        self.grants[grant_id] = grant
        return grant
    
    def exchange(self, grant_id: str, client_secret: str = None) -> Dict:
        """Exchange grant for token"""
        grant = self.grants.get(grant_id)
        if not grant:
            raise ValueError("Invalid grant")
        
        if grant.expires_at < time.time():
            raise ValueError("Grant expired")
        
        # Issue token
        access_token = f"caas_at_{uuid.uuid4().hex}"
        
        token = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": grant.expires_at - int(time.time()),
            "scope": " ".join(grant.scope),
            "agent_id": grant.agent_id,
            "resource_owner": grant.resource_owner,
            "grant_id": grant_id,
        }
        
        self.tokens[access_token] = token
        return token
    
    def validate(self, access_token: str) -> Dict:
        """Validate token"""
        token = self.tokens.get(access_token)
        if not token:
            return {"valid": False}
        
        # Check expiry (simplified - in real impl, check exp claim)
        if access_token not in self.tokens:
            return {"valid": False}
        
        return {"valid": True, "token": token}
    
    def revoke(self, access_token: str) -> bool:
        """Revoke token"""
        if access_token in self.tokens:
            del self.tokens[access_token]
            return True
        return False
    
    # ============ Scope Enforcement ============
    
    def require_scope(self, access_token: str, required_scope: str) -> bool:
        """Check if token has required scope"""
        token_info = self.validate(access_token)
        if not token_info.get("valid"):
            return False
        
        token = token_info.get("token", {})
        scopes = token.get("scope", "").split()
        
        return required_scope in scopes
    
    # ============ Delegation ============
    
    def delegate(self, from_agent: str, to_agent: str,
             scope: List[str], max_age: int = 3600) -> AgentGrant:
        """Create delegation"""
        if from_agent not in self.delegations:
            self.delegations[from_agent] = []
        
        delegation_id = f"del_{uuid.uuid4().hex[:12]}"
        self.delegations[from_agent].append(delegation_id)
        
        # Grant to delegated agent
        grant = self.authorize(to_agent, from_agent, scope, max_age)
        
        return grant
    
    def get_delegation_chain(self, agent_id: str) -> List[Dict]:
        """Get delegated access chain"""
        chain = []
        
        # Find delegations where agent is delegated to
        for from_a, chain_ids in self.delegations.items():
            for chain_id in chain_ids:
                # Find grants
                for grant in self.grants.values():
                    if grant.agent_id == agent_id:
                        chain.append({
                            "from": from_a,
                            "to": agent_id,
                            "scope": grant.scope,
                        })
        
        return chain
    
    # ============ Policy ============
    
    def set_policy(self, name: str, policy: Dict):
        """Set authorization policy"""
        self.policies[name] = policy
    
    def evaluate_policy(self, agent_id: str, action: str,
                    resource: str) -> Dict:
        """Evaluate policy"""
        # Check all policies
        for name, policy in self.policies.items():
            if "agent_id" in policy and policy["agent_id"] != agent_id:
                continue
            if "deny" in policy and action in policy["deny"]:
                return {"allowed": False, "policy": name}
        
        return {"allowed": True}
    
    # ============ Impersonation ============
    
    def impersonate(self, agent_id: str, target_agent: str,
                scope: List[str]) -> AgentGrant:
        """Impersonate another agent"""
        # Check if agent has impersonate scope
        # For now, allow
        
        return self.authorize(target_agent, agent_id, scope)
    
    # ============ Token Introspection ============
    
    def introspect(self, access_token: str) -> Dict:
        """Token introspection"""
        token_info = self.validate(access_token)
        if not token_info.get("valid"):
            return {"active": False}
        
        token = token_info.get("token", {})
        
        return {
            "active": True,
            "scope": token.get("scope"),
            "agent_id": token.get("agent_id"),
            "resource_owner": token.get("resource_owner"),
            "exp": token.get("expires_in", 0) + time.time(),
        }


# ============================================================
# OpenAGX Protocol
# ============================================================

class OpenAGXProvider:
    """OpenAGX Protocol Provider"""
    
    def __init__(self):
        self.caas = CAASClient()
        self.agents: Dict[str, Dict] = {}
    
    # ============ Agent Registration ============
    
    def register_agent(self, agent_id: str, metadata: Dict = None) -> Dict:
        """Register agent"""
        self.agents[agent_id] = {
            "agent_id": agent_id,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        return self.agents[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent"""
        return self.agents.get(agent_id)
    
    # ============ Agent Credentials ============
    
    def issue_credentials(self, agent_id: str, scopes: List[str]) -> Dict:
        """Issue agent credentials"""
        grant = self.caas.authorize(
            agent_id=agent_id,
            resource_owner=agent_id,  # Self-owned
            scope=scopes,
        )
        
        token = self.caas.exchange(grant.grant_id)
        
        return {
            "client_id": agent_id,
            "client_secret": token["access_token"],
            "scope": " ".join(scopes),
        }
    
    # ============ Service Discovery ============
    
    def discover(self) -> Dict:
        """Service discovery"""
        return {
            "issuer": "https://agent.example.com",
            "authorization_endpoint": "/caas/authorize",
            "token_endpoint": "/caas/token",
            "introspection_endpoint": "/caas/introspect",
            "revocation_endpoint": "/caas/revoke",
            "grant_types_supported": [
                "urn:openagx:grant:agent_credential",
                "urn:openagx:grant:delegated_agent",
                "urn:openagx:grant:agent_impersonation",
            ],
            "scopes_supported": [
                "agent:read", "agent:execute", "agent:admin",
                "agent:delegate", "agent:impersonate",
            ],
        }


__all__ = [
    'CAASClient', 'OpenAGXProvider', 'AgentGrant',
    'GrantType', 'Scope'
]