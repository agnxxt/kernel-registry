"""
OpenFGA - Open Fine-Grained Authorization
Google Zanzibar-style fine-grained permissions (FGA) model.

This implements the OpenFGA model DSL and tuple store API.
"""
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


# ============================================================
# FGA Model DSL Types
# ============================================================

class RelationType(Enum):
    USER = "user"
    COMPUTED = "computed"
    TUPLESET = "tupleset"
    Union = "union"


@dataclass
class RelationDef:
    """Relation definition"""
    name: str
    relation_types: Set[RelationType] = field(default_factory=set)
    rewrite: Dict = field(default_factory=dict)  # rewrite rules
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "relation_types": [rt.value for rt in self.relation_types],
            "rewrite": self.rewrite,
        }


@dataclass
class TypeDefinition:
    """Type definition (like user, document, etc)"""
    type: str
    relations: Dict[str, RelationDef] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "relations": {k: v.to_dict() for k, v in self.relations.items()},
        }


@dataclass
class FGAModel:
    """FGA Authorization Model"""
    model_id: str = field(default_factory=lambda: f"fga_{uuid.uuid4().hex[:8]}")
    schema_version: str = "1.1"
    types: Dict[str, TypeDefinition] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.model_id,
            "schema_version": self.schema_version,
            "type_definitions": [t.to_dict() for t in self.types.values()],
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "FGAModel":
        model = cls(model_id=data.get("id", ""))
        model.schema_version = data.get("schema_version", "1.1")
        for td in data.get("type_definitions", []):
            tdef = TypeDefinition(type=td["type"])
            for rn, rd in td.get("relations", {}).items():
                rtypes = [RelationType(rt) for rt in rd.get("relation_types", [])]
                tdef.relations[rn] = RelationDef(rn, set(rtypes), rd.get("rewrite", {}))
            model.types[td["type"]] = tdef
        return model


# ============================================================
# Tuple Store
# ============================================================

@dataclass
class Tuple:
    """Authorization tuple"""
    object: str  # format: "type:id"
    relation: str
    user: str    # format: "type:id" or "user:*" or "user:id"
    
    def to_key(self) -> str:
        return f"{self.object}#{self.relation}@{self.user}"
    
    def to_dict(self) -> Dict:
        return {"object": self.object, "relation": self.relation, "user": self.user}
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Tuple":
        return cls(object=d["object"], relation=d["relation"], user=d["user"])


class TupleStore:
    """Tuple store with optimized lookups"""
    
    def __init__(self):
        # Primary index: object#relation -> Set[user]
        self.by_object: Dict[str, Dict[str, Set[str]]] = {}
        # Index: user -> Set[object#relation]
        self.by_user: Dict[str, Set[str]] = {}
        # All tuples
        self.all_tuples: Set[str] = set()
    
    def write(self, tuple: Tuple) -> bool:
        """Write tuple"""
        key = tuple.to_key()
        if key in self.all_tuples:
            return False  # Already exists
        
        self.all_tuples.add(key)
        
        # Index by object
        if tuple.object not in self.by_object:
            self.by_object[tuple.object] = {}
        if tuple.relation not in self.by_object[tuple.object]:
            self.by_object[tuple.object][tuple.relation] = set()
        self.by_object[tuple.object][tuple.relation].add(tuple.user)
        
        # Index by user
        if tuple.user not in self.by_user:
            self.by_user[tuple.user] = set()
        self.by_user[tuple.user].add(key)
        
        return True
    
    def delete(self, tuple: Tuple) -> bool:
        """Delete tuple"""
        key = tuple.to_key()
        if key not in self.all_tuples:
            return False
        
        self.all_tuples.discard(key)
        
        # Remove from object index
        if tuple.object in self.by_object:
            if tuple.relation in self.by_object[tuple.object]:
                self.by_object[tuple.object][tuple.relation].discard(tuple.user)
        
        # Remove from user index
        if tuple.user in self.by_user:
            self.by_user[tuple.user].discard(key)
        
        return True
    
    def read(self, object: str = None, relation: str = None, 
            user: str = None) -> List[Tuple]:
        """Read tuples matching filter"""
        results = []
        
        if object:
            if object not in self.by_object:
                return []
            rels = self.by_object[object]
            if relation:
                users = rels.get(relation, set())
                for u in users:
                    results.append(Tuple(object, relation, u))
            else:
                for r, users in rels.items():
                    for u in users:
                        results.append(Tuple(object, r, u))
        elif user and user in self.by_user:
            for key in self.by_user[user]:
                obj, rel, usr = key.rsplit("#", 1)[0], key.rsplit("#", 1)[1].rsplit("@", 1)[0], key.rsplit("@", 1)[1]
                results.append(Tuple(obj, rel, usr))
        
        return results
    
    def read_by_type(self, object_type: str) -> List[Tuple]:
        """All tuples for a type"""
        results = []
        prefix = f"{object_type}:"
        for obj in self.by_object:
            if obj.startswith(prefix):
                for rel, users in self.by_object[obj].items():
                    for u in users:
                        results.append(Tuple(obj, rel, u))
        return results


