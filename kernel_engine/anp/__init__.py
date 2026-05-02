"""ANP - Agent Network Protocol"""
import asyncio
import uuid
import random
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class ProtocolVersion(Enum):
    V1 = "1.0"
    V2 = "2.0"

class PeerState(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SUSPECTED = "suspected"

@dataclass
class Peer:
    peer_id: str
    address: str
    state: PeerState = PeerState.CONNECTED
    last_seen: datetime = field(default_factory=datetime.now)
    reputation: float = 1.0
    
    def is_alive(self) -> bool:
        age = (datetime.now() - self.last_seen).total_seconds()
        return self.state == PeerState.CONNECTED and age < 300

class PeerRegistry:
    """Peer registry with reputation"""
    def __init__(self):
        self.peers: Dict[str, Peer] = {}
        
    def register(self, peer_id: str, address: str) -> Peer:
        self.peers[peer_id] = Peer(peer_id, address)
        return self.peers[peer_id]
        
    def unregister(self, peer_id: str):
        if peer_id in self.peers:
            self.peers[peer_id].state = PeerState.DISCONNECTED
            
    def get_peers(self, limit: int = 10) -> List[Peer]:
        alive = [p for p in self.peers.values() if p.is_alive()]
        return sorted(alive, key=lambda p: p.reputation, reverse=True)[:limit]
        
    def update_reputation(self, peer_id: str, delta: float):
        if peer_id in self.peers:
            self.peers[peer_id].reputation = max(0, min(1, 
                self.peers[peer_id].reputation + delta))

class ServiceDiscovery:
    """Service discovery"""
    def __init__(self):
        self.services: Dict[str, Dict[str, str]] = {}
        
    def register(self, service: str, agent_id: str, endpoint: str):
        if service not in self.services:
            self.services[service] = {}
        self.services[service][agent_id] = endpoint
        
    def discover(self, service: str) -> List[str]:
        return list(self.services.get(service, {}).values())

class GossipProtocol:
    """Gossip-based message propagation"""
    def __init__(self, fanout: int = 3):
        self.fanout = fanout
        self.messages: Set[str] = set()
        
    def propagate(self, message_id: str, peers: List[str]):
        self.messages.add(message_id)
        selected = random.sample(peers, min(self.fanout, len(peers)))
        return selected

__all__ = ['PeerRegistry', 'Peer', 'ServiceDiscovery', 'GossipProtocol']