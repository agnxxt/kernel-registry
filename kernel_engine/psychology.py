"""
Psychological Foundations - Awareness grounded in psychology

Theories included:
- Maslow's Hierarchy of Needs
- Self-Determination Theory (SDT)
- Theory of Mind
- Metacognition
- Emotional Intelligence (EQ)
- Self-Efficacy
- Growth Mindset
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Maslow's Hierarchy of Needs
# ============================================================

class MaslowNeedLevel:
    PHYSIOLOGICAL = "physiological"
    SAFETY = "safety"
    LOVE_BELONGING = "love_belonging"
    ESTEEM = "esteem"
    SELF_ACTUALIZATION = "self_actualization"
    TRANSCENDENCE = "transcendence"


@dataclass
class MaslowAwareness:
    """Maslow's hierarchy applied to agents"""
    current_level: str = MaslowNeedLevel.PHYSIOLOGICAL
    satisfied_needs: List[str] = field(default_factory=list)
    active_needs: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "current_level": self.current_level,
            "satisfied_needs": self.satisfied_needs,
            "active_needs": self.active_needs,
        }


# ============================================================
# Self-Determination Theory (SDT)
# ============================================================

@dataclass
class SDTBasicPsychologicalNeed:
    """One of the 3 basic needs"""
    satisfied: bool = True
    frustration: int = 0  # 0-100


@dataclass
class SDTAwareness:
    """SDT for agents"""
    autonomy: SDTBasicPsychologicalNeed = field(default_factory=SDTBasicPsychologicalNeed)
    competence: SDTBasicPsychologicalNeed = field(default_factory=SDTBasicPsychologicalNeed)
    relatedness: SDTBasicPsychologicalNeed = field(default_factory=SDTBasicPsychologicalNeed)
    
    def to_dict(self) -> Dict:
        return {
            "autonomy": {"satisfied": self.autonomy.satisfied, "frustration": self.autonomy.frustration},
            "competence": {"satisfied": self.competence.satisfied, "frustration": self.competence.frustration},
            "relatedness": {"satisfied": self.relatedness.satisfied, "frustration": self.relatedness.frustration},
        }


# ============================================================
# Theory of Mind
# ============================================================

@dataclass
class MentalState:
    """Mental state of an entity"""
    beliefs: Dict = field(default_factory=dict)
    desires: Dict = field(default_factory=dict)
    intentions: List[str] = field(default_factory=list)
    emotions: Dict[str, int] = field(default_factory=dict)  # emotion -> intensity
    knowledge: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "beliefs": self.beliefs,
            "desires": self.desires,
            "intentions": self.intentions,
            "emotions": self.emotions,
            "knowledge": self.knowledge,
        }


@dataclass
class ToMAwareness:
    """Theory of Mind - understanding others' mental states"""
    self_model: MentalState = field(default_factory=MentalState)
    user_model: Optional[MentalState] = None
    agent_models: Dict[str, MentalState] = field(default_factory=dict)
    
    # Inferences
    inferred_beliefs: Dict = field(default_factory=dict)
    inferred_intentions: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "self_model": self.self_model.to_dict(),
            "user_model": self.user_model.to_dict() if self.user_model else None,
            "agent_models": {k: v.to_dict() for k, v in self.agent_models.items()},
            "inferred_beliefs": self.inferred_beliefs,
            "inferred_intentions": self.inferred_intentions,
        }


# ============================================================
# Metacognition - Thinking about Thinking
# ============================================================

@dataclass
class Reflection:
    """A reflection on thinking"""
    thought: str
    insight: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Metacognition:
    """Metacognition - awareness of own thinking"""
    self_monitoring_level: int = 50  # 0-100
    
    aware_of_thinking: bool = True
    aware_of_learning: bool = True
    
    can_interrupt: bool = True
    can_replan: bool = True
    can_self_correct: bool = True
    
    reflection_history: List[Reflection] = field(default_factory=list)
    
    def add_reflection(self, thought: str, insight: str):
        """Add reflection"""
        self.reflection_history.append(Reflection(thought=thought, insight=insight))
        if len(self.reflection_history) > 20:
            self.reflection_history.pop(0)
    
    def to_dict(self) -> Dict:
        return {
            "self_monitoring_level": self.self_monitoring_level,
            "aware_of_thinking": self.aware_of_thinking,
            "aware_of_learning": self.aware_of_learning,
            "can_interrupt": self.can_interrupt,
            "can_replan": self.can_replan,
            "can_self_correct": self.can_self_correct,
            "reflection_history": [
                {"thought": r.thought, "insight": r.insight, "timestamp": r.timestamp}
                for r in self.reflection_history
            ],
        }


# ============================================================
# Emotional Intelligence (Goleman)
# ============================================================

