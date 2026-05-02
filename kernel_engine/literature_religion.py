"""
Literature Influence - Cultural Intelligence

Literary works and cultural texts that shape agent reasoning:
- Literary Works
- Philosophies
- Wisdom Traditions
- Religious Texts
- Influence Mapping
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import uuid


# ============================================================
# Literary Works
# ============================================================

class WorkType:
    PHILOSOPHY = "philosophy"
    NOVEL = "novel"
    POETRY = "poetry"
    DRAMA = "drama"
    ESSAY = "essay"
    MYTHOLOGY = "mythology"
    RELIGIOUS_TEXT = "religious_text"
    HISTORICAL = "historical"
    SCIENTIFIC = "scientific"
    PSYCHOLOGICAL = "psychological"


@dataclass
class LiteraryWork:
    """Literary work"""
    id: str
    title: str
    
    author: str = ""
    author_dates: str = ""
    
    work_type: str = "philosophy"
    
    era: str = ""
    year_published: Optional[int] = None
    
    influence: Optional[float] = None
    key_concepts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "work_type": self.work_type,
            "key_concepts": self.key_concepts,
        }


# ============================================================
# Philosophy Schools
# ============================================================

@dataclass
class PhilosophySchool:
    """Philosophy school"""
    id: str
    name: str
    
    origin: str = ""
    era: str = ""
    region: str = ""
    
    core_beliefs: List[str] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    
    methodology: List[str] = field(default_factory=list)
    
    figures: List[str] = field(default_factory=list)
    
    influence_score: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "origin": self.origin,
            "era": self.era,
            "region": self.region,
            "core_beliefs": self.core_beliefs,
            "key_concepts": self.key_concepts,
            "figures": self.figures,
        }


# ============================================================
# Wisdom Traditions
# ============================================================

@dataclass
class WisdomTradition:
    """Wisdom tradition"""
    id: str
    name: str
    
    origin: str = ""
    region: str = ""
    language: str = ""
    
    core_teachings: List[str] = field(default_factory=list)
    proverbs: List[str] = field(default_factory=list)
    metaphors: List[str] = field(default_factory=list)
    
    themes: List[str] = field(default_factory=list)
    
    values: List[str] = field(default_factory=list)
    
    modern_relevance: str = "moderate"  # high, moderate, low
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "origin": self.origin,
            "region": self.region,
            "core_teachings": self.core_teachings,
            "values": self.values,
            "modern_relevance": self.modern_relevance,
        }


# ============================================================
# Religious Traditions
# ============================================================

@dataclass
class Religion:
    """Major religion"""
    id: str
    name: str
    
    origin: str = ""
    founder: str = ""
    year_founded: Optional[int] = None
    origin_region: str = ""
    
    branches: List[str] = field(default_factory=list)
    
    holy_text: List[str] = field(default_factory=list)
    scripture: List[str] = field(default_factory=list)
    
    core_beliefs: List[str] = field(default_factory=list)
    deities: List[str] = field(default_factory=list)
    
    practices: List[str] = field(default_factory=list)
    rituals: List[str] = field(default_factory=list)
    dietary_laws: List[str] = field(default_factory=list)
    holy_days: List[str] = field(default_factory=list)
    
    ethics: List[str] = field(default_factory=list)
    moral_framework: str = ""
    
    followers: Optional[int] = None
    influence: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "founder": self.founder,
            "origin_region": self.origin_region,
            "branches": self.branches,
            "holy_text": self.holy_text,
            "core_beliefs": self.core_beliefs,
            "practices": self.practices,
            "ethics": self.ethics,
        }


# ============================================================
# Moral Framework
# ============================================================

class MoralSourceType:
    RELIGIOUS = "religious"
    PHILOSOPHICAL = "philosophical"
    CULTURAL = "cultural"
    LEGAL = "legal"


@dataclass
class MoralSource:
    """Moral principle source"""
    id: str
    
    source_type: str = "religious"
    source_id: str = ""
    source_name: str = ""
    
    principle: str = ""
    description: str = ""
    
    priority: int = 5  # 1-10
    
    applies_to: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "principle": self.principle,
            "priority": self.priority,
        }


# ============================================================
# Cultural Influence
# ============================================================

@dataclass
class CulturalInfluence:
    """Cultural influence on agent"""
    agent_id: str
    
    literary_works: List[str] = field(default_factory=list)
    
    philosophy_schools: List[str] = field(default_factory=list)
    
    wisdom_traditions: List[str] = field(default_factory=list)
    
    religion: str = ""
    religiosity: str = "spiritual"  # secular, spiritual, religious, devout
    denomination: str = ""
    
    key_texts: List[str] = field(default_factory=list)
    
    values: List[str] = field(default_factory=list)
    
    principles: List[str] = field(default_factory=list)
    
    def add_value(self, value: str):
        """Add value"""
        if value not in self.values:
            self.values.append(value)
    
    def add_principle(self, principle: str):
        """Add principle"""
        if principle not in self.principles:
            self.principles.append(principle)
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "religion": self.religiosity,
            "denomination": self.denomination,
            "literary_works": self.literary_works,
            "philosophy_schools": self.philosophy_schools,
            "values": self.values,
            "principles": self.principles,
        }


# ============================================================
# Predefined Works
# ============================================================

def get_major_philosophies() -> List[PhilosophySchool]:
    """Get major philosophies"""
    return [
        PhilosophySchool(
            id="stoicism",
            name="Stoicism",
            origin="ancient Greece/Rome",
            era="300 BCE - 200 CE",
            region="Greece, Rome",
            core_beliefs=[
                "Virtue is the only good",
                "Accept fate ( Stoic acceptance)",
                "Focus on what you can control",
                "Live according to nature",
            ],
            key_concepts=[
                " virtue",
                "wisdom",
                "courage",
                "justice",
                "temperance",
            ],
            figures=["Marcus Aurelius", "Seneca", "Epictetus", "Zeno"],
        ),
        PhilosophySchool(
            id="existentialism",
            name="Existentialism",
            origin="19th-20th century Europe",
            era="1800s-1900s",
            region="France, Germany",
            core_beliefs=[
                "Existence precedes essence",
                "Freedom and responsibility",
                "Anxiety is fundamental",
                "Authenticity",
            ],
            key_concepts=[
                " authenticity",
                "freedom",
                " responsibility",
                "anguish",
            ],
            figures=["Sartre", "Kierkegaard", "Nietzsche", "Heidegger"],
        ),
    ]


def get_wisdom_traditions() -> List[WisdomTradition]:
    """Get wisdom traditions"""
    return [
        WisdomTradition(
            id="confucian",
            name="Confucian Wisdom",
            origin="China",
            region="East Asia",
            language="Chinese",
            core_teachings=[
                "Ren (benevolence)",
                "Li (ritual propriety)",
                "Yi (righteousness",
                "Xin (trustworthiness)",
            ],
            values=["filial piety", "respect for elders", "social harmony"],
            modern_relevance="high",
        ),
        WisdomTradition(
            id="stoic_wisdom",
            name="Stoic Wisdom",
            origin="Ancient Greece",
            region="Mediterranean",
            language="Greek",
            proverbs=[
                "We suffer not from events, but from our judgment about them",
                "The happiness of your life depends on the quality of your thoughts",
            ],
            themes=["resilience", "virtue", "balance"],
            values=["wisdom", "courage", "justice", "temperance"],
            modern_relevance="high",
        ),
    ]


def get_world_religions() -> List[Religion]:
    """Get world religions"""
    return [
        Religion(
            id="christianity",
            name="Christianity",
            founder="Jesus of Nazareth",
            year_founded=30,  # CE
            origin_region="Middle East",
            branches=["Catholicism", "Orthodoxy", "Protestantism"],
            holy_text=["Bible"],
            core_beliefs=[
                "God as creator",
                "Jesus as Son of God",
                "Salvation through grace",
                "Resurrection",
            ],
            ethics=["love God", "love neighbor", "forgiveness"],
        ),
        Religion(
            id="islam",
            name="Islam",
            founder="Prophet Muhammad",
            year_founded=610,
            origin_region="Arabia",
            branches=["Sunni", "Shia"],
            holy_text=["Quran", "Hadith"],
            core_beliefs=[
                "One God (Allah)",
                "Prophethood of Muhammad",
                "Jihad (struggle)",
                "Qadar (destiny)",
            ],
            ethics=["shahada", "prayer", "zakat", "fasting", "pilgrimage"],
        ),
        Religion(
            id="buddhism",
            name="Buddhism",
            founder="Siddhartha Gautama",
            year_founded=-500,
            origin_region="India",
            branches=["Theravada", "Mahayana", "Vajrayana"],
            holy_text=["Tripitaka"],
            core_beliefs=["Four Noble Truths", "Eightfold Path", "Nirvana", "Impermanence"],
            ethics=["non-violence", "compassion", "mindfulness"],
        ),
        Religion(
            id="hinduism",
            name="Hinduism",
            origin="India",
            year_founded=-1500,
            origin_region="India",
            branches=["Vaishnavism", "Shaivism", "Shaktism"],
            holy_text=["Vedas", "Bhagavad Gita"],
            core_beliefs=["Dharma", "Karma", "Moksha", "Brahman"],
            ethics=["dharma", "ahimsa", "truth"],
        ),
    ]


__all__ = [
    'WorkType', 'LiteraryWork',
    'PhilosophySchool',
    'WisdomTradition',
    'Religion',
    'MoralSourceType', 'MoralSource',
    'CulturalInfluence',
    'get_major_philosophies', 'get_wisdom_traditions', 'get_world_religions'
]