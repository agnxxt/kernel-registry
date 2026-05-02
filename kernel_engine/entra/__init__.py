"""
Entra - Agent Identity & Governance Toolkit
Inspired by Microsoft Entra ID but written from scratch
"""
import hashlib
import json
import uuid
import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

# ============================================================================
# IDENTITY PROVIDER - User/Agent Authentication
# ============================================================================

class IdentityProvider:
    """Identity provider for agents and users"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.identities: Dict[str, Dict] = {}  # identity_id -> identity
        self.credentials: Dict[str, Dict] = {}  # identity_id -> {password_hash, totp_secret}
        self.sessions: Dict[str, Dict] = {}  # session_id -> session data
        self.refresh_tokens: Dict[str, str] = {}  # refresh_token -> identity_id
        
    def register(self, identity_id: str, identity_type: str, claims: Dict) -> bool:
        """Register a new identity"""
        self.identities[identity_id] = {
            'id': identity_id,
            'type': identity_type,  # user, serviceprincipal, managedidentity
            'claims': claims,
            'created_at': datetime.now(),
            'enabled': True,
            'metadata': {}
        }
        return True
        
    def authenticate(self, identity_id: str, credentials: Dict) -> Optional[Dict]:
        """Authenticate with credentials"""
        identity = self.identities.get(identity_id)
        if not identity or not identity.get('enabled'):
            return None
            
        # Check password/TOTP
        stored = self.credentials.get(identity_id, {})
        if 'password' in credentials:
            ph = self._hash_password(credentials['password'], identity_id)
            if ph != stored.get('password_hash'):
                return None
                
        # Create session
        session_id = f"sess_{uuid.uuid4().hex}"
        self.sessions[session_id] = {
            'identity_id': identity_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1),
            'scopes': identity.get('claims', {}).get('scopes', ['openid'])
        }
        return {'session_id': session_id, 'identity': identity}
        
    def create_refresh_token(self, identity_id: str) -> str:
        """Create refresh token"""
        token = f"ref_{uuid.uuid4().hex}"
        self.refresh_tokens[token] = identity_id
        return token
        
    def refresh_session(self, refresh_token: str) -> Optional[Dict]:
        """Refresh session using refresh token"""
        identity_id = self.refresh_tokens.get(refresh_token)
        if not identity_id:
            return None
        return self.authenticate(identity_id, {})  # Skip password for refresh
        
    def revoke_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            
    def get_identity(self, identity_id: str) -> Optional[Dict]:
        return self.identities.get(identity_id)
        
    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()


# ============================================================================
# CONDITIONAL ACCESS - Policy-based Authorization
# ============================================================================

class ConditionalAccessPolicy:
    """Conditional Access policy with conditions"""
    
    def __init__(self, policy_id: str, name: str):
        self.policy_id = policy_id
        self.name = name
        self.enabled = True
        self.conditions: Dict = {}
        self.grant_controls: List[str] = []
        self.exclude_users: Set[str] = set()
        self.exclude_apps: Set[str] = set()
        
    def add_condition(self, condition_type: str, values: List[str]):
        self.conditions[condition_type] = values
        
    def evaluate(self, context: Dict) -> Tuple[bool, str]:
        """Evaluate policy conditions"""
        # Check excluded users
        if context.get('user_id') in self.exclude_users:
            return False, "excluded"
            
        # Check excluded apps
        if context.get('application_id') in self.exclude_apps:
            return False, "excluded"
            
        # Evaluate conditions
        for cond_type, expected in self.conditions.items():
            actual = context.get(cond_type)
            if actual and actual not in expected:
                return False, cond_type
                
        return True, "granted"
        

class ConditionalAccessEngine:
    """Conditional Access evaluation engine"""
    
    def __init__(self):
        self.policies: Dict[str, ConditionalAccessPolicy] = {}
        
    def add_policy(self, policy: ConditionalAccessPolicy):
        self.policies[policy.policy_id] = policy
        
    def evaluate(self, context: Dict) -> Tuple[bool, List[str]]:
        """Evaluate all applicable policies"""
        results = []
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            allowed, reason = policy.evaluate(context)
            if not allowed:
                return False, [f"{policy.name}: {reason}"]
        return True, []


# ============================================================================
# PRIVILEGED IDENTITY MANAGEMENT (PIM)
# ============================================================================

class PIMAssignment:
    """Privileged Identity Management assignment"""
    
    def __init__(self, assignment_id: str, principal_id: str, role_id: str, 
                 assignment_type: str, start_at: datetime, end_at: datetime):
        self.assignment_id = assignment_id
        self.principal_id = principal_id
        self.role_id = role_id
        self.assignment_type = assignment_type  # eligible, active
        self.start_at = start_at
        self.end_at = end_at
        self.activated_at: Optional[datetime] = None
        self.status = "assigned"
        
    def activate(self, justification: str) -> bool:
        if self.assignment_type != "eligible":
            return False
        if datetime.now() < self.start_at or datetime.now() > self.end_at:
            return False
        self.activated_at = datetime.now()
        self.status = "activated"
        return True
        
    def deactivate(self):
        self.activated_at = None
        self.status = "assigned"


class PIMEngine:
    """Privileged Identity Management engine"""
    
    def __init__(self):
        self.assignments: Dict[str, PIMAssignment] = {}
        self.approvals: Dict[str, Dict] = {}  # assignment_id -> approval
        
    def assign(self, principal_id: str, role_id: str, duration_hours: int = 8) -> str:
        assignment_id = f"pim_{uuid.uuid4().hex[:8]}"
        now = datetime.now()
        assignment = PIMAssignment(
            assignment_id, principal_id, role_id, "eligible",
            now, now + timedelta(hours=duration_hours)
        )
        self.assignments[assignment_id] = assignment
        return assignment_id
        
    def activate(self, assignment_id: str, justification: str) -> bool:
        assignment = self.assignments.get(assignment_id)
        if not assignment:
            return False
            
        # Require approval for sensitive roles
        if assignment.role_id in ["admin", "super_admin"]:
            self.approvals[assignment_id] = {
                'justification': justification,
                'status': 'pending',
                'requested_at': datetime.now()
            }
            return False
            
        return assignment.activate(justification)
        
    def approve(self, assignment_id: str, approver_id: str) -> bool:
        if assignment_id in self.approvals:
            self.approvals[assignment_id]['status'] = 'approved'
            self.approvals[assignment_id]['approver_id'] = approver_id
            assignment = self.assignments.get(assignment_id)
            if assignment:
                return assignment.activate("approved")
        return False
        
    def get_active_roles(self, principal_id: str) -> List[str]:
        now = datetime.now()
        active = []
        for a in self.assignments.values():
            if a.principal_id != principal_id:
                continue
            if a.status == "activated" and a.start_at <= now <= a.end_at:
                active.append(a.role_id)
        return active


# ============================================================================
# IDENTITY PROTECTION - Risk-based Security
# ============================================================================

class RiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskDetector:
    """Risk-based identity protection"""
    
    def __init__(self):
        self.risk_signals: Dict[str, List[Dict]] = {}  # identity_id -> signals
        self.risk_scores: Dict[str, int] = {}  # identity_id -> risk score 0-100
        
    def add_signal(self, identity_id: str, signal_type: str, location: str, timestamp: datetime):
        if identity_id not in self.risk_signals:
            self.risk_signals[identity_id] = []
        self.risk_signals[identity_id].append({
            'type': signal_type,
            'location': location,
            'timestamp': timestamp
        })
        self._recalculate_score(identity_id)
        
    def _recalculate_score(self, identity_id: str):
        signals = self.risk_signals.get(identity_id, [])
        score = 0
        
        # Unfamiliar location: +20
        unfamiliar = [s for s in signals if s.get('type') == 'unfamiliar_location']
        if unfamiliar:
            score += min(20 * len(unfamiliar), 40)
            
        # Impossible travel: +30
        if any(s.get('type') == 'impossible_travel'):
            score += 30
            
        # Brute force: +40
        if any(s.get('type') == 'brute_force'):
            score += 40
            
        # Malware: +50
        if any(s.get('type') == 'malware'):
            score += 50
            
        self.risk_scores[identity_id] = min(score, 100)
        
    def get_risk_level(self, identity_id: str) -> RiskLevel:
        score = self.risk_scores.get(identity_id, 0)
        if score >= 80:
            return RiskLevel.CRITICAL
        if score >= 50:
            return RiskLevel.HIGH
        if score >= 25:
            return RiskLevel.MEDIUM
        if score >= 5:
            return RiskLevel.LOW
        return RiskLevel.NONE
        
    def requires_mfa(self, identity_id: str) -> bool:
        return self.get_risk_level(identity_id) >= RiskLevel.MEDIUM


# ============================================================================
# APPLICATION PROXY & SSO
# ============================================================================

class ServicePrincipal:
    """Service principal for applications"""
    
    def __init__(self, app_id: str, app_name: str):
        self.app_id = app_id
        self.app_name = app_name
        self.enabled = True
        self.required_scopes: List[str] = []
        self.owners: Set[str] = set()
        self.redirect_uris: List[str] = []
        
    def add_scope(self, scope: str):
        self.required_scopes.append(scope)
        
    def add_owner(self, owner_id: str):
        self.owners.add(owner_id)
        

class ApplicationProxy:
    """Application registry and SSO management"""
    
    def __init__(self):
        self.applications: Dict[str, ServicePrincipal] = {}
        self.consents: Dict[str, Dict] = {}  # (user_id, app_id) -> consent
        self.token_cache: Dict[str, Tuple[str, datetime]] = {}  # access_token -> (app_id, expires)
        
    def register_app(self, app_id: str, app_name: str) -> ServicePrincipal:
        app = ServicePrincipal(app_id, app_name)
        self.applications[app_id] = app
        return app
        
    def consent_to_app(self, user_id: str, app_id: str, scopes: List[str]):
        key = f"{user_id}:{app_id}"
        self.consents[key] = {
            'scopes': scopes,
            'granted_at': datetime.now()
        }
        
    def get_consent(self, user_id: str, app_id: str) -> Optional[List[str]]:
        key = f"{user_id}:{app_id}"
        consent = self.consents.get(key)
        return consent.get('scopes') if consent else None


# ============================================================================
# B2B COLLABORATION (Coming in v2)
# ============================================================================

# ============================================================================
# IDENTITY GOVERNANCE - Lifecycle Management
# ============================================================================

class IdentityLifecycle:
    """Identity lifecycle management"""
    
    def __init__(self):
        self.states: Dict[str, str] = {}  # identity_id -> state
        self.transitions: Dict[str, List[Dict]] = {}
        
    def transition(self, identity_id: str, from_state: str, to_state: str, reason: str) -> bool:
        """Transition identity state"""
        if self.states.get(identity_id) != from_state:
            return False
            
        self.states[identity_id] = to_state
        
        if identity_id not in self.transitions:
            self.transitions[identity_id] = []
        self.transitions[identity_id].append({
            'from': from_state,
            'to': to_state,
            'reason': reason,
            'timestamp': datetime.now()
        })
        return True
        
    def get_state(self, identity_id: str) -> str:
        return self.states.get(identity_id, "provisioned")
        
    def get_history(self, identity_id: str) -> List[Dict]:
        return self.transitions.get(identity_id, [])


# ============================================================================
# ACCESS REVIEW
# ============================================================================

class AccessReview:
    """Periodic access certification reviews"""
    
    def __init__(self):
        self.reviews: Dict[str, Dict] = {}
        
    def create_review(self, review_id: str, resource: str, reviewers: List[str], 
                   due_date: datetime) -> Dict:
        review = {
            'review_id': review_id,
            'resource': resource,
            'reviewers': reviewers,
            'due_date': due_date,
            'status': 'pending',
            'decisions': {},
            'created_at': datetime.now()
        }
        self.reviews[review_id] = review
        return review
        
    def submit_decision(self, review_id: str, reviewer_id: str, principal_id: str, 
                   decision: str, justification: str = "") -> bool:
        review = self.reviews.get(review_id)
        if not review or review['status'] != 'pending':
            return False
        if reviewer_id not in review['reviewers']:
            return False
            
        review['decisions'][principal_id] = {
            'decision': decision,  # approve, deny, not_reviewed
            'justification': justification,
            'reviewed_by': reviewer_id,
            'reviewed_at': datetime.now()
        }
        return True
        
    def complete_review(self, review_id: str) -> Dict:
        review = self.reviews.get(review_id)
        if not review:
            return {}
            
        decisions = review.get('decisions', {})
        review['status'] = 'completed'
        review['completed_at'] = datetime.now()
        
        # Summary
        review['summary'] = {
            'total': len(decisions),
            'approved': sum(1 for d in decisions.values() if d['decision'] == 'approve'),
            'denied': sum(1 for d in decisions.values() if d['decision'] == 'deny'),
            'not_reviewed': sum(1 for d in decisions.values() if d['decision'] == 'not_reviewed')
        }
        return review


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditLogger:
    """Comprehensive audit logging"""
    
    def __init__(self, config: Dict = None):
        self.config = config
        self.events: List[Dict] = []
        self.retention_days = (config or {}).get('retention_days', 90)
        
    def log(self, category: str, operation: str, identity_id: str, 
          resource: str = None, result: str = "success", details: Dict = None):
        event = {
            'category': category,  # authentication, authorization, identity, application
            'operation': operation,
            'identity_id': identity_id,
            'resource': resource,
            'result': result,
            'details': details or {},
            'timestamp': datetime.now(),
            'correlation_id': uuid.uuid4().hex
        }
        self.events.append(event)
        
        # Cleanup old events
        self._cleanup()
        
    def _cleanup(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        self.events = [e for e in self.events if e['timestamp'] > cutoff]
        
    def query(self, filters: Dict = None, limit: int = 100) -> List[Dict]:
        results = self.events
        if filters:
            if 'identity_id' in filters:
                results = [e for e in results if e['identity_id'] == filters['identity_id']]
            if 'category' in filters:
                results = [e for e in results if e['category'] == filters['category']]
            if 'result' in filters:
                results = [e for e in results if e['result'] == filters['result']]
        return results[-limit:]


# ============================================================================
# MAIN ENTRA CLASS
# ============================================================================

class EntraID:
    """Entra - Agent Identity & Governance"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Core components
        self.idp = IdentityProvider(config)
        self.ca = ConditionalAccessEngine()
        self.pim = PIMEngine()
        self.risk = RiskDetector()
        self.apps = ApplicationProxy()
        self.lifecycle = IdentityLifecycle()
        self.audit = AuditLogger(config)
        self.access_reviews = AccessReview()
        
    def bootstrap(self):
        """Bootstrap with default configuration"""
        # Register default applications
        self.apps.register_app("kernel_api", "Agent Kernel API")
        self.apps.register_app("kernel_ui", "Agent Kernel Dashboard")
        
        self.audit.log("system", "bootstrap", "system", result="success")


__all__ = [
    'EntraID',
    'IdentityProvider', 
    'ConditionalAccessEngine', 'ConditionalAccessPolicy',
    'PIMEngine', 'PIMAssignment',
    'RiskDetector', 'RiskLevel',
    'ApplicationProxy', 'ServicePrincipal',
    'IdentityLifecycle',
    'AccessReview',
    'AuditLogger'
]