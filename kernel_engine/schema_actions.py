"""
Schema.org Action Types for Agent Platform

Reference: https://schema.org/Action

Core Actions:
- Action (base)
- CreateAction, UpdateAction, DeleteAction
- ReadAction
- SearchAction, FindAction
- TradeAction (buy, sell)
- GiveAction, ReceiveAction
- SendAction, DeliverAction
- CommunicateAction (A2A)
- ControlAction (start, stop, pause)
- InstallAction, UnInstallAction
- ActivateAction, DeactivateAction
- authorizeAction
- ExecuteAction (run agent)

Agent-Specific:
- AgentExecuteAction
- AgentDelegateAction
- AgentImpersonateAction
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SchemaActionType(Enum):
    # CRUD
    CREATE = "CreateAction"
    READ = "ReadAction"
    UPDATE = "UpdateAction"
    DELETE = "DeleteAction"
    
    # Communication
    COMMUNICATE = "CommunicateAction"
    SEND = "SendAction"
    RECEIVE = "ReceiveAction"
    
    # Trade
    BUY = "BuyAction"
    SELL = "SellAction"
    GIVE = "GiveAction"
    TRADE = "TradeAction"
    
    # Control
    ACTIVATE = "ActivateAction"
    DEACTIVATE = "DeactivateAction"
    START = "StartAction"
    STOP = "StopAction"
    PAUSE = "PauseAction"
    RESUME = "ResumeAction"
    
    # Transfer
    DOWNLOAD = "DownloadAction"
    UPLOAD = "UploadAction"
    TRANSFER = "TransferAction"
    DELIVER = "DeliverAction"
    
    # Discovery
    DISCOVER = "DiscoverAction"
    FIND = "FindAction"
    SEARCH = "SearchAction"
    
    # Control (devices/tools)
    INSTALL = "InstallAction"
    UNINSTALL = "UnInstallAction"
    CONFIGURE = "ConfigureAction"
    
    # Agent-specific
    AGENT_EXECUTE = "AgentExecuteAction"
    AGENT_DELEGATE = "AgentDelegateAction"
    AGENT_IMPERSONATE = "AgentImpersonateAction"
    AUTHORIZE = "AuthorizeAction"
    AUTHENTICATE = "AuthenticateAction"


@dataclass
class ActionSpec:
    """Action specification from schema.org"""
    action_type: str
    description: str
    agent: Optional[str] = None  # Who performed
    object: Optional[str] = None  # What was acted upon
    target: Optional[str] = None  # Destination
    result: Optional[str] = None  # Outcome
    instrument: Optional[str] = None  # Tool used
    location: Optional[str] = None  # Where it happened
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None
    status: Optional[str] = None
    
    def to_schema_org(self) -> Dict:
        """Convert to schema.org JSON-LD"""
        return {
            "@context": "https://schema.org",
            "@type": self.action_type,
            "description": self.description,
            "agent": {"@type": "SoftwareApplication" if "Agent" in self.action_type else "Person", 
                     "name": self.agent} if self.agent else None,
            "object": self.object,
            "target": self.target,
            "result": self.result,
            "instrument": self.instrument,
            "location": self.location,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "error": self.error,
            "actionStatus": {
                "@type": self.status or "ActionStatus",
                "name": self.status or "CompletedAction"
            } if self.status else None,
        }


class ActionVocabulary:
    """Schema.org action vocabulary for agents"""
    
    # Map of action types to their properties
    ACTIONS = {
        # CRUD
        "CreateAction": {
            "parent": "Action",
            "description": "Create a new resource",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["object", "result", "instrument"],
            "acceptable_values": ["SoftwareApplication", "DataFeed", "Article", "Product", "Service"],
        },
        "ReadAction": {
            "parent": "Action", 
            "description": "Read or retrieve a resource",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["object", "result"],
            "acceptable_values": ["Thing", "Data", "Text", "ImageObject"],
        },
        "UpdateAction": {
            "parent": "Action",
            "description": "Update an existing resource",
            "object_type": "Thing",
            "result": "Thing", 
            "properties": ["object", "result", "targetCollection"],
            "acceptable_values": ["Thing", "Data", "Product"],
        },
        "DeleteAction": {
            "parent": "Action",
            "description": "Delete a resource",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["object", "instrument"],
            "acceptable_values": ["Thing", "Data", "Product"],
        },
        
        # Communication
        "CommunicateAction": {
            "parent": "Action",
            "description": "Communicate with another agent",
            "object_type": "Message",
            "result": "Message",
            "properties": ["about", "recipient", "language"],
            "acceptable_values": ["Message", "Comment", "Conversation"],
            "relations": ["sender", "recipient", "inReplyTo", "about"],
        },
        "SendAction": {
            "parent": "TransferAction",
            "description": "Send something to a destination",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["recipient", "deliveryMethod"],
            "acceptable_values": ["Message", "Product", "Parcel"],
            "relations": ["sender", "recipient", "deliveryMethod"],
        },
        "ReceiveAction": {
            "parent": "Action",
            "description": "Receive something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["sender", "deliveryMethod"],
            "acceptable_values": ["Message", "Product", "Parcel"],
            "relations": ["sender", "receiver"],
        },
        
        # Trade
        "BuyAction": {
            "parent": "TradeAction",
            "description": "Buy something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["seller", "buyer", "price", "priceCurrency"],
            "acceptable_values": ["Product", "Service", "Membership"],
            "relations": ["seller", "buyer", "broker", "offer"],
        },
        "SellAction": {
            "parent": "TradeAction", 
            "description": "Sell something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["seller", "buyer", "price", "priceCurrency"],
            "acceptable_values": ["Product", "Service"],
            "relations": ["seller", "buyer", "broker"],
        },
        "GiveAction": {
            "parent": "TransferAction",
            "description": "Give something to a recipient",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["recipient", "giver", "receiver"],
            "acceptable_values": ["Thing", "Product", "Award"],
            "relations": ["giver", "recipient", "receiver"],
        },
        
        # Control
        "ActivateAction": {
            "parent": "ControlAction",
            "description": "Activate something",
            "object_type": "Thing",
            "properties": ["instrument"],
            "acceptable_values": ["SoftwareApplication", "Device"],
            "relations": ["instrument", "target"],
        },
        "DeactivateAction": {
            "parent": "ControlAction",
            "description": "Deactivate something",
            "object_type": "Thing",
            "properties": ["instrument"],
            "acceptable_values": ["SoftwareApplication", "Device"],
            "relations": ["instrument", "target"],
        },
        "StartAction": {
            "parent": "ControlAction",
            "description": "Start something",
            "object_type": "Thing",
            "properties": ["instrument"],
            "acceptable_values": ["SoftwareApplication", "Process", "Task"],
            "relations": ["target", "instrument"],
        },
        "StopAction": {
            "parent": "ControlAction", 
            "description": "Stop something",
            "object_type": "Thing", 
            "properties": ["instrument"],
            "acceptable_values": ["SoftwareApplication", "Process", "Task"],
            "relations": ["target", "instrument"],
        },
        "PauseAction": {
            "parent": "ControlAction",
            "description": "Pause something",
            "object_type": "Thing",
            "properties": ["instrument"],
            "acceptable_values": ["SoftwareApplication", "Process"],
            "relations": ["target"],
        },
        
        # Transfer
        "DownloadAction": {
            "parent": "TransferAction",
            "description": "Download to local storage",
            "object_type": "SoftwareApplication",
            "result": "SoftwareApplication", 
            "properties": ["fromLocation", "toLocation"],
            "acceptable_values": ["SoftwareApplication", "Data", "ImageObject"],
            "relations": ["fromLocation", "toLocation", "downloadUrl"],
        },
        "UploadAction": {
            "parent": "TransferAction",
            "description": "Upload to remote storage", 
            "object_type": "SoftwareApplication",
            "result": "SoftwareApplication",
            "properties": ["fromLocation", "toLocation"],
            "acceptable_values": ["Data", "MediaObject", "ImageObject"],
            "relations": ["fromLocation", "toLocation"],
        },
        "TransferAction": {
            "parent": "Action",
            "description": "Transfer something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["fromLocation", "toLocation"],
            "acceptable_values": ["Thing", "Data"],
            "relations": ["fromLocation", "toLocation", "carrier"],
        },
        
        # Discovery
        "DiscoverAction": {
            "parent": "Action",
            "description": "Discover something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["object"],
            "acceptable_values": ["Thing", "Place", "Person"],
            "relations": ["object", "instrument"],
        },
        "FindAction": {
            "parent": "DiscoverAction",
            "description": "Find something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["found"],
            "acceptable_values": ["Thing", "Person", "Place"],
            "relations": ["found", "searcher"],
        },
        "SearchAction": {
            "parent": "Action",
            "description": "Search for something",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["query", "targetCollection"],
            "acceptable_values": ["Thing", "Product", "Article"],
            "relations": ["query", "targetCollection", "searcher"],
        },
        
        # Install/Uninstall
        "InstallAction": {
            "parent": "ControlAction",
            "description": "Install software",
            "object_type": "SoftwareApplication",
            "result": "SoftwareApplication",
            "properties": ["downloadUrl", "installUrl"],
            "acceptable_values": ["SoftwareApplication", "BrowserExtension"],
            "relations": ["downloadUrl", "installUrl", "targetPlatform"],
        },
        "UnInstallAction": {
            "parent": "ControlAction",
            "description": "Uninstall software",
            "object_type": "SoftwareApplication",
            "properties": ["targetCollection"],
            "acceptable_values": ["SoftwareApplication"],
            "relations": ["target", "installer"],
        },
        
        # Agent-specific
        "AgentExecuteAction": {
            "parent": "Action",
            "description": "Execute an agent",
            "object_type": "SoftwareApplication",
            "result": "Thing",
            "properties": ["agent", "input", "output", "context"],
            "acceptable_values": ["SoftwareApplication", "Task"],
            "relations": ["agent", "input", "output", "context", "runtime"],
        },
        "AgentDelegateAction": {
            "parent": "Action",
            "description": "Delegate to another agent",
            "object_type": "SoftwareApplication",
            "result": "Thing",
            "properties": ["delegate", "scope", "constraints"],
            "acceptable_values": ["SoftwareApplication", "Agent"],
            "relations": ["principal", "delegate", "scope", "constraints"],
        },
        "AgentImpersonateAction": {
            "parent": "Action",
            "description": "Impersonate another agent",
            "object_type": "SoftwareApplication",
            "result": "Thing",
            "properties": ["principal", "delegate", "scope"],
            "acceptable_values": ["SoftwareApplication", "Agent"],
            "relations": ["principal", "delegate", "scope", "authorizedBy"],
        },
        "AuthorizeAction": {
            "parent": "Action",
            "description": "Authorize an action",
            "object_type": "Thing",
            "result": "Thing",
            "properties": ["recipient", "scope"],
            "acceptable_values": ["Action", "Agent"],
            "relations": ["recipient", "scope", "witness"],
        },
    }
    
    # Common relations across all actions
    COMMON_RELATIONS = {
        "agent": {"type": "Thing", "description": "Direct performer"},
        "object": {"type": "Thing", "description": "Thing acted upon"},
        "result": {"type": "Thing", "description": "Outcome of action"},
        "instrument": {"type": "Thing", "description": "Tool used"},
        "location": {"type": "Place", "description": "Where action occurred"},
        "startTime": {"type": "DateTime", "description": "When started"},
        "endTime": {"type": "DateTime", "description": "When ended"},
        "error": {"type": "Thing", "description": "Error if action failed"},
        "actionStatus": {"type": "ActionStatus", "description": "Current status"},
    }
    
    @classmethod
    def get_action_spec(cls, action_type: str) -> Optional[Dict]:
        """Get action specification"""
        return cls.ACTIONS.get(action_type)
    
    @classmethod
    def list_actions(cls) -> List[str]:
        """List all action types"""
        return list(cls.ACTIONS.keys())
    
    @classmethod
    def get_actions_by_parent(cls, parent: str) -> List[str]:
        """Get actions that inherit from parent"""
        return [
            at for at, spec in cls.ACTIONS.items()
            if spec.get("parent") == parent
        ]
    
    @classmethod
    def validate_action(cls, action_type: str) -> bool:
        """Check if action type is valid"""
        return action_type in cls.ACTIONS


__all__ = [
    'SchemaActionType', 'ActionSpec', 'ActionVocabulary'
]