from kernel_engine.lifecycle_engine import LifecycleEngine
from kernel_engine.authz_caas.caas_gateway import CaasGateway
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Header
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends
import secrets
from kernel_engine.secret_kernel import SecretKernel

security = HTTPBasic()

# --- Tenant Isolation Middleware ---
def get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")):
    """Extract tenant ID from header for multi-tenant isolation."""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
    return x_tenant_id

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
from kernel_engine.authzen import AuthzenEngine, AuthzRequest, RBACBackend
from kernel_engine.anp import PeerRegistry, ServiceDiscovery, GossipProtocol
from kernel_engine.acp import MessageProtocol, MessageType, Message
from kernel_engine.rate_limiter import RateLimiter
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

# Protocol engines for multi-agent execution
# Authzen - Authorization/RBAC for agent actions
authzen_engine = AuthzenEngine()
rbac_backend = RBACBackend()

# ANP - Agent Network Protocol (peer discovery, gossip)
peer_registry = PeerRegistry()
service_discovery = ServiceDiscovery()
gossip_protocol = GossipProtocol(fanout=3)

# ACP - Agent Communication Protocol (messaging)
message_protocol = MessageProtocol(agent_id="kernel")

# Rate limiting across agents
rate_limiter = RateLimiter()

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

# Execute endpoint - called by Runner with pre-validated payload
class ExecuteRequest(BaseModel):
    agent_id: str
    framework: str  # langgraph, crewai, autogen, etc.
    payload: Dict[str, Any]
    config: Optional[Dict[str, Any]] = {}

class ExecuteResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    trace: Optional[List[Dict[str, Any]]] = None

@app.post("/api/v1/execute", response_model=ExecuteResponse)
async def execute_agent(
    request: ExecuteRequest,
    x_tenant_id: str = Depends(get_tenant_id)
):
    """
    Execute agent with framework and config from Platform/Runner.
    This is the main endpoint Runner invokes.
    
    Runner does policy enforcement BEFORE calling this endpoint.
    Kernel only executes pre-validated code.
    """
    execution_id = str(uuid.uuid4())
    
    # Validate tenant has access
    with SessionLocal() as session:
        # Check tenant-scoped access
        identity = session.query(CanonicalIdentity).filter(
            CanonicalIdentity.tenant_id == x_tenant_id
        ).first()
        if not identity:
            raise HTTPException(
                status_code=403, 
                detail=f"Tenant {x_tenant_id} not authorized"
            )
    
    # Execute based on framework
    result = {}
    if request.framework == "langgraph":
        # LangGraph specific execution
        result = await _execute_langgraph(request.payload, request.config)
    elif request.framework == "crewai":
        result = await _execute_crewai(request.payload, request.config)
    elif request.framework == "autogen":
        result = await _execute_autogen(request.payload, request.config)
    else:
        # Generic execution
        result = await executor.execute(execution_id, request.payload)
    
    return ExecuteResponse(
        execution_id=execution_id,
        status="completed",
        result=result,
        trace=[]
    )

async def _execute_langgraph(payload: Dict, config: Dict) -> Dict:
    """Execute LangGraph workflow."""
    # Implementation would call LangGraph runtime
    return {"framework": "langgraph", "output": "executed"}

async def _execute_crewai(payload: Dict, config: Dict) -> Dict:
    """Execute CrewAI crew."""
    return {"framework": "crewai", "output": "executed"}

async def _execute_autogen(payload: Dict, config: Dict) -> Dict:
    """Execute AutoGen agent."""
    return {"framework": "autogen", "output": "executed"}

# Streaming endpoint for long-running executions
@app.post("/api/v1/execute/stream")
async def execute_stream(
    request: ExecuteRequest,
    x_tenant_id: str = Depends(get_tenant_id)
):
    """
    Streaming execution - yields results as they complete.
    For long-running agent workflows.
    """
    execution_id = str(uuid.uuid4())
    
    async def event_generator():
        # Yield status updates
        yield {"event": "start", "execution_id": execution_id}
        # Execute and yield chunks
        yield {"event": "chunk", "data": {"status": "running"}}
        yield {"event": "done", "data": {"result": "completed"}}
    
    return event_generator()

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


# ============================================================
# Authzen - Authorization Protocol Endpoints
# ============================================================

class AuthzRequestModel(BaseModel):
    subject: str
    action: str
    resource: str
    context: Dict[str, Any] = {}

class AuthzResponseModel(BaseModel):
    decision: str
    effect: str
    policy_ids: List[str]

@app.post("/api/v1/authz/authorize", response_model=AuthzResponseModel)
async def authorize_request(request: AuthzRequestModel, tenant_id: str = Depends(get_tenant_id)):
    """
    Authzen: Authorize an agent action against policies.
    """
    authz_request = AuthzRequest(
        subject=request.subject,
        action=request.action,
        resource=request.resource,
        context=request.context
    )
    
    response = authzen_engine.authorize(authz_request)
    return AuthzResponseModel(
        decision=response.decision.value,
        effect=response.effect.value,
        policy_ids=response.policy_ids
    )

@app.post("/api/v1/authz/policies")
async def create_policy(policy_id: str, subject: str = "*", action: str = "*", 
                      resource: str = "*", effect: str = "permit",
                      tenant_id: str = Depends(get_tenant_id)):
    """
    Authzen: Create authorization policy.
    """
    from kernel_engine.authzen import AuthzPolicy
    policy = AuthzPolicy(policy_id)
    policy.add_rule(subject, action, resource, effect)
    authzen_engine.add_policy(policy)
    return {"status": "created", "policy_id": policy_id}

