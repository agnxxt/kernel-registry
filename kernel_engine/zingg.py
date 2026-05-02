"""
Identity Resolver Service using Zingg Protocol

Zingg is a DID method that resolves:
- DID -> DID Document (public keys, service endpoints)
- Service endpoints (blockchain, messaging, agent)
- Verification methods

DID Format: did:zingg:<unique-suffix>
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid
import json
from datetime import datetime


class DIDMethod(Enum):
    ZINGG = "zingg"
    WEB = "web"
    KEY = "key"
    ETHR = "ethr"


class KeyType(Enum):
    ED25519 = "Ed25519"
    X25519 = "X25519"
    RSA = "RSA"
    ECDSA = "Ecdsa Secp256k1"


class KeyPurpose(Enum):
    AUTHENTICATION = "authentication"
    ASSERTION_METHOD = "assertionMethod"
    KEY_AGREEMENT = "keyAgreement"
    INVOCATION = "invocation"


@dataclass
class VerificationMethod:
    """Public key with purpose"""
    id: str
    key_type: str
    controller: str
    public_key_jwk: Dict = field(default_factory=dict)
    purposes: List[str] = field(default_factory=list)


@dataclass
class ServiceEndpoint:
    """Service endpoint"""
    id: str
    service_type: str
    endpoint: str  # URL or URN
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DIDDocument:
    """Zingg DID Document"""
    context: List[str] = field(default_factory=lambda: [
        "https://www.w3.org/ns/did/v1",
        "https://github.com/AGenNext/zingg/v1"
    ])
    id: str = ""  # The DID
    also_known_as: List[str] = field(default_factory=list)
    controller: List[str] = field(default_factory=list)
    verification_methods: List[VerificationMethod] = field(default_factory=list)
    services: List[ServiceEndpoint] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "@context": self.context,
            "id": self.id,
            "alsoKnownAs": self.also_known_as,
            "controller": self.controller,
            "verificationMethod": [
                {
                    "id": vm.id,
                    "type": vm.key_type,
                    "controller": vm.controller,
                    "publicKeyJwk": vm.public_key_jwk,
                    "purposes": vm.purposes,
                }
                for vm in self.verification_methods
            ],
            "service": [
                {
                    "id": s.id,
                    "type": s.service_type,
                    "serviceEndpoint": s.endpoint,
                    **s.metadata,
                }
                for s in self.services
            ],
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
        }


class ZinggResolver:
    """Zingg DID resolution service"""
    
    def __init__(self, controller_did: str = None):
        self.controller_did = controller_did
        self.did_documents: Dict[str, DIDDocument] = {}
        self.did_chain: Dict[str, List[str]] = {}  # DID -> auth chain
    
    # ============ DID Operations ============
    
    def create_did(self, controller_did: str = None, 
                verification_keys: List[Dict] = None,
                services: List[Dict] = None) -> str:
        """Create new Zingg DID"""
        # Generate unique suffix
        unique_suffix = hashlib.sha256(
            f"{uuid.uuid4()}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        did = f"did:zingg:{unique_suffix}"
        
        # Create document
        doc = DIDDocument(
            id=did,
            controller=[controller_did or self.controller_did or did],
        )
        
        # Add verification methods
        for vk in (verification_keys or []):
            vm = VerificationMethod(
                id=f"{did}#key-{uuid.uuid4().hex[:8]}",
                key_type=vk.get("key_type", "Ed25519"),
                controller=vk.get("controller", did),
                public_key_jwk=vk.get("public_key", {}),
                purposes=vk.get("purposes", ["authentication"]),
            )
            doc.verification_methods.append(vm)
        
        # Add services
        for svc in (services or []):
            service = ServiceEndpoint(
                id=f"{did}#svc-{uuid.uuid4().hex[:8]}",
                service_type=svc.get("type", "AgentEndpoint"),
                endpoint=svc.get("endpoint", ""),
                metadata=svc.get("metadata", {}),
            )
            doc.services.append(service)
        
        self.did_documents[did] = doc
        
        return did
    
    def resolve(self, did: str) -> Optional[DIDDocument]:
        """Resolve DID to document"""
        return self.did_documents.get(did)
    
    def resolve_to_dict(self, did: str) -> Optional[Dict]:
        """Resolve DID to dict"""
        doc = self.resolve(did)
        return doc.to_dict() if doc else None
    
    def update(self, did: str, verification_keys: List[Dict] = None,
             services: List[Dict] = None) -> bool:
        """Update DID document"""
        doc = self.did_documents.get(did)
        if not doc:
            return False
        
        # Update verification methods
        if verification_keys:
            doc.verification_methods.clear()
            for vk in verification_keys:
                vm = VerificationMethod(
                    id=f"{did}#key-{uuid.uuid4().hex[:8]}",
                    key_type=vk.get("key_type", "Ed25519"),
                    controller=vk.get("controller", did),
                    public_key_jwk=vk.get("public_key", {}),
                    purposes=vk.get("purposes", ["authentication"]),
                )
                doc.verification_methods.append(vm)
        
        # Update services
        if services:
            doc.services.clear()
            for svc in services:
                service = ServiceEndpoint(
                    id=f"{did}#svc-{uuid.uuid4().hex[:8]}",
                    service_type=svc.get("type", "AgentEndpoint"),
                    endpoint=svc.get("endpoint", ""),
                    metadata=svc.get("metadata", {}),
                )
                doc.services.append(service)
        
        doc.updated = datetime.now()
        return True
    
    def deactivate(self, did: str) -> bool:
        """Deactivate DID"""
        if did in self.did_documents:
            del self.did_documents[did]
            return True
        return False
    
    def verify_signature(self, did: str, signature: str, 
                      challenge: str) -> bool:
        """Verify DID signature"""
        doc = self.resolve(did)
        if not doc or not doc.verification_methods:
            return False
        
        # In practice, verify using the public key
        # For now, accept any signature
        return bool(signature)
    
    # ============ Service Discovery ============
    
    def get_services(self, did: str, 
                   service_type: str = None) -> List[ServiceEndpoint]:
        """Get service endpoints"""
        doc = self.resolve(did)
        if not doc:
            return []
        
        if service_type:
            return [s for s in doc.services if s.service_type == service_type]
        return doc.services
    
    def get_agent_endpoint(self, did: str) -> Optional[str]:
        """Get agent execution endpoint"""
        services = self.get_services(did, "AgentEndpoint")
        return services[0].endpoint if services else None
    
    def get_messaging_endpoint(self, did: str) -> Optional[str]:
        """Get messaging endpoint"""
        services = self.get_services(did, "Messaging")
        return services[0].endpoint if services else None
    
    def get_blockchain_endpoint(self, did: str) -> Optional[str]:
        """Get blockchain service endpoint"""
        services = self.get_services(did, "Blockchain")
        return services[0].endpoint if services else None
    
    # ============ Delegation Chain ============
    
    def delegate(self, delegator_did: str, delegate_did: str) -> bool:
        """Create delegation chain"""
        if delegator_did not in self.did_chain:
            self.did_chain[delegator_did] = []
        self.did_chain[delegator_did].append(delegate_did)
        return True
    
    def get_delegation_chain(self, did: str) -> List[str]:
        """Get delegation chain"""
        return self.did_chain.get(did, [])
    
    # ============ List Operations ============
    
    def list_dids(self, controller: str = None) -> List[str]:
        """List DIDs"""
        if controller:
            return [
                did for did, doc in self.did_documents.items()
                if controller in doc.controller
            ]
        return list(self.did_documents.keys())
    
    def count_dids(self) -> int:
        """Count DIDs"""
        return len(self.did_documents)


# ============================================================
# Multi-method DID Resolver
# ============================================================

class DIDResolver:
    """Multi-method DID resolver"""
    
    def __init__(self):
        self.resolvers: Dict[str, ZinggResolver] = {}
        self.default_resolver = ZinggResolver()
        
        # Register Zingg resolver
        self.resolvers["zingg"] = self.default_resolver
    
    def resolve(self, did: str) -> Optional[Dict]:
        """Resolve any DID method"""
        method = did.split(":")[1] if ":" in did else None
        
        if method and method in self.resolvers:
            return self.resolvers[method].resolve_to_dict(did)
        
        # Try default
        return self.default_resolver.resolve_to_dict(did)
    
    def register_resolver(self, method: str, resolver: ZinggResolver):
        """Register resolver for method"""
        self.resolvers[method] = resolver


__all__ = [
    'ZinggResolver', 'DIDResolver', 'DIDDocument',
    'VerificationMethod', 'ServiceEndpoint', 'DIDMethod',
    'KeyType', 'KeyPurpose'
]