@dataclass
class EmotionalState:
    """Current emotional state"""
    emotion: str = "neutral"
    intensity: int = 0  # 0-100
    
    # Circumplex model
    valence: int = 0    # -100 (negative) to +100 (positive)
    arousal: int = 0     # -100 (low) to +100 (high)
    
    mood: str = "neutral"  # positive, neutral, negative
    
    regulation_strategy: str = ""
    regulation_success: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion,
            "intensity": self.intensity,
            "valence": self.valence,
            "arousal": self.arousal,
            "mood": self.mood,
            "regulation_strategy": self.regulation_strategy,
            "regulation_success": self.regulation_success,
        }


@dataclass
class EmotionalIntelligence:
    """EQ components"""
    # Self-Awareness
    emotional_awareness: bool = True
    self_confidence: int = 50
    
    # Self-Management
    self_control: int = 50
    adaptability: int = 50
    achievement_orientation: int = 50
    
    # Social Awareness
    empathy: int = 50
    organizational_awareness: int = 50
    
    # Relationship Management
    influence: int = 50
    conflict_management: int = 50
    teamwork: int = 50
    
    def to_dict(self) -> Dict:
        return {
            "self_awareness": {
                "emotional_awareness": self.emotional_awareness,
                "self_confidence": self.self_confidence,
            },
            "self_management": {
                "self_control": self.self_control,
                "adaptability": self.adaptability,
                "achievement_orientation": self.achievement_orientation,
            },
            "social_awareness": {
                "empathy": self.empathy,
                "organizational_awareness": self.organizational_awareness,
            },
            "relationship_management": {
                "influence": self.influence,
                "conflict_management": self.conflict_management,
                "teamwork": self.teamwork,
            },
        }


# ============================================================
# Self-Efficacy (Bandura)
# ============================================================

@dataclass
class SelfEfficacy:
    """Self-efficacy - belief in capabilities"""
    confidence: int = 50  # 0-100
    
    # Sources of efficacy
    mastery_experiences: int = 50
    vicarious_experiences: int = 50
    verbal_persuasion: int = 50
    emotional_states: int = 50
    
    # Outcome expectations
    expected_outcomes: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "confidence": self.confidence,
            "mastery_experiences": self.mastery_experiences,
            "vicarious_experiences": self.vicarious_experiences,
            "verbal_persuasion": self.verbal_persuasion,
            "emotional_states": self.emotional_states,
            "expected_outcomes": self.expected_outcomes,
        }


# ============================================================
# Growth Mindset (Dweck)
# ============================================================

@dataclass
class Mindset:
    """Fixed vs Growth mindset"""
    is_growth: bool = True
    
    ability_is_fixed: bool = False
    effort_leads_to_growth: bool = True
    failures_are_learning: bool = True
    challenges_are_opportunities: bool = True
    
    seeks_challenge: bool = True
    persists_through_failure: bool = True
    learns_from_criticism: bool = True
    inspired_by_others: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "is_growth": self.is_growth,
            "ability_is_fixed": self.ability_is_fixed,
            "effort_leads_to_growth": self.effort_leads_to_growth,
            "failures_are_learning": self.failures_are_learning,
            "challenges_are_opportunities": self.challenges_are_opportunities,
            "seeks_challenge": self.seeks_challenge,
            "persists_through_failure": self.persists_through_failure,
            "learns_from_criticism": self.learns_from_criticism,
            "inspired_by_others": self.inspired_by_others,
        }


# ============================================================
# Full Psychological Profile
# ============================================================

@dataclass
class PsychologicalProfile:
    """Complete psychological profile"""
    agent_id: str
    
    # Theories
    maslow: MaslowAwareness = field(default_factory=MaslowAwareness)
    sdt: SDTAwareness = field(default_factory=SDTAwareness)
    tom: ToMAwareness = field(default_factory=ToMAwareness)
    metacognition: Metacognition = field(default_factory=Metacognition)
    emotional_intelligence: EmotionalIntelligence = field(default_factory=EmotionalIntelligence)
    emotional_state: EmotionalState = field(default_factory=EmotionalState)
    self_efficacy: SelfEfficacy = field(default_factory=SelfEfficacy)
    mindset: Mindset = field(default_factory=Mindset)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update(self):
        """Mark updated"""
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "maslow": self.maslow.to_dict(),
            "sdt": self.sdt.to_dict(),
            "tom": self.tom.to_dict(),
            "metacognition": self.metacognition.to_dict(),
            "emotional_intelligence": self.emotional_intelligence.to_dict(),
            "emotional_state": self.emotional_state.to_dict(),
            "self_efficacy": self.self_efficacy.to_dict(),
            "mindset": self.mindset.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ============================================================
# Factory
# ============================================================

def create_psychological_profile(agent_id: str) -> PsychologicalProfile:
    """Create psychological profile for agent"""
    return PsychologicalProfile(agent_id=agent_id)


__all__ = [
    'MaslowNeedLevel', 'MaslowAwareness',
    'SDTBasicPsychologicalNeed', 'SDTAwareness',
    'MentalState', 'ToMAwareness',
    'Reflection', 'Metacognition',
    'EmotionalState', 'EmotionalIntelligence',
    'SelfEfficacy', 'Mindset',
    'PsychologicalProfile', 'create_psychological_profile'
]