@app.post("/api/v1/authz/rbac/roles/{role_id}/permissions")
async def grant_permission(role_id: str, action: str, resource: str,
                         tenant_id: str = Depends(get_tenant_id)):
    """
    Authzen: Grant RBAC permission to role.
    """
    rbac_backend.grant_permission(role_id, action, resource)
    return {"status": "granted", "role_id": role_id}

@app.post("/api/v1/authz/rbac/roles/{role_id}/members")
async def assign_role(role_id: str, agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Authzen: Assign agent to role.
    """
    rbac_backend.assign_role(role_id, agent_id)
    return {"status": "assigned", "role_id": role_id, "agent_id": agent_id}

@app.get("/api/v1/authz/rbac/agents/{agent_id}/permissions")
async def check_permissions(agent_id: str, action: str, resource: str,
                          tenant_id: str = Depends(get_tenant_id)):
    """
    Authzen: Check if agent has permission.
    """
    has_permission = rbac_backend.has_permission(agent_id, action, resource)
    return {"agent_id": agent_id, "action": action, "resource": resource, 
            "allowed": has_permission}


# ============================================================
# ANP - Agent Network Protocol Endpoints  
# ============================================================

class PeerRegisterModel(BaseModel):
    peer_id: str
    address: str
    metadata: Dict[str, Any] = {}

@app.post("/api/v1/anp/peers", response_model=Dict)
async def register_peer(peer: PeerRegisterModel, tenant_id: str = Depends(get_tenant_id)):
    """
    ANP: Register a peer agent.
    """
    result = peer_registry.register(peer.peer_id, peer.address)
    return {"peer_id": result.peer_id, "state": result.state.value, "reputation": result.reputation}

@app.get("/api/v1/anp/peers")
async def list_peers(limit: int = 10, tenant_id: str = Depends(get_tenant_id)):
    """
    ANP: Get active peers.
    """
    peers = peer_registry.get_peers(limit)
    return [{"peer_id": p.peer_id, "address": p.address, "reputation": p.reputation} for p in peers]

@app.post("/api/v1/anp/services")
async def register_service(service: str, agent_id: str, endpoint: str,
                        tenant_id: str = Depends(get_tenant_id)):
    """
    ANP: Register a service.
    """
    service_discovery.register(service, agent_id, endpoint)
    return {"status": "registered", "service": service, "agent_id": agent_id}

@app.get("/api/v1/anp/services/{service}")
async def discover_service(service: str, tenant_id: str = Depends(get_tenant_id)):
    """
    ANP: Discover services.
    """
    endpoints = service_discovery.discover(service)
    return {"service": service, "endpoints": endpoints}

@app.post("/api/v1/anp/gossip")
async def gossip_propagate(message_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    ANP: Propagate message via gossip.
    """
    peers = peer_registry.get_peers(limit=10)
    peer_ids = [p.peer_id for p in peers]
    selected = gossip_protocol.propagate(message_id, peer_ids)
    return {"message_id": message_id, "propagated_to": selected}


# ============================================================
# ACP - Agent Communication Protocol Endpoints
# ============================================================

class MessageSendModel(BaseModel):
    receiver: str
    content: Any
    msg_type: str = "request"
    priority: int = 2

@app.post("/api/v1/acp/messages")
async def send_message(message: MessageSendModel, tenant_id: str = Depends(get_tenant_id)):
    """
    ACP: Send message to agent.
    """
    msg_type = MessageType(message.msg_type)
    msg = await message_protocol.send(message.receiver, message.content, msg_type)
    return {"message_id": msg.message_id, "status": "sent"}

@app.post("/api/v1/acp/broadcast")
async def broadcast_message(content: Any, tenant_id: str = Depends(get_tenant_id)):
    """
    ACP: Broadcast message to all agents.
    """
    msg = await message_protocol.broadcast(content)
    return {"message_id": msg.message_id, "status": "broadcast"}

@app.post("/api/v1/acp/sessions")
async def create_session(peer_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    ACP: Create communication session.
    """
    session = message_protocol.create_session(peer_id)
    return {"session_id": session.session_id, "state": session.state.value}

@app.get("/api/v1/acp/sessions")
async def list_sessions(tenant_id: str = Depends(get_tenant_id)):
    """
    ACP: List active sessions.
    """
    return [{"session_id": s.session_id, "agent_id": s.agent_id, "peer_id": s.peer_id}
            for s in message_protocol.sessions.values()]


# ============================================================
# Rate Limiting
# ============================================================

@app.post("/api/v1/ratelimit/check")
async def check_rate_limit(agent_id: str, action: str, limit: int = 100,
                        tenant_id: str = Depends(get_tenant_id)):
    """
    Check rate limit for agent action.
    """
    allowed = rate_limiter.check(tenant_id, agent_id, action, limit)
    return {"agent_id": agent_id, "action": action, "allowed": allowed}


# ============================================================
# A2A - Agent to Agent Protocol Endpoints
# ============================================================

from kernel_engine.a2a import A2AMessage, AgentInfo, A2ARegistry, A2ARouter, TranslationEngine

# A2A singletons
a2a_registry = A2ARegistry()
a2a_router = A2ARouter()
translation_engine = TranslationEngine()


class AgentRegisterModel(BaseModel):
    agent_id: str
    name: str
    framework: str = "custom"
    language: str = "python"
    capabilities: List[str] = []
    cloud: str = "aws"
    endpoint: str = ""


@app.post("/api/v1/a2a/agents", response_model=Dict)
async def register_agent(agent: AgentRegisterModel, tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Register agent in registry.
    """
    info = AgentInfo(
        agent_id=agent.agent_id,
        name=agent.name,
        framework=agent.framework,
        language=agent.language,
        capabilities=agent.capabilities,
        cloud=agent.cloud,
        endpoint=agent.endpoint,
    )
    urn = a2a_registry.register(info)
    return {"agent_id": agent.agent_id, "urn": urn}


@app.get("/api/v1/a2a/agents")
async def discover_agents(framework: str = None, language: str = None,
                    cloud: str = None, capability: str = None,
                    tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Discover agents by criteria.
    """
    agents = a2a_registry.discover(framework, language, cloud, capability)
    return [{"agent_id": a.agent_id, "name": a.name, "urn": a.urn, 
             "framework": a.framework, "language": a.language}
            for a in agents]


@app.get("/api/v1/a2a/agents/{agent_id}")
async def get_agent(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Get agent info.
    """
    agent = a2a_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"agent_id": agent.agent_id, "name": agent.name, 
            "urn": agent.urn, "framework": agent.framework}


class A2AMessageModel(BaseModel):
    sender: str
    recipient: str
    content: Any
    modality: str = "text"
    language: str = "python"
    context: Dict[str, Any] = {}


@app.post("/api/v1/a2a/messages")
async def send_a2a_message(message: A2AMessageModel, tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Send agent-to-agent message.
    """
    msg = A2AMessage(
        sender=message.sender,
        recipient=message.recipient,
        content=message.content,
        modality=message.modality,
        language=message.language,
        framework_metadata=message.context,
    )
    message_id = await a2a_router.send(msg)
    return {"message_id": message_id, "status": "sent"}


@app.post("/api/v1/a2a/broadcast")
async def broadcast_a2a_message(message: A2AMessageModel, 
                           tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Broadcast to agents matching filter.
    """
    filter_dict = {}
    if message.context.get("framework"):
        filter_dict["framework"] = message.context["framework"]
    if message.context.get("language"):
        filter_dict["language"] = message.context["language"]
    
    msg = A2AMessage(
        sender=message.sender,
        recipient="*",
        content=message.content,
        modality=message.modality,
        language=message.language,
        framework_metadata=message.context,
    )
    message_ids = await a2a_router.broadcast(msg, filter_dict or None)
    return {"broadcast_count": len(message_ids), "message_ids": message_ids}


@app.get("/api/v1/a2a/messages/{agent_id}")
async def get_message_history(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Get message history for agent.
    """
    history = a2a_router.get_history(agent_id)
    return [{"message_id": m.message_id, "sender": m.sender, 
             "content": m.content, "modality": m.modality}
            for m in history[-10:]]  # Last 10


@app.post("/api/v1/a2a/translate")
async def translate_modality(message: A2AMessageModel, target_modality: str,
                       tenant_id: str = Depends(get_tenant_id)):
    """
    A2A: Translate between modalities.
    """
    msg = A2AMessage(
        sender=message.sender,
        recipient=message.recipient,
        content=message.content,
        modality=message.modality,
        language=message.language,
    )
    translated = await translation_engine.translate(msg, target_modality)
    return {"original_modality": message.modality,
            "target_modality": target_modality,
            "content": translated.content}


# ============================================================
# OpenFGA - Fine-Grained Authorization
# ============================================================

from kernel_engine.openfga import FGA, FGAModel, TypeDefinition, RelationDef, RelationType, Tuple, FGAChecker

# FGA singleton
fga = FGA()


class FGAModelCreate(BaseModel):
    types: List[Dict[str, Any]]
    schema_version: str = "1.1"


@app.post("/api/v1/fga/models")
async def create_fga_model(model: FGAModelCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: Create authorization model.
    """
    fga_model = FGAModel(schema_version=model.schema_version)
    
    for td in model.types:
        tdef = TypeDefinition(type=td["type"])
        for rn, rd in td.get("relations", {}).items():
            rtypes = {RelationType(rt) for rt in rd.get("relation_types", [])}
            tdef.relations[rn] = RelationDef(rn, rtypes, rd.get("rewrite", {}))
        fga_model.types[td["type"]] = tdef
    
    model_id = fga.create_model(fga_model)
    return {"model_id": model_id, "status": "created"}


@app.get("/api/v1/fga/models")
async def list_fga_models(tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: List models.
    """
    return [{"model_id": m.model_id, "types": list(m.types.keys())} 
            for m in fga.models.values()]


@app.get("/api/v1/fga/models/{model_id}")
async def get_fga_model(model_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: Get model.
    """
    model = fga.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model.to_dict()


class TupleWriteRequest(BaseModel):
    object: str
    relation: str
    user: str


@app.post("/api/v1/fga/write")
async def write_tuples(tuple: TupleWriteRequest, model_id: str = None,
                     tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: Write authorization tuple.
    """
    t = Tuple(tuple.object, tuple.relation, tuple.user)
    
    store = fga.tuple_stores.get(model_id or fga.default_model_id)
    if not store:
        raise HTTPException(status_code=400, detail="No model configured")
    
    checker = FGAChecker()
    checker.model = fga.get_model(model_id)
    checker.tuple_store = store
    checker.write(t)
    
    return {"status": "written", "tuple": tuple.dict()}


@app.post("/api/v1/fga/delete")
async def delete_tuple(tuple: TupleWriteRequest, model_id: str = None,
                     tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: Delete authorization tuple.
    """
    t = Tuple(tuple.object, tuple.relation, tuple.user)
    
    store = fga.tuple_stores.get(model_id or fga.default_model_id)
    if store:
        store.delete(t)
    
    return {"status": "deleted", "tuple": tuple.dict()}


@app.post("/api/v1/fga/check")
async def check_permission(object: str, relation: str, user: str, 
                       model_id: str = None, tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: Check permission.
    """
    allowed = fga.check(object, relation, user, model_id)
    return {"allowed": allowed, "object": object, "relation": relation, "user": user}


@app.get("/api/v1/fga/read")
async def read_tuples(object: str = None, relation: str = None,
                  user: str = None, model_id: str = None,
                  tenant_id: str = Depends(get_tenant_id)):
    """
    OpenFGA: Read tuples.
    """
    tuples = fga.read(object, relation, user, model_id)
    return {"tuples": [t.to_dict() for t in tuples]}


# ============================================================
# ABAC - Attribute-Based Access Control
# ============================================================

from kernel_engine.abac import ABACEngine, ABACPolicy, Attribute, AttributeType, AttributeOperator, Condition, ConditionType, AttributeExtractor

# ABAC singleton
abac_engine = ABACEngine()


class ABACPolicyCreate(BaseModel):
    name: str
    description: str = ""
    subjects: List[Dict[str, Any]] = []
    resources: List[Dict[str, Any]] = []
    environments: List[Dict[str, Any]] = []
    actions: List[str] = []
    priority: int = 0
    enabled: bool = True


@app.post("/api/v1/abac/policies")
async def create_abac_policy(policy: ABACPolicyCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    ABAC: Create policy.
    """
    p = ABACPolicy(
        name=policy.name,
        description=policy.description,
        subjects=policy.subjects,
        resources=policy.resources,
        environments=policy.environments,
        actions=policy.actions,
        priority=policy.priority,
        enabled=policy.enabled,
    )
    abac_engine.add_policy(p)
    return {"policy_id": p.policy_id, "name": p.name, "status": "created"}


@app.get("/api/v1/abac/policies")
async def list_abac_policies(tenant_id: str = Depends(get_tenant_id)):
    """
    ABAC: List policies.
    """
    policies = abac_engine.list_policies()
    return [{"policy_id": p.policy_id, "name": p.name, "priority": p.priority, 
             "enabled": p.enabled} for p in policies]


@app.get("/api/v1/abac/policies/{policy_id}")
async def get_abac_policy(policy_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    ABAC: Get policy.
    """
    policy = abac_engine.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"policy_id": policy.policy_id, "name": policy.name, 
            "description": policy.description, "actions": policy.actions,
            "priority": policy.priority, "enabled": policy.enabled}


@app.delete("/api/v1/abac/policies/{policy_id}")
async def delete_abac_policy(policy_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    ABAC: Delete policy.
    """
    abac_engine.remove_policy(policy_id)
    return {"status": "deleted", "policy_id": policy_id}


class ABACCheckRequest(BaseModel):
    subject: Dict[str, Any]
    resource: Dict[str, Any]
    action: str
    environment: Dict[str, Any] = {}


@app.post("/api/v1/abac/check")
async def check_abac(request: ABACCheckRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    ABAC: Check authorization.
    """
    allowed = abac_engine.authorize(
        request.subject, request.resource, request.action, request.environment
    )
    return {"allowed": allowed, "action": request.action}


@app.post("/api/v1/abac/check/all")
async def check_abac_all(request: ABACCheckRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    ABAC: Evaluate all policies.
    """
    results = abac_engine.evaluate_all(
        request.subject, request.resource, request.action, request.environment
    )
    return {"results": results}


# ============================================================
# Identity vs Account Distinction
# ============================================================

from kernel_engine.identity_v2 import (
    IdentityManager, Identity, Account, Principal,
    IdentityType, AccountType, IdentityStatus
)

# Identity manager singleton
identity_manager = IdentityManager()


# --- Identity Endpoints ---

class IdentityCreate(BaseModel):
    identifier: str
    identity_type: str = "uuid"
    display_name: str = ""
    metadata: Dict[str, Any] = {}


@app.post("/api/v1/identity")
async def create_identity(data: IdentityCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    Create identity (the persistent 'who').
    """
    identity = identity_manager.create_identity(
        identifier=data.identifier,
        identity_type=data.identity_type,
        display_name=data.display_name,
        metadata=data.metadata,
    )
    return identity.to_dict()


@app.get("/api/v1/identity/{identity_id}")
async def get_identity(identity_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get identity.
    """
    identity = identity_manager.get_identity(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    return identity.to_dict()


@app.get("/api/v1/identity/by-identifier/{identifier}")
async def get_identity_by_identifier(identifier: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get identity by identifier.
    """
    identity = identity_manager.get_identity_by_identifier(identifier)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    return identity.to_dict()


@app.put("/api/v1/identity/{identity_id}")
async def update_identity(identity_id: str, display_name: str = None,
                     metadata: Dict[str, Any] = None, tenant_id: str = Depends(get_tenant_id)):
    """
    Update identity.
    """
    updates = {}
    if display_name:
        updates["display_name"] = display_name
    if metadata:
        updates["metadata"] = metadata
    
    identity = identity_manager.update_identity(identity_id, **updates)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    return identity.to_dict()


@app.post("/api/v1/identity/{identity_id}/deactivate")
async def deactivate_identity(identity_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Deactivate identity.
    """
    result = identity_manager.deactivate_identity(identity_id)
    return {"status": "deactivated" if result else "not_found", "identity_id": identity_id}


@app.get("/api/v1/identity")
async def list_identities(status: str = None, tenant_id: str = Depends(get_tenant_id)):
    """
    List identities.
    """
    identities = identity_manager.list_identities(status)
    return {"identities": [i.to_dict() for i in identities], "total": len(identities)}


# --- Account Endpoints ---

class AccountCreate(BaseModel):
    identity_id: str
    account_type: str = "password"
    credential: str = ""
    metadata: Dict[str, Any] = {}
    primary: bool = False


@app.post("/api/v1/account")
async def create_account(data: AccountCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    Create account (credential for identity).
    """
    account = identity_manager.create_account(
        identity_id=data.identity_id,
        account_type=data.account_type,
        credential=data.credential,
        metadata=data.metadata,
        primary=data.primary,
    )
    return account.to_dict()


@app.get("/api/v1/account/{account_id}")
async def get_account(account_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get account.
    """
    account = identity_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.to_dict()


@app.get("/api/v1/account/identity/{identity_id}")
async def get_accounts_for_identity(identity_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get all accounts for identity.
    """
    accounts = identity_manager.get_accounts_for_identity(identity_id)
    return {"accounts": [a.to_dict() for a in accounts]}


@app.post("/api/v1/account/{account_id}/deactivate")
async def deactivate_account(account_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Deactivate account.
    """
    result = identity_manager.deactivate_account(account_id)
    return {"status": "deactivated" if result else "not_found", "account_id": account_id}


# --- Authentication Endpoints ---

class AuthRequest(BaseModel):
    identifier: str
    account_type: str = "password"
    credential: str = ""


@app.post("/api/v1/auth/login")
async def login(request: AuthRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    Authenticate and get principal.
    """
    principal = identity_manager.authenticate(
        identifier=request.identifier,
        account_type=request.account_type,
        credential=request.credential,
    )
    if not principal:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return principal.to_dict()


@app.post("/api/v1/auth/logout")
async def logout(principal_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Logout principal.
    """
    result = identity_manager.logout(principal_id)
    return {"status": "logged_out" if result else "not_found"}


@app.get("/api/v1/auth/principal/{principal_id}")
async def get_principal(principal_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get principal.
    """
    principal = identity_manager.get_principal(principal_id)
    if not principal:
        raise HTTPException(status_code=404, detail="Principal not valid")
    return principal.to_dict()


@app.post("/api/v1/auth/refresh")
async def refresh_token(principal_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Refresh principal session.
    """
    result = identity_manager.refresh_principal(principal_id)
    return {"status": "refreshed" if result else "expired"}


# ============================================================
# Zingg Identity Resolver
# ============================================================

from kernel_engine.zingg import ZinggResolver, DIDResolver, DIDMethod, KeyType, KeyPurpose

# Resolver singletons
zingg_resolver = ZinggResolver()
did_resolver = DIDResolver()


class DIDCreate(BaseModel):
    controller: str = ""
    verification_keys: List[Dict[str, Any]] = []
    services: List[Dict[str, Any]] = []


@app.post("/api/v1/did")
async def create_did(data: DIDCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    Create Zingg DID.
    """
    did = zingg_resolver.create_did(
        controller_did=data.controller,
        verification_keys=data.verification_keys,
        services=data.services,
    )
    return {"did": did}


@app.get("/api/v1/did/{did}")
async def resolve_did(did: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Resolve DID to document.
    """
    doc = zingg_resolver.resolve_to_dict(did)
    if not doc:
        raise HTTPException(status_code=404, detail="DID not found")
    return doc


@app.put("/api/v1/did/{did}")
async def update_did(did: str, verification_keys: List[Dict[str, Any]] = None,
                  services: List[Dict[str, Any]] = None,
                  tenant_id: str = Depends(get_tenant_id)):
    """
    Update DID document.
    """
    result = zingg_resolver.update(did, verification_keys, services)
    if not result:
        raise HTTPException(status_code=404, detail="DID not found")
    doc = zingg_resolver.resolve_to_dict(did)
    return doc


@app.post("/api/v1/did/{did}/deactivate")
async def deactivate_did(did: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Deactivate DID.
    """
    result = zingg_resolver.deactivate(did)
    return {"status": "deactivated" if result else "not_found", "did": did}


@app.get("/api/v1/did/{did}/services")
async def get_did_services(did: str, service_type: str = None,
                       tenant_id: str = Depends(get_tenant_id)):
    """
    Get DID service endpoints.
    """
    if service_type:
        services = zingg_resolver.get_services(did, service_type)
    else:
        services = zingg_resolver.get_services(did)
    
    return {"services": [
        {"id": s.id, "type": s.service_type, "endpoint": s.endpoint}
        for s in services
    ]}


@app.get("/api/v1/did/{did}/agent")
async def get_agent_endpoint(did: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get agent execution endpoint.
    """
    endpoint = zingg_resolver.get_agent_endpoint(did)
    return {"did": did, "agent_endpoint": endpoint}


@app.post("/api/v1/did/{did}/delegate")
async def delegate_did(did: str, delegate_did: str,
                    tenant_id: str = Depends(get_tenant_id)):
    """
    Delegate DID to another identity.
    """
    result = zingg_resolver.delegate(did, delegate_did)
    return {"status": "delegated" if result else "error", 
            "delegator": did, "delegate": delegate_did}


@app.get("/api/v1/did/{did}/delegate")
async def get_delegation_chain(did: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get delegation chain.
    """
    chain = zingg_resolver.get_delegation_chain(did)
    return {"did": did, "chain": chain}


@app.get("/api/v1/did")
async def list_dids(controller: str = None, tenant_id: str = Depends(get_tenant_id)):
    """
    List DIDs.
    """
    dids = zingg_resolver.list_dids(controller)
    return {"dids": dids, "count": len(dids)}


# ============================================================
# OIDC - OpenID Connect
# ============================================================

from kernel_engine.oidc import OIDCClient, OIDCProvider, TokenSet

# OIDC client singleton
oidc_client = OIDCClient()


@app.get("/api/v1/oidc/.well-known/openid-configuration")
async def oidc_discovery(tenant_id: str = Depends(get_tenant_id)):
    """
    OIDC Discovery endpoint.
    """
    issuer = "https://agent.example.com"
    return oidc_client.discover(issuer)


@app.get("/api/v1/oidc/authorize")
async def oidc_authorize(state: str = "", nonce: str = "",
                      scope: str = None, tenant_id: str = Depends(get_tenant_id)):
    """
    Create OIDC authorization URL.
    """
    url = oidc_client.create_authorization_url(state=state, nonce=nonce, scope=scope)
    return {"authorization_url": url}


@app.post("/api/v1/oidc/token")
async def oidc_token_exchange(code: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Exchange authorization code for tokens.
    """
    tokens = oidc_client.exchange_code(code)
    return {"access_token": tokens.access_token, "token_type": tokens.token_type,
            "expires_in": tokens.expires_in, "refresh_token": tokens.refresh_token,
            "id_token": tokens.id_token}


@app.post("/api/v1/oidc/refresh")
async def oidc_refresh(refresh_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Refresh tokens.
    """
    tokens = oidc_client.refresh(refresh_token)
    return {"access_token": tokens.access_token, "expires_in": tokens.expires_in}


@app.get("/api/v1/oidc/userinfo")
async def oidc_userinfo(access_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get userinfo (agent info).
    """
    try:
        info = oidc_client.get_userinfo(access_token)
        return info
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================
# Entra ID - Microsoft Azure AD
# ============================================================

from kernel_engine.entra import EntraClient, EntraApplication

# Entra client singleton
entra_client = EntraClient()


class EntraAppCreate(BaseModel):
    display_name: str
    app_type: str = "web"
    scope: List[str] = []


@app.post("/api/v1/entra/applications")
async def register_entra_app(data: EntraAppCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    Register application in Entra ID.
    """
    app = entra_client.register_application(
        display_name=data.display_name,
        app_type=data.app_type,
        scope=data.scope,
    )
    return {"app_id": app.app_id, "object_id": app.object_id, "display_name": app.display_name}


@app.get("/api/v1/entra/applications/{app_id}")
async def get_entra_app(app_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get application.
    """
    app = entra_client.get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return {"app_id": app.app_id, "object_id": app.object_id, "display_name": app.display_name}


@app.post("/api/v1/entra/applications/{app_id}/sp")
async def create_entra_sp(app_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Create service principal.
    """
    sp = entra_client.create_service_principal(app_id)
    return {"sp_object_id": sp.sp_object_id, "app_id": sp.app_id}


@app.post("/api/v1/entra/token")
async def acquire_entra_token(app_id: str, scope: str = None, 
                        tenant_id: str = Depends(get_tenant_id)):
    """
    Acquire token for application.
    """
    try:
        token = entra_client.acquire_token(app_id, oauth2_scopes=scope)
        return {"access_token": token.access_token, "expires_at": token.expires_at}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/v1/entra/token/validate")
async def validate_entra_token(access_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Validate token and get claims.
    """
    result = entra_client.validate_token(access_token)
    if not result.get("active"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return result


@app.get("/api/v1/entra/agent/id")
async def get_entra_agent_id(access_token: str = None, id_token: str = None,
                        tenant_id: str = Depends(get_tenant_id)):
    """
    Get agent ID from Entra token.
    """
    agent_id = entra_client.get_agent_id(access_token=access_token, id_token=id_token)
    if not agent_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"agent_id": agent_id}


@app.get("/api/v1/entra/agent/roles")
async def get_entra_agent_roles(access_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get agent's roles.
    """
    roles = entra_client.get_agent_roles(access_token)
    return {"roles": roles}


# ============================================================
# Entra Agent Lifecycle Management
# ============================================================

class EntraLifecycle:
    """Entra agent lifecycle operations"""
    
    def __init__(self, entra_client: EntraClient):
        self.entra = entra_client
        self.agents: Dict[str, Dict] = {}  # agent_id -> agent state
    
    # ============ Lifecycle States ============
    
    APPROVED = "approved"       # Agent approved but not provisioned
    PROVISIONING = "provisioning"   # Being created
    ACTIVE = "active"         # Running and authorized
    SUSPENDED = "suspended"  # Temporarily disabled
    DISABLED = "disabled"     # Stopped and deprovisioned
    
    def provision(self, app_id: str, agent_config: Dict) -> Dict:
        """Provision new agent"""
        import uuid
        
        agent_id = f"agent_{uuid.uuid4().hex[:12]}"
        
        # Create service principal
        sp = self.entra.create_service_principal(app_id)
        
        # Assign roles
        for role in agent_config.get("roles", ["Agent"]):
            self.entra.assign_app_role(sp.sp_object_id, role)
        
        # Register agent
        self.agents[agent_id] = {
            "agent_id": agent_id,
            "app_id": app_id,
            "sp_object_id": sp.sp_object_id,
            "state": self.PROVISIONING,
            "config": agent_config,
            "created_at": datetime.now().isoformat(),
        }
        
        return self.agents[agent_id]
    
    def activate(self, agent_id: str) -> Dict:
        """Activate agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        self.agents[agent_id]["state"] = self.ACTIVE
        return self.agents[agent_id]
    
    def suspend(self, agent_id: str) -> Dict:
        """Suspend agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        self.agents[agent_id]["state"] = self.SUSPENDED
        return self.agents[agent_id]
    
    def disable(self, agent_id: str) -> Dict:
        """Disable/deprovision agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        self.agents[agent_id]["state"] = self.DISABLED
        return self.agents[agent_id]
    
    def get(self, agent_id: str) -> Dict:
        """Get agent status"""
        return self.agents.get(agent_id)
    
    def list(self, state: str = None) -> List[Dict]:
        """List agents"""
        if state:
            return [a for a in self.agents.values() if a["state"] == state]
        return list(self.agents.values())


lifecycle = EntraLifecycle(entra_client)


class AgentProvisionRequest(BaseModel):
    app_id: str
    roles: List[str] = []
    config: Dict[str, Any] = {}


@app.post("/api/v1/entra/agent/provision")
async def provision_entra_agent(data: AgentProvisionRequest, 
                           tenant_id: str = Depends(get_tenant_id)):
    """
    Provision new Entra agent.
    """
    agent = lifecycle.provision(data.app_id, {
        "roles": data.roles,
        **data.config
    })
    return agent


@app.post("/api/v1/entra/agent/{agent_id}/activate")
async def activate_entra_agent(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Activate agent.
    """
    try:
        agent = lifecycle.activate(agent_id)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/v1/entra/agent/{agent_id}/suspend")
async def suspend_entra_agent(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Suspend agent.
    """
    try:
        agent = lifecycle.suspend(agent_id)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/v1/entra/agent/{agent_id}/disable")
async def disable_entra_agent(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Disable/deprovision agent.
    """
    try:
        agent = lifecycle.disable(agent_id)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/entra/agent/{agent_id}")
async def get_entra_agent(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get agent status.
    """
    agent = lifecycle.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.get("/api/v1/entra/agents")
async def list_entra_agents(state: str = None, tenant_id: str = Depends(get_tenant_id)):
    """
    List Entra agents.
    """
    agents = lifecycle.list(state)
    return {"agents": agents, "count": len(agents)}


# ============================================================
# Entra Governance Toolkit
# ============================================================

from kernel_engine.entra_governance import GovernanceToolkit, ComplianceFramework, PolicyType

governance = GovernanceToolkit()


# --- Policy Endpoints ---

class PolicyCreate(BaseModel):
    name: str
    policy_type: str
    rules: List[str] = []
    enforcement: str = "audit"


@app.post("/api/v1/entra/governance/policies")
async def create_governance_policy(data: PolicyCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    Create governance policy.
    """
    policy = governance.create_policy(data.name, data.policy_type, data.rules, data.enforcement)
    return {"policy_id": policy.policy_id, "name": policy.name}


@app.get("/api/v1/entra/governance/policies")
async def list_governance_policies(tenant_id: str = Depends(get_tenant_id)):
    """
    List policies.
    """
    policies = governance.list_policies()
    return {"policies": [{"id": p.policy_id, "name": p.name, "type": p.policy_type} 
                        for p in policies]}


@app.post("/api/v1/entra/governance/evaluate")
async def evaluate_governance(agent_id: str, action: str, 
                         context: Dict[str, Any] = {}, tenant_id: str = Depends(get_tenant_id)):
    """
    Evaluate policy for action.
    """
    result = governance.evaluate_policy(agent_id, action, context)
    return result


# --- Access Review Endpoints ---

class ReviewSchedule(BaseModel):
    agent_id: str
    reviewer: str
    frequency: str = "monthly"


@app.post("/api/v1/entra/governance/reviews")
async def schedule_review(data: ReviewSchedule, tenant_id: str = Depends(get_tenant_id)):
    """
    Schedule access review.
    """
    review = governance.schedule_review(data.agent_id, data.reviewer, data.frequency)
    return {"review_id": review.review_id, "agent_id": review.agent_id}


@app.get("/api/v1/entra/governance/reviews/pending")
async def get_pending_reviews(tenant_id: str = Depends(get_tenant_id)):
    """
    Get pending reviews.
    """
    reviews = governance.get_pending_reviews()
    return {"reviews": [{"review_id": r.review_id, "agent_id": r.agent_id} for r in reviews]}


@app.post("/api/v1/entra/governance/reviews/{review_id}/complete")
async def complete_review(review_id: str, approved: bool, notes: str = "",
                   tenant_id: str = Depends(get_tenant_id)):
    """
    Complete access review.
    """
    result = governance.complete_review(review_id, approved, notes)
    return {"status": "completed" if result else "not_found"}


# --- Risk Scoring ---

@app.post("/api/v1/entra/governance/risk")
async def calculate_risk(agent_id: str, activity: List[Dict[str, Any]] = [],
                     tenant_id: str = Depends(get_tenant_id)):
    """
    Calculate agent risk score.
    """
    risk = governance.calculate_risk(agent_id, activity)
    return {"agent_id": risk.agent_id, "score": risk.score, "factors": risk.factors}


@app.get("/api/v1/entra/governance/risk/{agent_id}")
async def get_risk_score(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get risk score.
    """
    risk = governance.get_risk_score(agent_id)
    if not risk:
        raise HTTPException(status_code=404, detail="No risk score")
    return {"agent_id": risk.agent_id, "score": risk.score, "factors": risk.factors}


# --- Consent ---

class ConsentGrant(BaseModel):
    principal_id: str
    resource: str
    scope: List[str] = []
    granted_by: str
    expires_days: int = 30


@app.post("/api/v1/entra/governance/consent")
async def grant_consent(data: ConsentGrant, tenant_id: str = Depends(get_tenant_id)):
    """
    Grant consent.
    """
    consent = governance.grant_consent(data.principal_id, data.resource, 
                                   data.scope, data.granted_by, data.expires_days)
    return consent.to_dict() if hasattr(consent, 'to_dict') else {"consent_id": consent.consent_id}


@app.delete("/api/v1/entra/governance/consent/{consent_id}")
async def revoke_consent(consent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Revoke consent.
    """
    result = governance.revoke_consent(consent_id)
    return {"status": "revoked" if result else "not_found"}


@app.get("/api/v1/entra/governance/consent/check")
async def check_consent(principal_id: str, resource: str, scope: str,
                     tenant_id: str = Depends(get_tenant_id)):
    """
    Check consent.
    """
    result = governance.check_consent(principal_id, resource, scope)
    return {"granted": result}


# --- Audit ---

@app.get("/api/v1/entra/governance/audit")
async def get_audit_log(agent_id: str = None, limit: int = 100,
                     tenant_id: str = Depends(get_tenant_id)):
    """
    Get audit log.
    """
    log = governance.get_audit_log(agent_id, limit)
    return {"entries": log, "count": len(log)}


# --- Compliance ---

@app.get("/api/v1/entra/governance/compliance/{framework}")
async def check_compliance(framework: str, agent_id: str,
                       tenant_id: str = Depends(get_tenant_id)):
    """
    Check compliance.
    """
    result = governance.check_compliance(framework, agent_id)
    return result


# ============================================================
# CAAS - Cloud Agent Authorization Service (OpenAGX)
# ============================================================

from kernel_engine.caas import CAASClient, OpenAGXProvider, GrantType, Scope

caas_client = CAASClient()
openagx_provider = OpenAGXProvider()


# --- Discovery ---

@app.get("/api/v1/caas/.well-known/openid-configuration")
async def caas_discovery(tenant_id: str = Depends(get_tenant_id)):
    """
    OpenAGX/CAAS discovery.
    """
    return openagx_provider.discover()


# --- Agent Registration ---

@app.post("/api/v1/caas/agents")
async def register_caas_agent(agent_id: str, metadata: Dict[str, Any] = {},
                          tenant_id: str = Depends(get_tenant_id)):
    """
    Register agent in CAAS.
    """
    agent = openagx_provider.register_agent(agent_id, metadata)
    return agent


@app.get("/api/v1/caas/agents/{agent_id}")
async def get_caas_agent(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get agent.
    """
    agent = openagx_provider.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


# --- Authorization ---

class CAAuthorizeRequest(BaseModel):
    agent_id: str
    resource_owner: str
    scope: List[str] = []


@app.post("/api/v1/caas/authorize")
async def caas_authorize(data: CAAuthorizeRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    Authorize agent.
    """
    grant = caas_client.authorize(data.agent_id, data.resource_owner, data.scope)
    return {"grant_id": grant.grant_id, "expires_in": grant.expires_at}


@app.post("/api/v1/caas/token")
async def caas_token_exchange(grant_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Exchange grant for token.
    """
    try:
        token = caas_client.exchange(grant_id)
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Token Operations ---

@app.post("/api/v1/caas/introspect")
async def caas_introspect(access_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Introspect token.
    """
    result = caas_client.introspect(access_token)
    return result


@app.post("/api/v1/caas/validate")
async def caas_validate(access_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Validate token.
    """
    result = caas_client.validate(access_token)
    return result


@app.post("/api/v1/caas/revoke")
async def caas_revoke(access_token: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Revoke token.
    """
    result = caas_client.revoke(access_token)
    return {"status": "revoked" if result else "not_found"}


@app.post("/api/v1/caas/scope/check")
async def caas_check_scope(access_token: str, required_scope: str,
                        tenant_id: str = Depends(get_tenant_id)):
    """
    Check scope.
    """
    result = caas_client.require_scope(access_token, required_scope)
    return {"has_scope": result}


# --- Delegation ---

class CADelegationRequest(BaseModel):
    from_agent: str
    to_agent: str
    scope: List[str] = []


@app.post("/api/v1/caas/delegation")
async def caas_delegate(data: CADelegationRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    Delegate agent access.
    """
    grant = caas_client.delegate(data.from_agent, data.to_agent, data.scope)
    return {"grant_id": grant.grant_id}


@app.get("/api/v1/caas/delegation/{agent_id}")
async def caas_delegation_chain(agent_id: str, tenant_id: str = Depends(get_tenant_id)):
    """
    Get delegation chain.
    """
    chain = caas_client.get_delegation_chain(agent_id)
    return {"chain": chain}


# --- Impersonation ---

class CAImpersonateRequest(BaseModel):
    agent_id: str
    target_agent: str
    scope: List[str] = []


@app.post("/api/v1/caas/impersonate")
async def caas_impersonate(data: CAImpersonateRequest, tenant_id: str = Depends(get_tenant_id)):
    """
    Impersonate another agent.
    """
    grant = caas_client.impersonate(data.agent_id, data.target_agent, data.scope)
    return {"grant_id": grant.grant_id}


# --- Policy ---

@app.post("/api/v1/caas/policies/{policy_name}")
async def set_caas_policy(policy_name: str, policy: Dict[str, Any],
                        tenant_id: str = Depends(get_tenant_id)):
    """
    Set policy.
    """
    caas_client.set_policy(policy_name, policy)
    return {"status": "set", "policy": policy_name}


@app.get("/api/v1/caas/evaluate")
async def caas_evaluate(agent_id: str, action: str, resource: str,
                       tenant_id: str = Depends(get_tenant_id)):
    """
    Evaluate policy.
    """
    result = caas_client.evaluate_policy(agent_id, action, resource)
    return result
