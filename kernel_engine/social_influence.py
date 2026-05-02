"""
Social Influences on Agent Awareness

External factors that shape agent decision-making:
- Macroeconomic Influences
- Cultural Factors
- Spiritual/Religious Values
- Family Values
- Organizational Policies
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Macroeconomic Influences
# ============================================================

@dataclass
class EconomicConditions:
    """Economic conditions"""
    gdp_growth: Optional[float] = None
    gdp_per_capita: Optional[float] = None
    
    unemployment_rate: Optional[float] = None
    labor_force_participation: Optional[float] = None
    
    inflation_rate: Optional[float] = None
    interest_rate: Optional[float] = None
    
    trade_balance: Optional[float] = None
    exchange_rate: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "gdp_growth": self.gdp_growth,
            "unemployment_rate": self.unemployment_rate,
            "inflation_rate": self.inflation_rate,
        }


@dataclass
class BusinessCycle:
    """Business cycle phase"""
    phase: str = "expansion"  # expansion, peak, contraction, trough
    
    leading_index: Optional[float] = None
    lagging_index: Optional[float] = None
    coincident_index: Optional[float] = None
    
    growth_forecast: Optional[float] = None
    confidence_level: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "phase": self.phase,
            "growth_forecast": self.growth_forecast,
            "confidence_level": self.confidence_level,
        }


@dataclass
class PolicyEnvironment:
    """Policy environment"""
    fiscal_policy: str = "neutral"  # expansionary, neutral, contractionary
    government_spending: Optional[float] = None
    tax_rate: Optional[float] = None
    
    monetary_policy: str = "neutral"  # accommodative, neutral, tight
    money_supply: Optional[float] = None
    
    trade_policy: str = "free_trade"  # protectionist, free_trade, managed
    tariffs: Optional[float] = None
    
    regulatory_burden: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "fiscal_policy": self.fiscal_policy,
            "monetary_policy": self.monetary_policy,
            "trade_policy": self.trade_policy,
        }


# ============================================================
# Cultural Factors
# ============================================================

@dataclass
class CulturalDimensions:
    """Cultural dimensions (Hofstede-inspired)"""
    power_distance: int = 50  # 0-100
    individualism: int = 50
    masculinity: int = 50
    uncertainty_avoidance: int = 50
    long_term_orientation: int = 50
    indulgence: int = 50
    
    def to_dict(self) -> Dict:
        return {
            "power_distance": self.power_distance,
            "individualism": self.individualism,
            "uncertainty_avoidance": self.uncertainty_avoidance,
        }


@dataclass
class CulturalValues:
    """Cultural values"""
    core_values: List[str] = field(default_factory=list)
    
    communication_style: str = "direct"  # direct, indirect
    time_orientation: str = "present"  # past, present, future
    context_level: str = "low"  # high, low
    
    greetings: List[str] = field(default_factory=list)
    taboos: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "core_values": self.core_values,
            "communication_style": self.communication_style,
            "time_orientation": self.time_orientation,
        }


@dataclass
class RegionalCulture:
    """Regional culture"""
    region: str
    
    dimensions: CulturalDimensions = field(default_factory=CulturalDimensions)
    values: CulturalValues = field(default_factory=CulturalValues)
    
    holidays: List[str] = field(default_factory=list)
    customs: List[str] = field(default_factory=list)
    dress_code: str = ""
    
    business_hours: str = ""
    work_week: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "region": self.region,
            "dimensions": self.dimensions.to_dict(),
            "values": self.values.to_dict(),
        }


# ============================================================
# Spiritual/Religious Values
# ============================================================

class SpiritualTraditionType:
    CHRISTIANITY = "christianity"
    ISLAM = "islam"
    JUDAISM = "judaism"
    HINDUISM = "hinduism"
    BUDDHISM = "buddhism"
    SIKHISM = "sikhism"
    CONFUCIANISM = "confucianism"
    TAOISM = "taoism"
    SHINTO = "shinto"
    SECULAR = "secular"


@dataclass
class SpiritualTradition:
    """Spiritual tradition"""
    id: str
    tradition: str = "secular"
    branch: str = ""
    
    observance: str = "moderate"  # strict, moderate, liberal, secular
    core_values: List[str] = field(default_factory=list)
    guiding_principles: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tradition": self.tradition,
            "observance": self.observance,
            "core_values": self.core_values,
        }


@dataclass
class ReligiousPractices:
    """Religious practices"""
    prayer_frequency: str = "weekly"  # daily, weekly, monthly, occasional, none
    
    dietary_rules: List[str] = field(default_factory=list)
    dress_requirements: List[str] = field(default_factory=list)
    rest_day: str = ""
    holy_periods: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "prayer_frequency": self.prayer_frequency,
            "dietary_rules": self.dietary_rules,
            "rest_day": self.rest_day,
        }


@dataclass
class MoralFramework:
    """Moral framework"""
    ethic_type: str = "mixed"  # deontological, consequentialist, virtue, care, mixed
    
    core_principles: List[str] = field(default_factory=list)
    
    honesty: str = "very_important"
    loyalty: str = "important"
    compassion: str = "very_important"
    fairness: str = "very_important"
    integrity: str = "very_important"
    
    def to_dict(self) -> Dict:
        return {
            "ethic_type": self.ethic_type,
            "core_principles": self.core_principles,
            "honesty": self.honesty,
            "compassion": self.compassion,
            "fairness": self.fairness,
        }


# ============================================================
# Family Values
# ============================================================

@dataclass
class FamilyStructure:
    """Family structure"""
    family_type: str = "nuclear"  # nuclear, extended, single_parent, blended, diverse
    
    patriarchal: bool = False
    matriarchal: bool = False
    egalitarian: bool = True
    
    living_with_elders: bool = False
    three_generations: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "family_type": self.family_type,
            "patriarchal": self.patriarchal,
            "egalitarian": self.egalitarian,
        }


@dataclass
class FamilyValues:
    """Family values"""
    education: str = "very_important"
    financial_security: str = "very_important"
    health: str = "very_important"
    family_time: str = "very_important"
    
    respect_for_elders: str = "very_important"
    family_honor: str = "important"
    duty_to_family: str = "important"
    family_unity: str = "very_important"
    
    family_decisions: str = "consensus"  # elders, consensus, individual, mixed
    
    def to_dict(self) -> Dict:
        return {
            "education": self.education,
            "family_unity": self.family_unity,
            "family_decisions": self.family_decisions,
        }


@dataclass
class Intergenerational:
    """Intergenerational values"""
    intergenerational_inheritance: bool = True
    inheritance_values: List[str] = field(default_factory=list)
    
    knowledge_transfer: bool = True
    oral_tradition: bool = False
    
    elder_care: str = "family"  # family, institution, mixed, none
    child_care: str = "family"
    
    def to_dict(self) -> Dict:
        return {
            "intergenerational_inheritance": self.intergenerational_inheritance,
            "elder_care": self.elder_care,
            "child_care": self.child_care,
        }


# ============================================================
# Organizational Policies
# ============================================================

class OrganizationTypeEnum:
    CORPORATION = "corporation"
    STARTUP = "startup"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    FAMILY_BUSINESS = "family_business"


@dataclass
class OrganizationType:
    """Organization type"""
    type: str = "corporation"
    sector: str = ""
    industry: str = ""
    
    size: str = "medium"  # micro, small, medium, large, enterprise
    
    public_company: bool = False
    publicly_traded: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "sector": self.sector,
            "size": self.size,
        }


@dataclass
class HRPolicies:
    """HR policies"""
    work_arrangement: str = "hybrid"  # in_person, remote, hybrid, flexible
    working_hours: int = 40
    flexible_hours: bool = True
    
    parental_leave: Optional[int] = None
    sick_leave: Optional[int] = None
    vacation_days: Optional[int] = None
    
    health_insurance: bool = True
    retirement_401k: bool = True
    stock_options: bool = False
    
    dei_policy: bool = True
    pay_equity_audit: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "work_arrangement": self.work_arrangement,
            "working_hours": self.working_hours,
            "health_insurance": self.health_insurance,
        }


@dataclass
class EthicsPolicies:
    """Ethics policies"""
    has_code_of_conduct: bool = True
    code_of_ethics: str = ""
    
    compliance_framework: List[str] = field(default_factory=list)
    internal_audit: bool = True
    
    whistleblower_protection: bool = True
    anonymous_reporting: bool = True
    
    environmental_policy: bool = False
    carbon_neutral: bool = False
    esg_reporting: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "has_code_of_conduct": self.has_code_of_conduct,
            "whistleblower_protection": self.whistleblower_protection,
            "environmental_policy": self.environmental_policy,
        }


@dataclass
class GovernancePolicies:
    """Governance policies"""
    board_structure: str = "unitary"  # unitary, two_tier, none
    board_independence: int = 50
    
    ceo_duality: bool = False
    executive_compensation: str = ""
    
    shareholder_rights: List[str] = field(default_factory=list)
    dividend_policy: str = ""
    
    disclosure_policy: str = "standard"  # full, standard, minimal
    reporting_frequency: str = "quarterly"
    
    def to_dict(self) -> Dict:
        return {
            "board_structure": self.board_structure,
            "board_independence": self.board_independence,
            "disclosure_policy": self.disclosure_policy,
        }


# ============================================================
# Social Influence Composite
# ============================================================

@dataclass
class SocialInfluence:
    """Social influence on agent"""
    agent_id: str
    
    # Macroeconomic
    economic_conditions: Optional[EconomicConditions] = None
    business_cycle: Optional[BusinessCycle] = None
    policy_environment: Optional[PolicyEnvironment] = None
    
    # Cultural
    cultural_dimensions: Optional[CulturalDimensions] = None
    regional_culture: Optional[RegionalCulture] = None
    
    # Spiritual
    spiritual_tradition: Optional[SpiritualTradition] = None
    religious_practices: Optional[ReligiousPractices] = None
    moral_framework: Optional[MoralFramework] = None
    
    # Family
    family_structure: Optional[FamilyStructure] = None
    family_values: Optional[FamilyValues] = None
    intergenerational: Optional[Intergenerational] = None
    
    # Organization
    organization_type: Optional[OrganizationType] = None
    hr_policies: Optional[HRPolicies] = None
    ethics_policies: Optional[EthicsPolicies] = None
    governance_policies: Optional[GovernancePolicies] = None
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "cultural_dimensions": self.cultural_dimensions.to_dict() if self.cultural_dimensions else None,
            "family_values": self.family_values.to_dict() if self.family_values else None,
            "organization_type": self.organization_type.to_dict() if self.organization_type else None,
        }


# ============================================================
# Factory
# ============================================================

def create_social_influence(agent_id: str) -> SocialInfluence:
    """Create social influence"""
    return SocialInfluence(agent_id=agent_id)


__all__ = [
    'EconomicConditions', 'BusinessCycle', 'PolicyEnvironment',
    'CulturalDimensions', 'CulturalValues', 'RegionalCulture',
    'SpiritualTradition', 'SpiritualTraditionType',
    'ReligiousPractices', 'MoralFramework',
    'FamilyStructure', 'FamilyValues', 'Intergenerational',
    'OrganizationType', 'OrganizationTypeEnum',
    'HRPolicies', 'EthicsPolicies', 'GovernancePolicies',
    'SocialInfluence', 'create_social_influence'
]