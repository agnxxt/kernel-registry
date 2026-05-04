from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="AGenNext Kernel", version="2.0.0")


class PolicyVerdict(BaseModel):
    allowed: bool
    policy_version: str
    checked_by: str
    checked_at: str


class TaskSpec(BaseModel):
    type: Literal["tool_call", "memory_op", "workflow_step", "external_call"]
    tool: Optional[str] = None
    input: Dict[str, Any] = Field(default_factory=dict)


class ExecutionEnvelope(BaseModel):
    tenant_id: str
    execution_id: str
    agent_id: str
    runner_id: str
    task: TaskSpec
    policy_verdict: PolicyVerdict
    trace_context: Dict[str, Any] = Field(default_factory=dict)
    memory_context: Dict[str, Any] = Field(default_factory=dict)
    signature: str

    @field_validator("tenant_id", "signature")
    @classmethod
    def required_non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field must be non-empty")
        return value


class MemoryWrite(BaseModel):
    tenant_id: str
    execution_id: str
    key: str
    value: Dict[str, Any] = Field(default_factory=dict)


SUPPORTED_TOOLS = {"github.create_issue", "slack.send_message", "jira.create_ticket"}
EXECUTIONS: Dict[str, Dict[str, Any]] = {}
TRACES: Dict[str, List[Dict[str, Any]]] = {}
MEMORY: Dict[str, Dict[str, Dict[str, Any]]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_envelope(req: ExecutionEnvelope) -> None:
    if not req.policy_verdict.allowed:
        raise HTTPException(status_code=403, detail="PolicyDenied")
    if req.policy_verdict.checked_by.lower() != "runner":
        raise HTTPException(status_code=400, detail="RunnerIssuedRequired")


def _execute(req: ExecutionEnvelope) -> Dict[str, Any]:
    if req.task.type == "tool_call":
        if not req.task.tool:
            raise HTTPException(status_code=400, detail="UnsupportedTool")
        if req.task.tool not in SUPPORTED_TOOLS:
            raise HTTPException(status_code=400, detail="AdapterNotConfigured")
        return {"tool": req.task.tool, "status": "executed", "output": req.task.input}

    if req.task.type in {"memory_op", "workflow_step", "external_call"}:
        return {"type": req.task.type, "status": "executed", "output": req.task.input}

    raise HTTPException(status_code=400, detail="UnsupportedTaskType")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "kernel"}


@app.post("/api/v1/execute")
def execute(req: ExecutionEnvelope) -> Dict[str, Any]:
    _validate_envelope(req)
    result = _execute(req)
    EXECUTIONS[req.execution_id] = {
        "execution_id": req.execution_id,
        "tenant_id": req.tenant_id,
        "agent_id": req.agent_id,
        "runner_id": req.runner_id,
        "status": "completed",
        "result": result,
        "completed_at": _now(),
    }
    TRACES.setdefault(req.execution_id, []).append({"event": "executed", "at": _now(), "result": result})
    return EXECUTIONS[req.execution_id]


@app.post("/api/v1/execute/stream")
def execute_stream(req: ExecutionEnvelope) -> Dict[str, Any]:
    payload = execute(req)
    return {
        "execution_id": payload["execution_id"],
        "events": [{"type": "execution.started", "at": _now()}, {"type": "execution.completed", "at": _now()}],
    }


@app.post("/api/v1/memory")
def write_memory(req: MemoryWrite) -> Dict[str, Any]:
    if not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id required")
    MEMORY.setdefault(req.tenant_id, {})[req.key] = req.value
    TRACES.setdefault(req.execution_id, []).append({"event": "memory.write", "at": _now(), "key": req.key})
    return {"status": "stored", "tenant_id": req.tenant_id, "key": req.key}


@app.get("/api/v1/executions/{execution_id}")
def get_execution(execution_id: str) -> Dict[str, Any]:
    if execution_id not in EXECUTIONS:
        raise HTTPException(status_code=404, detail="not found")
    return EXECUTIONS[execution_id]


@app.get("/api/v1/traces/{execution_id}")
def get_traces(execution_id: str) -> Dict[str, Any]:
    return {"execution_id": execution_id, "traces": TRACES.get(execution_id, [])}
