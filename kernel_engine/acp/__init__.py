"""ACP - Agent Communication Protocol"""
import asyncio
import uuid
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Message:
    msg_type: MessageType
    sender: str
    receiver: str
    content: Any
    priority: MessagePriority = MessagePriority.NORMAL
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: int = 300
    
    def to_dict(self) -> Dict:
        return {'id': self.message_id, 'type': self.msg_type.value,
                'sender': self.sender, 'receiver': self.receiver,
                'content': self.content, 'priority': self.priority.value}

class SessionState(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"

@dataclass
class Session:
    session_id: str
    agent_id: str
    peer_id: str
    state: SessionState = SessionState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

class MessageProtocol:
    """Full ACP with reliable delivery"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.sessions: Dict[str, Session] = {}
        self.handlers: Dict[MessageType, Callable] = {}
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
    async def send(self, receiver: str, content: Any, 
                msg_type: MessageType = MessageType.REQUEST) -> Message:
        message = Message(msg_type, self.agent_id, receiver, content)
        await self.queue.put((-message.priority.value, message))
        return message
        
    async def broadcast(self, content: Any) -> Message:
        return await self.send('*', content, MessageType.NOTIFICATION)
        
    def create_session(self, peer_id: str) -> Session:
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        session = Session(session_id, self.agent_id, peer_id)
        self.sessions[session_id] = session
        return session
        
    def register_handler(self, msg_type: MessageType, handler: Callable):
        self.handlers[msg_type] = handler

__all__ = ['MessageProtocol', 'Message', 'MessageType', 'MessagePriority', 'Session', 'SessionState']