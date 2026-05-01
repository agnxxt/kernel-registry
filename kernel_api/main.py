from kernel_engine.lifecycle_engine import LifecycleEngine
from kernel_engine.authz_caas.caas_gateway import CaasGateway
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
import json
from datetime import datetime

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends
import secrets
from kernel_engine.secret_kernel import SecretKernel

security = HTTPBasic()

def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Quick fix: In a real system this should check against a secure store
    # For now, we secure the endpoint by checking against the SecretKernel's master key
    sk = SecretKernel()
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, sk.get_master_key())
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

from kernel_engine.validator import KernelValidator
from kernel_engine.cyber_cai.meta_cognition import TheoryIdentifier
from kernel_engine.mlflow_tracker import KernelMLflowTracker
from kernel_engine.orchestrator import CognitiveOrchestrator
from kernel_engine.cyber_cai.watchdog import RogueWatchdog
from kernel_engine.gatekeeper import ToolGatekeeper
from kernel_engine.discovery import DiscoveryEngine
from kernel_engine.identity import IdentityTrustManager
from kernel_engine.graph_adapter import GraphAdapter
from kernel_engine.executor import ActionExecutor
from kernel_engine.cyber_cai.model_runner import CognitiveModelRunner
from kernel_engine.policy_engine import PolicyEngine
from kernel_engine.learning_loop import LearningLoop
from kernel_engine.feature_store import CognitiveFeatureStore
from persistence.models.identity import CanonicalIdentity, RegistryRecord
from persistence.db import SessionLocal


from kernel_engine.telemetry import setup_telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = setup_telemetry("kernel-api")

app = FastAPI(title="Agent Kernel Platform", version="1.0.0")

# --- System Singleton Registry ---
validator = KernelValidator("schemas/_semantic-extension.schema.json")
identifier = TheoryIdentifier()
tracker = KernelMLflowTracker()
watchdog = RogueWatchdog()
orchestrator = CognitiveOrchestrator(watchdog=watchdog)
discovery = DiscoveryEngine()
identity_manager = IdentityTrustManager()
graph = GraphAdapter()
executor = ActionExecutor(caas_gateway=caas)
model_runner = CognitiveModelRunner()
secrets = SecretKernel()
# policies = PolicyEngine() # Wrapped in CAAS
learning = LearningLoop(tracker=tracker)
feature_store = CognitiveFeatureStore()
caas = CaasGateway()
lifecycle = LifecycleEngine()

# Telemetry WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

telemetry_manager = ConnectionManager()

# --- API Endpoints ---

@app.websocket("/ws/telemetry")
async def telemetry_endpoint(websocket: WebSocket):
    await telemetry_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        telemetry_manager.disconnect(websocket)

