"""
Identity vs Account Distinction

- Identity: The persistent "who" - represented by DID, UUID, email, etc.
- Account: A specific credential/auth method linked to an identity
- Principal: The authenticated actor making requests
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timedelta
import hashlib


class IdentityType(Enum):
    DID = "did"              # Decentralized Identifier (preferred)
    UUID = "uuid"          # System UUID (preferred)
    SUBJECT = "subject"    # JWT/OIDC subject claim (preferred)
    # Note: Email is NOT an identity - it's an account/credential


class AccountType(Enum):
    PASSWORD = "password"  # Password credential
    EMAIL = "email"       # Email account (verification)
    PHONE = "phone"      # Phone account (verification)
    OAUTH = "oauth"        # OAuth provider
    SAML = "saml"          # SAML provider
    API_KEY = "api_key"    # API key
    JWT = "jwt"            # JWT token
    MFA = "mfa"           # MFA/2FA
    PASSKEY = "passkey"   # WebAuthn passkey
    # Note: Email/PHONE are accounts, not identities
    # Identity = DID/UUID/SUBJECT


class IdentityStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    PENDING = "pending"


@dataclass
class Identity:
    """Identity - the persistent 'who'"""
    identity_id: str = field(default_factory=lambda: f"id_{uuid.uuid4().hex[:12]}")
    identity_type: str = "uuid"
    identifier: str = ""  # The actual identifier (DID, email, etc.)
    display_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    
    def to_dict(self) -> Dict:
        return {
            "identity_id": self.identity_id,
            "identity_type": self.identity_type,
            "identifier": self.identifier,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


@dataclass
class Account:
    """Account - credential/auth method for an identity"""
    account_id: str = field(default_factory=lambda: f"acct_{uuid.uuid4().hex[:8]}")
    identity_id: str = ""  # Link to identity
    account_type: str = "password"
    credential_hash: str = ""  # Hashed credential
    credential_salt: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str = "active"
    primary: bool = False  # Primary account for identity?
    
    def is_expired(self) -> bool:
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            "account_id": self.account_id,
            "identity_id": self.identity_id,
            "account_type": self.account_type,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "status": self.status,
            "primary": self.primary,
        }


@dataclass 
class Principal:
    """The authenticated actor"""
    principal_id: str = field(default_factory=lambda: f"prin_{uuid.uuid4().hex[:8]}")
    identity_id: str = ""
    account_id: str = ""
    session_id: str = ""
    auth_method: str = ""
    claims: Dict[str, Any] = field(default_factory=dict)
    authenticated_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict:
        return {
            "principal_id": self.principal_id,
            "identity_id": self.identity_id,
            "account_id": self.account_id,
            "auth_method": self.auth_method,
            "claims": self.claims,
        }


class IdentityManager:
    """Manage identities"""
    
    def __init__(self):
        self.identities: Dict[str, Identity] = {}
        self.accounts: Dict[str, Account] = {}
        self.identifiers: Dict[str, str] = {}  # identifier -> identity_id
        self.principals: Dict[str, Principal] = {}
    
    # ============ Identity Operations ============
    
    def create_identity(self, identifier: str, identity_type: str = "uuid",
                     display_name: str = "", metadata: Dict = None) -> Identity:
        """Create identity"""
        identity = Identity(
            identity_type=identity_type,
            identifier=identifier,
            display_name=display_name or identifier,
            metadata=metadata or {},
        )
        self.identities[identity.identity_id] = identity
        self.identifiers[identifier] = identity.identity_id
        return identity
    
    def get_identity(self, identity_id: str) -> Optional[Identity]:
        """Get identity"""
        return self.identities.get(identity_id)
    
    def get_identity_by_identifier(self, identifier: str) -> Optional[Identity]:
        """Get identity by identifier"""
        identity_id = self.identifiers.get(identifier)
        return self.identities.get(identity_id) if identity_id else None
    
    def update_identity(self, identity_id: str, **updates) -> Optional[Identity]:
        """Update identity"""
        identity = self.identities.get(identity_id)
        if identity:
            for k, v in updates.items():
                setattr(identity, k, v)
            identity.updated_at = datetime.now()
        return identity
    
    def deactivate_identity(self, identity_id: str) -> bool:
        """Deactivate identity"""
        identity = self.identities.get(identity_id)
        if identity:
            identity.status = "suspended"
            return True
        return False
    
    # ============ Account Operations ============
    
    def create_account(self, identity_id: str, account_type: str = "password",
                    credential: str = "", metadata: Dict = None, 
                    primary: bool = False) -> Account:
        """Create account for identity"""
        # Generate salt and hash
        salt = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
        cred_hash = hashlib.sha256(f"{credential}{salt}".encode()).hexdigest()
        
        account = Account(
            identity_id=identity_id,
            account_type=account_type,
            credential_hash=cred_hash,
            credential_salt=salt,
            metadata=metadata or {},
            primary=primary,
        )
        self.accounts[account.account_id] = account
        
        # Update identity's account list in metadata
        identity = self.identities.get(identity_id)
        if identity:
            if "account_ids" not in identity.metadata:
                identity.metadata["account_ids"] = []
            identity.metadata["account_ids"].append(account.account_id)
        
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account"""
        return self.accounts.get(account_id)
    
    def get_accounts_for_identity(self, identity_id: str) -> List[Account]:
        """Get all accounts for identity"""
        return [a for a in self.accounts.values() if a.identity_id == identity_id]
    
    def authenticate_account(self, identity_id: str, account_type: str, 
                       credential: str) -> Optional[Account]:
        """Authenticate account"""
        accounts = self.get_accounts_for_identity(identity_id)
        
        for account in accounts:
            if account.account_type != account_type:
                continue
            if account.is_expired():
                continue
            
            # Verify credential
            cred_hash = hashlib.sha256(
                f"{credential}{account.credential_salt}".encode()
            ).hexdigest()
            
            if cred_hash == account.credential_hash:
                account.last_used = datetime.now()
                return account
        
        return None
    
    def link_account(self, identity_id: str, account_id: str) -> bool:
        """Link existing account to identity"""
        account = self.accounts.get(account_id)
        if account and not account.identity_id:
            account.identity_id = identity_id
            return True
        return False
    
    def deactivate_account(self, account_id: str) -> bool:
        """Deactivate account"""
        account = self.accounts.get(account_id)
        if account:
            account.status = "disabled"
            return True
        return False
    
    # ============ Principal/Auth Operations ============
    
    def authenticate(self, identifier: str, account_type: str, 
                  credential: str) -> Optional[Principal]:
        """Authenticate and return principal"""
        # Find identity
        identity = self.get_identity_by_identifier(identifier)
        if not identity:
            return None
        
        # Authenticate account
        account = self.authenticate_account(
            identity.identity_id, account_type, credential
        )
        if not account:
            return None
        
        # Create principal
        principal = Principal(
            identity_id=identity.identity_id,
            account_id=account.account_id,
            auth_method=account_type,
            claims={"identity_type": identity.identity_type},
        )
        self.principals[principal.principal_id] = principal
        
        return principal
    
    def get_principal(self, principal_id: str) -> Optional[Principal]:
        """Get principal"""
        return self.principals.get(principal_id)
    
    def refresh_principal(self, principal_id: str) -> bool:
        """Refresh principal expiry"""
        principal = self.principals.get(principal_id)
        if principal and not principal.is_expired():
            principal.expires_at = datetime.now() + timedelta(hours=24)
            return True
        return False
    
    def logout(self, principal_id: str) -> bool:
        """Logout principal"""
        if principal_id in self.principals:
            del self.principals[principal_id]
            return True
        return False
    
    # ============ Utility Methods ============
    
    def resolve_principal_identity(self, principal_id: str) -> Optional[Identity]:
        """Resolve principal to identity"""
        principal = self.principals.get(principal_id)
        if not principal:
            return None
        return self.identities.get(principal.identity_id)
    
    def list_identities(self, status: str = None) -> List[Identity]:
        """List identities"""
        results = list(self.identities.values())
        if status:
            results = [i for i in results if i.status == status]
        return results
    
    def get_identity_count(self) -> int:
        """Count identities"""
        return len(self.identities)


__all__ = [
    'Identity', 'Account', 'Principal', 'IdentityType', 'AccountType',
    'IdentityStatus', 'IdentityManager'
]