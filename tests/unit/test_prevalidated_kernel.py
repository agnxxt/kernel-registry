import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient

from kernel_api.prevalidated_kernel import app

client = TestClient(app)


def _base_body(tenant="t1"):
    return {
        "tenant_id": tenant,
        "payload": {"task": "run"},
        "actor": {
            "type": "agent",
            "id": "a1",
            "tenant_id": tenant,
            "auth_method": "mtls",
            "verified_by": "AGenNext-Runner",
        },
        "prevalidation": {
            "validated_by": "AGenNext-Runner",
            "tenant_id": tenant,
            "identity_verified": True,
            "authorization_result": {"allowed": True},
            "policy_result": {"allowed": True},
            "authorization_standard": "AuthZEN",
            "authorization_engine": "OpenFGA",
            "policy_engine": "OPA",
            "authorization_check_id": "chk-1",
            "policy_decision_id": "dec-1",
        },
        "protocol": {
            "communication_protocol": "A2A",
            "client_protocol": "Agent Client Protocol",
            "network_protocol": "Agent Network Protocol",
            "protocol_version": "1.0",
            "message_id": "m-1",
            "task_id": "task-1",
        },
    }


def test_execute_rejects_missing_prevalidation():
    body = _base_body()
    del body["prevalidation"]
    r = client.post("/execute", json=body)
    assert r.status_code == 422


def test_execute_rejects_denied_policy_or_authz():
    body = _base_body()
    body["prevalidation"]["authorization_result"] = {"allowed": False}
    body["prevalidation"]["policy_result"] = {"allowed": False}
    r = client.post("/execute", json=body)
    assert r.status_code == 403


def test_execute_accepts_allowed_runner_prevalidation():
    r = client.post("/execute", json=_base_body())
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


def test_memory_rejects_missing_tenant():
    body = _base_body()
    del body["tenant_id"]
    r = client.post("/memory", json=body)
    assert r.status_code == 422


def test_trace_is_tenant_scoped():
    r = client.post("/execute", json=_base_body("ta"))
    trace_id = r.json()["trace_id"]
    forbidden = client.get(f"/trace/{trace_id}", params={"tenant_id": "tb"})
    assert forbidden.status_code == 403


def test_authzen_openfga_opa_and_protocol_metadata_persisted():
    r = client.post("/execute", json=_base_body())
    trace_id = r.json()["trace_id"]
    trace = client.get(f"/trace/{trace_id}", params={"tenant_id": "t1"})
    data = trace.json()
    assert data["authorization"]["authorization_standard"] == "AuthZEN"
    assert data["authorization"]["authorization_engine"] == "OpenFGA"
    assert data["authorization"]["policy_engine"] == "OPA"
    assert data["protocol"]["communication_protocol"] == "A2A"
    assert data["protocol"]["client_protocol"] == "Agent Client Protocol"
    assert data["protocol"]["network_protocol"] == "Agent Network Protocol"


def test_cross_tenant_actor_mismatch_rejected():
    body = _base_body("t1")
    body["actor"]["tenant_id"] = "t2"
    r = client.post("/execute", json=body)
    assert r.status_code == 403
