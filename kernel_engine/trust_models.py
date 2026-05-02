"""
Trust Models and Logic - Advanced Trust Scoring

Sophisticated trust scoring models and reasoning:
- Trust Scoring Algorithms
- Trust Propagation
- Trust Verification
- Trust Queries
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Trust Scoring Models
# ============================================================

class TrustScoreModelType:
    WEIGHTED_SUM = "weighted_sum"
    BAYESIAN = "bayesian"
    EIGENVECTOR = "eigenvector"
    MACHINE_LEARNING = "machine_learning"
    FUZZY = "fuzzy"


@dataclass
class TrustScoreModel:
    """Trust scoring model"""
    id: str
    
    model_type: str = "weighted_sum"
    
    weights: Dict = field(default_factory=lambda: {
        "competence": 0.3,
        "benevolence": 0.3,
        "integrity": 0.25,
        "predictability": 0.15,
    })
    
    thresholds: Dict = field(default_factory=lambda: {
        "trusted": 0.7,
        "neutral": 0.4,
        "untrusted": 0.2,
    })
    
    def calculate(self, competence: float, benevolence: float, 
                integrity: float, predictability: float) -> float:
        """Calculate trust score"""
        score = (
            competence * self.weights["competence"] +
            benevolence * self.weights["benevolence"] +
            integrity * self.weights["integrity"] +
            predictability * self.weights["predictability"]
        )
        return min(1.0, max(0.0, score))
    
    def classify(self, score: float) -> str:
        """Classify trust level"""
        if score >= self.thresholds["trusted"]:
            return "trusted"
        elif score >= self.thresholds["neutral"]:
            return "neutral"
        else:
            return "untrusted"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "model_type": self.model_type,
            "weights": self.weights,
            "thresholds": self.thresholds,
        }


# ============================================================
# Trust Calculation
# ============================================================

@dataclass
class TrustCalculationInput:
    """Trust calculation input"""
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    recommendations: List[Dict] = field(default_factory=list)
    credentials: List[Dict] = field(default_factory=list)
    context: Dict = field(default_factory=dict)


@dataclass
class TrustCalculationResult:
    """Trust calculation result"""
    score: float = 0
    
    component_scores: Dict = field(default_factory=dict)
    confidence: float = 0
    
    factors: List[Dict] = field(default_factory=list)
    
    verdict: str = "neutral"
    reasoning: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "confidence": self.confidence,
            "verdict": self.verdict,
            "reasoning": self.reasoning,
        }


# ============================================================
# Trust Propagation
# ============================================================

@dataclass
class TrustPath:
    """Trust path"""
    path: List[str] = field(default_factory=list)
    length: int = 0
    trust_values: Dict[str, float] = field(default_factory=dict)
    aggregate_score: Optional[float] = None
    confidence: float = 0
    
    def calculate_aggregate(self):
        """Calculate aggregate score"""
        if not self.trust_values:
            self.aggregate_score = 0
            return
        
        # Multiply trust values along path
        result = 1.0
        for trust in self.trust_values.values():
            result *= trust
        
        # Normalize by path length
        if self.length > 0:
            result = result ** (1.0 / self.length)
        
        self.aggregate_score = result
        return result


@dataclass
class TrustPropagationResult:
    """Trust propagation result"""
    paths: List[TrustPath] = field(default_factory=list)
    best_path: Optional[TrustPath] = None
    propagated_trust: float = 0
    confidence: float = 0
    method: str = "direct"
    
    def find_paths(self, graph: Dict, source: str, target: str, 
                  max_depth: int = 3):
        """Find trust paths"""
        def dfs(current: str, path: List[str], visited: Set):
            if current == target:
                trust_path = TrustPath(
                    path=path[:],
                    length=len(path) - 1,
                )
                self.paths.append(trust_path)
                return
            
            if len(path) > max_depth:
                return
            
            visited.add(current)
            
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor], visited.copy())
        
        dfs(source, [source], set())
        
        # Calculate aggregates
        for p in self.paths:
            p.calculate_aggregate()
        
        # Find best path
        if self.paths:
            self.paths.sort(key=lambda x: x.aggregate_score or 0, reverse=True)
            self.best_path = self.paths[0]
            self.propagated_trust = self.best_path.aggregate_score or 0
    
    def to_dict(self) -> Dict:
        return {
            "path_count": len(self.paths),
            "propagated_trust": self.propagated_trust,
            "method": self.method,
        }


# ============================================================
# Trust Verification
# ============================================================

@dataclass
class TrustVerification:
    """Trust verification"""
    claim: str
    claimant_id: str
    
    evidence: List[str] = field(default_factory=list)
    
    is_verified: bool = False
    verification_level: str = "none"
    
    confidence: float = 0
    
    methods: List[str] = field(default_factory=list)
    
    def verify(self) -> bool:
        """Verify claim"""
        if len(self.evidence) >= 3:
            self.is_verified = True
            self.verification_level = "high"
            self.confidence = 0.9
        elif len(self.evidence) >= 1:
            self.is_verified = True
            self.verification_level = "basic"
            self.confidence = 0.5
        else:
            self.is_verified = False
            self.verification_level = "none"
            self.confidence = 0.1
        
        self.methods.append("evidence_check")
        return self.is_verified
    
    def to_dict(self) -> Dict:
        return {
            "claim": self.claim,
            "claimant_id": self.claimant_id,
            "is_verified": self.is_verified,
            "verification_level": self.verification_level,
            "confidence": self.confidence,
        }


@dataclass
class TrustAttestation:
    """Trust attestation"""
    id: str
    
    attestor_id: str
    subject_id: str
    
    claim: str
    
    signature: str = ""
    is_verified: bool = False
    
    issued_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = ""
    
    def verify(self) -> bool:
        """Verify attestation"""
        # Simplified - would verify signature
        self.is_verified = True
        return True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "attestor_id": self.attestor_id,
            "subject_id": self.subject_id,
            "claim": self.claim,
            "is_verified": self.is_verified,
        }


# ============================================================
# Trust Queries
# ============================================================

class TrustQueryType:
    SCORE = "score"
    PATHS = "paths"
    RECOMMENDATION = "recommendation"
    VERIFICATION = "verification"


@dataclass
class TrustQuery:
    """Trust query"""
    query_type: str = "score"
    
    trustor_id: str = ""
    trustee_id: str = ""
    
    context: Dict = field(default_factory=dict)
    
    include_history: bool = False
    include_paths: bool = False
    max_depth: int = 3
    
    def to_dict(self) -> Dict:
        return {
            "query_type": self.query_type,
            "trustor_id": self.trustor_id,
            "trustee_id": self.trustee_id,
        }


@dataclass
class TrustRecommendation:
    """Trust recommendation"""
    for_id: str = ""
    
    recommendations: List[Dict] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)
    method: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "for_id": self.for_id,
            "recommendations": self.recommendations,
            "method": self.method,
        }


# ============================================================
# Trust Logic
# ============================================================

@dataclass
class TrustRule:
    """Trust rule"""
    id: str
    
    condition: str = ""
    action: str = "increase"  # increase, decrease, verify, propagate
    
    parameters: Dict = field(default_factory=dict)
    priority: int = 5
    
    is_active: bool = True
    
    def evaluate(self, context: Dict) -> bool:
        """Evaluate rule"""
        # Simplified condition evaluation
        return True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority,
            "is_active": self.is_active,
        }


@dataclass
class TrustPolicy:
    """Trust policy"""
    id: str
    
    rules: List[TrustRule] = field(default_factory=list)
    
    default_score: float = 0.5
    min_score: float = 0
    max_score: float = 1
    
    is_active: bool = True
    
    def add_rule(self, rule: TrustRule):
        """Add rule"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
    
    def apply(self, score: float, context: Dict) -> float:
        """Apply policy"""
        new_score = score
        
        for rule in self.rules:
            if not rule.is_active:
                continue
            
            if rule.evaluate(context):
                if rule.action == "increase":
                    new_score += rule.parameters.get("delta", 0.1)
                elif rule.action == "decrease":
                    new_score -= rule.parameters.get("delta", 0.1)
        
        return min(self.max_score, max(self.min_score, new_score))
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "rule_count": len(self.rules),
            "default_score": self.default_score,
            "is_active": self.is_active,
        }


# ============================================================
# Factory
# ============================================================

def create_trust_model(model_type: str = "weighted_sum") -> TrustScoreModel:
    """Create trust model"""
    return TrustScoreModel(
        id=str(uuid.uuid4()),
        model_type=model_type,
    )


def create_trust_policy() -> TrustPolicy:
    """Create trust policy"""
    return TrustPolicy(
        id=str(uuid.uuid4()),
    )


__all__ = [
    'TrustScoreModelType', 'TrustScoreModel',
    'TrustCalculationInput', 'TrustCalculationResult',
    'TrustPath', 'TrustPropagationResult',
    'TrustVerification', 'TrustAttestation',
    'TrustQueryType', 'TrustQuery', 'TrustRecommendation',
    'TrustRule', 'TrustPolicy',
    'create_trust_model', 'create_trust_policy'
]