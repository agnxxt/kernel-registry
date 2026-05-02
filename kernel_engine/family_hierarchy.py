"""
Family Hierarchy - Family Structures and Relationships

Family as first-class entity with roles, hierarchy, and dynamics:
- Family Members
- Family Roles
- Family Structure
- Genealogical Relationships
- Intergenerational Transfer
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Family Members
# ============================================================

class FamilyRole:
    PATRIARCH = "patriarch"
    MATRIARCH = "matriarch"
    FATHER = "father"
    MOTHER = "mother"
    PARENT = "parent"
    SON = "son"
    DAUGHTER = "daughter"
    CHILD = "child"
    HUSBAND = "husband"
    WIFE = "wife"
    SPOUSE = "spouse"
    BROTHER = "brother"
    SISTER = "sister"
    SIBLING = "sibling"
    GRANDFATHER = "grandfather"
    GRANDMOTHER = "grandmother"
    GRANDPARENT = "grandparent"
    GRANDSON = "grandson"
    GRANDDAUGHTER = "granddaughter"
    UNCLE = "uncle"
    AUNT = "aunt"
    COUSIN = "cousin"
    NEPHEW = "nephew"
    NIECE = "niece"


@dataclass
class FamilyMember:
    """Person in family"""
    id: str
    person_id: Optional[str] = None
    
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    nickname: str = ""
    
    date_of_birth: str = ""
    place_of_birth: str = ""
    
    sex: str = ""  # male, female, intersex
    gender_identity: str = ""
    
    is_living: bool = True
    date_of_death: str = ""
    
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name(),
            "date_of_birth": self.date_of_birth,
            "is_living": self.is_living,
        }


class FamilyRelationshipType:
    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    GRANDPARENT = "grandparent"
    GRANDCHILD = "grandchild"
    AUNT_UNCLE = "aunt_uncle"
    NIECE_NEPHEW = "niece_nephew"
    COUSIN = "cousin"
    STEP_PARENT = "step_parent"
    STEP_CHILD = "step_child"
    STEP_SIBLING = "step_sibling"
    IN_LAW = "in_law"
    FOSTER = "foster"
    ADOPTIVE = "adoptive"
    GUARDIAN = "guardian"


@dataclass
class FamilyRelationship:
    """Family relationship"""
    id: str
    
    from_person: str  # Person 1
    to_person: str   # Person 2
    
    relationship_type: str = "child"
    
    is_biological: bool = True
    is_legal: bool = False
    is_adoptive: bool = False
    
    start_date: str = ""
    end_date: str = ""
    
    is_primary: bool = True
    shared_custody: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from": self.from_person,
            "to": self.to_person,
            "relationship_type": self.relationship_type,
            "is_biological": self.is_biological,
            "is_primary": self.is_primary,
        }


# ============================================================
# Family Structure
# ============================================================

class FamilyType:
    NUCLEAR = "nuclear"
    EXTENDED = "extended"
    SINGLE_PARENT = "single_parent"
    BLENDED = "blended"
    RECONSTITUTED = "reconstituted"
    EMPTY_NEST = "empty_nest"
    SKIP_GENERATION = "skip_generation"
    FOSTER = "foster"
    ADOPTIVE = "adoptive"
    GRANDPARENT = "grandparent"


@dataclass
class Family:
    """Family"""
    id: str
    name: str  # Family name
    
    family_type: str = "nuclear"
    
    members: List[str] = field(default_factory=list)
    
    head_of_family: str = ""
    spouse: str = ""
    
    home_location: str = ""
    
    formed_date: str = ""
    dissolved_date: str = ""
    
    is_intact: bool = True
    income: Optional[float] = None
    
    def add_member(self, member_id: str):
        """Add member"""
        if member_id not in self.members:
            self.members.append(member_id)
    
    def remove_member(self, member_id: str):
        """Remove member"""
        if member_id in self.members:
            self.members.remove(member_id)
    
    def member_count(self) -> int:
        """Get member count"""
        return len(self.members)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "family_type": self.family_type,
            "members": self.members,
            "member_count": self.member_count(),
            "head_of_family": self.head_of_family,
            "is_intact": self.is_intact,
        }


@dataclass
class Household:
    """Household"""
    id: str
    
    address: str = ""
    location_id: str = ""
    
    occupants: List[str] = field(default_factory=list)
    
    tenure: str = "rented"  # owned, rented, public, shelter
    household_type: str = "family"
    
    income: Optional[float] = None
    income_source: str = ""
    
    bedrooms: Optional[int] = None
    vehicles: int = 0
    
    def add_occupant(self, person_id: str):
        """Add occupant"""
        if person_id not in self.occupants:
            self.occupants.append(person_id)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "address": self.address,
            "occupants": self.occupants,
            "occupant_count": len(self.occupants),
            "tenure": self.tenure,
            "income": self.income,
        }


# ============================================================
# Family Roles
# ============================================================

@dataclass
class FamilyRole:
    """Role in family"""
    id: str
    member_id: str
    
    role: str = "child"
    
    authority: str = "none"  # primary, secondary, none
    responsibilities: List[str] = field(default_factory=list)
    
    since: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "role": self.role,
            "authority": self.authority,
        }


@dataclass
class RoleHierarchy:
    """Role hierarchy"""
    family_id: str
    
    roles: List[FamilyRole] = field(default_factory=list)
    
    primary_decision_maker: str = ""
    secondary_decision_maker: str = ""
    
    breadwinners: List[str] = field(default_factory=list)
    finance_controller: str = ""
    
    primary_caregiver: str = ""
    secondary_caregiver: str = ""
    
    def get_member_role(self, member_id: str) -> Optional[FamilyRole]:
        """Get member's role"""
        for role in self.roles:
            if role.member_id == member_id:
                return role
        return None
    
    def get_breadwinners(self) -> List[str]:
        """Get breadwinners"""
        return self.breadwinners
    
    def to_dict(self) -> Dict:
        return {
            "family_id": self.family_id,
            "primary_decision_maker": self.primary_decision_maker,
            "breadwinners": self.breadwinners,
            "finance_controller": self.finance_controller,
        }


