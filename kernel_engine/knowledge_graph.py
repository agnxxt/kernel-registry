"""
Knowledge Graph - Semantic Knowledge Representation

Graph-based knowledge representation and reasoning:
- Entities and Concepts
- Relationships (taxonomic, associative, causal)
- Knowledge Schema
- Reasoning
- Inference
- Schema Matching
"""
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import uuid
import math


# ============================================================
# Entities and Concepts
# ============================================================

class EntityType:
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    CONCEPT = "concept"
    OBJECT = "object"
    DOCUMENT = "document"
    PROCESS = "process"
    RESOURCE = "resource"


@dataclass
class KnowledgeEntity:
    """Entity in knowledge graph"""
    id: str
    name: str
    entity_type: str = "concept"
    
    properties: Dict = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    
    confidence: float = 1.0
    source: str = ""
    retrieved_at: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "confidence": self.confidence,
        }


@dataclass
class Concept:
    """Concept (taxonomic)"""
    id: str
    name: str
    
    parent: str = ""
    ancestors: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    
    definition: str = ""
    properties: Dict = field(default_factory=dict)
    
    related_concepts: List[Tuple[str, float]] = field(default_factory=list)  # (concept, similarity)
    
    is_abstract: bool = False
    is_primitive: bool = False
    
    def get_ancestors_chain(self) -> List[str]:
        """Get full ancestor chain"""
        chain = []
        current = self
        
        while current.parent:
            chain.append(current.parent)
            # Would need to fetch parent
        
        return chain
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "parent": self.parent,
            "is_abstract": self.is_abstract,
            "definition": self.definition,
        }


# ============================================================
# Relationship Types
# ============================================================

class RelationshipType:
    IS_A = "is_a"
    PART_OF = "part_of"
    HAS_PROPERTY = "has_property"
    SIMILAR_TO = "similar_to"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    ENABLES = "enables"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    MEMBER_OF = "member_of"
    LOCATED_IN = "located_in"
    OWNS = "owns"
    USES = "uses"
    AUTHORED_BY = "authored_by"
    CREATED_BY = "created_by"


@dataclass
class KnowledgeRelationship:
    """Relationship between entities"""
    id: str
    source: str
    target: str
    relationship_type: str = "related_to"
    
    properties: Dict = field(default_factory=dict)
    weight: float = 1.0
    confidence: float = 1.0
    
    source_ref: str = ""
    retrieved_at: str = ""
    
    valid_from: str = ""
    valid_to: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relationship_type": self.relationship_type,
            "weight": self.weight,
            "confidence": self.confidence,
        }


@dataclass
class CausalRelationship:
    """Causal relationship"""
    id: str
    cause: str
    effect: str
    
    mechanism: str = ""
    strength: float = 0.5
    confidence: float = 0.5
    
    causation_type: str = "contributory"  # necessary, sufficient, contributory, preventive
    evidence_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "cause": self.cause,
            "effect": self.effect,
            "strength": self.strength,
            "causation_type": self.causation_type,
        }


# ============================================================
# Knowledge Graph
# ============================================================

@dataclass
class KnowledgeGraph:
    """Knowledge graph"""
    id: str
    name: str = ""
    
    entities: Dict[str, KnowledgeEntity] = field(default_factory=dict)
    relationships: List[KnowledgeRelationship] = field(default_factory=list)
    concepts: Dict[str, Concept] = field(default_factory=dict)
    
    # Indexes
    entity_by_name: Dict[str, str] = field(default_factory=dict)
    relationships_by_type: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    
    schema: str = ""
    
    def add_entity(self, entity: KnowledgeEntity):
        """Add entity"""
        self.entities[entity.id] = entity
        self.entity_by_name[entity.name.lower()] = entity.id
        
        # Index relationship by type
        self.relationships_by_type["entity"].append(entity.id)
    
    def add_relationship(self, rel: KnowledgeRelationship):
        """Add relationship"""
        self.relationships.append(rel)
        self.relationships_by_type[rel.relationship_type].append(rel.id)
    
    def add_concept(self, concept: Concept):
        """Add concept"""
        self.concepts[concept.id] = concept
    
    def find_entity(self, name: str) -> Optional[KnowledgeEntity]:
        """Find entity by name"""
        entity_id = self.entity_by_name.get(name.lower())
        return self.entities.get(entity_id) if entity_id else None
    
    def find_relationships(self, entity_id: str,
                          relationship_type: Optional[str] = None) -> List[KnowledgeRelationship]:
        """Find relationships for entity"""
        results = []
        
        for rel in self.relationships:
            if rel.source == entity_id or rel.target == entity_id:
                if relationship_type is None or rel.relationship_type == relationship_type:
                    results.append(rel)
        
        return results
    
    def find_path(self, start: str, end: str, 
                  max_length: int = 3) -> List[List[str]]:
        """Find path between entities"""
        if start == end:
            return [[start]]
        
        paths = []
        
        def dfs(current: str, path: List[str], visited: Set[str]):
            if len(path) > max_length:
                return
            
            if current == end:
                paths.append(path[:])
                return
            
            visited.add(current)
            
            for rel in self.relationships:
                if rel.source == current and rel.target not in visited:
                    path.append(rel.target)
                    dfs(rel.target, path, visited)
                    path.pop()
                
                if rel.target == current and rel.source not in visited:
                    path.append(rel.source)
                    dfs(rel.source, path, visited)
                    path.pop()
        
        dfs(start, [start], set())
        return paths
    
    def get_common_neighbors(self, entity1: str, entity2: str) -> List[str]:
        """Get common neighbors"""
        neighbors1 = set()
        for rel in self.relationships:
            if rel.source == entity1:
                neighbors1.add(rel.target)
            elif rel.target == entity1:
                neighbors1.add(rel.source)
        
        neighbors2 = set()
        for rel in self.relationships:
            if rel.source == entity2:
                neighbors2.add(rel.target)
            elif rel.target == entity2:
                neighbors2.add(rel.source)
        
        return list(neighbors1 & neighbors2)
    
    def infer_relationship(self, source: str, target: str) -> Optional[KnowledgeRelationship]:
        """Infer relationship through transitivity"""
        # Find path
        paths = self.find_path(source, target, max_length=2)
        
        if not paths:
            return None
        
        # Get relationship from path
        for rel in self.relationships:
            if rel.source == source and rel.target == target:
                return rel
        
        return None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships),
            "concept_count": len(self.concepts),
        }


