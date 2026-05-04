from fastapi.testclient import TestClient

from kernel_api.main import app


client = TestClient(app)


def _payload(**overrides):
    base = {
        "tenant_id": "tenant_123",
        "execution_id": "exec_456",
        "agent_id": "agent_abc",
        "runner_id": "runner_default",
        "task": {"type": "tool_call", "tool": "github.create_issue", "input": {"title": "x"}},
        "policy_verdict": {
            "allowed": True,
            "policy_version": "v12",
            "checked_by": "runner",
            "checked_at": "2026-05-04T00:00:00Z",
        },
        "trace_context": {},
        "memory_context": {},
        "signature": "runner_sig",
    }
    base.update(overrides)
    return base


def test_execute_accepts_valid_envelope():
    r = client.post("/api/v1/execute", json=_payload())
    assert r.status_code == 200


def test_execute_rejects_missing_tenant_id():
    r = client.post("/api/v1/execute", json=_payload(tenant_id=""))
    assert r.status_code == 422


def test_execute_rejects_policy_denied():
    p = _payload()
    p["policy_verdict"]["allowed"] = False
    r = client.post("/api/v1/execute", json=p)
    assert r.status_code == 403


def test_execute_rejects_missing_signature():
    p = _payload()
    p.pop("signature")
    r = client.post("/api/v1/execute", json=p)
    assert r.status_code == 422


def test_unsupported_tool_returns_explicit_error():
    p = _payload()
    p["task"]["tool"] = "unknown.tool"
    r = client.post("/api/v1/execute", json=p)
    assert r.status_code == 400
    assert r.json()["detail"] == "AdapterNotConfigured"


def test_old_admin_endpoint_not_active():
    r = client.get("/api/v1/admin/policies")
    assert r.status_code == 404
