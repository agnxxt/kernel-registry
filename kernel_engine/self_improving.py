"""
Self-Improving Harness - Learning and Adaptation

Feedback loops for continuous agent improvement:
- Learning Loop
- Feedback Processing
- Self-Reflection
- Adaptation
- Performance Optimization
- Meta-Learning
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# Learning Loop
# ============================================================

class LearningSource:
    SUCCESS = "success"
    FAILURE = "failure"
    OBSERVATION = "observation"
    INSTRUCTION = "instruction"
    REFLECTION = "reflection"


@dataclass
class LearningInstance:
    """Learning instance"""
    id: str
    concept: str
    description: str = ""
    
    source: str = "success"
    context: Dict = field(default_factory=dict)
    
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    
    applied: bool = False
    application_count: int = 0
    
    def apply(self, times: int = 1):
        """Mark as applied"""
        self.applied = True
        self.application_count += times
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "concept": self.concept,
            "source": self.source,
            "confidence": self.confidence,
            "applied": self.applied,
            "application_count": self.application_count,
        }


@dataclass
class LearningSession:
    """Learning session"""
    id: str
    
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    duration: Optional[float] = None
    
    instances: List[LearningInstance] = field(default_factory=list)
    
    success_count: int = 0
    failure_count: int = 0
    
    def add_instance(self, instance: LearningInstance):
        """Add instance"""
        self.instances.append(instance)
        if instance.source == LearningSource.SUCCESS:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def learning_rate(self) -> float:
        """Get learning rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "learning_rate": self.learning_rate(),
        }


# ============================================================


# Feedback Processing
# ============================================================

class FeedbackType:
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    SELF = "self"
    EXTERNAL = "external"
    PEER = "peer"


class FeedbackCategory:
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    ETHICS = "ethics"
    TIMING = "timing"
    COMMUNICATION = "communication"
    REASONING = "reasoning"


@dataclass
class Feedback:
    """Feedback"""
    id: str
    
    feedback_type: str = "explicit"
    source_id: str = ""
    
    content: str = ""
    polarity: str = "neutral"  # positive, negative, neutral
    severity: float = 0  # -1 to 1
    
    category: str = "accuracy"
    
    processed: bool = False
    action_items: List[str] = field(default_factory=list)
    
    def process(self, action_items: List[str]):
        """Process feedback"""
        self.processed = True
        self.action_items = action_items
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "feedback_type": self.feedback_type,
            "content": self.content,
            "polarity": self.polarity,
            "severity": self.severity,
            "category": self.category,
            "processed": self.processed,
        }