# ============================================================
# Reasoning
# ============================================================

@dataclass
class InferenceRule:
    """Inference rule"""
    id: str
    name: str
    description: str
    
    premise_pattern: str
    conclusion: str
    
    confidence: float = 1.0
    applies_to: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "premise_pattern": self.premise_pattern,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
        }


@dataclass
class InferenceResult:
    """Inference result"""
    rule: str
    premises: List[Tuple[str, Any]] = field(default_factory=list)
    conclusion: Any = None
    conclusion_entity: str = ""
    confidence: float = 1.0
    
    trace: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "rule": self.rule,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "trace": self.trace,
        }


@dataclass
class ReasoningChain:
    """Reasoning chain"""
    id: str
    steps: List[Dict] = field(default_factory=list)
    
    final_conclusion: Any = None
    overall_confidence: float = 0
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    duration: float = 0
    
    def add_step(self, step_number: int, rule: str, inputs: List[str], 
                output: Any, confidence: float):
        """Add reasoning step"""
        self.steps.append({
            "step_number": step_number,
            "rule": rule,
            "inputs": inputs,
            "output": output,
            "confidence": confidence,
        })
        
        if step_number == len(self.steps):
            self.final_conclusion = output
            self.overall_confidence = confidence
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "steps": self.steps,
            "final_conclusion": self.final_conclusion,
            "overall_confidence": self.overall_confidence,
        }


# ============================================================
# Embeddings
# ============================================================

@dataclass
class KnowledgeEmbedding:
    """Knowledge embedding"""
    entity_id: str
    embedding: List[float] = field(default_factory=list)
    
    method: str = "transE"  # transE, distMult, ComplEx, RotatE, ConvE
    dimension: int = 100
    
    similar_entities: List[Tuple[str, float]] = field(default_factory=list)
    
    def find_similar(self, kg: KnowledgeGraph, top_k: int = 10):
        """Find similar entities"""
        if not self.embedding:
            return []
        
        similarities = []
        
        # Would need embeddings for other entities
        # Simplified - use name similarity
        
        for entity_id, entity in kg.entities.items():
            if entity_id == self.entity_id:
                continue
            
            # Use name similarity
            name_sim = self._similarity(self.entity_id, entity_id)
            similarities.append((entity_id, name_sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        self.similar_entities = similarities[:top_k]
        
        return self.similar_entities
    
    def _similarity(self, id1: str, id2: str) -> float:
        """Simple similarity"""
        # Would use actual embeddings
        return 0.0
    
    def to_dict(self) -> Dict:
        return {
            "entity_id": self.entity_id,
            "embedding": self.embedding[:10],
            "similar_entities": self.similar_entities[:5],
        }


# ============================================================
# Schema Matching
# ============================================================

@dataclass
class Schema:
    """Schema"""
    id: str
    name: str
    
    entity_types: List[Dict] = field(default_factory=list)
    relationship_types: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_types": self.entity_types,
        }


@dataclass
class SchemaMapping:
    """Schema mapping"""
    source_schema_id: str
    target_schema_id: str
    
    entity_mappings: List[Tuple[str, str]] = field(default_factory=list)
    property_mappings: List[Tuple[str, str]] = field(default_factory=list)
    
    mapping_confidence: float = 0.5
    transformations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source_schema_id,
            "target": self.target_schema_id,
            "entity_mappings": self.entity_mappings,
            "mapping_confidence": self.mapping_confidence,
        }


# ============================================================
# Factory
# ============================================================

def create_knowledge_graph(id: str, name: str = "") -> KnowledgeGraph:
    """Create knowledge graph"""
    return KnowledgeGraph(id=id, name=name)


def add_entity(kg: KnowledgeGraph, name: str, 
              entity_type: str = "concept",
              properties: Dict = None) -> KnowledgeEntity:
    """Add entity to graph"""
    entity = KnowledgeEntity(
        id=str(uuid.uuid4()),
        name=name,
        entity_type=entity_type,
        properties=properties or {},
    )
    kg.add_entity(entity)
    return entity


def create_relationship(kg: KnowledgeGraph, source: str, target: str,
                        rel_type: str = RelationshipType.RELATED_TO,
                        weight: float = 1.0) -> KnowledgeRelationship:
    """Create relationship"""
    rel = KnowledgeRelationship(
        id=str(uuid.uuid4()),
        source=source,
        target=target,
        relationship_type=rel_type,
        weight=weight,
    )
    kg.add_relationship(rel)
    return rel


__all__ = [
    'EntityType',
    'KnowledgeEntity', 'Concept',
    'RelationshipType', 'KnowledgeRelationship', 'CausalRelationship',
    'KnowledgeGraph',
    'InferenceRule', 'InferenceResult', 'ReasoningChain',
    'KnowledgeEmbedding',
    'Schema', 'SchemaMapping',
    'create_knowledge_graph', 'add_entity', 'create_relationship'
]