"""AID - Agent Identification"""
import hashlib
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class DIDMethod(Enum):
    AID = "aid"
    
def generate_did() -> str:
    return f"did:aid:{uuid.uuid4().hex}"

class VerifiableCredential:
    """Verifiable credential"""
    def __init__(self, credential_id: str, issuer: str, subject: str, claims: Dict):
        self.credential_id = credential_id
        self.issuer = issuer
        self.subject = subject
        self.claims = claims
        self.issued_at = datetime.now()
        
    def to_dict(self) -> Dict:
        return {'id': self.credential_id, 'issuer': self.issuer,
                'subject': self.subject, 'claims': self.claims}

class AgentRegistry:
    """Agent registry"""
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        
    def register(self, agent_id: str, did: str, metadata: Dict):
        self.agents[agent_id] = {'did': did, 'metadata': metadata,
                                'registered_at': datetime.now()}
        
    def resolve(self, agent_id: str) -> Optional[Dict]:
        return self.agents.get(agent_id)

class AgentWallet:
    """Agent wallet for credentials"""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.credentials: List[VerifiableCredential] = []
        self.keys: Dict[str, str] = {}
        
    def add_credential(self, credential: VerifiableCredential):
        self.credentials.append(credential)
        
    def get_credentials(self) -> List[Dict]:
        return [c.to_dict() for c in self.credentials]

__all__ = ['generate_did', 'VerifiableCredential', 'AgentRegistry', 'AgentWallet', 'DIDMethod']