@dataclass
class FeedbackAnalysis:
    """Feedback analysis"""
    
    patterns: List[Dict] = field(default_factory=list)
    
    trends: Dict[str, float] = field(default_factory=dict)
    
    recommendations: List[str] = field(default_factory=list)
    
    processed_feedback: List[str] = field(default_factory=list)
    
    def add_pattern(self, category: str, frequency: int, severity: float):
        """Add pattern"""
        self.patterns.append({
            "category": category,
            "frequency": frequency,
            "severity": severity,
        })
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations"""
        return self.recommendations
    
    def to_dict(self) -> Dict:
        return {
            "patterns": self.patterns,
            "trends": self.trends,
            "recommendations": self.recommendations,
        }


# ============================================================
# Self-Reflection
# ============================================================

class ReflectionTrigger:
    SUCCESS = "success"
    FAILURE = "failure"
    SCHEDULED = "scheduled"
    PROMPTED = "prompted"
    CRISIS = "crisis"


@dataclass
class Reflection:
    """Self-reflection"""
    id: str
    
    trigger: str = "scheduled"
    event_id: str = ""
    
    analysis: str = ""
    insights: List[str] = field(default_factory=list)
    lessons: List[str] = field(default_factory=list)
    
    changes_implemented: List[str] = field(default_factory=list)
    
    impact_score: float = 0
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed: bool = False
    
    def add_insight(self, insight: str):
        """Add insight"""
        if insight not in self.insights:
            self.insights.append(insight)
    
    def add_lesson(self, lesson: str):
        """Add lesson"""
        if lesson not in self.lessons:
            self.lessons.append(lesson)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trigger": self.trigger,
            "analysis": self.analysis,
            "insights": self.insights,
            "lessons": self.lessons,
            "impact_score": self.impact_score,
        }


@dataclass
class SelfAssessment:
    """Self-assessment"""
    
    dimension: str = "reasoning"  # reasoning, communication, empathy, creativity, ethics, efficiency
    
    rating: int = 5  # 1-10
    
    evidence: List[str] = field(default_factory=list)
    
    improvement_targets: List[str] = field(default_factory=list)
    
    confidence: float = 0.5
    
    def improve_rating(self, delta: int):
        """Improve rating"""
        self.rating = max(1, min(10, self.rating + delta))
    
    def to_dict(self) -> Dict:
        return {
            "dimension": self.dimension,
            "rating": self.rating,
            "confidence": self.confidence,
            "improvement_targets": self.improvement_targets,
        }


# ============================================================
# Adaptation
# ============================================================

class ChangeType:
    PARAMETER_TUNING = "parameter_tuning"
    STRATEGY_CHANGE = "strategy_change"
    KNOWLEDGE_UPDATE = "knowledge_update"
    BEHAVIOR_MODIFICATION = "behavior_modification"
    BELIEF_REVISION = "belief_revision"


@dataclass
class Adaptation:
    """Adaptation"""
    id: str
    
    change_type: str = "parameter_tuning"
    
    target: str = ""
    old_value: Any = None
    new_value: Any = None
    
    rationale: str = ""
    
    expected_impact: float = 0
    actual_impact: Optional[float] = None
    
    status: str = "applied"  # planned, applied, reverted, verified
    
    def apply(self):
        """Apply adaptation"""
        self.status = "applied"
    
    def revert(self):
        """Revert adaptation"""
        self.status = "reverted"
    
    def verify(self, impact: float):
        """Verify impact"""
        self.status = "verified"
        self.actual_impact = impact
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "change_type": self.change_type,
            "target": self.target,
            "expected_impact": self.expected_impact,
            "status": self.status,
        }


# ============================================================
# Performance
# ============================================================

@dataclass
class PerformanceMetric:
    """Performance metric"""
    metric: str
    
    value: float
    baseline: Optional[float] = None
    target: Optional[float] = None
    
    change: Optional[float] = None
    change_percent: Optional[float] = None
    
    period: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_change(self):
        """Calculate change"""
        if self.baseline:
            self.change = self.value - self.baseline
            self.change_percent = (self.change / self.baseline * 100) if self.baseline != 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "metric": self.metric,
            "value": self.value,
            "baseline": self.baseline,
            "change": self.change,
        }


@dataclass
class PerformanceSummary:
    """Performance summary"""
    
    overall_score: float = 0.5
    
    dimensions: List[PerformanceMetric] = field(default_factory=list)
    
    trend: str = "stable"  # improving, stable, declining
    
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    
    def add_dimension(self, metric: str, value: float):
        """Add dimension"""
        self.dimensions.append(PerformanceMetric(metric=metric, value=value))
    
    def get_strengths(self) -> List[str]:
        """Get strengths"""
        return self.strengths
    
    def get_improvements(self) -> List[str]:
        """Get improvements"""
        return self.improvements
    
    def to_dict(self) -> Dict:
        return {
            "overall_score": self.overall_score,
            "trend": self.trend,
            "strengths": self.strengths,
            "improvements": self.improvements,
        }


# ============================================================
# Meta-Learning
# ============================================================

@dataclass
class LearningPattern:
    """Learning pattern"""
    trigger: str
    
    effective_strategies: List[str] = field(default_factory=list)
    
    success_rate: float = 0.5
    sample_size: int = 0
    
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update(self, success: bool):
        """Update pattern"""
        self.sample_size += 1
        if success:
            self.success_rate = (
                self.success_rate * (self.sample_size - 1) + 1
            ) / self.sample_size
        else:
            self.success_rate = (
                self.success_rate * (self.sample_size - 1)
            ) / self.sample_size
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "trigger": self.trigger,
            "effective_strategies": self.effective_strategies,
            "success_rate": self.success_rate,
            "sample_size": self.sample_size,
        }


@dataclass
class MetaLearning:
    """Meta-learning"""
    
    patterns: List[LearningPattern] = field(default_factory=list)
    
    approaches_by_context: Dict[str, str] = field(default_factory=dict)
    
    current_strategy: str = ""
    adaptation_history: List[str] = field(default_factory=list)
    
    def get_best_approach(self, context: str) -> str:
        """Get best approach for context"""
        return self.approaches_by_context.get(context, "")
    
    def to_dict(self) -> Dict:
        return {
            "current_strategy": self.current_strategy,
            "pattern_count": len(self.patterns),
            "adaptation_history": self.adaptation_history,
        }


# ============================================================
# Improvement Engine
# ============================================================

class PlanStatus:
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class ImprovementAction:
    """Improvement action"""
    action: str
    priority: int = 5
    deadline: str = ""
    status: str = "pending"


@dataclass
class ImprovementPlan:
    """Improvement plan"""
    id: str
    
    goals: List[str] = field(default_factory=list)
    
    actions: List[ImprovementAction] = field(default_factory=list)
    
    progress: float = 0  # 0-100
    
    status: str = "planning"
    
    def add_action(self, action: str, priority: int = 5):
        """Add action"""
        self.actions.append(ImprovementAction(action=action, priority=priority))
    
    def complete_action(self, action: str):
        """Complete action"""
        for a in self.actions:
            if a.action == action:
                a.status = "completed"
        self.update_progress()
    
    def update_progress(self):
        """Update progress"""
        if self.actions:
            completed = len([a for a in self.actions if a.status == "completed"])
            self.progress = (completed / len(self.actions)) * 100
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "goals": self.goals,
            "action_count": len(self.actions),
            "progress": self.progress,
            "status": self.status,
        }


__all__ = [
    'LearningSource', 'LearningInstance', 'LearningSession',
    'FeedbackType', 'FeedbackCategory', 'Feedback', 'FeedbackAnalysis',
    'ReflectionTrigger', 'Reflection', 'SelfAssessment',
    'ChangeType', 'Adaptation',
    'PerformanceMetric', 'PerformanceSummary',
    'LearningPattern', 'MetaLearning',
    'PlanStatus', 'ImprovementAction', 'ImprovementPlan',
]