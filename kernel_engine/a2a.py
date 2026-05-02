"""A2A - Agent to Agent Protocol
Universal interoperability for multi-modal, multi-language, multi-tool, 
multi-framework, and multi-cloud agent communication.
"""
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class Modality(Enum):
    TEXT = "text"
    IMAGE_REF = "image_ref"
    AUDIO_STREAM = "audio_stream"
    VIDEO_SEGMENT = "video_segment"
    STRUCTURED_DATA = "structured_data"


class Language(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"


class Framework(Enum):
    LANGCHAIN = "langchain"
    CREWAI = "crewai"
    AUTOGEN = "autogen"
    PYDANTICAI = "pydanticai"
    LLAMA_INDEX = "llamaindex"
    MASTRA = "mastra"
    SEMANTIC_KERNEL = "semantickernel"
    CUSTOM = "custom"


@dataclass
class AgentInfo:
    """Agent metadata"""
    agent_id: str
    name: str
    framework: str = "custom"
    language: str = "python"
    capabilities: List[str] = field(default_factory=list)
    cloud: str = "aws"  # aws, gcp, azure, private
    endpoint: str = ""
    urn: str = ""


@dataclass
class A2AMessage:
    """Universal A2A message envelope"""
    message_id: str = field(default_factory=lambda: f"a2a_{uuid.uuid4().hex[:12]}")
    sender: str = ""
    recipient: str = ""
    modality: str = "text"
    content: Any = ""
    language: str = "python"
    framework_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    ttl: int = 300  # 5 minutes default
    
    def to_schema_org(self) -> Dict:
        """Convert to Schema.org CommunicateAction"""
        return {
            "@context": "https://schema.org",
            "@type": "CommunicateAction",
            "name": "A2A Exchange",
            "agent": {"@type": "SoftwareApplication", "name": self.sender},
            "recipient": {"@type": "SoftwareApplication", "name": self.recipient},
            "object": {
                "@type": "DigitalDocument",
                "content": self.content,
                "encoding": {
                    "@type": "MediaObject",
                    "encodingFormat": self.modality,
                    "programmingLanguage": self.language,
                }
            },
            "result": self.framework_metadata,
        }
    
    @classmethod
    def from_schema_org(cls, data: Dict) -> "A2AMessage":
        """Parse from Schema.org CommunicateAction"""
        agent = data.get("agent", {})
        recipient = data.get("recipient", {})
        obj = data.get("object", {})
        encoding = obj.get("encoding", {})
        
        return cls(
            message_id=f"a2a_{uuid.uuid4().hex[:12]}",
            sender=agent.get("name", ""),
            recipient=recipient.get("name", ""),
            content=obj.get("content", ""),
            modality=encoding.get("encodingFormat", "text"),
            language=encoding.get("programmingLanguage", "python"),
            framework_metadata=data.get("result", {}),
        )


class A2ARegistry:
    """Agent registry for A2A discovery"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
    
    def register(self, agent: AgentInfo) -> str:
        """Register agent, return URN"""
        if not agent.urn:
            agent.urn = f"urn:agennext:agent:{agent.agent_id}"
        self.agents[agent.agent_id] = agent
        return agent.urn
    
    def unregister(self, agent_id: str):
        """Remove agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def get(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent"""
        return self.agents.get(agent_id)
    
    def discover(self, framework: str = None, language: str = None, 
               cloud: str = None, capability: str = None) -> List[AgentInfo]:
        """Discover agents by criteria"""
        results = list(self.agents.values())
        
        if framework:
            results = [a for a in results if a.framework == framework]
        if language:
            results = [a for a in results if a.language == language]
        if cloud:
            results = [a for a in results if a.cloud == cloud]
        if capability:
            results = [a for a in results if capability in a.capabilities]
        
        return results
    
    def get_by_urn(self, urn: str) -> Optional[AgentInfo]:
        """Find agent by URN"""
        for agent in self.agents.values():
            if agent.urn == urn:
                return agent
        return None


class A2ARouter:
    """Route A2A messages between agents"""
    
    def __init__(self):
        self.registry = A2ARegistry()
        self.message_history: Dict[str, List[A2AMessage]] = {}
    
    async def send(self, message: A2AMessage) -> str:
        """Send A2A message"""
        # Store in history
        if message.recipient not in self.message_history:
            self.message_history[message.recipient] = []
        self.message_history[message.recipient].append(message)
        
        # Validate recipient exists
        recipient = self.registry.get(message.recipient)
        if not recipient:
            raise ValueError(f"Unknown recipient: {message.recipient}")
        
        return message.message_id
    
    async def broadcast(self, message: A2AMessage, target_filter: Dict = None) -> List[str]:
        """Broadcast to matching agents"""
        matching = self.registry.discover(**target_filter) if target_filter else list(self.registry.agents.values())
        
        message_ids = []
        for agent in matching:
            msg = A2AMessage(
                message_id=f"a2a_{uuid.uuid4().hex[:12]}",
                sender=message.sender,
                recipient=agent.agent_id,
                content=message.content,
                modality=message.modality,
                language=message.language,
                framework_metadata=message.framework_metadata,
            )
            self.message_history[agent.agent_id].append(msg)
            message_ids.append(msg.message_id)
        
        return message_ids
    
    def get_history(self, agent_id: str) -> List[A2AMessage]:
        """Get message history for agent"""
        return self.message_history.get(agent_id, [])


class TranslationEngine:
    """Inter-modal and inter-language translation"""
    
    # Modality translation mappings
    TRANSLATIONS = {
        ("image_ref", "text"): "describe_image",
        ("audio_stream", "text"): "transcribe_audio",
        ("video_segment", "text"): "transcribe_video",
    }
    
    async def translate(self, message: A2AMessage, target_modality: str) -> A2AMessage:
        """Translate modality"""
        if message.modality == target_modality:
            return message
        
        translation_fn = self.TRANSLATIONS.get((message.modality, target_modality))
        
        return A2AMessage(
            message_id=f"a2a_{uuid.uuid4().hex[:12]}",
            sender=message.sender,
            recipient=message.recipient,
            modality=target_modality,
            content=f"[Translated from {message.modality}]: {message.content}",
            language=message.language,
            framework_metadata={
                "original_modality": message.modality,
                "translation": translation_fn,
                **message.framework_metadata,
            },
        )


__all__ = [
    'A2AMessage', 'AgentInfo', 'A2ARegistry', 'A2ARouter',
    'TranslationEngine', 'Modality', 'Language', 'Framework'
]