from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

RUNNER_ID = "AGenNext-Runner"
MAX_PAYLOAD_KEYS = int(os.getenv("KERNEL_MAX_PAYLOAD_KEYS", "256"))
MAX_KEY_LEN = int(os.getenv("KERNEL_MAX_MEMORY_KEY_LEN", "256"))
RUNNER_SHARED_SECRET = os.getenv("RUNNER_SHARED_SECRET")
DB_PATH = os.getenv("KERNEL_STATE_DB", "/tmp/kernel_prevalidated.db")


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


class StateStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = Lock()
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.lock:
            with self._connect() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS executions (execution_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, status TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL)""")
                conn.execute("""CREATE TABLE IF NOT EXISTS traces (trace_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, trace_json TEXT NOT NULL, created_at TEXT NOT NULL)""")
                conn.execute("""CREATE TABLE IF NOT EXISTS memory (tenant_id TEXT NOT NULL, mem_key TEXT NOT NULL, value_json TEXT, updated_at TEXT NOT NULL, PRIMARY KEY (tenant_id, mem_key))""")
                conn.execute("""CREATE TABLE IF NOT EXISTS idempotency (tenant_id TEXT NOT NULL, idem_key TEXT NOT NULL, response_json TEXT NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY (tenant_id, idem_key))""")

    def put_execution(self, execution_id: str, tenant_id: str, status: str, result: Dict[str, Any]):
        with self.lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO executions VALUES (?, ?, ?, ?, ?)",
                    (execution_id, tenant_id, status, json.dumps(result), _now()),
                )

    def put_trace(self, trace_id: str, tenant_id: str, trace: Dict[str, Any]):
        with self.lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO traces VALUES (?, ?, ?, ?)",
                    (trace_id, tenant_id, json.dumps(trace), _now()),
                )

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT trace_json FROM traces WHERE trace_id = ?", (trace_id,)).fetchone()
            return json.loads(row["trace_json"]) if row else None

    def write_memory(self, tenant_id: str, key: str, value: Any):
        with self.lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO memory VALUES (?, ?, ?, ?)",
                    (tenant_id, key, json.dumps(value), _now()),
                )

    def read_memory(self, tenant_id: str, key: str) -> Any:
        with self._connect() as conn:
            row = conn.execute("SELECT value_json FROM memory WHERE tenant_id = ? AND mem_key = ?", (tenant_id, key)).fetchone()
            return json.loads(row["value_json"]) if row else None

    def get_idempotent_response(self, tenant_id: str, idem_key: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT response_json FROM idempotency WHERE tenant_id = ? AND idem_key = ?", (tenant_id, idem_key)).fetchone()
            return json.loads(row["response_json"]) if row else None

    def put_idempotent_response(self, tenant_id: str, idem_key: str, response: Dict[str, Any]):
        with self.lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO idempotency VALUES (?, ?, ?, ?)",
                    (tenant_id, idem_key, json.dumps(response), _now()),
                )


app = FastAPI(title="AGenNext Kernel (Prevalidated)", version="0.2.0")
store = StateStore(DB_PATH)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_allowed(result: Optional[Dict[str, Any]]) -> bool:
    if not result:
        return False
    return any(result.get(k) is True for k in ["allowed", "allow", "authorized"])


def _verify_runner_signature(raw_body: bytes, signature: Optional[str]):
    if not RUNNER_SHARED_SECRET:
        return
    if not signature:
        raise HTTPException(status_code=401, detail="missing runner signature")
    expected = hmac.new(RUNNER_SHARED_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="invalid runner signature")


def _validate_request(req: KernelRequest, require_actor: bool) -> str:
    if not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if not req.payload:
        raise HTTPException(status_code=400, detail="payload is required")
    if len(req.payload.keys()) > MAX_PAYLOAD_KEYS:
        raise HTTPException(status_code=413, detail="payload too large")
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


def _build_trace(execution_id: str, tenant_id: str, req: KernelRequest, status: str, result: Dict[str, Any], event: str = "execution.completed") -> Dict[str, Any]:
    return {
        "trace_id": execution_id,
        "tenant_id": tenant_id,
        "status": status,
        "result": result,
        "audit": [
            {"event": "runner.prevalidation.received", "timestamp": _now(), "metadata": req.prevalidation.model_dump()},
            {"event": "execution.started", "timestamp": _now(), "actor": req.actor.model_dump() if req.actor else None},
            {"event": event, "timestamp": _now()},
        ],
        "authorization": req.prevalidation.model_dump(),
        "identity": req.actor.model_dump() if req.actor else None,
        "protocol": req.protocol.model_dump() if req.protocol else None,
    }


@app.post("/execute")
def execute(req: KernelRequest, x_runner_signature: Optional[str] = Header(default=None), x_idempotency_key: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _verify_runner_signature(req.model_dump_json().encode(), x_runner_signature)
    if x_idempotency_key:
        cached = store.get_idempotent_response(req.tenant_id, x_idempotency_key)
        if cached:
            return cached

    execution_id = _validate_request(req, require_actor=True)
    result = {"echo": req.payload}
    trace = _build_trace(execution_id, req.tenant_id, req, "completed", result)
    store.put_execution(execution_id, req.tenant_id, "completed", result)
    store.put_trace(execution_id, req.tenant_id, trace)
    response = {"execution_id": execution_id, "status": "completed", "result": result, "trace_id": execution_id}
    if x_idempotency_key:
        store.put_idempotent_response(req.tenant_id, x_idempotency_key, response)
    return response


@app.post("/stream")
def stream(req: KernelRequest, x_runner_signature: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _verify_runner_signature(req.model_dump_json().encode(), x_runner_signature)
    execution_id = _validate_request(req, require_actor=True)
    trace = _build_trace(execution_id, req.tenant_id, req, "streaming-placeholder", {"message": "streaming placeholder"}, event="execution.completed")
    store.put_trace(execution_id, req.tenant_id, trace)
    return {"execution_id": execution_id, "status": "accepted", "events": ["execution.started", "execution.completed"], "note": "Streaming infrastructure placeholder; Runner handles orchestration.", "trace_id": execution_id}


@app.post("/memory")
def memory(req: KernelRequest, x_runner_signature: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _verify_runner_signature(req.model_dump_json().encode(), x_runner_signature)
    execution_id = _validate_request(req, require_actor=False)
    key = str(req.payload.get("key", "default"))
    if len(key) > MAX_KEY_LEN:
        raise HTTPException(status_code=400, detail="memory key too long")

    op = req.payload.get("op", "read")
    if op == "write":
        store.write_memory(req.tenant_id, key, req.payload.get("value"))
        value = req.payload.get("value")
        event = "memory.write"
    else:
        value = store.read_memory(req.tenant_id, key)
        event = "memory.read"

    trace = _build_trace(execution_id, req.tenant_id, req, "completed", {"key": key, "value": value}, event=event)
    store.put_trace(execution_id, req.tenant_id, trace)
    return {"execution_id": execution_id, "status": "completed", "key": key, "value": value, "trace_id": execution_id}


@app.get("/trace/{trace_id}")
def get_trace(trace_id: str, tenant_id: str) -> Dict[str, Any]:
    trace = store.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="trace not found")
    if trace["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="tenant scope violation")
    return trace
