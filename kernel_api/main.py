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
