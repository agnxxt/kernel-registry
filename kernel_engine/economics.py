"""
Economic Models for Agent Decision Making

Economic theories for resource allocation, pricing, market dynamics:
- Supply and Demand
- Market Structures
- Pricing Models
- Resource Allocation
- Transaction Cost Economics
- Game Theoretic Economics
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import math
import uuid


# ============================================================
# Supply and Demand
# ============================================================

@dataclass
class Demand:
    """Demand curve Q = a - b * P"""
    id: str
    intercept: float  # a
    slope: float    # b (negative)
    
    elasticity: Optional[float] = None
    shift_factors: Dict[str, float] = field(default_factory=dict)
    
    def quantity(self, price: float) -> float:
        """Q(P) = a - b * P"""
        return max(0, self.intercept + self.slope * price)
    
    def price(self, quantity: float) -> float:
        """P(Q) = (a - Q) / b"""
        if self.slope == 0:
            return float('inf')
        return (self.intercept - quantity) / self.slope
    
    def elasticity_at(self, price: float) -> float:
        """ε = (dQ/dP) * (P/Q)"""
        q = self.quantity(price)
        if q == 0:
            return 0
        return self.slope * price / q
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intercept": self.intercept,
            "slope": self.slope,
            "elasticity": self.elasticity_at(0.5 * self.intercept / abs(self.slope)),
        }


@dataclass
class Supply:
    """Supply curve Q = c + d * P"""
    id: str
    intercept: float  # c
    slope: float    # d
    
    marginal_cost: Optional[float] = None
    shift_factors: Dict[str, float] = field(default_factory=dict)
    
    def quantity(self, price: float) -> float:
        """Q(P) = c + d * P"""
        return max(0, self.intercept + self.slope * price)
    
    def price(self, quantity: float) -> float:
        """P(Q) = (Q - c) / d"""
        if self.slope == 0:
            return float('inf')
        return (quantity - self.intercept) / self.slope
    
    def marginal_cost_at(self, quantity: float) -> float:
        """Marginal cost = dQ/dP"""
        return self.price(quantity + 1) - self.price(quantity)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intercept": self.intercept,
            "slope": self.slope,
            "marginal_cost": self.marginal_cost_at(0),
        }


@dataclass
class Equilibrium:
    """Market equilibrium"""
    id: str
    demand_id: str
    supply_id: str
    
    equilibrium_price: Optional[float] = None
    equilibrium_quantity: Optional[float] = None
    
    excess_supply: Optional[float] = None
    excess_demand: Optional[float] = None
    is_stable: Optional[bool] = None
    
    def find_equilibrium(self, demand: Demand, supply: Supply, tolerance: float = 1e-6) -> tuple:
        """Find equilibrium price and quantity"""
        # Q_d = Q_s
        # a - b * P = c + d * P
        # P* = (a - c) / (b + d)
        
        price = (demand.intercept - supply.intercept) / (demand.slope + supply.slope)
        
        if price < 0:
            price = 0
        
        q_d = demand.quantity(price)
        q_s = supply.quantity(price)
        
        self.equilibrium_price = price
        self.equilibrium_quantity = (q_d + q_s) / 2
        self.excess_supply = max(0, q_s - q_d)
        self.excess_demand = max(0, q_d - q_s)
        self.is_stable = self.excess_supply < tolerance and self.excess_demand < tolerance
        
        return self.equilibrium_price, self.equilibrium_quantity
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "equilibrium_price": self.equilibrium_price,
            "equilibrium_quantity": self.equilibrium_quantity,
            "is_stable": self.is_stable,
        }


# ============================================================
# Market Structures
# ============================================================

class MarketStructureType:
    PERFECT_COMPETITION = "perfect_competition"
    MONOPOLISTIC = "monopolistic"
    OLIGOPOLY = "oligopoly"
    MONOPOLY = "monopoly"


@dataclass
class MarketStructure:
    """Market structure"""
    id: str
    structure_type: str = "perfect_competition"
    
    firm_count: int = 1
    hhi: Optional[float] = None  # Herfindahl-Hirschman Index
    
    entry_barriers: List[str] = field(default_factory=list)
    product_differentiation: float = 0
    
    price_markup: Optional[float] = None
    marginal_revenue: Optional[float] = None
    
    def calculate_hhi(self, market_shares: List[float]) -> float:
        """HHI = sum(share_i^2)"""
        self.hhi = sum(s ** 2 for s in market_shares)
        return self.hhi
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "structure_type": self.structure_type,
            "firm_count": self.firm_count,
            "hhi": self.hhi,
        }


@dataclass
class Firm:
    """Firm in market"""
    id: str
    name: str
    market_share: float = 0
    
    marginal_cost: float = 0
    average_cost: Optional[float] = None
    
    strategy: str = "price_taker"
    profit: Optional[float] = None
    revenue: Optional[float] = None
    
    def calculate_profit(self, price: float, quantity: float) -> float:
        """Profit = (P - AC) * Q"""
        ac = self.average_cost or self.marginal_cost
        self.revenue = price * quantity
        self.profit = (price - ac) * quantity
        return self.profit
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "market_share": self.market_share,
            "marginal_cost": self.marginal_cost,
            "profit": self.profit,
        }


# ============================================================
# Pricing Models
# ============================================================

class PricingStrategy:
    COST_PLUS = "cost_plus"
    MARKET_ORIENTED = "market_oriented"
    VALUE_BASED = "value_based"
    PENETRATION = "penetration"
    SKIMMING = "skimming"
    DYNAMIC = "dynamic"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"


@dataclass
class Pricing:
    """Pricing strategy"""
    id: str
    strategy: str = "cost_plus"
    
    base_cost: float = 0
    margin: float = 0.2  # 20%
    value_premium: float = 0
    
    price: Optional[float] = None
    
    price_discrimination: bool = False
    customer_segments: Dict[str, float] = field(default_factory=dict)
    
    def calculate_price(self) -> float:
        """Calculate price based on strategy"""
        if self.strategy == "cost_plus":
            self.price = self.base_cost * (1 + self.margin)
        elif self.strategy == "value_based":
            self.price = self.base_cost + self.value_premium
        elif self.strategy == "penetration":
            self.price = self.base_cost * 0.8
        elif self.strategy == "skimming":
            self.price = self.base_cost * 2
        
        return self.price or self.base_cost
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "strategy": self.strategy,
            "base_cost": self.base_cost,
            "margin": self.margin,
            "price": self.price,
        }


@dataclass
class Auction:
    """Auction model"""
    id: str
    auction_type: str = "english"
    
    bidders: List[str] = field(default_factory=list)
    reserve_price: Optional[float] = None
    
    winner: Optional[str] = None
    winning_bid: Optional[float] = None
    
    is_efficient: Optional[bool] = None
    revenue: Optional[float] = None
    
    def vickrey_winner(self, bids: Dict[str, float]) -> tuple:
        """Vickrey auction: winner pays second highest"""
        if not bids:
            return None, 0
        
        sorted_bids = sorted(bids.items(), key=lambda x: x[1], reverse=True)
        winner, highest = sorted_bids[0]
        
        if len(sorted_bids) > 1:
            second_highest = sorted_bids[1][1]
        else:
            second_highest = self.reserve_price or 0
        
        self.winner = winner
        self.winning_bid = second_highest
        self.revenue = second_highest
        
        return winner, second_highest
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "auction_type": self.auction_type,
            "winner": self.winner,
            "winning_bid": self.winning_bid,
            "revenue": self.revenue,
        }


# ============================================================
# Resource Allocation
# ============================================================

@dataclass
class Resource:
    """Allocatable resource"""
    id: str
    name: str
    
    total: float = 0
    available: float = 0
    allocated: float = 0
    
    unit_cost: float = 0
    marginal_cost: Optional[float] = None
    
    scarcity: float = 0  # 0 = abundant, 1 = scarce
    
    def allocate(self, amount: float) -> bool:
        """Allocate resource"""
        if amount > self.available:
            return False
        self.allocated += amount
        self.available -= amount
        self.scarcity = 1 - (self.available / self.total) if self.total > 0 else 1
        return True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "total": self.total,
            "available": self.available,
            "allocated": self.allocated,
            "scarcity": self.scarcity,
        }


@dataclass
class Allocation:
    """Resource allocation problem"""
    id: str
    objective: str = "maximize_utilitarian"  # maximize total utility
    
    resources: List[Resource] = field(default_factory=list)
    demands: Dict[str, float] = field(default_factory=dict)
    allocation: Dict[str, float] = field(default_factory=dict)
    
    efficiency: Optional[float] = None
    fairness: Optional[float] = None
    pareto_optimal: Optional[bool] = None
    
    def allocate_proportional(self) -> Dict[str, float]:
        """Proportional allocation"""
        total_demand = sum(self.demands.values())
        if total_demand == 0:
            return {}
        
        total_resource = sum(r.allocated for r in self.resources)
        
        self.allocation = {
            agent: (demand / total_demand) * total_resource
            for agent, demand in self.demands.items()
        }
        
        return self.allocation
    
    def allocate_utilitarian(self) -> Dict[str, float]:
        """Maximize total utility"""
        # Simplified - would use marginal utility
        return self.allocate_proportional()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "objective": self.objective,
            "allocation": self.allocation,
            "efficiency": self.efficiency,
        }


# ============================================================
# Transaction Cost Economics
# ============================================================

@dataclass
class Transaction:
    """Economic transaction"""
    id: str
    buyer: str
    seller: str
    
    asset: str = ""
    quantity: float = 0
    price: float = 0
    
    search_cost: float = 0
    bargaining_cost: float = 0
    enforcement_cost: float = 0
    
    transaction_cost: Optional[float] = None
    
    def total_cost(self) -> float:
        """Total transaction cost"""
        self.transaction_cost = self.search_cost + self.bargaining_cost + self.enforcement_cost
        return self.transaction_cost
    
    def efficiency(self) -> float:
        """Trading efficiency"""
        return 1 - (self.transaction_cost / self.price) if self.price > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "buyer": self.buyer,
            "seller": self.seller,
            "price": self.price,
            "transaction_cost": self.transaction_cost,
        }


@dataclass
class Governance:
    """Governance structure"""
    id: str
    governance_type: str = "market"  # market, hybrid, hierarchy
    
    transaction_costs: Dict[str, float] = field(default_factory=dict)
    
    asset_specificity: float = 0
    measurability: float = 1
    
    recommended_type: Optional[str] = None
    
    def recommend(self) -> str:
        """Recommend governance based on transaction cost economics"""
        # Williamson's rule: higher specificity -> more hierarchy
        if self.asset_specificity > 0.6:
            self.recommended_type = "hierarchy"
        elif self.asset_specificity > 0.3:
            self.recommended_type = "hybrid"
        else:
            self.recommended_type = "market"
        
        return self.recommended_type
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "governance_type": self.governance_type,
            "recommended_type": self.recommended_type,
        }


# ============================================================
# Factory
# ============================================================

def create_market(demand_intercept: float, supply_intercept: float, slope_ratio: float = 0.5) -> Equilibrium:
    """Create market with demand and supply"""
    demand = Demand(id="demand", intercept=demand_intercept, slope=-slope_ratio)
    supply = Supply(id="supply", intercept=supply_intercept, slope=slope_ratio)
    
    eq = Equilibrium(id="eq", demand_id="demand", supply_id="supply")
    eq.find_equilibrium(demand, supply)
    
    return eq


__all__ = [
    'Demand', 'Supply', 'Equilibrium',
    'MarketStructure', 'MarketStructureType', 'Firm',
    'Pricing', 'PricingStrategy', 'Auction',
    'Resource', 'Allocation',
    'Transaction', 'Governance',
    'create_market'
]