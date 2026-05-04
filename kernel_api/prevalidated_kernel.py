from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

RUNNER_ID = "AGenNext-Runner"


class PrevalidationMetadata(BaseModel):
    validated_by: str
    tenant_id: Optional[str] = None
    identity_verified: Optional[bool] = None
    authorization_standard: Optional[str] = None
    authorization_engine: Optional[str] = None
    authorization_engines: Optional[List[str]] = None
    policy_engine: Optional[str] = None
    policy_result: Optional[Dict[str, Any]] = None
    authorization_result: Optional[Dict[str, Any]] = None
    policy_decision_id: Optional[str] = None
    authorization_check_id: Optional[str] = None
    policy_bundle_version: Optional[str] = None
    subject: Optional[Dict[str, Any]] = None
    resource: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    relation: Optional[str] = None
    object: Optional[str] = None


class ActorMetadata(BaseModel):
    type: str
    id: str
    tenant_id: str
    auth_method: str
    verified_by: str


class ProtocolMetadata(BaseModel):
    communication_protocol: Optional[str] = None
    client_protocol: Optional[str] = None
    network_protocol: Optional[str] = None
    protocol_version: Optional[str] = None
    local_agent_id: Optional[str] = None
    remote_agent_id: Optional[str] = None
    agent_card_url: Optional[str] = None
    task_id: Optional[str] = None
    message_id: Optional[str] = None
    session_id: Optional[str] = None
    capability_id: Optional[str] = None
    skill_id: Optional[str] = None
    remote_agent_verified: Optional[bool] = None


class KernelRequest(BaseModel):
    tenant_id: str
    execution_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    actor: Optional[ActorMetadata] = None
    prevalidation: PrevalidationMetadata
    protocol: Optional[ProtocolMetadata] = None


app = FastAPI(title="AGenNext Kernel (Prevalidated)", version="0.1.0")
executions: Dict[str, Dict[str, Any]] = {}
traces: Dict[str, Dict[str, Any]] = {}
memory_store: Dict[str, Dict[str, Any]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_allowed(result: Optional[Dict[str, Any]]) -> bool:
    if not result:
        return False
    return any(result.get(k) is True for k in ["allowed", "allow", "authorized"])


def _validate_request(req: KernelRequest, require_actor: bool) -> str:
    if not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if not req.payload:
        raise HTTPException(status_code=400, detail="payload is required")
    if req.prevalidation.validated_by != RUNNER_ID:
        raise HTTPException(status_code=403, detail="prevalidation must come from AGenNext-Runner")
    if not (_is_allowed(req.prevalidation.authorization_result) or _is_allowed(req.prevalidation.policy_result)):
        raise HTTPException(status_code=403, detail="prevalidation denied or missing allowed decision")
    if req.prevalidation.tenant_id and req.prevalidation.tenant_id != req.tenant_id:
        raise HTTPException(status_code=403, detail="cross-tenant mismatch in prevalidation")

    if require_actor:
        if req.actor is None:
            raise HTTPException(status_code=400, detail="actor metadata is required")
        if req.actor.type != "agent" or req.actor.verified_by != RUNNER_ID:
            raise HTTPException(status_code=403, detail="actor identity not verified by Runner")
        if req.actor.tenant_id != req.tenant_id:
            raise HTTPException(status_code=403, detail="cross-tenant mismatch in actor")
        if req.prevalidation.identity_verified is not True:
            raise HTTPException(status_code=403, detail="identity_verified must be true")

    return req.execution_id or str(uuid4())


def _build_trace(execution_id: str, tenant_id: str, req: KernelRequest, status: str, result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "trace_id": execution_id,
        "tenant_id": tenant_id,
        "status": status,
        "result": result,
        "audit": [
            {"event": "runner.prevalidation.received", "timestamp": _now(), "metadata": req.prevalidation.model_dump()},
            {"event": "execution.started", "timestamp": _now(), "actor": req.actor.model_dump() if req.actor else None},
            {"event": "execution.completed", "timestamp": _now()},
        ],
        "authorization": req.prevalidation.model_dump(),
        "identity": req.actor.model_dump() if req.actor else None,
        "protocol": req.protocol.model_dump() if req.protocol else None,
    }


@app.post("/execute")
def execute(req: KernelRequest) -> Dict[str, Any]:
    execution_id = _validate_request(req, require_actor=True)
    result = {"echo": req.payload}
    trace = _build_trace(execution_id, req.tenant_id, req, "completed", result)
    executions[execution_id] = {"tenant_id": req.tenant_id, "status": "completed", "result": result}
    traces[execution_id] = trace
    return {"execution_id": execution_id, "status": "completed", "result": result, "trace_id": execution_id}


@app.post("/stream")
def stream(req: KernelRequest) -> Dict[str, Any]:
    execution_id = _validate_request(req, require_actor=True)
    traces[execution_id] = _build_trace(execution_id, req.tenant_id, req, "streaming-placeholder", {"message": "streaming placeholder"})
    return {
        "execution_id": execution_id,
        "status": "accepted",
        "events": ["execution.started", "execution.completed"],
        "note": "Streaming infrastructure placeholder; Runner handles orchestration.",
        "trace_id": execution_id,
    }


@app.post("/memory")
def memory(req: KernelRequest) -> Dict[str, Any]:
    execution_id = _validate_request(req, require_actor=False)
    key = str(req.payload.get("key", "default"))
    op = req.payload.get("op", "read")
    tenant_memory = memory_store.setdefault(req.tenant_id, {})
    if op == "write":
        tenant_memory[key] = req.payload.get("value")
        value = tenant_memory[key]
        event = "memory.write"
    else:
        value = tenant_memory.get(key)
        event = "memory.read"

    traces[execution_id] = {
        "trace_id": execution_id,
        "tenant_id": req.tenant_id,
        "status": "completed",
        "audit": [
            {"event": "runner.prevalidation.received", "timestamp": _now(), "metadata": req.prevalidation.model_dump()},
            {"event": event, "timestamp": _now(), "key": key},
        ],
        "authorization": req.prevalidation.model_dump(),
        "identity": req.actor.model_dump() if req.actor else None,
        "protocol": req.protocol.model_dump() if req.protocol else None,
    }
    return {"execution_id": execution_id, "status": "completed", "key": key, "value": value, "trace_id": execution_id}


@app.get("/trace/{trace_id}")
def get_trace(trace_id: str, tenant_id: str) -> Dict[str, Any]:
    trace = traces.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="trace not found")
    if trace["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="tenant scope violation")
    return trace