# ============================================================
# Genealogical
# ============================================================

@dataclass
class Ancestor:
    """Ancestor"""
    id: str
    
    generation: int = 1  # 1 = parent, 2 = grandparent
    
    lineage: str = "paternal"  # paternal, maternal
    
    is_known: bool = True
    
    name: str = ""
    dates: str = ""
    birthplace: str = ""
    occupation: str = ""
    
    genetic_contribution: float = 0.5  # 50% = parent, 25% = grandparent
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "generation": self.generation,
            "lineage": self.lineage,
            "name": self.name,
            "genetic_contribution": self.genetic_contribution,
        }


@dataclass
class Pedigree:
    """Pedigree"""
    id: str
    person_id: str
    
    ancestors: List[Ancestor] = field(default_factory=list)
    
    max_generation: int = 4
    
    inbreeding_coefficient: Optional[float] = None
    
    genetic_disorders: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    def add_ancestor(self, ancestor: Ancestor):
        """Add ancestor"""
        self.ancestors.append(ancestor)
    
    def get_ancestors_by_generation(self, generation: int) -> List[Ancestor]:
        """Get ancestors by generation"""
        return [a for a in self.ancestors if a.generation == generation]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "person_id": self.person_id,
            "max_generation": self.max_generation,
            "ancestor_count": len(self.ancestors),
            "genetic_disorders": self.genetic_disorders,
        }


# ============================================================
# Intergenerational
# ============================================================

class AssetType:
    MONEY = "money"
    PROPERTY = "property"
    BUSINESS = "business"
    INVESTMENT = "investment"
    DEBT = "debt"
    MIXED = "mixed"


class TransferType:
    WILL = "will"
    TRUST = "trust"
    GIFT = "gift"
    INSURANCE = "insurance"
    JOINT_OWNERSHIP = "joint_ownership"


@dataclass
class Inheritance:
    """Inheritance"""
    id: str
    
    from_person: str
    to_person: str
    
    asset_type: str = "money"
    asset_description: str = ""
    value: Optional[float] = None
    
    transfer_type: str = "will"
    
    taxable: bool = True
    tax_value: Optional[float] = None
    
    status: str = "planned"  # planned, declared, transferred, disputed
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from_person": self.from_person,
            "to_person": self.to_person,
            "asset_type": self.asset_type,
            "value": self.value,
            "status": self.status,
        }


