"""
Multi-Framework Graph Adapters

Adapter implementations for:
- LangChain
- CrewAI
- AutoGen
- LlamaIndex
- Mastra
- PydanticAI
- Custom
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid


class FrameworkType(Enum):
    LANGCHAIN = "langchain"
    CREWAI = "crewai"
    AUTOGEN = "autogen"
    LLAMAINDEX = "llamaindex"
    MASTRA = "mastra"
    PYDANTICAI = "pydanticai"
    CUSTOM = "custom"


# ============================================================
# LangChain Adapter
# ============================================================

class LangChainAdapter:
    """LangChain graph adapter"""
    
    @staticmethod
    def to_lc(graph) -> Dict:
        """Convert to LangChain format"""
        return {
            "nodes": [
                {"id": n.id, "type": n.type, "name": n.name}
                for n in graph.nodes.values()
            ],
            "edges": [
                {"source": e.source, "target": e.target}
                for e in graph.edges.values()
            ]
        }
    
    @staticmethod
    def from_lc(state_graph: Dict) -> Dict:
        """Convert from LangChain format"""
        return state_graph


# ============================================================
# CrewAI Adapter
# ============================================================

class CrewAIAdapter:
    """CrewAI crew adapter"""
    
    @staticmethod
    def to_crewai(agents: List[Dict], process: str = "sequential") -> Dict:
        """Convert to CrewAI format"""
        return {
            "agents": agents,
            "process": process,
            "tasks": [],
        }
    
    @staticmethod
    def from_crewai(crew: Dict) -> Dict:
        """Convert from CrewAI format"""
        return crew


# ============================================================
# AutoGen Adapter
# ============================================================

class AutoGenAdapter:
    """AutoGen group chat adapter"""
    
    @staticmethod
    def to_autogen(agents: List[Dict], speaker_selection: str = "round_robin") -> Dict:
        """Convert to AutoGen format"""
        return {
            "participants": agents,
            "speaker_selection": speaker_selection,
        }
    
    @staticmethod
    def from_autogen(groupchat: Dict) -> Dict:
        """Convert from AutoGen format"""
        return groupchat


# ============================================================
# LlamaIndex Adapter
# ============================================================

class LlamaIndexAdapter:
    """LlamaIndex workflow adapter"""
    
    @staticmethod
    def to_llamaindex(workflow: Dict) -> Dict:
        """Convert to LlamaIndex format"""
        return workflow
    
    @staticmethod
    def from_llamaindex(workflow: Dict) -> Dict:
        """Convert from LlamaIndex format"""
        return workflow


# ============================================================
# Mastra Adapter
# ============================================================

class MastraAdapter:
    """Mastra agent adapter"""
    
    @staticmethod
    def to_mastra(agents: List[Dict], workflow: Dict = None) -> Dict:
        """Convert to Mastra format"""
        return {
            "agents": agents,
            "workflow": workflow or {},
        }
    
    @staticmethod
    def from_mastra(mastra: Dict) -> Dict:
        """Convert from Mastra format"""
        return mastra


# ============================================================
# PydanticAI Adapter
# ============================================================

class PydanticAIAdapter:
    """PydanticAI agent adapter"""
    
    @staticmethod
    def to_pydanticai(agents: List[Dict]) -> Dict:
        """Convert to PydanticAI format"""
        return {"agents": agents}
    
    @staticmethod
    def from_pydanticai(ai: Dict) -> Dict:
        """Convert from PydanticAI format"""
        return ai


# ============================================================
# Framework Registry
# ============================================================

class FrameworkRegistry:
    """Multi-framework registry"""
    
    def __init__(self):
        self.adapters = {
            FrameworkType.LANGCHAIN.value: LangChainAdapter(),
            FrameworkType.CREWAI.value: CrewAIAdapter(),
            FrameworkType.AUTOGEN.value: AutoGenAdapter(),
            FrameworkType.LLAMAINDEX.value: LlamaIndexAdapter(),
            FrameworkType.MASTRA.value: MastraAdapter(),
            FrameworkType.PYDANTICAI.value: PydanticAIAdapter(),
        }
    
    def get_adapter(self, framework: str):
        """Get adapter"""
        return self.adapters.get(framework)
    
    def convert_to(self, framework: str, graph) -> Dict:
        """Convert to framework"""
        adapter = self.get_adapter(framework)
        if adapter:
            return adapter.to_lc(graph) if framework == "langchain" else adapter.to_crewai(graph)
        return {}
    
    def list_frameworks(self) -> List[str]:
        """List frameworks"""
        return list(self.adapters.keys())


# ============================================================
# Unified Graph
# ============================================================

@dataclass
class UnifiedGraph:
    """Framework-agnostic graph"""
    graph_id: str
    name: str
    framework: str
    nodes: List[Dict] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_framework(self, framework: str) -> Dict:
        """Export to framework format"""
        registry = FrameworkRegistry()
        adapter = registry.get_adapter(framework)
        if not adapter:
            return {}
        
        if framework == FrameworkType.LANGCHAIN.value:
            return adapter.to_lc(self)
        elif framework == FrameworkType.CREWAI.value:
            return adapter.to_crewai(self.nodes)
        elif framework == FrameworkType.AUTOGEN.value:
            return adapter.to_autogen(self.nodes)
        elif framework == FrameworkType.MASTRA.value:
            return adapter.to_mastra(self.nodes)
        elif framework == FrameworkType.PYDANTICAI.value:
            return adapter.to_pydanticai(self.nodes)
        return {}
    
    def to_dict(self) -> Dict:
        return {
            "graph_id": self.graph_id,
            "name": self.name,
            "framework": self.framework,
            "nodes": self.nodes,
            "edges": self.edges,
            "metadata": self.metadata,
        }


__all__ = [
    'FrameworkType', 'UnifiedGraph', 'FrameworkRegistry',
    'LangChainAdapter', 'CrewAIAdapter', 'AutoGenAdapter',
    'LlamaIndexAdapter', 'MastraAdapter', 'PydanticAIAdapter'
]