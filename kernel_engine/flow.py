"""
Flow Primitives - Nodes, Edges, Branches, Loops, States

Core execution graph primitives for agent orchestration.
"""
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class NodeType(Enum):
    """Node types"""
    START = "start"
    TASK = "task"
    ACTION = "action"
    CONDITION = "condition"
    BRANCH = "branch"
    MERGE = "merge"
    LOOP = "loop"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"
    WAIT = "wait"
    HTTP = "http"
    FUNCTION = "function"
    SUBAGENT = "subagent"
    TOOL = "tool"
    LLM = "llm"
    END = "end"
    ERROR = "error"


class EdgeType(Enum):
    """Edge types"""
    DIRECT = "direct"
    CONDITIONAL = "conditional"
    DEFAULT = "default"
    ERROR = "error"
    TIMEOUT = "timeout"
    SUCCESS = "success"
    FAILURE = "failure"


class BranchType(Enum):
    """Branch types"""
    IF = "if"
    SWITCH = "switch"
    MATCH = "match"
    SPLIT = "split"


class LoopType(Enum):
    """Loop types"""
    WHILE = "while"
    UNTIL = "until"
    FOR = "for"
    COUNT = "count"
    INFINITE = "infinite"


class StateType(Enum):
    """State types"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


# ============================================================
# Nodes
# ============================================================

@dataclass
class Node:
    """Base node"""
    id: str
    type: str
    name: str
    description: str = ""
    config: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    timeout: int = 300
    retry: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "metadata": self.metadata,
            "timeout": self.timeout,
            "retry": self.retry,
        }


@dataclass
class StartNode(Node):
    def __init__(self, id: str = None, name: str = "Start"):
        super().__init__(id=id or str(uuid.uuid4()), type=NodeType.START.value, name=name)


@dataclass
class EndNode(Node):
    def __init__(self, id: str = None, name: str = "End", result: str = ""):
        super().__init__(id=id or str(uuid.uuid4()), type=NodeType.END.value, name=name, config={"result": result})


@dataclass
class TaskNode(Node):
    """Task node - execute a task"""
    def __init__(self, id: str, name: str, task_type: str, config: Dict = None):
        super().__init__(id=id, type=NodeType.TASK.value, name=name, config=config or {})
        self.config["task_type"] = task_type


@dataclass
class ActionNode(Node):
    """Action node - call function/tool"""
    def __init__(self, id: str, name: str, action: str, config: Dict = None):
        super().__init__(id=id, type=NodeType.ACTION.value, name=name, config=config or {})
        self.config["action"] = action


@dataclass
class ConditionNode(Node):
    """Condition node - branch decision"""
    def __init__(self, id: str, name: str, expression: str):
        super().__init__(id=id, type=NodeType.CONDITION.value, name=name, config={"expression": expression})


@dataclass
class BranchNode(Node):
    """Branch node - multi-way split"""
    def __init__(self, id: str, name: str, branch_type: str, cases: Dict = None):
        super().__init__(id=id, type=NodeType.BRANCH.value, name=name, config={"branch_type": branch_type, "cases": cases or {}})


@dataclass
class LoopNode(Node):
    """Loop node - iterate"""
    def __init__(self, id: str, name: str, loop_type: str, max_iterations: int = 100):
        super().__init__(id=id, type=NodeType.LOOP.value, name=name, config={"loop_type": loop_type, "max_iterations": max_iterations})


@dataclass
class ParallelNode(Node):
    """Parallel node - run branches concurrently"""
    def __init__(self, id: str, name: str, branches: List[str]):
        super().__init__(id=id, type=NodeType.PARALLEL.value, name=name, config={"branches": branches})


@dataclass
class SequenceNode(Node):
    """Sequence node - run nodes in order"""
    def __init__(self, id: str, name: str, nodes: List[str]):
        super().__init__(id=id, type=NodeType.SEQUENCE.value, name=name, config={"nodes": nodes})


@dataclass
class WaitNode(Node):
    """Wait node - pause execution"""
    def __init__(self, id: str, name: str, duration: float):
        super().__init__(id=id, type=NodeType.WAIT.value, name=name, config={"duration": duration})


@dataclass
class HttpNode(Node):
    """HTTP node - make request"""
    def __init__(self, id: str, name: str, url: str, method: str = "GET", headers: Dict = None, body: Any = None):
        super().__init__(id=id, type=NodeType.HTTP.value, name=name, config={"url": url, "method": method, "headers": headers or {}, "body": body})


@dataclass
class FunctionNode(Node):
    """Function node - execute code"""
    def __init__(self, id: str, name: str, code: str, lang: str = "python"):
        super().__init__(id=id, type=NodeType.FUNCTION.value, name=name, config={"code": code, "lang": lang})


@dataclass
class SubAgentNode(Node):
    """Sub-agent node - delegate to agent"""
    def __init__(self, id: str, name: str, agent_id: str, config: Dict = None):
        super().__init__(id=id, type=NodeType.SUBAGENT.value, name=name, agent_id=agent_id, config=config or {})
        self.config["agent_id"] = agent_id


@dataclass
class ToolNode(Node):
    """Tool node - use tool"""
    def __init__(self, id: str, name: str, tool: str, args: Dict = None):
        super().__init__(id=id, type=NodeType.TOOL.value, name=name, config={"tool": tool, "args": args or {}})


@dataclass
class LLMNode(Node):
    """LLM node - call model"""
    def __init__(self, id: str, name: str, model: str, prompt: str, params: Dict = None):
        super().__init__(id=id, type=NodeType.LLM.value, name=name, config={"model": model, "prompt": prompt, "params": params or {}})


@dataclass
class ErrorNode(Node):
    """Error node - handle errors"""
    def __init__(self, id: str, name: str = "Error"):
        super().__init__(id=id, type=NodeType.ERROR.value, name=name)


# ============================================================
# Edges
# ============================================================

@dataclass
class Edge:
    """Base edge"""
    id: str
    source: str  # node_id
    target: str  # node_id
    edge_type: str = EdgeType.DIRECT.value
    condition: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": self.edge_type,
            "condition": self.condition,
        }


@dataclass
class ConditionalEdge(Edge):
    def __init__(self, source: str, target: str, condition: str):
        super().__init__(id=f"{source}->{target}", source=source, target=target, edge_type=EdgeType.CONDITIONAL.value, condition=condition)


@dataclass
class DefaultEdge(Edge):
    def __init__(self, source: str, target: str):
        super().__init__(id=f"{source}->{target}", source=source, target=target, edge_type=EdgeType.DEFAULT.value)


@dataclass
class ErrorEdge(Edge):
    def __init__(self, source: str, target: str):
        super().__init__(id=f"{source}->{target}", source=source, target=target, edge_type=EdgeType.ERROR.value)


@dataclass
class SuccessEdge(Edge):
    def __init__(self, source: str, target: str):
        super().__init__(id=f"{source}->{target}", source=source, target=target, edge_type=EdgeType.SUCCESS.value)


@dataclass
class FailureEdge(Edge):
    def __init__(self, source: str, target: str):
        super().__init__(id=f"{source}->{target}", source=source, target=target, edge_type=EdgeType.FAILURE.value)


# ============================================================
# Execution State
# ============================================================

@dataclass
class ExecutionState:
    """State of execution"""
    execution_id: str
    node_id: str
    state: str
    input: Any = None
    output: Any = None
    error: str = ""
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "node_id": self.node_id,
            "state": self.state,
            "input": self.input,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class FlowState:
    """Flow execution state"""
    flow_id: str
    execution_id: str
    status: str = StateType.PENDING.value
    current_node: str = ""
    context: Dict = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0
    
    def to_dict(self) -> Dict:
        return {
            "flow_id": self.flow_id,
            "execution_id": self.execution_id,
            "status": self.status,
            "current_node": self.current_node,
            "context": self.context,
            "history": self.history,
        }


# ============================================================
# Flow Graph
# ============================================================

class FlowGraph:
    """Execution graph"""
    
    def __init__(self, flow_id: str = None, name: str = ""):
        self.flow_id = flow_id or str(uuid.uuid4())
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.start_node: str = ""
        self.end_nodes: Set[str] = set()
    
    def add_node(self, node: Node) -> 'FlowGraph':
        """Add node"""
        self.nodes[node.id] = node
        if node.type == NodeType.START.value:
            self.start_node = node.id
        elif node.type == NodeType.END.value:
            self.end_nodes.add(node.id)
        return self
    
    def add_edge(self, edge: Edge) -> 'FlowGraph':
        """Add edge"""
        self.edges[f"{edge.source}->{edge.target}"] = edge
        return self
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node"""
        return self.nodes.get(node_id)
    
    def get_edges_from(self, node_id: str) -> List[Edge]:
        """Get outgoing edges"""
        return [e for e in self.edges.values() if e.source == node_id]
    
    def get_edges_to(self, node_id: str) -> List[Edge]:
        """Get incoming edges"""
        return [e for e in self.edges.values() if e.target == node_id]
    
    def get_next_node(self, node_id: str, context: Dict = None) -> Optional[str]:
        """Get next node based on edges"""
        edges = self.get_edges_from(node_id)
        
        # Direct edge
        for edge in edges:
            if edge.edge_type == EdgeType.DIRECT.value:
                return edge.target
        
        # Conditional edge
        for edge in edges:
            if edge.edge_type == EdgeType.CONDITIONAL.value:
                if context and self._evaluate_condition(edge.condition, context):
                    return edge.target
        
        return None
    
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Simple condition evaluation"""
        try:
            return eval(condition, {"context": context})
        except:
            return False
    
    def validate(self) -> List[str]:
        """Validate graph"""
        errors = []
        
        # Check start node
        if not self.start_node:
            errors.append("No start node")
        
        # Check connectivity
        if self.start_node:
            visited = set()
            queue = [self.start_node]
            while queue:
                node_id = queue.pop(0)
                if node_id in visited:
                    continue
                visited.add(node_id)
                for edge in self.get_edges_from(node_id):
                    queue.append(edge.target)
            
            # Check unreachable nodes
            for node_id in self.nodes:
                if node_id not in visited:
                    errors.append(f"Unreachable node: {node_id}")
        
        return errors
    
    def to_dict(self) -> Dict:
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": {eid: e.to_dict() for eid, e in self.edges.items()},
            "start_node": self.start_node,
            "end_nodes": list(self.end_nodes),
        }


# ============================================================
# Flow Builder
# ============================================================

class FlowBuilder:
    """Build execution graphs"""
    
    def __init__(self, name: str = ""):
        self.flow = FlowGraph(name=name)
    
    def start(self, name: str = "Start") -> 'FlowBuilder':
        self.flow.add_node(StartNode(name=name))
        return self
    
    def end(self, name: str = "End") -> 'FlowBuilder':
        self.flow.add_node(EndNode(name=name))
        return self
    
    def task(self, node_id: str, name: str, task_type: str, config: Dict = None) -> 'FlowBuilder':
        self.flow.add_node(TaskNode(node_id, name, task_type, config))
        return self
    
    def action(self, node_id: str, name: str, action: str) -> 'FlowBuilder':
        self.flow.add_node(ActionNode(node_id, name, action))
        return self
    
    def condition(self, node_id: str, name: str, expression: str) -> 'FlowBuilder':
        self.flow.add_node(ConditionNode(node_id, name, expression))
        return self
    
    def branch(self, node_id: str, name: str, branch_type: str = "if") -> 'FlowBuilder':
        self.flow.add_node(BranchNode(node_id, name, branch_type))
        return self
    
    def loop(self, node_id: str, name: str, loop_type: str, max_iterations: int = 100) -> 'FlowBuilder':
        self.flow.add_node(LoopNode(node_id, name, loop_type, max_iterations))
        return self
    
    def http(self, node_id: str, name: str, url: str, method: str = "GET") -> 'FlowBuilder':
        self.flow.add_node(HttpNode(node_id, name, url, method))
        return self
    
    def function(self, node_id: str, name: str, code: str) -> 'FlowBuilder':
        self.flow.add_node(FunctionNode(node_id, name, code))
        return self
    
    def subagent(self, node_id: str, name: str, agent_id: str) -> 'FlowBuilder':
        self.flow.add_node(SubAgentNode(node_id, name, agent_id))
        return self
    
    def tool(self, node_id: str, name: str, tool: str) -> 'FlowBuilder':
        self.flow.add_node(ToolNode(node_id, name, tool))
        return self
    
    def llm(self, node_id: str, name: str, model: str, prompt: str) -> 'FlowBuilder':
        self.flow.add_node(LLMNode(node_id, name, model, prompt))
        return self
    
    def on(self, source: str, target: str, condition: str = None) -> 'FlowBuilder':
        """Add edge"""
        if condition:
            self.flow.add_edge(ConditionalEdge(source, target, condition))
        else:
            self.flow.add_edge(DefaultEdge(source, target))
        return self
    
    def on_error(self, source: str, target: str) -> 'FlowBuilder':
        self.flow.add_edge(ErrorEdge(source, target))
        return self
    
    def on_success(self, source: str, target: str) -> 'FlowBuilder':
        self.flow.add_edge(SuccessEdge(source, target))
        return self
    
    def on_failure(self, source: str, target: str) -> 'FlowBuilder':
        self.flow.add_edge(FailureEdge(source, target))
        return self
    
    def build(self) -> FlowGraph:
        """Build graph"""
        return self.flow
    
    def validate(self) -> List[str]:
        """Validate"""
        return self.flow.validate()


__all__ = [
    'NodeType', 'EdgeType', 'BranchType', 'LoopType', 'StateType',
    'Node', 'Edge', 'ExecutionState', 'FlowState', 'FlowGraph', 'FlowBuilder'
]