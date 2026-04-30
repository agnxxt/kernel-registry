from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
from datetime import datetime

from kernel_engine.validator import KernelValidator
from kernel_engine.theory_identifier import TheoryIdentifier
from kernel_engine.mlflow_tracker import KernelMLflowTracker
from kernel_engine.orchestrator import CognitiveOrchestrator
from kernel_engine.watchdog import RogueWatchdog
from kernel_engine.gatekeeper import ToolGatekeeper
from kernel_engine.discovery import DiscoveryEngine

app = FastAPI(title="Agent Kernel Platform", version="1.0.0")

# Singleton Engine Instances
validator = KernelValidator("schemas/_semantic-extension.schema.json")
identifier = TheoryIdentifier()
tracker = KernelMLflowTracker()
watchdog = RogueWatchdog()
orchestrator = CognitiveOrchestrator(watchdog=watchdog)
discovery = DiscoveryEngine()
github_gatekeeper = ToolGatekeeper("GitHub")

@app.get("/health")
async def health():
    return {"status": "active", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/action")
async def process_action(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Unified entry point for all governed agent actions.
    """
    # 1. Schema Rigor
    is_valid, err = validator.validate_artifact(data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Schema Violation: {err}")

    agent_id = data.get("agent", {}).get("name", "unknown")
    run_id = str(uuid.uuid4())

    # 2. Intelligent Authentication (Gatekeeping)
    if "github" in str(data.get("object", "")).lower():
        auth_result = github_gatekeeper.authenticate_request(agent_id, data)
        if not auth_result["authenticated"]:
            return {"status": "Auth-Failed", "reason": auth_result["reason"]}

    # 3. Cognitive Orchestration
    context = {"weather": "Clear", "goal_alignment": 0.85, "failure_risk": 0.3}
    exec_result = await orchestrator.execute_plan(agent_id, data, context)
    
    # 4. Behavioral Identification & Auditing
    theories = identifier.identify_behavior(data, context)
    audit_log = identifier.generate_audit_log(data, theories)
    
    # 5. Rogue Monitoring (Watchdog)
    watchdog_status = watchdog.monitor_action(agent_id, data, exec_result)

    # 6. Lifecycle Tracking (MLflow)
    background_tasks.add_task(tracker.log_theory_identification, agent_id, run_id, audit_log)

    return {
        "execution_id": exec_result.get("execution_id", run_id),
        "status": exec_result["status"],
        "watchdog_status": watchdog_status,
        "identified_patterns": theories,
        "metadata": {
            "pathway": exec_result.get("pathway_used"),
            "authenticated": True
        }
    }

@app.post("/api/v1/admin/discover")
async def admin_discover(app_name: str):
    """
    Admin-only: Trigger discovery from connected apps.
    """
    discovered = discovery.crawl_app(app_name)
    return {"discovered_entities": discovered, "status": "Pending-Admin-Review"}

@app.post("/api/v1/admin/onboard")
async def admin_onboard(user_id: str):
    """
    Admin-only: Approve and trigger user provisioning outreach.
    """
    outreach_action = discovery.generate_provisioning_request(user_id)
    # In full system, this sends the outreach via CommunicateAction bus
    return {"status": "Outreach-Sent", "action": outreach_action}

