import os
from typing import Dict, Any, Optional
from web3 import Web3
from persistence.db import SessionLocal
from persistence.models.identity import Wallet, CanonicalIdentity

class WalletManager:
    """
    Manages agent monetary sovereignty and blockchain identities.
    Integrates with Anvil (local Ethereum) or Mainnet.
    """
    def __init__(self):
        self.rpc_url = os.getenv("BLOCKCHAIN_RPC_URL", "http://blockchain:8545")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def create_agent_wallet(self, agent_id: str) -> Dict[str, Any]:
        """
        Generates a new ETH wallet for an agent and links it to their identity.
        """
        # 1. Create Account
        account = self.w3.eth.account.create()
        
        # 2. Persist to Kernel Ledger
        with SessionLocal() as session:
            identity = session.query(CanonicalIdentity).filter(
                (CanonicalIdentity.canonical_id == agent_id) | 
                (CanonicalIdentity.subject_ref == agent_id)
            ).first()
            
            if not identity:
                 raise ValueError(f"Identity {agent_id} not found. Cannot link wallet.")

            wallet = Wallet(
                wallet_id=f"urn:agnxxt:wallet:eth:{account.address}",
                holder_canonical_id=identity.canonical_id,
                chain="Ethereum",
                network="Anvil-Local",
                address=account.address,
                public_key=str(account.key.hex()), # Encrypted in production
                verified=True
            )
            session.add(wallet)
            session.commit()

        return {
            "address": account.address,
            "chain": "Ethereum",
            "status": "Linked"
        }

    def get_balance(self, address: str) -> float:
        """
        Returns the current balance of an agent's wallet in ETH.
        """
        if not self.w3.is_connected():
            return 0.0
        balance_wei = self.w3.eth.get_balance(address)
        return float(self.w3.from_wei(balance_wei, 'ether'))

    def fund_agent(self, address: str, amount_eth: float = 1.0):
        """
        Bootstrap funding for an agent (from the local faucet/miner).
        Only works on local Anvil/Hardhat.
        """
        # Anvil's first account typically has 10k ETH
        # We can use it as a faucet
        faucet_address = self.w3.eth.accounts[0]
        tx = {
            'to': address,
            'value': self.w3.to_wei(amount_eth, 'ether'),
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(faucet_address),
        }
        # Note: faucet signing would happen here in a real script
        # On Anvil, accounts are usually unlocked.
        self.w3.eth.send_transaction(tx)

