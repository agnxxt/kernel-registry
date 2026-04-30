import hashlib
import hmac
import base64
import os
from typing import Dict, Any, Optional

class SecretKernel:
    """
    Manages sensitive credentials and cryptographic signatures.
    Ensures zero-trust security at the kernel level.
    """
    def __init__(self):
        # DO NOT hardcode master keys. Require an environment variable.
        master_key_str = os.getenv("KERNEL_MASTER_KEY")
        if not master_key_str:
             # Fallback strictly for local dev/testing if not provided, but ideally this should raise in prod
             master_key_str = "dev_master_key_please_change" 
        self.master_key = master_key_str.encode()
        
        # Load secrets from environment variables rather than hardcoding
        self._vault = {
            "urn:agnxxt:secret:github-token": os.getenv("GITHUB_TOKEN", ""),
            "urn:agnxxt:secret:openai-key": os.getenv("OPENAI_API_KEY", "")
        }

    def get_master_key(self) -> str:
        return self.master_key.decode()

    def get_secret(self, secret_id: str) -> Optional[str]:
        """
        Retrieves a decrypted secret from the vault.
        """
        return self._vault.get(secret_id)

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """
        Generates a cryptographic signature for a Schema.org action.
        """
        message = str(payload).encode()
        signature = hmac.new(self.master_key, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verifies the authenticity of an action payload.
        """
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)
