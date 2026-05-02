"""
Workflow Execution Engine

Execute workflows from DB or code with full lifecycle.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json
import time

from kernel_engine.flow import FlowGraph, FlowState, ExecutionState, StateType
from kernel_engine.decision import DecisionEngine


class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================
# Run Models
# ============================================================

@dataclass
class WorkflowRun:
    """Execution of a workflow"""
    id: str
    workflow_id: str
    version_id: str = ""
    tenant_id: str = ""
    status: str = WorkflowStatus.CREATED.value
    context: Dict = field(default_factory=dict)
    current_node: str = ""
    started_at: float = 0
    completed_at: float = 0
    created_by: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "version_id": self.version_id,
            "tenant_id": self.tenant_id,
            "status": self.status,
            "context": self.context,
            "current_node": self.current_node,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class NodeRun:
    """Execution of a single node"""
    id: str
    run_id: str
    node_id: str
    status: str = StateType.PENDING.value
    input: Any = None
    output: Any = None
    error: str = ""
    started_at: float = 0
    completed_at: float = 0
    retries: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "status": self.status,
            "input": self.input,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class HumanApproval:
    """Human approval step"""
    id: str
    node_id: str
    run_id: str
    approver_email: str = ""
    status: str = "pending"  # pending, approved, rejected
    comments: str = ""
    approved_by: str = ""
    approved_at: float = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "approver_email": self.approver_email,
            "status": self.status,
            "comments": self.comments,
            "approved_by": self.approved_by,
        }


# ============================================================
# Node Executors
# ============================================================

class NodeExecutor:
    """Execute individual nodes"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool"""
        self.tools[name] = func
    
    def execute(self, node, context: Dict) -> Any:
        """Execute node"""
        node_type = node.type
        
        if node_type == "llm":
            return self._execute_llm(node, context)
        elif node_type == "tool":
            return self._execute_tool(node, context)
        elif node_type == "http":
            return self._execute_http(node, context)
        elif node_type == "condition":
            return self._execute_condition(node, context)
        elif node_type == "function":
            return self._execute_function(node, context)
        elif node_type == "subagent":
            return self._execute_subagent(node, context)
        elif node_type == "human_approval":
            return self._execute_human_approval(node, context)
        else:
            return {"status": "completed", "node": node.id}
    
    def _execute_llm(self, node, context: Dict) -> Dict:
        """Execute LLM node"""
        config = node.config
        # In real implementation, call LLM
        return {
            "status": "completed",
            "response": f"LLM response for: {config.get('prompt', '')[:50]}...",
            "node": node.id,
        }
    
    def _execute_tool(self, node, context: Dict) -> Dict:
        """Execute tool node"""
        tool_name = node.config.get("tool")
        tool = self.tools.get(tool_name)
        if tool:
            result = tool(context)
            return {"status": "completed", "result": result, "node": node.id}
        return {"status": "completed", "node": node.id}
    
    def _execute_http(self, node, context: Dict) -> Dict:
        """Execute HTTP node"""
        return {"status": "completed", "node": node.id, "note": "HTTP call simulated"}
    
    def _execute_condition(self, node, context: Dict) -> Dict:
        """Execute condition node"""
        expr = node.config.get("expression", "true")
        try:
            result = eval(expr, {"context": context})
            return {"status": "completed", "result": result, "node": node.id}
        except:
            return {"status": "completed", "result": False, "node": node.id}
    
    def _execute_function(self, node, context: Dict) -> Dict:
        """Execute function node"""
        return {"status": "completed", "node": node.id}
    
    def _execute_subagent(self, node, context: Dict) -> Dict:
        """Execute sub-agent"""
        return {"status": "completed", "node": node.id}
    
    def _execute_human_approval(self, node, context: Dict) -> Dict:
        """Execute human approval"""
        return {
            "status": "awaiting_approval",
            "node": node.id,
            "message": "Human approval required",
        }


# ============================================================
# Workflow Executor
# ============================================================

