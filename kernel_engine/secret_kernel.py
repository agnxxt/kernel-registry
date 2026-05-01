import hashlib
import hmac
import base64
import os
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from persistence.db import SessionLocal
from persistence.models.identity import RegistryRecord

class SecretKernel:
    """
    Industrial Secret Engine.
    Implements AES-GCM 256-bit encryption for database-backed secrets.
    """
    def __init__(self, provided_key: Optional[str] = None):
        master_key_str = provided_key or os.getenv("KERNEL_MASTER_KEY")
        if not master_key_str:
            master_key_str = "uninitialized_bootstrap_key"
        
        # Derive 32-byte key for AES-GCM
        self.master_key = hashlib.sha256(master_key_str.encode()).digest()
        self.aes = AESGCM(self.master_key)
        self.nonce = self.master_key[:12] # Deterministic nonce for this version (use random + storage in v2)

    def is_initialized(self) -> bool:
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="system_config", 
                source="kernel:setup"
            ).first()
            return record is not None

    def get_secret(self, secret_id: str, agent_id: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a secret. Checks Env first, then DB (AES-GCM Decrypted).
        """
        # 1. Check Env
        env_map = {
            "urn:agnxxt:secret:github-token": "GITHUB_TOKEN",
            "urn:agnxxt:secret:openai-key": "OPENAI_API_KEY",
            "urn:agnxxt:secret:slack-token": "SLACK_TOKEN",
            "urn:agnxxt:secret:jira-key": "JIRA_API_KEY"
        }
        env_key = env_map.get(secret_id)
        if env_key and os.getenv(env_key):
            return os.getenv(env_key)

        # 2. Check DB
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="encrypted_secret",
                source=secret_id
            ).first()
            
            if record and "encrypted_value" in record.attributes:
                return self._decrypt(record.attributes["encrypted_value"])
        
        return None

    def store_secret(self, secret_id: str, value: str):
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
        ciphertext = self.aes.encrypt(self.nonce, value.encode(), None)
        return base64.b64encode(ciphertext).decode()

    def _decrypt(self, encrypted_value: str) -> str:
        try:
            ciphertext = base64.b64decode(encrypted_value)
            return self.aes.decrypt(self.nonce, ciphertext, None).decode()
        except Exception:
            return "[DECRYPTION_ERROR]"

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        message = str(payload).encode()
        signature = hmac.new(self.master_key, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)
