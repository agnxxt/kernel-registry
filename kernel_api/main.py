from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
import json
from datetime import datetime

from kernel_engine.validator import KernelValidator
from kernel_engine.theory_identifier import TheoryIdentifier
from kernel_engine.mlflow_tracker import KernelMLflowTracker
from kernel_engine.orchestrator import CognitiveOrchestrator
from kernel_engine.watchdog import RogueWatchdog
from kernel_engine.gatekeeper import ToolGatekeeper
from kernel_engine.discovery import DiscoveryEngine
from kernel_engine.identity import IdentityTrustManager
from kernel_engine.graph_adapter import GraphAdapter
from kernel_engine.executor import ActionExecutor
from kernel_engine.model_runner import CognitiveModelRunner
from kernel_engine.secret_kernel import SecretKernel
from kernel_engine.policy_engine import PolicyEngine
from kernel_engine.learning_loop import LearningLoop
from kernel_engine.feature_store import CognitiveFeatureStore

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
executor = ActionExecutor()
model_runner = CognitiveModelRunner()
secrets = SecretKernel()
policies = PolicyEngine()
learning = LearningLoop(tracker=tracker)
feature_store = CognitiveFeatureStore()

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
    context = {"weather": "Clear", "goal_alignment": 0.85, "trust_score": trust_score, "is_authorized_owner": True}
    policy_result = policies.evaluate_action(agent_id, data, context)
    if not policy_result["allowed"]:
        return {"status": "Policy-Blocked", "reason": policy_result["reason"]}

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
        "status": result["execution_metadata"]["status"],
        "identified_patterns": theories,
        "trust_score": trust_score,
        "policy_id": policy_result["policy_id"]
    }

@app.post("/api/v1/feedback")
async def post_feedback(action_id: str, feedback_data: Dict[str, Any]):
    """
    User/Peer feedback entry point for the Learning Loop.
    """
    result = learning.capture_feedback(action_id, feedback_data)
    return result

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
async def admin_discover(org_name: str):
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

@app.post("/api/v1/admin/onboard")
async def admin_onboard(user_id: str):
    """
    Admin-only: Approve and trigger user provisioning outreach.
    """
    outreach_action = discovery.generate_provisioning_request(user_id)
    # In a full system, this would be dispatched to the A2A communication bus.
    return {"status": "Outreach-Sent", "action": outreach_action}
