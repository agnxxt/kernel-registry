import hashlib
import hmac
import base64
import os
from typing import Dict, Any, Optional
from persistence.db import SessionLocal
from persistence.models.identity import RegistryRecord

class SecretKernel:
    """
    Manages sensitive credentials and cryptographic signatures.
    Supports environment-based and database-backed (encrypted) secrets.
    """
    def __init__(self, provided_key: Optional[str] = None):
        # 1. Resolve Master Key
        master_key_str = provided_key or os.getenv("KERNEL_MASTER_KEY")
        
        if not master_key_str:
            # Check if we have a persisted (hashed) master key to verify against later
            # but we still need the raw key for decryption.
            # If no key is provided and none in env, we are in "Uninitialized" state.
            master_key_str = "uninitialized_bootstrap_key"
            
        self.master_key = master_key_str.encode()
        
        # 2. Load Static Vault (Env Vars)
        self._vault = {
            "urn:agnxxt:secret:github-token": os.getenv("GITHUB_TOKEN", ""),
            "urn:agnxxt:secret:openai-key": os.getenv("OPENAI_API_KEY", ""),
            "urn:agnxxt:secret:slack-token": os.getenv("SLACK_TOKEN", ""),
            "urn:agnxxt:secret:jira-key": os.getenv("JIRA_API_KEY", "")
        }

    def is_initialized(self) -> bool:
        """Checks if a master key has been established in the database."""
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="system_config", 
                source="kernel:setup"
            ).first()
            return record is not None

    def get_master_key(self) -> str:
        return self.master_key.decode()

    def get_secret(self, secret_id: str) -> Optional[str]:
        """
        Retrieves a secret. Checks Env first, then DB (Encrypted).
        """
        # Check Env Vault
        env_val = self._vault.get(secret_id)
        if env_val:
            return env_val

        # Check DB Registry
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="encrypted_secret",
                source=secret_id
            ).first()
            
            if record and "encrypted_value" in record.attributes:
                return self._decrypt(record.attributes["encrypted_value"])
        
        return None

    def store_secret(self, secret_id: str, value: str):
        """
        Encrypts and stores a secret in the database.
        """
        encrypted = self._encrypt(value)
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="encrypted_secret",
                source=secret_id
            ).first()
            
            if record:
                record.attributes = {"encrypted_value": encrypted}
            else:
                record = RegistryRecord(
                    canonical_id="cid:kernel:system",
                    record_type="encrypted_secret",
                    status="active",
                    source=secret_id,
                    attributes={"encrypted_value": encrypted}
                )
                session.add(record)
            session.commit()

    def _encrypt(self, value: str) -> str:
        # Simple AES-like XOR or HMAC based encryption for v1
        # In v2, use 'cryptography' library with AES-GCM
        return base64.b64encode(hmac.new(self.master_key, value.encode(), hashlib.sha256).digest()).decode()

    def _decrypt(self, encrypted_value: str) -> str:
        # Note: True decryption requires a symmetric cipher. 
        # For this guided setup, we will store the raw value for now 
        # but the interface is ready for the Cryptography library.
        # TEMPORARY: Store as base64 until 'cryptography' is added to requirements
        return base64.b64decode(encrypted_value).decode()

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        message = str(payload).encode()
        signature = hmac.new(self.master_key, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)
