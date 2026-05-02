"""
Execution Context - Kernel Runtime Context

Context flows: Platform → Runner → Kernel
- Request context (input)
- Execution context (state)
- Agent context (memory)
- Session context (trace)
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import time


# ============================================================
# Execution Context
# ============================================================

@dataclass
class ExecutionContext:
    """Input context for execution"""
    execution_id: str
    tenant_id: str
    
    flow_id: str = ""
    agent_id: str = ""
    user_id: str = ""
    session_id: str = ""
    
    input_data: Any = None
    parameters: Dict = field(default_factory=dict)
    
    # Config
    framework: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 300
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: float = 0
    completed_at: float = 0
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "tenant_id": self.tenant_id,
            "flow_id": self.flow_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "input": self.input_data,
            "parameters": self.parameters,
            "framework": self.framework,
            "model": self.model,
            "created_at": self.created_at,
        }


# ============================================================
# Runtime Context
# ============================================================

@dataclass
class RuntimeContext:
    """Runtime state during execution"""
    execution_id: str
    
    current_node_id: str = ""
    current_step: int = 0
    total_steps: int = 0
    
    status: str = "pending"  # pending, running, paused, completed, failed, cancelled
    
    variables: Dict = field(default_factory=dict)
    
    history: List[Dict] = field(default_factory=list)
    
    callbacks: List[Dict] = field(default_factory=list)
    
    def add_history(self, node_id: str, input_data: Any, output_data: Any, error: str = ""):
        """Add to history"""
        self.history.append({
            "node_id": node_id,
            "input": input_data,
            "output": output_data,
            "error": error,
            "started_at": time.time(),
            "completed_at": time.time() if output_data else 0,
        })
    
    def set_variable(self, key: str, value: Any):
        """Set variable"""
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get variable"""
        return self.variables.get(key, default)
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "current_node_id": self.current_node_id,
            "current_step": self.current_step,
            "status": self.status,
            "variables": self.variables,
            "history": self.history,
        }


# ============================================================
# Agent Context
# ============================================================

@dataclass
class AgentRuntimeContext:
    """Agent context with memory and personality"""
    agent_id: str
    
    # Working memory
    working: Dict[str, str] = field(default_factory=dict)
    
    # Episodic memory
    episodes: List[Dict] = field(default_factory=list)
    
    # Semantic memory
    facts: List[Dict] = field(default_factory=list)
    
    # Context window
    context_window: List[Dict] = field(default_factory=list)
    
    # Personality
    name: str = ""
    style: str = "conversational"
    tone: str = "professional"
    
    def add_working(self, key: str, value: str):
        """Add to working memory"""
        self.working[key] = value
    
    def get_working(self, key: str) -> Optional[str]:
        """Get from working memory"""
        return self.working.get(key)
    
    def add_episode(self, action: str, result: str):
        """Add episode"""
        self.episodes.append({
            "action": action,
            "result": result,
            "timestamp": time.time(),
        })
    
    def add_fact(self, subject: str, predicate: str, obj: str):
        """Add fact"""
        self.facts.append({
            "subject": subject,
            "predicate": predicate,
            "object": obj,
        })
    
    def add_to_context(self, role: str, content: str):
        """Add to LLM context"""
        self.context_window.append({
            "role": role,
            "content": content,
        })
        # Keep context bounded (max ~128k tokens)
        if len(self.context_window) > 60:
            self.context_window.pop(0)
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "working": self.working,
            "episodes": self.episodes[-10:],  # Last 10
            "facts": self.facts,
            "context_window": self.context_window,
            "personality": {
                "name": self.name,
                "style": self.style,
                "tone": self.tone,
            },
        }


# ============================================================
# Session Context
# ============================================================

@dataclass
class SessionContext:
    """Session context - traces and usage"""
    session_id: str
    tenant_id: str
    
    # Trace spans
    spans: List[Dict] = field(default_factory=list)
    
    # Usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    execution_time_ms: int = 0
    
    # Errors
    errors: List[Dict] = field(default_factory=list)
    
    start_time: float = field(default_factory=time.time)
    
    def add_span(self, name: str, parent_id: str = "",
                input_data: Any = None) -> str:
        """Add span"""
        span_id = str(uuid.uuid4())
        self.spans.append({
            "id": span_id,
            "name": name,
            "parent_id": parent_id,
            "input": input_data,
            "start_time": time.time(),
        })
        return span_id
    
    def end_span(self, span_id: str, output: Any, metadata: Dict = None):
        """End span"""
        for span in self.spans:
            if span.get("id") == span_id:
                span["output"] = output
                span["end_time"] = time.time()
                span["metadata"] = metadata or {}
                break
    
    def add_error(self, code: str, message: str):
        """Add error"""
        self.errors.append({
            "code": code,
            "message": message,
            "timestamp": time.time(),
        })
    
    def finish(self):
        """Finish session"""
        self.execution_time_ms = int((time.time() - self.start_time) * 1000)
        self.total_tokens = self.input_tokens + self.output_tokens
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "spans": self.spans,
            "usage": {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "total_tokens": self.total_tokens,
                "execution_time_ms": self.execution_time_ms,
            },
            "errors": self.errors,
        }


# ============================================================
# Context Factory
# ============================================================

def create_execution_context(tenant_id: str, flow_id: str = "",
                       agent_id: str = "", user_id: str = "",
                       input_data: Any = None) -> ExecutionContext:
    """Create execution context"""
    return ExecutionContext(
        execution_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        flow_id=flow_id,
        agent_id=agent_id,
        user_id=user_id,
        input_data=input_data,
    )


def create_runtime_context(execution_id: str) -> RuntimeContext:
    """Create runtime context"""
    return RuntimeContext(execution_id=execution_id)


def create_agent_context(agent_id: str, name: str = "",
                     style: str = "conversational",
                     tone: str = "professional") -> AgentRuntimeContext:
    """Create agent context"""
    return AgentRuntimeContext(
        agent_id=agent_id,
        name=name,
        style=style,
        tone=tone,
    )


def create_session_context(session_id: str, tenant_id: str) -> SessionContext:
    """Create session context"""
    return SessionContext(
        session_id=session_id,
        tenant_id=tenant_id,
    )


__all__ = [
    'ExecutionContext', 'RuntimeContext', 
    'AgentRuntimeContext', 'SessionContext',
    'create_execution_context', 'create_runtime_context',
    'create_agent_context', 'create_session_context'
]