# ============================================================
# Check Engine
# ============================================================

class FGAChecker:
    """Fine-grained authorization checker"""
    
    def __init__(self):
        self.model: Optional[FGAModel] = None
        self.tuple_store = TupleStore()
        self.cache: Dict[str, bool] = {}  # Cache results
    
    def set_model(self, model: FGAModel):
        """Set authorization model"""
        self.model = model
        self.cache.clear()
    
    def write(self, tuple: Tuple) -> bool:
        """Write tuple"""
        self.cache.clear()
        return self.tuple_store.write(tuple)
    
    def delete(self, tuple: Tuple) -> bool:
        """Delete tuple"""
        self.cache.clear()
        return self.tuple_store.delete(tuple)
    
    def check(self, object: str, relation: str, user: str) -> bool:
        """Check if user has relation to object"""
        cache_key = f"{object}#{relation}@{user}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Direct tuple check
        direct = self.tuple_store.read(object, relation, user)
        if direct:
            self.cache[cache_key] = True
            return True
        
        # Computed relations via model
        if self.model and object.split(":")[0] in self.model.types:
            type_def = self.model.types[object.split(":")[0]]
            if relation in type_def.relations:
                rel_def = type_def.relations[relation]
                
                # Handle computed (union) relations
                if RelationType.COMPUTED in rel_def.relation_types:
                    # Check rewritten relations
                    for rewrite in rel_def.rewrite.get("union", []):
                        if "computedUserset" in rewrite:
                            # e.g., owner -> user:... or viewer -> writer
                            computed_relation = rewrite["computedUserset"]["relation"]
                            # Recursively check
                            if self.check(object, computed_relation, user):
                                self.cache[cache_key] = True
                                return True
                
                # Handle tupleset relations
                if RelationType.TUPLESET in rel_def.relation_types:
                    # Check related users via tupleset
                    ts_rel = rel_def.rewrite.get("tupleset", {}).get("relation")
                    if ts_rel:
                        # Get all users who have ts_rel
                        related = self.tuple_store.read(object, ts_rel)
                        for t in related:
                            if self.check(t.user, relation, user):
                                self.cache[cache_key] = True
                                return True
        
        # Check wildcard
        if user != "*":
            wildcard = self.tuple_store.read(object, relation, "user:*")
            if wildcard:
                self.cache[cache_key] = True
                return True
        
        self.cache[cache_key] = False
        return False
    
    def expand(self, object: str, relation: str) -> List[str]:
        """Expand relation to users"""
        direct = self.tuple_store.read(object, relation)
        users = [t.user for t in direct]
        
        # Handle computed relations
        if self.model and object.split(":")[0] in self.model.types:
            type_def = self.model.types[object.split(":")[0]]
            if relation in type_def.relations:
                rel_def = type_def.relations[relation]
                if RelationType.COMPUTED in rel_def.relation_types:
                    for rewrite in rel_def.rewrite.get("union", []):
                        if "computedUserset" in rewrite:
                            comp_rel = rewrite["computedUserset"]["relation"]
                            expanded = self.expand(object, comp_rel)
                            users.extend(expanded)
        
        return list(set(users))


# ============================================================
# FGA Server (API wrapper)
# ============================================================

class FGA:
    """OpenFGA server"""
    
    def __init__(self):
        self.models: Dict[str, FGAModel] = {}
        self.tuple_stores: Dict[str, TupleStore] = {}  # by model_id
        self.default_model_id: Optional[str] = None
    
    def create_model(self, model: FGAModel) -> str:
        """Create authorization model"""
        self.models[model.model_id] = model
        self.tuple_stores[model.model_id] = TupleStore()
        if not self.default_model_id:
            self.default_model_id = model.model_id
        return model.model_id
    
    def get_model(self, model_id: str = None) -> Optional[FGAModel]:
        """Get model"""
        return self.models.get(model_id or self.default_model_id)
    
    def write(self, tuples: List[Tuple], model_id: str = None) -> bool:
        """Write tuples"""
        store = self.tuple_stores.get(model_id or self.default_model_id)
        if not store:
            return False
        checker = FGAChecker()
        checker.model = self.get_model(model_id)
        checker.tuple_store = store
        for t in tuples:
            checker.write(t)
        return True
    
    def check(self, object: str, relation: str, user: str, 
              model_id: str = None) -> bool:
        """Check permission"""
        checker = FGAChecker()
        checker.model = self.get_model(model_id)
        checker.tuple_store = self.tuple_stores.get(model_id or self.default_model_id, TupleStore())
        return checker.check(object, relation, user)
    
    def read(self, object: str = None, relation: str = None,
            user: str = None, model_id: str = None) -> List[Tuple]:
        """Read tuples"""
        store = self.tuple_stores.get(model_id or self.default_model_id)
        if not store:
            return []
        return store.read(object, relation, user)


__all__ = [
    'FGA', 'FGAModel', 'TypeDefinition', 'RelationDef', 'RelationType',
    'Tuple', 'TupleStore', 'FGAChecker'
]