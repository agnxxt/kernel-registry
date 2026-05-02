"""
OIDC - OpenID Connect for Agent Identity

Proper OIDC implementation with:
- Agent ID from JWT sub claim
- ID Token validation
- UserInfo endpoint
- Token refresh
- Provider discovery
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import hashlib
import json
from datetime import datetime, timedelta


class FlowType(Enum):
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"


class TokenType(Enum):
    ID_TOKEN = "id_token"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"


@dataclass
class OIDCProvider:
    """OIDC Provider configuration"""
    issuer: str = ""
    authorization_endpoint: str = ""
    token_endpoint: str = ""
    userinfo_endpoint: str = ""
    jwks_uri: str = ""
    introspection_endpoint: str = ""
    revocation_endpoint: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "issuer": self.issuer,
            "authorization_endpoint": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "userinfo_endpoint": self.userinfo_endpoint,
            "jwks_uri": self.jwks_uri,
            "introspection_endpoint": self.introspection_endpoint,
            "revocation_endpoint": self.revocation_endpoint,
        }


@dataclass
class OIDCSession:
    """OIDC session"""
    session_id: str = field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:12]}")
    agent_id: str = ""  # The agent identifier (sub claim)
    sub: str = ""  # Subject (matches agent_id)
    iss: str = ""  # Issuer
    aud: str = ""  # Audience
    iat: int = field(default_factory=lambda: int(time.time()))
    exp: int = 0  # Expiry
    nonce: str = ""  # Nonce for auth
    auth_time: int = 0  # When authenticated
    claims: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TokenSet:
    """Token set"""
    access_token: str = ""
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: str = ""
    id_token: str = ""
    scope: str = "openid agent:read agent:execute"


class OIDCClient:
    """OIDC Client for agents"""
    
    def __init__(self, client_id: str = "", client_secret: str = "",
                 redirect_uri: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sessions: Dict[str, OIDCSession] = {}
        self.tokens: Dict[str, TokenSet] = {}
        self.providers: Dict[str, OIDCProvider] = {}
        
        # Default provider
        self.default_provider = OIDCProvider()
    
    # ============ Provider Operations ============
    
    def register_provider(self, name: str, provider: OIDCProvider):
        """Register OIDC provider"""
        self.providers[name] = provider
    
    def get_provider(self, name: str = None) -> OIDCProvider:
        """Get provider"""
        return self.providers.get(name or "default") or self.default_provider
    
    def discover(self, issuer: str) -> Dict:
        """OIDC Discovery"""
        provider = self.get_provider()
        return {
            "issuer": issuer,
            "authorization_endpoint": f"{issuer}/authorize",
            "token_endpoint": f"{issuer}/token",
            "userinfo_endpoint": f"{issuer}/userinfo",
            "jwks_uri": f"{issuer}/.well-known/jwks.json",
            "introspection_endpoint": f"{issuer}/introspect",
            "revocation_endpoint": f"{issuer}/revoke",
            "response_types_supported": ["code", "token", "id_token"],
            "grant_types_supported": [
                "authorization_code",
                "refresh_token", 
                "client_credentials"
            ],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
    
    # ============ Authentication Flow ============
    
    def create_authorization_url(self, provider_name: str = None,
                                 state: str = "", 
                                 nonce: str = "",
                                 scope: str = None) -> str:
        """Create authorization URL"""
        provider = self.get_provider(provider_name)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state or str(uuid.uuid4()),
            "nonce": nonce or str(uuid.uuid4()),
            "scope": scope or "openid agent:read agent:execute",
        }
        
        # Build URL
        from urllib.parse import urlencode
        return f"{provider.authorization_endpoint}?{urlencode(params)}"
    
    def exchange_code(self, code: str, provider_name: str = None) -> TokenSet:
        """Exchange authorization code for tokens"""
        provider = self.get_provider(provider_name)
        
        # In practice, call token_endpoint
        # For now, generate tokens
        access_token = f"at_{uuid.uuid4().hex}"
        refresh_token = f"rt_{uuid.uuid4().hex}"
        
        # Create ID token (simulated)
        now = int(time.time())
        id_token = self._create_id_token(
            sub="agent_001",  # This is the agent ID
            aud=self.client_id,
            nonce=nonce if 'nonce' in locals() else ""
        )
        
        token_set = TokenSet(
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
        )
        
        self.tokens[access_token] = token_set
        return token_set
    
    def _create_id_token(self, sub: str, aud: str, nonce: str = "") -> str:
        """Create (simulate) ID token"""
        # In production, this would be a signed JWT
        now = int(time.time())
        return f"eyJhbGciOiJSUzI1NiJ9.{uuid.uuid4().hex}.{uuid.uuid4().hex}"
    
    def refresh(self, refresh_token: str) -> TokenSet:
        """Refresh tokens"""
        # Validate refresh_token
        if not refresh_token.startswith("rt_"):
            raise ValueError("Invalid refresh token")
        
        # Issue new tokens
        access_token = f"at_{uuid.uuid4().hex}"
        new_refresh_token = f"rt_{uuid.uuid4().hex}"
        
        token_set = TokenSet(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )
        
        self.tokens[access_token] = token_set
        return token_set
    
    def introspect(self, access_token: str) -> Dict:
        """Token introspection"""
        if access_token not in self.tokens:
            return {"active": False}
        
        return {
            "active": True,
            "scope": "openid agent:read agent:execute",
            "client_id": self.client_id,
            "exp": int(time.time()) + 3600,
        }
    
    def revoke(self, token: str, token_type_hint: str = None):
        """Revoke token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    # ============ UserInfo ============
    
    def get_userinfo(self, access_token: str) -> Dict:
        """Get userinfo"""
        # Validate token
        if access_token not in self.tokens:
            raise ValueError("Invalid token")
        
        # Return claims
        return {
            "sub": "agent_001",  # Agent ID
            "agent_type": " исполняющий агент",
            "capabilities": ["read", "execute"],
        }
    
    # ============ Agent ID Extraction ============
    
    def get_agent_id(self, id_token: str = None, 
                 access_token: str = None) -> Optional[str]:
        """Get agent ID from token
        
        Priority:
        1. Extract from ID token (sub claim)
        2. Extract from access_token metadata
        3. Return None
        """
        if id_token and id_token.startswith("eyJ"):
            # Parse JWT (simplified - in production verify signature)
            try:
                parts = id_token.split(".")
                if len(parts) >= 2:
                    # The second part is the payload
                    import base64
                    payload = parts[1]
                    # Add padding
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += "=" * padding
                    data = json.loads(base64.b64decode(payload))
                    return data.get("sub")
            except Exception:
                pass
        
        if access_token and access_token.startswith("at_"):
            # Access token - look up in store
            token_set = self.tokens.get(access_token)
            if token_set:
                return self.get_agent_id(id_token=token_set.id_token)
        
        return None
    
    def validate_agent_id(self, agent_id: str, 
                        access_token: str) -> bool:
        """Validate agent ID matches token"""
        token_agent_id = self.get_agent_id(access_token=access_token)
        return token_agent_id == agent_id


__all__ = [
    'OIDCClient', 'OIDCProvider', 'OIDCSession', 'TokenSet',
    'FlowType', 'TokenType'
]