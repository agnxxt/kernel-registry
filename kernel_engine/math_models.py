"""
Mathematical Models for Agent Intelligence

Models included:
- Utility Theory (preferences, utilities)
- Probability Models (bayesian, distributions)
- Decision Theory (MDP, POMDP)
- Game Theory (strategic interactions)
- Information Theory (entropy, mutual information)
- Optimization (gradient, genetic)
- Control Theory (feedback, stability)
- Learning Theory (VC dimension, bounds)
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import math
import uuid


# ============================================================
# Utility Theory
# ============================================================

@dataclass
class Utility:
    """Utility function over outcomes"""
    id: str
    utilities: Dict[str, float] = field(default_factory=dict)
    
    # Risk preferences
    risk_attitude: str = "risk_neutral"  # risk_seeking, risk_neutral, risk_averse
    risk_coefficient: float = 0
    
    # Multi-attribute weights
    attribute_weights: Dict[str, float] = field(default_factory=dict)
    
    def get_utility(self, outcome: str) -> float:
        """Get utility of outcome"""
        return self.utilities.get(outcome, 0)
    
    def expected_utility(self, outcomes: List[str], probs: List[float]) -> float:
        """Expected utility E[U(x)]"""
        return sum(self.get_utility(o) * p for o, p in zip(outcomes, probs))
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "utilities": self.utilities,
            "risk_attitude": self.risk_attitude,
            "risk_coefficient": self.risk_coefficient,
            "attribute_weights": self.attribute_weights,
        }


@dataclass
class Preference:
    """Preference ordering"""
    id: str
    strict_preferences: List[tuple] = field(default_factory=list)  # [(A, B), ...] means A > B
    indifferences: List[tuple] = field(default_factory=list)   # [(A, B), ...] means A = B
    
    def add_strict(self, a: str, b: str):
        """Add strict preference A > B"""
        self.strict_preferences.append((a, b))
    
    def add_indifference(self, a: str, b: str):
        """Add indifference A = B"""
        self.indifferences.append((a, b))
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "strict_preferences": self.strict_preferences,
            "indifferences": self.indifferences,
        }


# ============================================================
# Probability Models
# ============================================================

@dataclass
class ProbabilityDistribution:
    """Probability distribution"""
    id: str
    probabilities: Dict[str, float] = field(default_factory=dict)
    distribution_type: str = "categorical"
    parameters: Dict[str, float] = field(default_factory=dict)
    
    def mean(self) -> float:
        """Expected value"""
        return sum(float(k) * v for k, v in self.probabilities.items())
    
    def variance(self) -> float:
        """Variance"""
        m = self.mean()
        return sum((float(k) - m) ** 2 * v for k, v in self.probabilities.items())
    
    def entropy(self) -> float:
        """Entropy H(X) = -sum(P(x) * log(P(x))"""
        h = 0.0
        for p in self.probabilities.values():
            if p > 0:
                h -= p * math.log(p)
        return h
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "probabilities": self.probabilities,
            "distribution_type": self.distribution_type,
            "mean": self.mean(),
            "variance": self.variance(),
            "entropy": self.entropy(),
        }


@dataclass
class BayesianUpdate:
    """Bayesian update"""
    prior: ProbabilityDistribution
    likelihood: Dict[str, float]  # P(D|h)
    evidence: float = 0
    
    posterior: Optional[ProbabilityDistribution] = None
    bayes_factor: float = 1
    
    def update(self) -> ProbabilityDistribution:
        """Bayes rule: P(H|D) = P(D|H) * P(H) / P(D)"""
        evidence = 0
        for h, p_h in self.prior.probabilities.items():
            p_d_h = self.likelihood.get(h, 0)
            evidence += p_d_h * p_h
        
        self.evidence = evidence
        
        # Calculate posterior
        posterior_probs = {}
        for h, p_h in self.prior.probabilities.items():
            p_d_h = self.likelihood.get(h, 0)
            posterior_probs[h] = (p_d_h * p_h) / evidence if evidence > 0 else 0
        
        self.posterior = ProbabilityDistribution(
            id=str(uuid.uuid4()),
            probabilities=posterior_probs,
            distribution_type=self.prior.distribution_type,
        )
        
        # Bayes factor (prior odds to posterior odds)
        self.bayes_factor = evidence
        return self.posterior
    
    def to_dict(self) -> Dict:
        return {
            "prior": self.prior.to_dict() if self.prior else None,
            "evidence": self.evidence,
            "bayes_factor": self.bayes_factor,
            "posterior": self.posterior.to_dict() if self.posterior else None,
        }


# ============================================================
# Decision Theory (MDP/POMDP)
# ============================================================

@dataclass
class MDPState:
    """MDP state"""
    id: str
    value: float = 0  # V(s)
    reward: float = 0


@dataclass
class MDPAction:
    """MDP action"""
    id: str
    transitions: Dict[str, Dict[str, float]] = field(default_factory=dict)  # s -> s' -> P
    q_value: float = 0  # Q(s, a)
    
    def expected_value(self, state_values: Dict[str, float], gamma: float) -> float:
        """Expected value of action"""
        ev = self.reward if hasattr(self, 'reward') else 0
        for s_next, p in self.transitions.get("", {}).items():
            ev += p * state_values.get(s_next, 0) * gamma
        return ev


@dataclass
class MDP:
    """Markov Decision Process"""
    id: str
    discount_factor: float = 0.9  # gamma
    
    states: List[MDPState] = field(default_factory=list)
    actions: Dict[str, List[MDPAction]] = field(default_factory=dict)
    policy: Dict[str, str] = field(default_factory=dict)  # s -> a
    value_function: Dict[str, float] = field(default_factory=dict)
    
    algorithm: str = "value_iteration"
    
    def value_iteration(self, max_iters: int = 100, tol: float = 1e-6) -> Dict[str, float]:
        """Value iteration"""
        # Initialize
        self.value_function = {s.id: 0 for s in self.states}
        
        for _ in range(max_iters):
            new_v = {}
            for state in self.states:
                # Max over actions
                max_q = -float('inf')
                for action in self.actions.get(state.id, []):
                    q = self._q_value(state.id, action)
                    max_q = max(max_q, q)
                
                new_v[state.id] = max_q if max_q != -float('inf') else 0
            
            # Check convergence
            if self._converged(self.value_function, new_v, tol):
                break
            self.value_function = new_v
        
        return self.value_function
    
    def _q_value(self, state_id: str, action: MDPAction) -> float:
        """Q(s, a) = R(s,a) + gamma * sum(P(s'|s,a) * V(s'))"""
        # Simplified (would need reward model)
        return sum(p * self.value_function.get(s_next, 0) 
                for s_next, p in action.transitions.get(state_id, {}).items()) * self.discount_factor
    
    def _converged(self, v1: Dict, v2: Dict, tol: float) -> bool:
        for s in v1:
            if abs(v1[s] - v2.get(s, 0)) > tol:
                return False
        return True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "discount_factor": self.discount_factor,
            "value_function": self.value_function,
            "policy": self.policy,
        }


@dataclass
class POMDP:
    """Partially Observable MDP"""
    id: str
    belief_states: Dict[str, float] = field(default_factory=dict)
    observation_model: Dict[str, Dict[str, float]] = field(default_factory=dict)
    discount_factor: float = 0.9
    
    def update_belief(self, obs: str) -> Dict[str, float]:
        """Update belief after observation"""
        new_belief = {}
        for s, b in self.belief_states.items():
            p_obs = self.observation_model.get(s, {}).get(obs, 0)
            new_belief[s] = b * p_obs
        
        # Normalize
        total = sum(new_belief.values())
        if total > 0:
            new_belief = {s: b / total for s, b in new_belief.items()}
        
        return new_belief
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "belief_states": self.belief_states,
            "discount_factor": self.discount_factor,
        }


# ============================================================
# Game Theory
# ============================================================

@dataclass
class Game:
    """Strategic game"""
    id: str
    players: List[str] = field(default_factory=list)
    action_spaces: Dict[str, List[str]] = field(default_factory=dict)
    payoff_matrices: Dict[str, Dict[str, Dict[str, float]] = field(default_factory=dict)
    nash_equilibria: List[Dict[str, str]] = field(default_factory=list)
    game_type: str = "normal"
    
    def find_nash(self) -> List[Dict[str, str]]:
        """Find Nash equilibria (simplified for 2-player)"""
        # Would need full implementation
        return self.nash_equilibria
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "players": self.players,
            "game_type": self.game_type,
            "nash_equilibria": self.nash_equilibria,
        }


@dataclass
class Mechanism:
    """Mechanism (mechanism design)"""
    id: str
    allocation_rule: Dict[str, str] = field(default_factory=dict)
    payment_rule: Dict[str, float] = field(default_factory=dict)
    
    is_strategyproof: bool = False
    is_efficient: bool = False
    is_individual_rational: bool = False
    is_fair: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "allocation_rule": self.allocation_rule,
            "payment_rule": self.payment_rule,
            "is_strategyproof": self.is_strategyproof,
            "is_efficient": self.is_efficient,
        }


# ============================================================
# Information Theory
# ============================================================

@dataclass
class InformationMetrics:
    """Information-theoretic metrics"""
    
    @staticmethod
    def entropy(probs: Dict[str, float]) -> float:
        """H(X) = -sum(P(x) * log(P(x))"""
        h = 0.0
        for p in probs.values():
            if p > 0:
                h -= p * math.log(p)
        return h
    
    @staticmethod
    def mutual_information(p_xy: Dict[tuple, float], p_x: Dict, p_y: Dict) -> float:
        """I(X; Y) = sum(P(x,y) * log(P(x,y) / (P(x) * P(y)))"""
        mi = 0.0
        for (x, y), p in p_xy.items():
            if p > 0 and p_x.get(x, 0) > 0 and p_y.get(y, 0) > 0:
                mi += p * math.log(p / (p_x[x] * p_y[y]))
        return mi
    
    @staticmethod
    def kl_divergence(p: Dict, q: Dict) -> float:
        """D(P || Q) = sum(P(x) * log(P(x) / Q(x)))"""
        kl = 0.0
        for x, p_x in p.items():
            if p_x > 0 and q.get(x, 0) > 0:
                kl += p_x * math.log(p_x / q[x])
        return kl


# ============================================================
# Optimization
# ============================================================

@dataclass
class Optimization:
    """Optimization problem"""
    id: str
    objective_type: str = "minimize"
    variables: List[Dict] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    algorithm: str = "gradient_descent"
    
    max_iterations: int = 1000
    tolerance: float = 1e-6
    
    optimal_value: Optional[float] = None
    optimal_solution: Dict[str, float] = field(default_factory=dict)
    converged: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "objective_type": self.objective_type,
            "algorithm": self.algorithm,
            "optimal_value": self.optimal_value,
            "converged": self.converged,
        }


@dataclass
class GeneticAlgorithm:
    """Genetic algorithm"""
    id: str
    population_size: int = 100
    selection_method: str = "tournament"
    crossover_rate: float = 0.8
    mutation_rate: float = 0.01
    fitness_function: str = ""
    
    max_generations: int = 100
    current_generation: int = 0
    
    best_fitness: Optional[float] = None
    best_genome: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "population_size": self.population_size,
            "current_generation": self.current_generation,
            "best_fitness": self.best_fitness,
        }


# ============================================================
# Control Theory
# ============================================================

@dataclass
class ControlSystem:
    """Control system"""
    id: str
    state_dimension: int
    control_dimension: int
    
    is_stable: Optional[bool] = None
    settling_time: Optional[float] = None
    overshoot: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "state_dimension": self.state_dimension,
            "control_dimension": self.control_dimension,
            "is_stable": self.is_stable,
        }


@dataclass
class PIDController:
    """PID Controller"""
    id: str
    kp: float = 1  # Proportional
    ki: float = 0  # Integral
    kd: float = 0  # Derivative
    
    output_min: float = -100
    output_max: float = 100
    
    def control(self, error: float, error_integral: float, error_derivative: float) -> float:
        """u(t) = Kp * e(t) + Ki * integral(e) + Kd * de/dt"""
        u = self.kp * error + self.ki * error_integral + self.kd * error_derivative
        return max(self.output_min, min(self.output_max, u))
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
        }


# ============================================================
# Learning Theory
# ============================================================

@dataclass
class LearningBounds:
    """Learning bounds"""
    sample_complexity: Optional[int] = None
    vc_dimension: Optional[int] = None
    
    empirical_error: float = 0
    true_error: Optional[float] = None
    confidence: float = 0.95
    
    @staticmethod
    def pac_bound(vc_dim: int, epsilon: float, delta: float) -> int:
        """Sample complexity: m >= (VC + ln(1/delta)) / epsilon"""
        return int((vc_dim + math.log(1 / delta)) / epsilon)
    
    @staticmethod
    def rademacher_bound(n: int, m: int, delta: float) -> float:
        """Rademacher complexity bound"""
        return math.sqrt((2 * math.log(2 * n) / m) + math.log(2 * n / delta)) / m


# ============================================================
# Factory
# ============================================================

def create_mdp(id: str, states: int, actions_per_state: int) -> MDP:
    """Create MDP"""
    return MDP(
        id=id,
        states=[MDPState(id=f"s{i}") for i in range(states)],
    )


__all__ = [
    'Utility', 'Preference',
    'ProbabilityDistribution', 'BayesianUpdate',
    'MDPState', 'MDPAction', 'MDP', 'POMDP',
    'Game', 'Mechanism',
    'InformationMetrics',
    'Optimization', 'GeneticAlgorithm',
    'ControlSystem', 'PIDController',
    'LearningBounds',
    'create_mdp'
]