@app.post("/api/v1/action")
async def process_action(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Unified entry point for all governed agent actions.
    """
    # 1. Schema Validation
    is_valid, err = validator.validate_artifact(data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Schema Violation: {err}")

    agent_id = data.get("agent", {}).get("name", "unknown")
    action_id = str(uuid.uuid4())
    data["id"] = action_id

    # 2. Epistemic Trust Check
    trust_score = identity_manager.get_trust_score(agent_id)
    features = feature_store.get_agent_features(agent_id)

    # 3. Policy Evaluation (Deontic Constraints)
    # Identify current user for FGA check (default to admin for now)
    current_user = "admin"
    context = {"weather": "Clear", "goal_alignment": 0.85, "trust_score": trust_score, "user_id": current_user}
    policy_result = caas.pre_access_audit(agent_id, data, context)
    if not policy_result["authorized"]:
        return {"status": "CAAS-Blocked", "reason": policy_result["reason"]}

    # 4. Intelligent Authentication (Gatekeeping)
    if "github" in str(data.get("object", "")).lower():
        auth_result = ToolGatekeeper("GitHub").authenticate_request(agent_id, data)
        if not auth_result["authenticated"]:
             return {"status": "Auth-Failed", "reason": auth_result["reason"]}

    # 4. Cognitive Orchestration
    context = {"weather": "Clear", "goal_alignment": 0.85, "trust_score": trust_score}
    exec_plan = await orchestrator.execute_plan(agent_id, data, context)
    
    # 5. Cognitive Realization (Model Runner)
    # If the action requires reasoning, invoke the model runner
    if data.get("@type") in ["AssessAction", "SearchAction", "CommunicateAction"]:
        inference_result = await model_runner.invoke_model({"model": "gpt-4o", "provider": "openai"}, context)
        data["result_raw"] = inference_result["model_output"]

    # 6. Physical Execution
    result = await executor.execute(action_id, data)

    # 6. Graph Ingestion
    graph.ingest_action(data)

    # 7. Behavioral Identification & MLflow Audit
    theories = identifier.identify_behavior(data, context)
    audit_log = identifier.generate_audit_log(data, theories)
    background_tasks.add_task(tracker.log_theory_identification, agent_id, action_id, audit_log)

    # 8. Real-time Telemetry Broadcast
    telemetry_payload = {
        "event": "action_processed",
        "agent": agent_id,
        "action_id": action_id,
        "pathway": exec_plan.get("pathway_used"),
        "theories": theories,
        "trust_score": trust_score,
        "historical_reliability": features.get("historical_hallucination_rate")
    }
    background_tasks.add_task(telemetry_manager.broadcast, telemetry_payload)

    return {
        "execution_id": action_id,
        "status": result["execution_metadata"].get("status"),
        "identified_patterns": theories,
        "trust_score": trust_score,
        "policy_id": policy_result.get("policy_id")
    }

@app.post("/api/v1/feedback")
async def post_feedback(action_id: str, feedback_data: Dict[str, Any]):
    """
    User/Peer feedback entry point for the Learning Loop.
    """
    result = learning.capture_feedback(action_id, feedback_data)
    return result



@app.post("/api/v1/identity/register")
async def register_agent_identity(spec: Dict[str, Any], username: str = Depends(get_current_admin)):
    """
    Federated Identity: Register an agent with Domain and Sponsor metadata.
    """
    identity = identity_manager.register_identity(spec)
    return {
        "canonical_id": identity.canonical_id,
        "domain": identity.domain,
        "sponsor_id": identity.sponsor_id,
        "did": identity.did
    }

@app.get("/api/v1/identity/{agent_id}/did")
async def get_agent_did(agent_id: str):
    """
    Returns the Decentralized Identifier (DID) and DDO for an agent.
    """
    with SessionLocal() as session:
        identity = session.query(CanonicalIdentity).filter(
            (CanonicalIdentity.canonical_id == agent_id) | 
            (CanonicalIdentity.subject_ref == agent_id)
        ).first()
        
        if not identity or not identity.did:
            raise HTTPException(status_code=404, detail="DID not found for agent")
            
        from kernel_engine.did_manager import AgentDidManager
        dm = AgentDidManager()
        ddo = dm.create_did_document(agent_id, identity.did)
        
        return {
            "did": identity.did,
            "document": ddo
        }

@app.get("/api/v1/identity/{agent_id}")
async def get_agent_identity(agent_id: str):
    return {
        "agent_id": agent_id,
        "trust_score": identity_manager.get_trust_score(agent_id),
        "signature": identity_manager.generate_identity_signature(agent_id)
    }

@app.get("/api/v1/graph/query")
async def query_graph(subject_id: str):
    return {"subject": subject_id, "facts": graph.query_facts(subject_id)}


@app.post("/api/v1/admin/discover")
async def admin_discover(org_name: str, username: str = Depends(get_current_admin)):
    """
    Admin-only: Trigger discovery from a real GitHub Organization.
    """
    discovered = discovery.crawl_github_org(org_name)
    return {
        "organization": org_name,
        "discovered_entities_count": len(discovered),
        "entities": discovered,
        "status": "Pending-Admin-Review"
    }



@app.get("/api/v1/setup/status")
async def get_setup_status():
    sk = SecretKernel()
    return {"initialized": sk.is_initialized()}

@app.post("/api/v1/setup/init")
async def initialize_kernel(data: Dict[str, Any]):
    sk = SecretKernel()
    if sk.is_initialized():
        raise HTTPException(status_code=400, detail="Kernel already initialized")
    
    master_key = data.get("master_key")
    if not master_key or len(master_key) < 8:
        raise HTTPException(status_code=400, detail="Master key must be at least 8 characters")

    # 1. Initialize with the new key
    new_sk = SecretKernel(provided_key=master_key)
    
    # 2. Persist the fact that we are initialized (mark the system)
    with SessionLocal() as session:
        marker = RegistryRecord(
            canonical_id="cid:kernel:system",
            record_type="system_config",
            status="active",
            source="kernel:setup",
            attributes={"initialized_at": datetime.utcnow().isoformat()}
        )
        session.add(marker)
        
        # 3. Store any initial secrets provided
        secrets_data = data.get("secrets", {})
        for key, val in secrets_data.items():
            if val:
                # Store in base64 for now as per SecretKernel._encrypt implementation
                encrypted = base64.b64encode(val.encode()).decode()
                record = RegistryRecord(
                    canonical_id="cid:kernel:system",
                    record_type="encrypted_secret",
                    status="active",
                    source=f"urn:agnxxt:secret:{key}",
                    attributes={"encrypted_value": encrypted}
                )
                session.add(record)
        
        session.commit()
    
    return {"status": "Initialized"}


@app.post("/api/v1/caas/audit_cot")
async def caas_audit_cot(agent_id: str, reasoning: str):
    """
    CAAS: Audits an agent's internal reasoning process.
    """
    return caas.audit_reasoning(agent_id, reasoning)

@app.post("/api/v1/caas/authorize")
async def caas_authorize(agent_id: str, action: Dict[str, Any], context: Dict[str, Any] = {}):
    """
    CAAS: Performs multi-layer continuous authorization check.
    """
    return caas.pre_access_audit(agent_id, action, context)


@app.post("/api/v1/lifecycle/provision")
async def provision_agent(spec: Dict[str, Any], username: str = Depends(get_current_admin)):
    """
    Industrial Lifecycle: Provision a new agent (Birth/Joiner).
    """
    agent_id = lifecycle.provision_agent(spec)
    return {"agent_id": agent_id, "status": "PROVISIONING"}

@app.post("/api/v1/lifecycle/activate/{agent_id}")
async def activate_agent(agent_id: str, username: str = Depends(get_current_admin)):
    """
    Industrial Lifecycle: Move agent to production (Activation).
    """
    lifecycle.activate_agent(agent_id)
    return {"status": "ACTIVE"}

@app.post("/api/v1/lifecycle/decommission/{agent_id}")
async def decommission_agent(agent_id: str, username: str = Depends(get_current_admin)):
    """
    Industrial Lifecycle: Revoke and retire agent (Death/Leaver).
    """
    lifecycle.decommission_agent(agent_id)
    return {"status": "REVOKED"}

@app.get("/api/v1/admin/policies")
async def get_admin_policies(username: str = Depends(get_current_admin)):
    policy_path = os.getenv("POLICY_PATH", "config/policies.json")
    try:
        with open(policy_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/admin/policies")
async def update_admin_policies(data: Dict[str, Any], username: str = Depends(get_current_admin)):
    policy_path = os.getenv("POLICY_PATH", "config/policies.json")
    try:
        with open(policy_path, "w") as f:
            json.dump(data, f, indent=2)
        return {"status": "Updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/identities")
async def get_admin_identities(username: str = Depends(get_current_admin)):
    with SessionLocal() as session:
        identities = session.query(CanonicalIdentity).all()
        return identities

@app.post("/api/v1/admin/onboard")
async def admin_onboard(user_id: str, username: str = Depends(get_current_admin)):
    """
    Admin-only: Approve and trigger user provisioning outreach.
    """
    outreach_action = discovery.generate_provisioning_request(user_id)
    # In a full system, this would be dispatched to the A2A communication bus.
    return {"status": "Outreach-Sent", "action": outreach_action}