@dataclass
class FamilySupport:
    """Family support agreement"""
    id: str
    
    from_person: str
    to_person: str
    
    support_type: str = "financial"  # financial, housing, care, emotional, educational, mixed
    amount: Optional[float] = None
    frequency: str = "monthly"  # one_time, monthly, quarterly, annually
    
    conditions: str = ""
    start_date: str = ""
    end_date: str = ""
    is_permanent: bool = False
    
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from_person": self.from_person,
            "to_person": self.to_person,
            "support_type": self.support_type,
            "amount": self.amount,
            "is_active": self.is_active,
        }


@dataclass
class CareResponsibility:
    """Care responsibility"""
    id: str
    
    care_recipient: str
    caregivers: List[str] = field(default_factory=list)
    
    primary_caregiver: str = ""
    
    care_type: str = "daily_living"  # medical, daily_living, emotional, financial, mixed
    hours_per_week: Optional[float] = None
    
    is_compensated: bool = False
    compensation_amount: Optional[float] = None
    
    has_legal_authority: bool = False
    authority_type: str = ""
    
    def add_caregiver(self, caregiver_id: str):
        """Add caregiver"""
        if caregiver_id not in self.caregivers:
            self.caregivers.append(caregiver_id)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "care_recipient": self.care_recipient,
            "primary_caregiver": self.primary_caregiver,
            "caregivers": self.caregivers,
            "care_type": self.care_type,
        }


# ============================================================
# Family Events
# ============================================================

class FamilyEventType:
    BIRTH = "birth"
    DEATH = "death"
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    SEPARATION = "separation"
    ADOPTION = "adoption"
    EDUCATION_START = "education_start"
    EDUCATION_END = "education_end"
    EMPLOYMENT = "employment"
    RETIREMENT = "retirement"
    RELOCATION = "relocation"
    HEALTH_EVENT = "health_event"


@dataclass
class FamilyEvent:
    """Family event"""
    id: str
    
    event_type: str = "birth"
    
    participants: List[str] = field(default_factory=list)
    
    date: str = ""
    
    impact_on_family: str = "moderate"  # minimal, moderate, significant, transformative
    
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "participants": self.participants,
            "date": self.date,
            "impact_on_family": self.impact_on_family,
        }


class CrisisType:
    FINANCIAL = "financial"
    HEALTH = "health"
    RELATIONSHIP = "relationship"
    ADDICTION = "addiction"
    LEGAL = "legal"
    DEATH = "death"
    DISASTER = "disaster"


@dataclass
class FamilyCrisis:
    """Family crisis"""
    id: str
    
    crisis_type: str = "financial"
    
    severity: str = "moderate"  # mild, moderate, severe, critical
    
    affected_members: List[str] = field(default_factory=list)
    
    is_resolved: bool = False
    resolution_date: str = ""
    
    support_needed: List[str] = field(default_factory=list)
    
    def resolve(self):
        """Mark resolved"""
        self.is_resolved = True
        self.resolution_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "crisis_type": self.crisis_type,
            "severity": self.severity,
            "is_resolved": self.is_resolved,
            "support_needed": self.support_needed,
        }


# ============================================================
# Factory
# ============================================================

def create_family(name: str, family_type: str = "nuclear") -> Family:
    """Create family"""
    return Family(id=str(uuid.uuid4()), name=name, family_type=family_type)


def add_family_member(family: Family, member: FamilyMember) -> FamilyMember:
    """Add member to family"""
    family.add_member(member.id)
    return member


def create_family_relationship(from_id: str, to_id: str, rel_type: str) -> FamilyRelationship:
    """Create family relationship"""
    return FamilyRelationship(
        id=str(uuid.uuid4()),
        from_person=from_id,
        to_person=to_id,
        relationship_type=rel_type,
    )


__all__ = [
    'FamilyRole', 'FamilyRelationshipType', 'FamilyMember', 'FamilyRelationship',
    'FamilyType', 'Family', 'Household',
    'FamilyRole', 'RoleHierarchy',
    'Ancestor', 'Pedigree',
    'AssetType', 'TransferType', 'Inheritance', 'FamilySupport', 'CareResponsibility',
    'FamilyEventType', 'FamilyEvent', 'CrisisType', 'FamilyCrisis',
    'create_family', 'add_family_member', 'create_family_relationship'
]