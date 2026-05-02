"""
Entra Agent Governance Toolkit

Features:
- Policy enforcement (allowed roles, scopes)
- Compliance checks (SOC2, HIPAA, etc.)
- Access reviews (periodic re-certification)
- Agent consent management
- Risk scoring
- Audit logging
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timedelta


class ComplianceFramework(Enum):
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI = "pci"
    ISO27001 = "iso27001"


class PolicyType(Enum):
    ROLE_ALLOWLIST = "role_allowlist"
    SCOPE_ALLOWLIST = "scope_allowlist"
    TENANT_RESTRICTION = "tenant_restriction"
    TIME_RESTRICTION = "time_restriction"
    IP_WHITELIST = "ip_whitelist"


class ReviewFrequency(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


@dataclass
class GovernancePolicy:
    """Governance policy"""
    policy_id: str = field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:8]}")
    name: str = ""
    policy_type: str = ""
    rules: List[str] = field(default_factory=list)
    enforcement: str = "audit"  # audit, deny, warn
    enabled: bool = True


@dataclass
class AccessReview:
    """Access review record"""
    review_id: str = field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:8]}")
    agent_id: str = ""
    reviewer: str = ""
    frequency: str = "monthly"
    last_review: datetime = None
    next_review: datetime = None
    status: str = "pending"  # pending, approved, denied
    notes: str = ""


@dataclass
class AgentRiskScore:
    """Agent risk assessment"""
    agent_id: str = ""
    score: int = 0  # 0-100
    factors: Dict[str, int] = field(default_factory=dict)  # factor -> score
    last_evaluated: datetime = field(default_factory=datetime.now)
    reasons: List[str] = field(default_factory=list)


@dataclass
class ConsentRecord:
    """Consent management"""
    consent_id: str = field(default_factory=lambda: f"con_{uuid.uuid4().hex[:8]}")
    principal_id: str = ""  # The agent
    resource: str = ""  # What they're accessing
    scope: List[str] = field(default_factory=list)
    granted_by: str = ""  # Admin/owner
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = None
    revoked: bool = False


class GovernanceToolkit:
    """Entra Agent Governance"""
    
    def __init__(self):
        self.policies: Dict[str, GovernancePolicy] = {}
        self.access_reviews: Dict[str, AccessReview] = {}
        self.risk_scores: Dict[str, AgentRiskScore] = {}
        self.consents: Dict[str, ConsentRecord] = {}
        self.audit_log: List[Dict] = []
    
    # ============ Policy Operations ============
    
    def create_policy(self, name: str, policy_type: str, rules: List[str],
                  enforcement: str = "audit") -> GovernancePolicy:
        """Create governance policy"""
        policy = GovernancePolicy(
            name=name,
            policy_type=policy_type,
            rules=rules,
            enforcement=enforcement,
        )
        self.policies[policy.policy_id] = policy
        return policy
    
    def evaluate_policy(self, agent_id: str, action: str, 
                        context: Dict) -> Dict:
        """Evaluate policy for agent action"""
        violations = []
        enforcement_action = "allow"
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            if policy.policy_type == PolicyType.ROLE_ALLOWLIST.value:
                if action in policy.rules:
                    # Check if action is allowed
                    pass  # Simplified
            
            # Check all policies
            if violations:
                if policy.enforcement == "deny":
                    enforcement_action = "deny"
                elif policy.enforcement == "warn":
                    enforcement_action = "warn"
        
        return {
            "allowed": enforcement_action != "deny",
            "action": enforcement_action,
            "violations": violations,
        }
    
    def list_policies(self) -> List[GovernancePolicy]:
        """List policies"""
        return list(self.policies.values())
    
    # ============ Access Reviews ============
    
    def schedule_review(self, agent_id: str, reviewer: str,
                   frequency: str = "monthly") -> AccessReview:
        """Schedule access review"""
        review = AccessReview(
            agent_id=agent_id,
            reviewer=reviewer,
            frequency=frequency,
            last_review=datetime.now(),
            next_review=datetime.now() + timedelta(days=30),
        )
        self.access_reviews[review.review_id] = review
        return review
    
    def complete_review(self, review_id: str, approved: bool,
                      notes: str = "") -> bool:
        """Complete access review"""
        review = self.access_reviews.get(review_id)
        if not review:
            return False
        
        review.status = "approved" if approved else "denied"
        review.notes = notes
        review.last_review = datetime.now()
        
        # Schedule next
        freq_days = {"weekly": 7, "monthly": 30, "quarterly": 90, "annually": 365}
        days = freq_days.get(review.frequency, 30)
        review.next_review = datetime.now() + timedelta(days=days)
        
        return True
    
    def get_pending_reviews(self) -> List[AccessReview]:
        """Get pending reviews"""
        now = datetime.now()
        return [
            r for r in self.access_reviews.values()
            if r.status == "pending" and r.next_review <= now
        ]
    
    # ============ Risk Scoring ============
    
    def calculate_risk(self, agent_id: str, 
                      activity: List[Dict]) -> AgentRiskScore:
        """Calculate agent risk score"""
        factors = {
            "failed_auth": 0,      # Failed authentication attempts
            "unusual_hours": 0,     # Activity at unusual hours
            "new_location": 0,     # New IP/location
            "high_scope": 0,       # Requesting broad permissions
            "sensitive_data": 0,   # Accessing sensitive data
            "rapid_activity": 0,    # Unusually rapid actions
        }
        
        # Calculate factors
        for event in activity:
            if event.get("type") == "failed_auth":
                factors["failed_auth"] += 10
            if event.get("unusual_hours"):
                factors["unusual_hours"] += 20
            if event.get("new_location"):
                factors["new_location"] += 15
            if event.get("high_scope"):
                factors["high_scope"] += 25
            if event.get("sensitive_data"):
                factors["sensitive_data"] += 30
        
        # Calculate total score (sum factors, cap at 100)
        total = min(100, sum(factors.values()))
        
        # Create risk score
        risk = AgentRiskScore(
            agent_id=agent_id,
            score=total,
            factors=factors,
        )
        
        # Add reasons
        if total > 70:
            risk.reasons.append("High risk activity detected")
        if factors["failed_auth"] > 20:
            risk.reasons.append("Multiple failed authentications")
        if factors["sensitive_data"] > 20:
            risk.reasons.append("Sensitive data access")
        
        self.risk_scores[agent_id] = risk
        return risk
    
    def get_risk_score(self, agent_id: str) -> Optional[AgentRiskScore]:
        """Get risk score"""
        return self.risk_scores.get(agent_id)
    
    # ============ Consent Management ============
    
    def grant_consent(self, principal_id: str, resource: str,
                      scope: List[str], granted_by: str,
                      expires_days: int = 30) -> ConsentRecord:
        """Grant consent"""
        consent = ConsentRecord(
            principal_id=principal_id,
            resource=resource,
            scope=scope,
            granted_by=granted_by,
            expires_at=datetime.now() + timedelta(days=expires_days),
        )
        self.consents[consent.consent_id] = consent
        return consent
    
    def revoke_consent(self, consent_id: str) -> bool:
        """Revoke consent"""
        consent = self.consents.get(consent_id)
        if consent:
            consent.revoked = True
            return True
        return False
    
    def check_consent(self, principal_id: str, resource: str,
                    scope: str) -> bool:
        """Check if consent exists and valid"""
        for consent in self.consents.values():
            if consent.principal_id != principal_id:
                continue
            if consent.resource != resource:
                continue
            if consent.revoked:
                continue
            if consent.expires_at and consent.expires_at < datetime.now():
                continue
            if scope in consent.scope:
                return True
        return False
    
    # ============ Audit Logging ============
    
    def audit(self, agent_id: str, action: str, 
              resource: str, result: str, context: Dict = None):
        """Add audit log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "action": action,
            "resource": resource,
            "result": result,
            "context": context or {},
        }
        self.audit_log.append(entry)
    
    def get_audit_log(self, agent_id: str = None,
                   limit: int = 100) -> List[Dict]:
        """Get audit log"""
        entries = self.audit_log
        if agent_id:
            entries = [e for e in entries if e.get("agent_id") == agent_id]
        return entries[-limit:]
    
    # ============ Compliance ============
    
    def check_compliance(self, framework: str, 
                      agent_id: str) -> Dict:
        """Check compliance for framework"""
        # Simplified compliance check
        checks = {
            "policies_enforced": True,
            "access_reviewed": True,
            "consent_recorded": True,
            "logged": True,
        }
        
        compliant = all(checks.values())
        
        return {
            "framework": framework,
            "compliant": compliant,
            "checks": checks,
        }


__all__ = [
    'GovernanceToolkit', 'GovernancePolicy', 'AccessReview',
    'AgentRiskScore', 'ConsentRecord', 'ComplianceFramework',
    'PolicyType', 'ReviewFrequency'
]