class WorkflowExecutor:
    """Execute workflows"""
    
    def __init__(self):
        self.db_adapter = None  # Set from outside
        self.executor = NodeExecutor()
        self.runs: Dict[str, WorkflowRun] = {}
        self.node_runs: Dict[str, List[NodeRun]] = {}
        self.approvals: Dict[str, HumanApproval] = {}
        self.decision_engine = DecisionEngine()
    
    def set_db_adapter(self, adapter):
        """Set DB adapter"""
        self.db_adapter = adapter
    
    def start(self, workflow_id: str, tenant_id: str = "",
             context: Dict = None, created_by: str = "") -> WorkflowRun:
        """Start workflow execution"""
        run = WorkflowRun(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            context=context or {},
            status=WorkflowStatus.RUNNING.value,
            started_at=time.time(),
            created_by=created_by,
        )
        self.runs[run.id] = run
        self.node_runs[run.id] = []
        return run
    
    def execute_run(self, run_id: str, flow: FlowGraph = None) -> Dict:
        """Execute a run"""
        run = self.runs.get(run_id)
        if not run:
            return {"error": "Run not found"}
        
        # Load flow from DB if not provided
        if not flow and self.db_adapter:
            flow = self.db_adapter.load_flow(run.workflow_id)
        
        if not flow:
            return {"error": "Workflow not found"}
        
        # Execute
        current = flow.start_node
        node_runs = self.node_runs[run_id]
        
        while current:
            flow_state = FlowState(
                flow_id=run.workflow_id,
                execution_id=run.id,
                current_node=current,
            )
            
            node = flow.get_node(current)
            if not node:
                break
            
            # Create node run
            node_run = NodeRun(
                id=str(uuid.uuid4()),
                run_id=run_id,
                node_id=current,
                status=StateType.RUNNING.value,
                started_at=time.time(),
            )
            node_runs.append(node_run)
            
            # Execute
            try:
                result = self.executor.execute(node, run.context)
                
                node_run.status = StateType.COMPLETED.value
                node_run.output = result
                node_run.completed_at = time.time()
                
                # Check for approval
                if result.get("status") == "awaiting_approval":
                    run.status = WorkflowStatus.PAUSED.value
                    self._create_approval(node, run_id, result)
                    break
                
                run.context[node.id] = result
                
            except Exception as e:
                node_run.status = StateType.FAILED.value
                node_run.error = str(e)
                run.status = WorkflowStatus.FAILED.value
                break
            
            # Get next node
            current = flow.get_next_node(current, run.context)
            run.current_node = current
        
        # Check completion
        if run.status == WorkflowStatus.RUNNING.value and not current:
            run.status = WorkflowStatus.COMPLETED.value
            run.completed_at = time.time()
        
        return run.to_dict()
    
    def _create_approval(self, node, run_id: str, result: Dict):
        """Create approval"""
        approval = HumanApproval(
            id=str(uuid.uuid4()),
            node_id=node.id,
            run_id=run_id,
        )
        self.approvals[approval.id] = approval
    
    def approve(self, approval_id: str, approved: bool, 
              comments: str = "", approved_by: str = "") -> bool:
        """Approve or reject"""
        approval = self.approvals.get(approval_id)
        if not approval:
            return False
        
        approval.status = "approved" if approved else "rejected"
        approval.comments = comments
        approved_by = approved_by
        approval.approved_at = time.time()
        
        # Continue run
        if approved:
            run_id = approval.run_id
            run = self.runs.get(run_id)
            if run:
                flow = self.db_adapter.load_flow(run.workflow_id) if self.db_adapter else None
                self.execute_run(run_id, flow)
        
        return True
    
    def cancel(self, run_id: str) -> bool:
        """Cancel run"""
        run = self.runs.get(run_id)
        if not run:
            return False
        
        run.status = WorkflowStatus.CANCELLED.value
        run.completed_at = time.time()
        return True
    
    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Get run"""
        return self.runs.get(run_id)
    
    def get_node_runs(self, run_id: str) -> List[NodeRun]:
        """Get node runs"""
        return self.node_runs.get(run_id, [])
    
    def get_approval(self, node_id: str, run_id: str) -> Optional[HumanApproval]:
        """Get approval"""
        return next((a for a in self.approvals.values()
                   if a.node_id == node_id and a.run_id == run_id), None)


__all__ = [
    'WorkflowStatus', 'WorkflowRun', 'NodeRun', 'HumanApproval',
    'NodeExecutor', 'WorkflowExecutor'
]