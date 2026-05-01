import os
import json
import requests
from typing import Dict, Any

FGA_URL = os.getenv("FGA_API_URL", "http://localhost:8081")

def setup_openfga():
    """
    Initializes the OpenFGA Authorization Model for the Agent Kernel.
    """
    print(f"Connecting to OpenFGA at {FGA_URL}...")
    
    # 1. Create Store
    try:
        res = requests.post(f"{FGA_URL}/stores", json={"name": "agent-kernel-authz"})
        store_id = res.json()["id"]
        print(f"Store created: {store_id}")
    except Exception as e:
        print(f"Store exists or connection failed: {e}")
        return

    # 2. Define Authorization Model
    model = {
      "schema_version": "1.1",
      "type_definitions": [
        {
          "type": "user",
          "relations": {}
        },
        {
          "type": "agent",
          "relations": {
            "owner": { "this": {} },
            "sponsor": { "this": {} },
            "can_manage": {
              "computed_userset": { "relation": "owner" }
            },
            "can_act_as": {
              "union": {
                "child": [
                  { "computed_userset": { "relation": "owner" } },
                  { "computed_userset": { "relation": "sponsor" } }
                ]
              }
            }
          }
        },
        {
          "type": "resource",
          "relations": {
            "viewer": { "this": {} },
            "editor": { "this": {} },
            "manager": { "this": {} }
          }
        }
      ]
    }

    res = requests.post(f"{FGA_URL}/stores/{store_id}/authorization-models", json=model)
    model_id = res.json()["authorization_model_id"]
    print(f"Authorization model defined: {model_id}")
    
    # Save IDs for the kernel
    with open(".fga_config.json", "w") as f:
        json.dump({"store_id": store_id, "model_id": model_id}, f)

if __name__ == "__main__":
    setup_openfga()
