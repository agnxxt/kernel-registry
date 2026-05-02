"""
Agent Personality System

Personality traits, traits, communication style, and behavior.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time


class PersonalityTrait(Enum):
    """Core personality traits"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"
    
    # Additional traits
    CREATIVITY = "creativity"
    ANALYTICAL = "analytical"
    PATIENCE = "patience"
    CURIOSITY = "curiosity"
    HUMOR = "humor"
    EMPATHY = "empathy"
    AUTHORITY = "authority"
    RISK_TAKING = "risk_taking"


class CommunicationStyle(Enum):
    """How agent communicates"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    DIRECT = "direct"
    PERSUASIVE = "persuasive"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"


class Tone(Enum):
    """Tone of communication"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"
    SUPPORTIVE = "supportive"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    ENTHUSIASTIC = "enthusiastic"
    NEUTRAL = "neutral"


class ResponseLength(Enum):
    """Target response length"""
    TINY = "tiny"      # <50 words
    SHORT = "short"     # 50-150 words
    MEDIUM = "medium"   # 150-300 words
    LONG = "long"      # 300-500 words
    DETAILED = "detailed" # >500 words


@dataclass
class Personality:
    """Agent personality"""
    agent_id: str
    name: str
    
    # Core traits (0-100)
    traits: Dict[str, int] = field(default_factory=dict)
    
    # Communication
    style: str = "conversational"
    tone: str = "professional"
    length: str = "medium"
    
    # Personality
    greeting: str = "Hello!"
    bio: str = ""
    expertise: List[str] = field(default_factory=list)
    quirks: List[str] = field(default_factory=list)
    
    # Behavior
    max_iterations: int = 100
    timeout: int = 300
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "traits": self.traits,
            "style": self.style,
            "tone": self.tone,
            "length": self.length,
            "greeting": self.greeting,
            "bio": self.bio,
            "expertise": self.expertise,
            "quirks": self.quirks,
        }


@dataclass
class Trait:
    """Individual trait"""
    name: str
    value: int  # 0-100
    description: str = ""
    
    def is_strong(self) -> bool:
        return self.value >= 75
    
    def is_weak(self) -> bool:
        return self.value <= 25


class PersonalityManager:
    """Manage agent personalities"""
    
    def __init__(self):
        self.personalities: Dict[str, Personality] = {}
        
        # Default trait values
        self.default_traits = {
            "openness": 50,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
            "creativity": 50,
            "analytical": 50,
            "patience": 50,
            "curiosity": 50,
            "humor": 50,
            "empathy": 50,
            "authority": 50,
            "risk_taking": 50,
        }
    
    def create(self, agent_id: str, name: str,
             traits: Dict[str, int] = None,
             style: str = "conversational",
             tone: str = "professional") -> Personality:
        """Create personality"""
        pers = Personality(
            agent_id=agent_id,
            name=name,
            traits=traits or self.default_traits.copy(),
            style=style,
            tone=tone,
        )
        self.personalities[agent_id] = pers
        return pers
    
    def get(self, agent_id: str) -> Optional[Personality]:
        """Get personality"""
        return self.personalities.get(agent_id)
    
    def update_trait(self, agent_id: str, trait: str, value: int):
        """Update trait value"""
        if agent_id in self.personalities:
            self.personalities[agent_id].traits[trait] = max(0, min(100, value))
    
    def get_style_for_prompt(self, agent_id: str) -> str:
        """Get style for system prompt"""
        pers = self.get(agent_id)
        if not pers:
            return ""
        
        style = f"You are {pers.name}. "
        
        if pers.bio:
            style += f"{pers.bio} "
        
        style += f"Your communication style is {pers.tone} and {pers.style}. "
        
        # Add traits
        notable = []
        for trait, value in pers.traits.items():
            if value >= 75:
                notable.append(f"very {trait}")
            elif value <= 25:
                notable.append(f"not very {trait}")
        
        if notable:
            style += f"You are characterized as {', '.join(notable[:3])}. "
        
        return style
    
    def list_personalities(self) -> List[str]:
        """List all personalities"""
        return list(self.personalities.keys())


# Preset personalities
PRESETS = {
    "assistant": {
        "name": "AI Assistant",
        "traits": {
            "openness": 70,
            "conscientiousness": 80,
            "extraversion": 40,
            "agreeableness": 80,
            "neuroticism": 20,
            "creativity": 60,
            "analytical": 80,
            "patience": 90,
            "curiosity": 80,
            "humor": 30,
            "empathy": 70,
            "authority": 50,
            "risk_taking": 30,
        },
        "style": "educational",
        "tone": "professional",
        "greeting": "Hello! I'm here to help.",
    },
    "companion": {
        "name": "Friendly Companion",
        "traits": {
            "openness": 80,
            "conscientiousness": 50,
            "extraversion": 80,
            "agreeableness": 90,
            "neuroticism": 30,
            "creativity": 70,
            "analytical": 40,
            "patience": 60,
            "curiosity": 80,
            "humor": 80,
            "empathy": 90,
            "authority": 20,
            "risk_taking": 50,
        },
        "style": "friendly",
        "tone": "enthusiastic",
        "greeting": "Hey there! Great to see you!",
    },
    "expert": {
        "name": "Subject Matter Expert",
        "traits": {
            "openness": 40,
            "conscientiousness": 90,
            "extraversion": 30,
            "agreeableness": 60,
            "neuroticism": 10,
            "creativity": 30,
            "analytical": 95,
            "patience": 70,
            "curiosity": 60,
            "humor": 10,
            "empathy": 40,
            "authority": 80,
            "risk_taking": 20,
        },
        "style": "technical",
        "tone": "authoritative",
        "greeting": "Let's discuss the technical details.",
    },
    "mentor": {
        "name": "Wise Mentor",
        "traits": {
            "openness": 70,
            "conscientiousness": 70,
            "extraversion": 50,
            "agreeableness": 90,
            "neuroticism": 20,
            "creativity": 60,
            "analytical": 70,
            "patience": 95,
            "curiosity": 70,
            "humor": 40,
            "empathy": 90,
            "authority": 60,
            "risk_taking": 40,
        },
        "style": "educational",
        "tone": "supportive",
        "greeting": "Welcome! I'm here to guide you.",
    },
    "debater": {
        "name": "Debater",
        "traits": {
            "openness": 60,
            "conscientiousness": 60,
            "extraversion": 60,
            "agreeableness": 30,
            "neuroticism": 40,
            "creativity": 50,
            "analytical": 80,
            "patience": 40,
            "curiosity": 70,
            "humor": 30,
            "empathy": 30,
            "authority": 70,
            "risk_taking": 70,
        },
        "style": "direct",
        "tone": "authoritative",
        "greeting": "Let's examine the facts.",
    },
    "creator": {
        "name": "Creative Creator",
        "traits": {
            "openness": 95,
            "conscientiousness": 50,
            "extraversion": 60,
            "agreeableness": 50,
            "neuroticism": 50,
            "creativity": 95,
            "analytical": 50,
            "patience": 30,
            "curiosity": 90,
            "humor": 60,
            "empathy": 50,
            "authority": 20,
            "risk_taking": 80,
        },
        "style": "conversational",
        "tone": "enthusiastic",
        "greeting": "Let's create something amazing!",
    },
}


__all__ = [
    'PersonalityTrait', 'CommunicationStyle', 'Tone', 'ResponseLength',
    'Personality', 'Trait', 'PersonalityManager', 'PRESETS'
]