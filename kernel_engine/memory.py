"""
Agent Memory System

Implements:
- Working memory (short-term)
- Episodic memory (experiences)
- Semantic memory (knowledge)
- Procedural memory (skills)
- Context window (LLM context)
- Vector memory (embeddings)
- Knowledge graph
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import time


class MemoryType(Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CONTEXT = "context"
    VECTOR = "vector"
    KNOWLEDGE_GRAPH = "knowledge_graph"


class MemoryPriority(Enum):
    CRITICAL = 3
    HIGH = 2
    MEDIUM = 1
    LOW = 0


@dataclass
class Memory:
    """Base memory unit"""
    id: str
    memory_type: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    priority: int = 1
    
    def touch(self):
        """Update access time"""
        self.accessed_at = time.time()
        self.access_count += 1
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.memory_type,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "access_count": self.access_count,
            "priority": self.priority,
        }


@dataclass
class Episode:
    """Episodic memory - experience"""
    id: str
    agent_id: str
    action: str
    result: str
    context: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "action": self.action,
            "result": self.result,
            "context": self.context,
            "timestamp": self.timestamp,
            "duration": self.duration,
        }


@dataclass
class Fact:
    """Semantic memory - knowledge"""
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
        }


@dataclass
class Procedure:
    """Procedural memory - skill"""
    id: str
    name: str
    description: str
    steps: List[Dict] = field(default_factory=list)
    tool: str = ""
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "tool": self.tool,
            "enabled": self.enabled,
        }


class AgentMemory:
    """Agent memory system"""
    
    def __init__(self, agent_id: str, max_working: int = 10, max_context: int = 128000):
        self.agent_id = agent_id
        self.max_working = max_working
        self.max_context = max_context
        
        # Memory stores
        self.working: Dict[str, Memory] = {}
        self.episodes: Dict[str, Episode] = {}
        self.facts: Dict[str, Fact] = {}
        self.procedures: Dict[str, Procedure] = {}
        self.context: List[Dict] = []
        self.vectors: Dict[str, Memory] = {}
        self.graph: Dict[str, List[str]] = {}
    
    # ============ Working Memory ============
    
    def store_working(self, key: str, value: str, priority: int = 1) -> Memory:
        """Store in working memory"""
        mem = Memory(
            id=key,
            memory_type=MemoryType.WORKING.value,
            content=value,
            priority=priority,
        )
        self.working[key] = mem
        self._prune_working()
        return mem
    
    def get_working(self, key: str) -> Optional[str]:
        """Retrieve from working memory"""
        mem = self.working.get(key)
        if mem:
            mem.touch()
            return mem.content
        return None
    
    def _prune_working(self):
        """Keep working memory bounded"""
        if len(self.working) > self.max_working:
            # Remove lowest priority
            sorted_mem = sorted(
                self.working.values(),
                key=lambda m: (m.priority, m.accessed_at)
            )
            for mem in sorted_mem[:len(self.working) - self.max_working]:
                del self.working[mem.id]
    
    # ============ Episodic Memory ============
    
    def store_episode(self, action: str, result: str, context: Dict = None) -> Episode:
        """Store experience"""
        ep = Episode(
            id=f"ep_{len(self.episodes)}",
            agent_id=self.agent_id,
            action=action,
            result=result,
            context=context or {},
        )
        self.episodes[ep.id] = ep
        return ep
    
    def get_episodes(self, limit: int = 10) -> List[Episode]:
        """Get recent episodes"""
        sorted_eps = sorted(
            self.episodes.values(),
            key=lambda e: e.timestamp,
            reverse=True
        )
        return sorted_eps[:limit]
    
    # ============ Semantic Memory ============
    
    def store_fact(self, subject: str, predicate: str, obj: str,
                  confidence: float = 1.0, source: str = "") -> Fact:
        """Store knowledge"""
        fact = Fact(
            id=f"fact_{len(self.facts)}",
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            source=source,
        )
        self.facts[fact.id] = fact
        return fact
    
    def query_facts(self, subject: str = None, predicate: str = None) -> List[Fact]:
        """Query knowledge"""
        results = []
        for fact in self.facts.values():
            if subject and fact.subject != subject:
                continue
            if predicate and fact.predicate != predicate:
                continue
            results.append(fact)
        return results
    
    # ============ Procedural Memory ============
    
    def store_procedure(self, name: str, description: str,
                     steps: List[Dict], tool: str = "") -> Procedure:
        """Store skill/procedure"""
        proc = Procedure(
            id=f"proc_{len(self.procedures)}",
            name=name,
            description=description,
            steps=steps,
            tool=tool,
        )
        self.procedures[proc.id] = proc
        return proc
    
    def get_procedures(self) -> List[Procedure]:
        """Get all procedures"""
        return list(self.procedures.values())
    
    # ============ Context Window ============
    
    def add_context(self, role: str, content: str, meta: Dict = None):
        """Add to context window"""
        self.context.append({
            "role": role,
            "content": content,
            "meta": meta or {},
        })
        self._prune_context()
    
    def _prune_context(self):
        """Keep context within limit (by tokens)"""
        # Simple approximation: ~4 chars per token
        max_tokens = self.max_context * 4
        total = sum(len(c["content"]) for c in self.context)
        while total > max_tokens and len(self.context) > 1:
            self.context.pop(0)
            total = sum(len(c["content"]) for c in self.context)
    
    def get_context(self) -> List[Dict]:
        """Get context"""
        return self.context
    
    # ============ Vector Memory ============
    
    def store_vector(self, key: str, content: str,
                  embedding: List[float], meta: Dict = None) -> Memory:
        """Store embedding"""
        mem = Memory(
            id=key,
            memory_type=MemoryType.VECTOR.value,
            content=content,
            embedding=embedding,
            metadata=meta or {},
        )
        self.vectors[key] = mem
        return mem
    
    def search_similar(self, query_embedding: List[float],
                      limit: int = 5, threshold: float = 0.7) -> List[Memory]:
        """Semantic search"""
        results = []
        for mem in self.vectors.values():
            if mem.embedding is None:
                continue
            score = self._cosine_similarity(query_embedding, mem.embedding)
            if score >= threshold:
                results.append((score, mem))
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity"""
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x * x for x in a) ** 0.5
        mag_b = sum(x * x for x in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)
    
    # ============ Knowledge Graph ============
    
    def add_edge(self, subject: str, predicate: str, obj: str):
        """Add graph edge"""
        key = f"{subject}:{predicate}"
        if key not in self.graph:
            self.graph[key] = []
        if obj not in self.graph[key]:
            self.graph[key].append(obj)
    
    def get_neighbors(self, subject: str) -> List[str]:
        """Get connected nodes"""
        results = []
        for key, objs in self.graph.items():
            if key.startswith(f"{subject}:"):
                results.extend(objs)
        return results
    
    # ============ Summary ============
    
    def stats(self) -> Dict:
        """Get memory stats"""
        return {
            "agent_id": self.agent_id,
            "working": len(self.working),
            "episodes": len(self.episodes),
            "facts": len(self.facts),
            "procedures": len(self.procedures),
            "context": len(self.context),
            "vectors": len(self.vectors),
            "graph_edges": len(self.graph),
        }
    
    def export(self) -> Dict:
        """Export all memory"""
        return {
            "stats": self.stats(),
            "working": [m.to_dict() for m in self.working.values()],
            "episodes": [e.to_dict() for e in self.episodes.values()],
            "facts": [f.to_dict() for f in self.facts.values()],
            "procedures": [p.to_dict() for p in self.procedures.values()],
            "context": self.context,
        }


__all__ = [
    'MemoryType', 'MemoryPriority', 'Memory', 'Episode', 'Fact', 'Procedure', 'AgentMemory'
]