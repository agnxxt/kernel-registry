"""
Probabilistic Reasoning for Awareness

Bayesian belief networks, causal inference, reasoning under uncertainty:
- Belief Networks
- Causal Inference
- Bayesian Reasoning
- Uncertainty Quantification
- Probabilistic Programming
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import math
import uuid


# ============================================================
# Belief Network
# ============================================================

@dataclass
class RandomVariable:
    """Random variable"""
    id: str
    name: str
    
    domain_type: str = "boolean"  # boolean, discrete, continuous
    domain_values: Optional[List[str]] = None
    
    distribution_type: str = "bernoulli"
    parameters: Dict[str, float] = field(default_factory=dict)
    
    probability: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "domain_type": self.domain_type,
            "distribution_type": self.distribution_type,
            "probability": self.probability,
        }


@dataclass
class CausalEdge:
    """Causal edge"""
    from_var: str  # Parent
    to_var: str    # Child
    
    cpt: Dict[str, float] = field(default_factory=dict)  # Conditional probability table
    edge_type: str = "causal"
    
    def to_dict(self) -> Dict:
        return {
            "from": self.from_var,
            "to": self.to_var,
            "cpt": self.cpt,
            "edge_type": self.edge_type,
        }


@dataclass
class BeliefNetwork:
    """Bayesian Belief Network"""
    id: str
    name: str
    
    variables: List[RandomVariable] = field(default_factory=list)
    edges: List[CausalEdge] = field(default_factory=list)
    
    structure: str = "dag"
    evidence: Dict[str, Any] = field(default_factory=dict)
    beliefs: Dict[str, float] = field(default_factory=dict)
    
    def marginal(self, var_id: str) -> float:
        """Get marginal probability"""
        return self.beliefs.get(var_id, 0.5)
    
    def update_beliefs(self, new_beliefs: Dict[str, float]):
        """Update beliefs"""
        self.beliefs = new_beliefs
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "structure": self.structure,
            "evidence": self.evidence,
            "beliefs": self.beliefs,
        }


# ============================================================
# Causal Inference
# ============================================================

@dataclass
class CausalRelationship:
    """Causal relationship"""
    id: str
    cause: str
    effect: str
    
    causal_effect: float = 0  # ATE
    causal_effect_variance: Optional[float] = None
    
    mechanism: str = ""
    is_valid: Optional[bool] = None
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "cause": self.cause,
            "effect": self.effect,
            "causal_effect": self.causal_effect,
            "is_valid": self.is_valid,
            "confidence": self.confidence,
        }


@dataclass
class CausalGraph:
    """Causal DAG"""
    id: str
    nodes: List[str] = field(default_factory=list)
    edges: List[CausalEdge] = field(default_factory=list)
    
    confounders: List[str] = field(default_factory=list)
    identified_effects: Dict[str, float] = field(default_factory=dict)
    
    def get_backdoor_paths(self, x: str, y: str) -> List[List[str]]:
        """Find backdoor paths"""
        # Would need graph traversal
        return []
    
    def identify_effect(self, treatment: str, outcome: str) -> Optional[float]:
        """Identify causal effect using do-calculus"""
        return self.identified_effects.get(f"{treatment}->{outcome}")
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nodes": self.nodes,
            "confounders": self.confounders,
            "identified_effects": self.identified_effects,
        }


@dataclass
class Intervention:
    """Intervention (do-calculus)"""
    id: str
    do_variable: str
    do_value: Any = None
    
    resulting_graph: Optional[str] = None
    identified_effect: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "do_variable": self.do_variable,
            "do_value": self.do_value,
            "identified_effect": self.identified_effect,
        }


# ============================================================
# Bayesian Reasoning
# ============================================================

@dataclass
class Hypothesis:
    """Hypothesis"""
    id: str
    name: str
    description: str = ""
    
    prior: float = 0.5  # P(H)
    likelihood: float = 0.5  # P(E|H)
    posterior: Optional[float] = None  # P(H|E)
    
    def update(self, evidence_likelihood: float):
        """Bayesian update: P(H|E) = P(E|H) * P(H) / P(E)"""
        self.likelihood = evidence_likelihood
        # P(E) = P(E|H) * P(H) + P(E|~H) * P(~H)
        p_e = self.likelihood * self.prior + (1 - self.likelihood) * (1 - self.prior)
        self.posterior = (self.likelihood * self.prior) / p_e if p_e > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "prior": self.prior,
            "posterior": self.posterior,
        }


@dataclass
class HypothesisTest:
    """Test multiple hypotheses"""
    id: str
    hypotheses: List[Hypothesis] = field(default_factory=list)
    
    def update_all(self, evidence_likelihoods: Dict[str, float]):
        """Update all hypotheses"""
        for h in self.hypotheses:
            h.update(evidence_likelihoods.get(h.id, 0.5))
    
    def best_hypothesis(self) -> Optional[Hypothesis]:
        """Get hypothesis with highest posterior"""
        if not self.hypotheses:
            return None
        return max(self.hypotheses, key=lambda h: h.posterior or h.prior)
    
    def bayes_factors(self) -> Dict[str, float]:
        """Bayes factors vs null"""
        best = self.best_hypothesis()
        if not best:
            return {}
        
        bf = {}
        for h in self.hypotheses:
            if h.id != best.id:
                # BF = P(E|H1) / P(E|H2)
                p_e_h1 = best.likelihood or best.prior
                p_e_h2 = h.likelihood or h.prior
                bf[h.id] = p_e_h1 / p_e_h2 if p_e_h2 > 0 else 0
        
        return bf
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "best": self.best_hypothesis().to_dict() if self.best_hypothesis() else None,
        }


# ============================================================
# Uncertainty Quantification
# ============================================================

class UncertaintyType:
    ALEATORIC = "aleatoric"
    EPISTEMIC = "epistemic"
    MODEL = "model"
    DECISION = "decision"


@dataclass
class Uncertainty:
    """Uncertainty representation"""
    id: str
    uncertainty_type: str  # aleatoric, epistemic, model, decision
    
    magnitude: float = 0  # 0 = certain, 1 = uncertain
    
    source: str = ""
    description: str = ""
    
    variance: Optional[float] = None
    entropy: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.uncertainty_type,
            "magnitude": self.magnitude,
            "variance": self.variance,
            "entropy": self.entropy,
        }


@dataclass
class EpistemicUncertainty:
    """Epistemic (reducible) uncertainty"""
    variable: str
    
    current_belief: float = 0.5
    reduction_if_known: float = 0
    
    voi: Optional[float] = None  # Value of Information
    vos: Optional[float] = None  # Value of Selection
    
    recommended_observations: List[str] = field(default_factory=list)
    
    def calculate_voi(self, posterior_variance: float) -> float:
        """Value of Information = reduction in expected loss"""
        prior_variance = self.current_belief * (1 - self.current_belief)
        self.voi = prior_variance - posterior_variance
        return self.voi
    
    def to_dict(self) -> Dict:
        return {
            "variable": self.variable,
            "current_belief": self.current_belief,
            "voi": self.voi,
            "reduction_if_known": self.reduction_if_known,
        }


@dataclass
class AleatoricUncertainty:
    """Aleatoric (irreducible) uncertainty"""
    variable: str
    
    inherent_variance: float = 0.25
    
    distribution: str = "bernoulli"
    parameters: Dict[str, float] = field(default_factory=dict)
    
    best_prediction: Optional[float] = None
    prediction_interval: Optional[tuple] = None
    
    def to_dict(self) -> Dict:
        return {
            "variable": self.variable,
            "inherent_variance": self.inherent_variance,
            "distribution": self.distribution,
            "best_prediction": self.best_prediction,
        }


# ============================================================
# Probabilistic Programming
# ============================================================

@dataclass
class GenerativeModel:
    """Generative model p(latent, observed)"""
    id: str
    name: str
    
    latent_variables: List[str] = field(default_factory=list)
    observed_variables: List[str] = field(default_factory=list)
    
    p_latent: str = "normal"  # Distribution over latent
    p_observed_given_latent: str = "normal"  # Distribution over observed
    
    parameters: Dict[str, float] = field(default_factory=dict)
    posterior: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "latent_variables": self.latent_variables,
            "observed_variables": self.observed_variables,
        }


@dataclass
class SamplingModel:
    """Sampling model for inference"""
    id: str
    
    distribution: str = "normal"
    parameters: Dict[str, float] = field(default_factory=dict)
    
    proposal: str = "normal"
    proposal_parameters: Dict[str, float] = field(default_factory=dict)
    
    sampler: str = "metropolis_hastings"
    samples: List[Dict[str, float]] = field(default_factory=list)
    sample_count: int = 1000
    
    def sample(self) -> Dict[str, float]:
        """Generate sample"""
        # Simplified - would need full sampler
        return {k: v for k, v in self.parameters.items()}
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "distribution": self.distribution,
            "sampler": self.sampler,
            "sample_count": self.sample_count,
        }


@dataclass
class VariationalModel:
    """Variational inference model"""
    id: str
    
    true_posterior: str = "normal"
    variational_family: str = "mean_field"
    variational_params: Dict[str, float] = field(default_factory=dict)
    
    elbo: Optional[float] = None
    kl_divergence: Optional[float] = None
    
    iterations: int = 0
    converged: bool = False
    
    def optimize(self, max_iters: int = 100) -> float:
        """Optimize variational parameters"""
        for _ in range(max_iters):
            # Would need full optimization
            self.iterations += 1
        
        self.converged = True
        return self.elbo or 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "variational_family": self.variational_family,
            "elbo": self.elbo,
            "converged": self.converged,
        }


# ============================================================
# Factory
# ============================================================

def create_belief_network(id: str, name: str, variables: List[str]) -> BeliefNetwork:
    """Create belief network"""
    return BeliefNetwork(
        id=id,
        name=name,
        variables=[RandomVariable(id=v, name=v) for v in variables],
    )


def create_causal_graph(id: str, nodes: List[str]) -> CausalGraph:
    """Create causal graph"""
    return CausalGraph(id=id, nodes=nodes)


__all__ = [
    'RandomVariable', 'CausalEdge', 'BeliefNetwork',
    'CausalRelationship', 'CausalGraph', 'Intervention',
    'Hypothesis', 'HypothesisTest',
    'Uncertainty', 'UncertaintyType',
    'EpistemicUncertainty', 'AleatoricUncertainty',
    'GenerativeModel', 'SamplingModel', 'VariationalModel',
    'create_belief_network', 'create_causal_graph'
]