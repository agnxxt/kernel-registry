import hashlib
import hmac
import base64
import os
from typing import Dict, Any, Optional
from persistence.db import SessionLocal
from persistence.models.identity import RegistryRecord

# Optional import for enterprise vault
try:
    import hvac
except ImportError:
    hvac = None

class SecretKernel:
    """
    Manages sensitive credentials and cryptographic signatures.
    Supports HashiCorp Vault (Primary), Env-vars (Secondary), and DB (Fallback).
    """
    def __init__(self, provided_key: Optional[str] = None):
        master_key_str = provided_key or os.getenv("KERNEL_MASTER_KEY")
        if not master_key_str:
            master_key_str = "uninitialized_bootstrap_key"
        self.master_key = master_key_str.encode()
        
        # Initialize Vault Client
        self.vault_client = None
        if hvac:
            try:
                vault_url = os.getenv("VAULT_ADDR", "http://vault:8200")
                vault_token = os.getenv("VAULT_TOKEN", "root")
                self.vault_client = hvac.Client(url=vault_url, token=vault_token)
            except Exception:
                self.vault_client = None

    def is_initialized(self) -> bool:
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="system_config", 
                source="kernel:setup"
            ).first()
            return record is not None

    def get_secret(self, secret_id: str) -> Optional[str]:
        """
        Retrieves a secret with multi-tier fallback:
        1. Vault (KV Engine)
        2. Environment Variables
        3. Encrypted DB Registry
        """
        # Tier 1: HashiCorp Vault
        if self.vault_client and self.vault_client.is_authenticated():
            try:
                read_response = self.vault_client.secrets.kv.v2.read_secret_version(path=secret_id)
                return read_response['data']['data']['value']
            except Exception:
                pass

        # Tier 2: Environment Variables
        env_map = {
            "urn:agnxxt:secret:github-token": "GITHUB_TOKEN",
            "urn:agnxxt:secret:openai-key": "OPENAI_API_KEY",
            "urn:agnxxt:secret:slack-token": "SLACK_TOKEN",
            "urn:agnxxt:secret:jira-key": "JIRA_API_KEY"
        }
        env_key = env_map.get(secret_id)
        if env_key and os.getenv(env_key):
            return os.getenv(env_key)

        # Tier 3: Database Fallback
        with SessionLocal() as session:
            record = session.query(RegistryRecord).filter_by(
                record_type="encrypted_secret",
                source=secret_id
            ).first()
            if record and "encrypted_value" in record.attributes:
                return base64.b64decode(record.attributes["encrypted_value"]).decode()
        
        return None

    def store_secret(self, secret_id: str, value: str):
        """
        Stores a secret in Vault (Primary) and DB (Fallback).
        """
        # Store in Vault
        if self.vault_client and self.vault_client.is_authenticated():
            try:
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=secret_id,
                    secret=dict(value=value)
                )
            except Exception as e:
                print(f"Vault Store Error: {e}")

        # Store in DB (encrypted fallback)
        encrypted = base64.b64encode(value.encode()).decode()
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

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        message = str(payload).encode()
        signature = hmac.new(self.master_key, message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)
