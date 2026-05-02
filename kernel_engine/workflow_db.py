"""
Workflow DB Adapter - Persist Workflows to Database

Converts Kernel flow primitives to/from database storage (like Decide).
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


# ============================================================
# DB Models (matching Decide schema)
# ============================================================

@dataclass
class WorkflowDefinitionDB:
    """Workflow stored in DB"""
    id: str
    tenant_id: str
    name: str
    description: str = ""
    source_type: str = "kernel"  # kernel, langflow, manual
    source_json: str = ""  # Original JSON
    is_published: bool = False
    published_version_id: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "source_type": self.source_type,
            "source_json": self.source_json,
            "is_published": self.is_published,
            "published_version_id": self.published_version_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class WorkflowVersionDB:
    """Version of workflow"""
    id: str
    workflow_id: str
    version: int = 1
    changelog: str = ""
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "changelog": self.changelog,
            "created_at": self.created_at,
        }


@dataclass
class WorkflowNodeDB:
    """Node stored in DB (matching Decide)"""
    id: str
    version_id: str
    node_type: str  # start, llm, tool, condition, human_approval, end
    node_id: str  # Original node ID
    label: str = ""
    config: str = "{}"  # JSON config
    position_x: int = 0
    position_y: int = 0
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "version_id": self.version_id,
            "node_type": self.node_type,
            "node_id": self.node_id,
            "label": self.label,
            "config": self.config,
            "position_x": self.position_x,
            "position_y": self.position_y,
        }
    
    @staticmethod
    def from_flow_node(node, version_id: str) -> 'WorkflowNodeDB':
        """Create from flow node"""
        return WorkflowNodeDB(
            id=str(uuid.uuid4()),
            version_id=version_id,
            node_type=node.type,
            node_id=node.id,
            label=node.name,
            config=json.dumps(node.to_dict()),
        )


@dataclass
class WorkflowEdgeDB:
    """Edge stored in DB (matching Decide)"""
    id: str
    version_id: str
    edge_id: str = ""
    source_node_id: str = ""
    target_node_id: str = ""
    edge_type: str = "smooth"  # smooth, straight
    label: str = ""
    condition: str = "{}"  # JSON condition
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "version_id": self.version_id,
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "edge_type": self.edge_type,
            "label": self.label,
            "condition": self.condition,
        }
    
    @staticmethod
    def from_flow_edge(edge, version_id: str) -> 'WorkflowEdgeDB':
        """Create from flow edge"""
        return WorkflowEdgeDB(
            id=str(uuid.uuid4()),
            version_id=version_id,
            edge_id=edge.id,
            source_node_id=edge.source,
            target_node_id=edge.target,
            edge_type="smooth",
            condition=edge.condition if hasattr(edge, 'condition') else "{}",
        )


@dataclass
class WorkflowValidationDB:
    """Validation result"""
    id: str
    workflow_id: str
    version_id: str = ""
    is_valid: bool = False
    issues: str = "[]"  # JSON array
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "version_id": self.version_id,
            "is_valid": self.is_valid,
            "issues": json.loads(self.issues),
        }


# ============================================================
# Workflow DB Adapter
# ============================================================

class WorkflowDBAdapter:
    """Convert between Kernel flow and DB storage"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinitionDB] = {}
        self.versions: Dict[str, WorkflowVersionDB] = {}
        self.nodes: Dict[str, List[WorkflowNodeDB]] = {}
        self.edges: Dict[str, List[WorkflowEdgeDB]] = {}
    
    # --- Save to DB ---
    
    def save_flow(self, tenant_id: str, flow, name: str = "") -> WorkflowDefinitionDB:
        """Save flow to DB format"""
        # Create workflow
        wf = WorkflowDefinitionDB(
            id=flow.flow_id,
            tenant_id=tenant_id,
            name=name or flow.name,
            source_type="kernel",
            source_json=json.dumps(flow.to_dict()),
        )
        self.workflows[wf.id] = wf
        
        # Create version
        version_id = str(uuid.uuid4())
        version = WorkflowVersionDB(
            id=version_id,
            workflow_id=wf.id,
            version=1,
        )
        self.versions[version_id] = version
        
        # Add nodes
        node_dbs = []
        for node in flow.nodes.values():
            node_dbs.append(WorkflowNodeDB.from_flow_node(node, version_id))
        self.nodes[version_id] = node_dbs
        
        # Add edges
        edge_dbs = []
        for edge in flow.edges.values():
            edge_dbs.append(WorkflowEdgeDB.from_flow_edge(edge, version_id))
        self.edges[version_id] = edge_dbs
        
        return wf
    
    # --- Load from DB ---
    
    def load_flow(self, workflow_id: str):
        """Load flow from DB format"""
        from kernel_engine.flow import FlowGraph, Node, Edge
        
        wf = self.workflows.get(workflow_id)
        if not wf:
            return None
        
        # Find latest version
        versions = [v for v in self.versions.values() if v.workflow_id == workflow_id]
        if not versions:
            return None
        
        latest = max(versions, key=lambda v: v.version)
        
        # Create flow
        flow = FlowGraph(flow_id=wf.id, name=wf.name)
        
        # Add nodes
        for node_db in self.nodes.get(latest.id, []):
            node = Node(
                id=node_db.node_id,
                type=node_db.node_type,
                name=node_db.label,
                config=json.loads(node_db.config),
            )
            flow.add_node(node)
        
        # Add edges
        for edge_db in self.edges.get(latest.id, []):
            edge = Edge(
                id=edge_db.edge_id or f"{edge_db.source_node_id}->{edge_db.target_node_id}",
                source=edge_db.source_node_id,
                target=edge_db.target_node_id,
            )
            flow.add_edge(edge)
        
        return flow
    
    # --- Validate ---
    
    def validate(self, workflow_id: str) -> WorkflowValidationDB:
        """Validate workflow"""
        flow = self.load_flow(workflow_id)
        
        validation = WorkflowValidationDB(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
        )
        
        if flow:
            errors = flow.validate()
            validation.is_valid = len(errors) == 0
            validation.issues = json.dumps(errors)
        
        return validation
    
    # --- Export ---
    
    def export_workflow(self, workflow_id: str) -> Dict:
        """Export full workflow"""
        wf = self.workflows.get(workflow_id)
        if not wf:
            return {}
        
        versions = [v for v in self.versions.values() if v.workflow_id == workflow_id]
        
        return {
            "workflow": wf.to_dict(),
            "versions": [v.to_dict() for v in versions],
        }


__all__ = [
    'WorkflowDefinitionDB', 'WorkflowVersionDB', 'WorkflowNodeDB', 
    'WorkflowEdgeDB', 'WorkflowValidationDB', 'WorkflowDBAdapter'
]