"""
Schema.org Thing Types for Agent Platform

Reference: https://schema.org/Thing

Core types with properties, acceptable relations, and actions.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ThingCategory(Enum):
    CREATIVE = "CreativeWork"
    EVENT = "Event"
    GROUP = "Group"
    ORG = "Organization"
    PERSON = "Person"
    PLACE = "Place"
    PRODUCT = "Product"
    INTANGIBLE = "Intangible"
    ACTION = "Action"


# ============================================================
# Thing Types with Properties
# ============================================================

THING_TYPES = {
    # Software
    "SoftwareApplication": {
        "category": "CreativeWork",
        "description": "A software application",
        "properties": ["name", "applicationCategory", "operatingSystem", "url", "softwareVersion"],
        "actions": ["InstallAction", "UnInstallAction", "ActivateAction", "DeactivateAction"],
        "relations": ["creator", "offers", "softwareRequirements"],
    },
    "BrowserExtension": {
        "category": "SoftwareApplication",
        "description": "A browser extension",
        "properties": ["name", "alternateName", "permissions"],
        "actions": ["InstallAction", "UnInstallAction"],
        "relations": ["browser", "installUrl"],
    },
    "WebAPI": {
        "category": "SoftwareApplication",
        "description": "A Web API",
        "properties": ["name", "url", "documentation", "provider"],
        "actions": ["ReadAction", "SearchAction"],
        "relations": ["serviceUrl", "provider", "documentation"],
    },
    
    # Agent-specific
    "Agent": {
        "category": "SoftwareApplication",
        "description": "An autonomous agent",
        "properties": ["name", "description", "capabilities", "runtime"],
        "actions": ["AgentExecuteAction", "AgentDelegateAction", "ReadAction", "UpdateAction"],
        "relations": ["owner", "runtime", "capabilities", "credentials"],
    },
    "Assistant": {
        "category": "Agent",
        "description": "An AI assistant agent",
        "properties": ["name", "model", "provider"],
        "actions": ["AgentExecuteAction", "CommunicateAction"],
        "relations": ["model", "provider", "instructions"],
    },
    "Task": {
        "category": "Intangible",
        "description": "A task to be executed",
        "properties": ["name", "description", "status"],
        "actions": ["AgentExecuteAction", "StartAction", "StopAction"],
        "relations": ["agent", "input", "output", "status", "result"],
    },
    
    # Data
    "Data": {
        "category": "Intangible",
        "description": "Structured data",
        "properties": ["name", "encoding"],
        "actions": ["ReadAction", "UpdateAction", "DeleteAction"],
        "relations": ["encoding", "schema"],
    },
    "ImageObject": {
        "category": "CreativeWork",
        "description": "An image",
        "properties": ["name", "contentUrl", "encoding", "width", "height"],
        "actions": ["DownloadAction", "UploadAction", "ReadAction"],
        "relations": ["caption", "creator", "copyrightHolder"],
    },
    "MediaObject": {
        "category": "CreativeWork",
        "description": "Audio or video",
        "properties": ["name", "contentUrl", "duration", "encoding"],
        "actions": ["DownloadAction", "UploadAction", "PlayAction"],
        "relations": ["caption", "director", "actor"],
    },
    "Text": {
        "category": "Intangible",
        "description": "Text content",
        "properties": ["name", "encoding"],
        "actions": ["ReadAction", "UpdateAction"],
        "relations": ["creator"],
    },
    
    # Communication
    "Message": {
        "category": "CreativeWork",
        "description": "A communication",
        "properties": ["name", "sender", "recipient", "dateSent"],
        "actions": ["SendAction", "ReceiveAction", "CommunicateAction"],
        "relations": ["sender", "recipient", "inReplyTo", "thread"],
    },
    "Comment": {
        "category": "CreativeWork",
        "description": "A comment",
        "properties": ["name", "text", "creator"],
        "actions": ["CreateAction", "ReadAction", "DeleteAction"],
        "relations": ["creator", "about", "replyToUrl"],
    },
    "Conversation": {
        "category": "CreativeWork",
        "description": "A conversation",
        "properties": ["name", "participants"],
        "actions": ["SendAction", "ReceiveAction"],
        "relations": ["participants", "creator"],
    },
    
    # Organization & Person
    "Organization": {
        "category": "Organization",
        "description": "An organization",
        "properties": ["name", "url", "logo", "contactPoint"],
        "actions": ["UpdateAction", "ReadAction"],
        "relations": ["member", "founder", "address", "contactPoint"],
    },
    "Person": {
        "category": "Person",
        "description": "A person",
        "properties": ["name", "email", "jobTitle"],
        "actions": ["ReadAction", "UpdateAction"],
        "relations": ["memberOf", "worksFor", "address"],
    },
    
    # Product & Service
    "Product": {
        "category": "Product",
        "description": "A product",
        "properties": ["name", "brand", "price", "sku"],
        "actions": ["BuyAction", "SellAction", "GiveAction"],
        "relations": ["seller", "manufacturer", "offers"],
    },
    "Service": {
        "category": "Intangible",
        "description": "A service",
        "properties": ["name", "description", "provider"],
        "actions": ["BuyAction", "SellAction"],
        "relations": ["provider", "offers", "areaServed"],
    },
    "Membership": {
        "category": "Intangible",
        "description": "Membership",
        "properties": ["member", "status", "startDate"],
        "actions": ["GiveAction", "BuyAction"],
        "relations": ["member", "organization", "level"],
    },
    
    # Place
    "Place": {
        "category": "Place",
        "description": "A place",
        "properties": ["name", "address", "geo"],
        "actions": ["FindAction", "DiscoverAction"],
        "relations": ["address", "geo", "containedIn"],
    },
    "VirtualLocation": {
        "category": "Place",
        "description": "A virtual location",
        "properties": ["name", "url"],
        "actions": ["EnterAction", "LeaveAction"],
        "relations": ["url", "additionalType"],
    },
    
    # Event
    "Event": {
        "category": "Event",
        "description": "An event",
        "properties": ["name", "startDate", "endDate", "location"],
        "actions": ["UpdateAction", "DeleteAction"],
        "relations": ["organizer", "attendee", "location"],
    },
    
    # Action-related
    "Action": {
        "category": "Action",
        "description": "An action",
        "properties": ["name", "agent", "object", "result"],
        "actions": ["AuthorizeAction"],
        "relations": ["agent", "object", "result", "instrument"],
    },
    "Offer": {
        "category": "Intangible",
        "description": "An offer",
        "properties": ["price", "priceCurrency", "availability"],
        "actions": ["AcceptAction", "RejectAction"],
        "relations": ["seller", "buyer", "itemOffered"],
    },
    
    # Admin
    "ApiKey": {
        "category": "Intangible",
        "description": "API key or credential",
        "properties": ["name", "key", "scope"],
        "actions": ["CreateAction", "RevokeAction", "ReadAction"],
        "relations": ["owner", "scope", "expires"],
    },
    "Role": {
        "category": "Intangible",
        "description": "A role",
        "properties": ["name", "permissions"],
        "actions": ["AssignAction", "UnassignAction"],
        "relations": ["member", "permissions", "scope"],
    },
    "Policy": {
        "category": "Intangible",
        "description": "A policy",
        "properties": ["name", "description", "rules"],
        "actions": ["CreateAction", "UpdateAction", "ReadAction"],
        "relations": ["authority", "jurisdiction"],
    },
}


# ============================================================
# Thing Vocabulary
# ============================================================

class ThingVocabulary:
    """Schema.org thing types"""
    
    TYPES = THING_TYPES
    
    @classmethod
    def get_type_spec(cls, thing_type: str) -> Optional[Dict]:
        """Get thing specification"""
        return cls.TYPES.get(thing_type)
    
    @classmethod
    def list_types(cls, category: str = None) -> List[str]:
        """List types"""
        if category:
            return [
                t for t, spec in cls.TYPES.items()
                if spec.get("category") == category
            ]
        return list(cls.TYPES.keys())
    
    @classmethod
    def validate_type(cls, thing_type: str) -> bool:
        """Check if type is valid"""
        return thing_type in cls.TYPES
    
    @classmethod
    def get_actions_for_type(cls, thing_type: str) -> List[str]:
        """Get actions applicable to type"""
        spec = cls.TYPES.get(thing_type)
        return spec.get("actions", []) if spec else []
    
    @classmethod
    def get_relations_for_type(cls, thing_type: str) -> List[str]:
        """Get relations for type"""
        spec = cls.TYPES.get(thing_type)
        return spec.get("relations", []) if spec else []


__all__ = ['ThingCategory', 'THING_TYPES', 'ThingVocabulary']