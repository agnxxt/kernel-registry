import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_simulation():
    print("🚀 Starting End-to-End Gemini Agent Simulation...")
    
    # 1. Construct a Universal Schema Action
    action_payload = {
        "@context": "https://schema.org",
        "@type": "ControlAction",
        "name": "Gemini Multi-Cloud Migration",
        "agent": { "@type": "SoftwareApplication", "name": "Gemini-Pro-Agent" },
        "object": { "name": "Enterprise-Data-Store", "id": "urn:agnxxt:artifact:dataset-v1" },
        "payload": {
            "text": "Migrate encrypted user records from US-East-1 to West-Europe.",
            "intent": "cross_cloud_migration",
            "model": "gemini-1.5-pro"
        },
        "runtime": {
            "provider_topology": { "primary_provider": "aws", "is_multi_cloud": True },
            "framework_signature": { "name": "LangChain", "language": "Python" }
        },
        "semantic_extension": {
            "taxonomy": { "labels": ["high_risk", "geopolitical_compliance"] },
            "attributes": {
                "failure_risk": 0.85,
                "goal_alignment": 0.95
            },
            "lineage": {
                "source_artifacts": ["urn:agnxxt:policy:gdpr-mandate"],
                "transformation_logic": "Encrypted tunnel transfer with regional validation."
            },
            "audit_tracking": {
                "created_by": "Gemini-Pro-Agent",
                "change_reason": "Scheduled quarterly data balancing."
            }
        }
    }

    # 2. Process Action (This triggers Validator, Orchestrator, ModelRunner, and Graph)
    try:
        print("\n[Kernel] Ingesting Action...")
        response = requests.post(f"{BASE_URL}/api/v1/action", json=action_payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Kernel Result:")
            print(json.dumps(result, indent=2))
            
            # 3. Check MLflow Audit / Identity
            print("\n[Kernel] Verifying Identity & Trust Score...")
            id_resp = requests.get(f"{BASE_URL}/api/v1/identity/Gemini-Pro-Agent")
            print(json.dumps(id_resp.json(), indent=2))
            
            # 4. Query Knowledge Graph for Lineage
            print("\n[Kernel] Querying Knowledge Graph for Lineage...")
            graph_resp = requests.get(f"{BASE_URL}/api/v1/graph/query?subject_id={result['execution_id']}")
            print(json.dumps(graph_resp.json(), indent=2))
            
        else:
            print(f"❌ Simulation Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: Ensure the server is running. {e}")

if __name__ == "__main__":
    run_simulation()
