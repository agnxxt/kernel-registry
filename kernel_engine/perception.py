"""
Perception - First-Class Entity

Perception as a core entity for agent awareness:
- Sensory Input
- Perceptual Processing
- Interpretation
- Attention
- Memory Integration
- Multi-modal Perception
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Perception Core
# ============================================================

class Modality:
    VISUAL = "visual"
    AUDITORY = "auditory"
    TACTILE = "tactile"
    OLFACTORY = "olfactory"
    GUSTATORY = "gustatory"
    PROPRIOCEPTIVE = "proprioceptive"
    LANGUAGE = "language"
    TEXT = "text"
    CODE = "code"
    SYMBOLIC = "symbolic"
    ABSTRACT = "abstract"


class SourceType:
    EXTERNAL = "external"
    INTERNAL = "internal"
    MEMORY = "memory"
    REASONING = "reasoning"


@dataclass
class Perception:
    """Perception (First-Class Entity)"""
    id: str
    content: str  # Raw sensory data
    interpreted: Any = None
    
    modality: str = "abstract"
    
    source: str = ""
    source_type: str = "external"
    
    quality: float = 0.5
    confidence: float = 0.5
    clarity: float = 0.5
    
    processed: bool = False
    interpretation: str = ""
    
    attention_level: float = 0.5
    salience: float = 0.5
    
    perceived_at: str = field(default_factory=lambda: datetime.now().isoformat())
    duration: Optional[float] = None  # ms
    
    def interpret(self, meaning: str, confidence: float = 0.5):
        """Interpret perception"""
        self.interpretation = meaning
        self.confidence = confidence
        self.processed = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content[:100],  # Truncate for display
            "modality": self.modality,
            "confidence": self.confidence,
            "processed": self.processed,
            "interpretation": self.interpretation,
        }


# ============================================================
# Sensory Input
# ============================================================

@dataclass
class SensoryInput:
    """Sensory input"""
    id: str
    
    modality: str = "visual"
    
    data: Any = None
    format: str = ""
    
    intensity: float = 0.5
    frequency: Optional[float] = None
    
    location: Dict = field(default_factory=dict)
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "modality": self.modality,
            "intensity": self.intensity,
            "timestamp": self.timestamp,
        }


# ============================================================
# Perceptual Processing
# ============================================================

class ProcessingStage:
    SENSATION = "sensation"
    TRANSDUCTION = "transduction"
    FEATURE_DETECTION = "feature_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    OBJECT_DETECTION = "object_detection"
    SCENE_PARSING = "scene_parsing"
    INTERPRETATION = "interpretation"
    INTEGRATION = "integration"


@dataclass
class PerceptualInference:
    """Perceptual inference"""
    hypothesis: str = ""
    probability: float = 0.5
    
    evidence: List[str] = field(default_factory=list)
    
    prior: float = 0.5
    likelihood: float = 0.5
    posterior: Optional[float] = None
    
    def calculate_posterior(self):
        """Bayes theorem: P(H|E) = P(E|H) * P(H) / P(E)"""
        p_e = self.likelihood * self.prior + (1 - self.likelihood) * (1 - self.prior)
        self.posterior = (self.likelihood * self.prior) / p_e if p_e > 0 else 0
        return self.posterior
    
    def to_dict(self) -> Dict:
        return {
            "hypothesis": self.hypothesis,
            "probability": self.probability,
            "posterior": self.posterior,
        }


# ============================================================
# Interpretation
# ============================================================

class InterpretationType:
    LITERAL = "literal"
    FIGURATIVE = "figurative"
    CONTEXTUAL = "contextual"
    INFERENTIAL = "inferential"
    SYMBOLIC = "symbolic"
    EMOTIONAL = "emotional"


@dataclass
class Interpretation:
    """Interpretation"""
    id: str
    
    perception_id: str
    
    meaning: str = ""
    interpretation_type: str = "literal"
    
    confidence: float = 0.5
    
    alternatives: List[Dict] = field(default_factory=list)
    
    context_ids: List[str] = field(default_factory=list)
    
    interpreted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "meaning": self.meaning,
            "interpretation_type": self.interpretation_type,
            "confidence": self.confidence,
        }


# ============================================================
# Attention
# ============================================================

class AttentionType:
    VOLUNTARY = "voluntary"
    INVOLUNTARY = "involuntary"
    EXECUTIVE = "executive"
    STIMULUS_DRIVEN = "stimulus_driven"


@dataclass
class Attention:
    """Attention"""
    focus: str = ""
    attention_type: str = "voluntary"
    
    level: float = 0.5
    
    span: int = 7  # Miller's 7±2
    
    resources: float = 0.5
    
    sustained: float = 0.5  # Sustained attention
    selective: float = 0.5  # Selective attention
    divided: float = 0.5   # Divided attention
    
    def shift_focus(self, new_focus: str):
        """Shift attention focus"""
        self.focus = new_focus
    
    def to_dict(self) -> Dict:
        return {
            "focus": self.focus,
            "type": self.attention_type,
            "level": self.level,
            "span": self.span,
        }


# ============================================================
# Multi-modal Integration
# ============================================================

class IntegrationMethod:
    EARLY = "early"
    LATE = "late"
    INTERMEDIATE = "intermediate"
    HYBRID = "hybrid"


@dataclass
class MultiModalPerception:
    """Multi-modal perception"""
    modalities: Dict[str, str] = field(default_factory=dict)  # modality -> perception_id
    
    integrated: bool = False
    integration_method: str = "late"
    
    unified_perception: str = ""
    cross_modal_confidence: float = 0.5
    
    def integrate(self):
        """Integrate modalities"""
        self.integrated = True
        # Simplified integration
    
    def to_dict(self) -> Dict:
        return {
            "modalities": list(self.modalities.keys()),
            "integrated": self.integrated,
            "method": self.integration_method,
        }


# ============================================================
# Perception State
# ============================================================

@dataclass
class PerceptionState:
    """Perception state"""
    active: List[str] = field(default_factory=list)  # Perception IDs
    
    working_memory: List[str] = field(default_factory=list)
    
    attention: Attention = field(default_factory=Attention)
    
    recent: List[str] = field(default_factory=list)
    
    multi_modal: Optional[MultiModalPerception] = None
    
    def add_to_working_memory(self, perception_id: str):
        """Add to working memory"""
        if perception_id not in self.working_memory:
            self.working_memory.append(perception_id)
            # Keep working memory bounded
            if len(self.working_memory) > 7:
                self.working_memory.pop(0)
    
    def to_dict(self) -> Dict:
        return {
            "active_count": len(self.active),
            "working_memory_size": len(self.working_memory),
            "attention_focus": self.attention.focus,
        }


# ============================================================
# Perception Profile
# ============================================================

@dataclass
class PerceptionProfile:
    """Perception profile"""
    id: str
    entity_id: str
    
    # Capabilities by modality
    capabilities: Dict[str, Dict] = field(default_factory=dict)
    
    history: List[str] = field(default_factory=list)
    
    state: PerceptionState = field(default_factory=PerceptionState)
    
    stats: Dict = field(default_factory=lambda: {
        "total_perceptions": 0,
        "avg_confidence": 0,
        "dominant_modality": ""
    })
    
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_perception(self, perception: Perception):
        """Add perception"""
        self.history.append(perception.id)
        self.state.active.append(perception.id)
        
        # Update stats
        self.stats["total_perceptions"] += 1
        # Could update avg confidence
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "total_perceptions": self.stats["total_perceptions"],
            "dominant_modality": self.stats.get("dominant_modality", ""),
        }


# ============================================================
# Factory
# ============================================================

def create_perception(content: str, modality: str = "abstract",
                     confidence: float = 0.5) -> Perception:
    """Create perception"""
    return Perception(
        id=str(uuid.uuid4()),
        content=content,
        modality=modality,
        confidence=confidence,
    )


def create_sensory_input(modality: str, data: Any) -> SensoryInput:
    """Create sensory input"""
    return SensoryInput(
        id=str(uuid.uuid4()),
        modality=modality,
        data=data,
    )


__all__ = [
    'Modality', 'SourceType',
    'Perception',
    'SensoryInput',
    'ProcessingStage', 'PerceptualInference',
    'InterpretationType', 'Interpretation',
    'AttentionType', 'Attention',
    'IntegrationMethod', 'MultiModalPerception',
    'PerceptionState',
    'PerceptionProfile',
    'create_perception', 'create_sensory_input'
]