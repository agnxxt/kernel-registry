import json
import jsonschema
from typing import Dict, Any

class KernelValidator:
    """
    Validates artifacts against the Universal Schema.org + Semantic Extension.
    """
    def __init__(self, schema_path: str = "schemas/_semantic-extension.schema.json"):
        with open(schema_path, 'r') as f:
            self.extension_schema = json.load(f)

    def validate_extension(self, extension_data: Dict[str, Any]):
        """
        Validates the semantic_extension block specifically.
        """
        try:
            jsonschema.validate(instance=extension_data, schema=self.extension_schema)
            return True, None
        except jsonschema.exceptions.ValidationError as e:
            return False, str(e)

    def validate_artifact(self, artifact_payload: Dict[str, Any]):
        """
        Validates the full Schema.org + Kernel Envelope.
        """
        # 1. Check Schema.org context
        if artifact_payload.get("@context") != "https://schema.org":
            return False, "Invalid @context. Must be https://schema.org"
        
        # 2. Check semantic_extension
        ext = artifact_payload.get("semantic_extension")
        if not ext:
            return False, "Missing semantic_extension block"
        
        valid, error = self.validate_extension(ext)
        if not valid:
            return False, f"Semantic Extension Error: {error}"
        
        # 3. Check for Audit Tracking (Mandatory for Implementation)
        if "audit_tracking" not in ext:
            return False, "Audit Tracking is mandatory for implementation"
            
        return True, None

if __name__ == "__main__":
    # Quick test
    validator = KernelValidator("../schemas/_semantic-extension.schema.json")
    test_payload = {
        "@context": "https://schema.org",
        "@type": "AssessAction",
        "semantic_extension": {
            "audit_tracking": {"created_by": "tester"}
        }
    }
    is_valid, err = validator.validate_artifact(test_payload)
    print(f"Is Valid: {is_valid}, Error: {err}")
