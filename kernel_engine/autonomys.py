"""
Autonomys (Authonomyx) Identity Protocol

Auto ID - Decentralized identity for autonomous entities:
- Public identifier + cryptographic key pair
- Self-issued or externally issued
- Composite IDs (multi-party issuance)
- Delegation via nested signatures
- Auto PKI trust model

Auto AuthZ - Authorization:
- OAuth/OIDC compatible
- Capability-based access
- Delegated claims
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import json
from datetime import datetime


class AutoIDType(Enum):
    NATURAL = "natural"      # Person
    LEGAL = "legal"         # Organization
    AGENT = "agent"        # AI agent
    MODEL = "model"         # AI model
    DEVICE = "device"      # IoT device
    SERVICE = "service"   # Web service


class AutoIDStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class AutoID:
    """Autonomys Auto ID"""
    auto_id: str = field(default_factory=lambda: f"auto_{uuid.uuid4().hex[:12]}")
    public_id: str = ""  # Human-readable identifier
    auto_id_type: str = "agent"
    public_key: str = ""  # Public key (base64)
    issuer: str = ""      # Who issued (empty = self-issued)
    status: str = "active"
    auto_score: int = 0    # Proof-of-personhood score
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "auto_id": self.auto_id,
            "public_id": self.public_id,
            "type": self.auto_id_type,
            "issuer": self.issuer,
            "status": self.status,
            "auto_score": self.auto_score,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Delegation:
    """Delegation of authority"""
    delegation_id: str = field(default_factory=lambda: f"del_{uuid.uuid4().hex[:8]}")
    issuer_auto_id: str = ""
    delegate_auto_id: str = ""
    scope: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        if self.valid_until and datetime.now() > self.valid_until:
            return False
        return True


@dataclass
class Capability:
    """Capability grant"""
    cap_id: str = field(default_factory=lambda: f"cap_{uuid.uuid4().hex[:8}]")
    resource: str = ""
    actions: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)


class AutoPKI:
    """Auto PKI - Public Key Infrastructure"""
    
    def __init__(self):
        self.identities: Dict[str, AutoID] = {}
        self.delegations: Dict[str, Delegation] = {}
        self.capabilities: Dict[str, List[Capability]] = {}
        self.revocations: List[str] = []  # Revoked auto_ids
    
    # ============ Auto ID Operations ============
    
    def self_issue(self, public_id: str, auto_id_type: str = "agent",
               public_key: str = "") -> AutoID:
        """Self-issue Auto ID"""
        auto_id = AutoID(
            public_id=public_id,
            auto_id_type=auto_id_type,
            public_key=public_key or f"pk_{uuid.uuid4().hex[:24]}",
            issuer="",  # Self-issued
        )
        self.identities[auto_id.auto_id] = auto_id
        return auto_id
    
    def issue(self, public_id: str, issuer_auto_id: str,
             auto_id_type: str = "agent", public_key: str = "") -> AutoID:
        """Issue Auto ID to another entity"""
        issuer = self.identities.get(issuer_auto_id)
        if not issuer:
            raise ValueError("Invalid issuer")
        
        auto_id = AutoID(
            public_id=public_id,
            auto_id_type=auto_id_type,
            public_key=public_key or f"pk_{uuid.uuid4().hex[:24]}",
            issuer=issuer_auto_id,
        )
        self.identities[auto_id.auto_id] = auto_id
        return auto_id
    
    def get(self, auto_id: str) -> Optional[AutoID]:
        """Get Auto ID"""
        if auto_id in self.revocations:
            return None
        return self.identities.get(auto_id)
    
    def resolve(self, public_id: str) -> Optional[AutoID]:
        """Resolve by public_id"""
        for auto_id in self.identities.values():
            if auto_id.public_id == public_id:
                return auto_id
        return None
    
    def revoke(self, auto_id: str) -> bool:
        """Revoke Auto ID"""
        if auto_id in self.identities:
            self.identities[auto_id].status = "revoked"
            self.revocations.append(auto_id)
            return True
        return False
    
    def suspend(self, auto_id: str) -> bool:
        """Suspend Auto ID"""
        if auto_id in self.identities:
            self.identities[auto_id].status = "suspended"
            return True
        return False
    
    def reactivate(self, auto_id: str) -> bool:
        """Reactivate Auto ID"""
        if auto_id in self.identities:
            self.identities[auto_id].status = "active"
            return True
        return False
    
    # ============ Delegation ============
    
    def delegate(self, issuer_auto_id: str, delegate_auto_id: str,
             scope: List[str], constraints: Dict = None,
             valid_days: int = 30) -> Delegation:
        """Delegate authority"""
        # Verify both exist
        if issuer_auto_id not in self.identities:
            raise ValueError("Invalid issuer")
        if delegate_auto_id not in self.identities:
            raise ValueError("Invalid delegate")
        
        from datetime import timedelta
        delegation = Delegation(
            issuer_auto_id=issuer_auto_id,
            delegate_auto_id=delegate_auto_id,
            scope=scope,
            constraints=constraints or {},
            valid_until=datetime.now() + timedelta(days=valid_days),
        )
        
        self.delegations[delegation.delegation_id] = delegation
        return delegation
    
    def get_delegation(self, delegation_id: str) -> Optional[Delegation]:
        """Get delegation"""
        return self.delegations.get(delegation_id)
    
    def verify_delegation(self, delegate_auto_id: str, scope: str) -> bool:
        """Verify delegation is valid for scope"""
        for delg in self.delegations.values():
            if delg.delegate_auto_id != delegate_auto_id:
                continue
            if not delg.is_valid():
                continue
            if scope in delg.scope or " *" in delg.scope:
                return True
        return False
    
    # ============ Capabilities ============
    
    def grant_capability(self, auto_id: str, resource: str,
                   actions: List[str], constraints: Dict = None) -> Capability:
        """Grant capability"""
        cap = Capability(
            resource=resource,
            actions=actions,
            constraints=constraints or {},
        )
        
        if auto_id not in self.capabilities:
            self.capabilities[auto_id] = []
        self.capabilities[auto_id].append(cap)
        return cap
    
    def check_capability(self, auto_id: str, resource: str,
                      action: str) -> bool:
        """Check if has capability"""
        caps = self.capabilities.get(auto_id, [])
        
        for cap in caps:
            if cap.resource != resource and cap.resource != "*":
                continue
            if action in cap.actions or "*" in cap.actions:
                return True
        return False
    
    def list_capabilities(self, auto_id: str) -> List[Capability]:
        """List capabilities"""
        return self.capabilities.get(auto_id, [])
    
    def validate_action(self, action_type: str) -> bool:
        """Validate schema.org action type"""
        from kernel_engine.schema_actions import ActionVocabulary
        return ActionVocabulary.validate_action(action_type)
    
    def authorize_action(self, auto_id: str, action_type: str,
                      resource: str, obj: str = None) -> Dict:
        """Authorize with schema.org action validation"""
        if not self.validate_action(action_type):
            return {"allowed": False, "reason": "invalid_action_type"}
        if not self.check_capability(auto_id, resource, action_type):
            return {"allowed": False, "reason": "no_capability"}
        return {"allowed": True, "action_type": action_type}
    
    # ============ Authentication ============
    
    def authenticate(self, auto_id: str, challenge: str = "") -> bool:
        """Authenticate (verify key possession)"""
        identity = self.get(auto_id)
        if not identity or identity.status != "active":
            return False
        
        # In production, verify signature
        # For now, accept any challenge
        return True
    
    # ============ Listing ============
    
    def list_auto_ids(self, auto_id_type: str = None,
                issuer: str = None) -> List[AutoID]:
        """List Auto IDs"""
        results = list(self.identities.values())
        
        if auto_id_type:
            results = [a for a in results if a.auto_id_type == auto_id_type]
        if issuer:
            results = [a for a in results if a.issuer == issuer]
        
        return results
    
    def count_auto_ids(self) -> int:
        """Count Auto IDs"""
        return len(self.identities)


# ============================================================
# Auto AuthZ - Authorization
# ============================================================

class AutoAuthZ:
    """Auto AuthZ - Authorization service"""
    
    def __init__(self):
        self.pki = AutoPKI()
    
    def authorize(self, auto_id: str, resource: str,
              action: str) -> Dict:
        """Authorize action"""
        # Check Auto ID status
        identity = self.pki.get(auto_id)
        if not identity:
            return {"allowed": False, "reason": "identity_not_found"}
        
        if identity.status != "active":
            return {"allowed": False, "reason": "identity_not_active"}
        
        # Check capability
        if not self.pki.check_capability(auto_id, resource, action):
            return {"allowed": False, "reason": "no_capability"}
        
        return {"allowed": True, "auto_id": auto_id}
    
    def delegate_authorize(self, delegate_auto_id: str, 
                      issuer_auto_id: str, scope: str) -> Dict:
        """Authorize via delegation"""
        # Verify delegation exists and is valid
        if not self.pki.verify_delegation(delegate_auto_id, scope):
            return {"allowed": False, "reason": "no_delegation"}
        
        return {"allowed": True, "delegate": delegate_auto_id, "issuer": issuer_auto_id}


__all__ = [
    'AutoID', 'AutoIDType', 'AutoIDStatus',
    'Delegation', 'Capability', 'AutoPKI', 'AutoAuthZ'
]