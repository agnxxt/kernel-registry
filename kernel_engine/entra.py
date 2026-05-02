"""
Microsoft Entra ID (Azure AD) Integration for Agent Identity

Entra ID provides:
- Agent authentication via Microsoft identity
- Application registration
- Service principal for agents
- Token claims extraction
- Group-based access
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
from datetime import datetime


class EntraTenantType(Enum):
    SINGLE_TENANT = "single_tenant"
    MULTI_TENANT = "multi_tenant"
    PERSONAL = "personal"


class EntraAppRole(Enum):
    AGENT = "Agent"
    ADMIN = "Administrator"
    USER = "User"
    OPERATOR = "Operator"


@dataclass
class EntraApplication:
    """Entra application registration"""
    app_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    object_id: str = ""  # Azure object ID
    display_name: str = ""
    owner_tenant_id: str = ""
    type: str = "web"  # web, daemon, spa
    required_scope: List[str] = field(default_factory=list)
    app_roles: List[str] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)


@dataclass
class ServicePrincipal:
    """Entra service principal"""
    sp_object_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    app_id: str = ""
    display_name: str = ""
    tenant_id: str = ""
    app_role_assignments: List[str] = field(default_factory=list)
    service_principal_type: str = "Application"


@dataclass
class EntraToken:
    """Entra token"""
    access_token: str = ""
    id_token: str = ""
    refresh_token: str = ""
    expires_at: int = 0
    token_type: str = "Bearer"
    issued_for: str = ""  # Who it was issued for


class EntraClient:
    """Entra ID Client"""
    
    def __init__(self, tenant_id: str = "", client_id: str = "",
                 client_secret: str = ""):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Registry
        self.applications: Dict[str, EntraApplication] = {}
        self.service_principals: Dict[str, ServicePrincipal] = {}
        self.tokens: Dict[str, EntraToken] = {}
        self.agent_mappings: Dict[str, str] = {}  # app_id+object_id -> agent_id
    
    # ============ Application Registration ============
    
    def register_application(self, display_name: str = None,
                          app_type: str = "web",
                          scope: List[str] = None) -> EntraApplication:
        """Register application in Entra"""
        app = EntraApplication(
            object_id=str(uuid.uuid4()),
            display_name=display_name or f"Agent-{uuid.uuid4().hex[:8]}",
            owner_tenant_id=self.tenant_id,
            type=app_type,
            required_scope=scope or ["User.Read", "Agent.Execute"],
            app_roles=["Agent", "Operator", "Administrator"],
        )
        
        self.applications[app.app_id] = app
        return app
    
    def get_application(self, app_id: str) -> Optional[EntraApplication]:
        """Get application"""
        return self.applications.get(app_id)
    
    def update_application(self, app_id: str, **updates) -> bool:
        """Update application"""
        app = self.applications.get(app_id)
        if app:
            for k, v in updates.items():
                setattr(app, k, v)
            return True
        return False
    
    # ============ Service Principal Operations ============
    
    def create_service_principal(self, app_id: str) -> ServicePrincipal:
        """Create service principal for app"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"App {app_id} not found")
        
        sp = ServicePrincipal(
            app_id=app_id,
            display_name=app.display_name,
            tenant_id=app.owner_tenant_id,
            app_role_assignments=app.app_roles,
        )
        
        self.service_principals[sp.sp_object_id] = sp
        return sp
    
    def assign_app_role(self, sp_object_id: str, role: str) -> bool:
        """Assign app role"""
        sp = self.service_principals.get(sp_object_id)
        if sp and role in ["Agent", "Operator", "Administrator"]:
            sp.app_role_assignments.append(role)
            return True
        return False
    
    # ============ Token Operations ============
    
    def acquire_token(self, app_id: str, oauth2_scopes: str = None) -> EntraToken:
        """Acquire token for application"""
        app = self.applications.get(app_id)
        if not app:
            raise ValueError(f"App {app_id} not found")
        
        # In production, call Microsoft token endpoint
        # Simulate token
        import base64
        import json
        
        now = int(time.time())
        
        # ID token claims
        id_claims = {
            "iss": f"https://login.microsoftonline.com/{self.tenant_id}",
            "sub": app.app_id,
            "oid": app.object_id,
            "tid": self.tenant_id,
            "roles": app.app_roles,
            "iat": now,
            "exp": now + 3600,
        }
        
        id_token = base64.b64encode(json.dumps(id_claims).encode()).decode()
        
        token = EntraToken(
            access_token=f"at_{uuid.uuid4().hex}",
            id_token=id_token,
            refresh_token=f"rt_{uuid.uuid4().hex}",
            expires_at=now + 3600,
            issued_for=app_id,
        )
        
        self.tokens[token.access_token] = token
        return token
    
    def acquire_token_by_username(self, app_id: str, 
                                 upn: str) -> EntraToken:
        """Acquire token for user (delegate)"""
        # This is for delegate flow
        return self.acquire_token(app_id)
    
    def refresh_token(self, refresh_token: str) -> EntraToken:
        """Refresh token"""
        if not refresh_token.startswith("rt_"):
            raise ValueError("Invalid refresh token")
        
        # Issue new token
        return self.acquire_token(str(uuid.uuid4()))
    
    def validate_token(self, access_token: str) -> Dict:
        """Validate token and return claims"""
        if access_token not in self.tokens:
            return {"active": False}
        
        token = self.tokens[access_token]
        
        if token.expires_at < int(time.time()):
            return {"active": False}
        
        import base64
        import json
        
        # Decode claims
        id_token = token.id_token
        padding = 4 - len(id_token) % 4
        if padding != 4:
            id_token += "=" * padding
        claims = json.loads(base64.b64decode(id_token))
        
        return {
            "active": True,
            "claims": claims,
        }
    
    # ============ Agent ID Extraction ============
    
    def get_agent_id(self, access_token: str = None,
                   id_token: str = None) -> Optional[str]:
        """Extract agent ID from Entra token
        
        Agent ID comes from:
        - oid (object ID) - Microsoft-assigned
        - sub (subject) - if using custom claims
        - app_id + oid combination
        """
        if id_token:
            try:
                import base64
                import json
                
                padding = 4 - len(id_token) % 4
                if padding != 4:
                    id_token += "=" * padding
                claims = json.loads(base64.b64decode(id_token))
                
                # Useoid as agent ID (preferred)
                if claims.get("oid"):
                    return f"entra:{claims['oid']}"
                
                # Or app_id + roles
                if claims.get("app_id"):
                    roles = claims.get("roles", [])
                    return f"entra:app:{claims['app_id']}"
                    
            except Exception:
                pass
        
        if access_token:
            token = self.tokens.get(access_token)
            if token:
                return self.get_agent_id(id_token=token.id_token)
        
        return None
    
    def get_agent_claims(self, access_token: str) -> Dict:
        """Get full agent claims"""
        result = self.validate_token(access_token)
        if result.get("active"):
            return result.get("claims", {})
        return {}
    
    def get_agent_roles(self, access_token: str) -> List[str]:
        """Get agent's app roles"""
        claims = self.get_agent_claims(access_token)
        return claims.get("roles", [])
    
    def has_agent_role(self, access_token: str, role: str) -> bool:
        """Check if agent has role"""
        roles = self.get_agent_roles(access_token)
        return role in roles
    
    # ============ Group Operations ============
    
    def get_agent_groups(self, access_token: str) -> List[str]:
        """Get agent's group memberships"""
        claims = self.get_agent_claims(access_token)
        # In production, call /memberOf endpoint
        return claims.get("groups", [])
    
    # ============ Graph API ============
    
    def get_service_principal(self, sp_object_id: str) -> Optional[ServicePrincipal]:
        """Get service principal"""
        return self.service_principals.get(sp_object_id)
    
    def list_applications(self) -> List[EntraApplication]:
        """List applications"""
        return list(self.applications.values())
    
    def list_service_principals(self) -> List[ServicePrincipal]:
        """List service principals"""
        return list(self.service_principals.values())


__all__ = [
    'EntraClient', 'EntraApplication', 'ServicePrincipal', 'EntraToken',
    'EntraTenantType', 'EntraAppRole'
]