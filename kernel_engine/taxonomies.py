"""
Taxonomies - Classification Systems

Categories for agents, capabilities, industries, tasks, and more.
"""
from typing import Dict, List, Any
from enum import Enum


class AgentTaxonomy(Enum):
    """Agent classification by type"""
    ASSISTANT = "assistant"           # AI assistant
    AUTONOMOUS = "autonomous"         # Autonomous agent
    DELEGATE = "delegate"            # Delegate agent
    COPILOT = "copilot"              # Co-pilot agent
    ANALYZER = "analyzer"            # Analysis agent
    ORCHESTRATOR = "orchestrator"      # Orchestration agent


class AgentCapability(Enum):
    """Agent capability categories"""
    REASONING = "reasoning"
    EXECUTION = "execution"
    DISCOVERY = "discovery"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    ORCHESTRATION = "orchestration"
    MONITORING = "monitoring"


class TaskTaxonomy(Enum):
    """Task classification"""
    ANALYSIS = "analysis"
    RESEARCH = "research"
    EXECUTION = "execution"
    CREATION = "creation"
    ORCHESTRATION = "orchestration"
    MONITORING = "monitoring"
    AUTOMATION = "automation"
    DECISION = "decision"


class IndustryTaxonomy(Enum):
    """Industry classification"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    LEGAL = "legal"
    MARKETING = "marketing"


class RiskLevel(Enum):
    """Risk classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ComplianceFramework(Enum):
    """Compliance/taxonomy"""
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI = "pci"
    ISO27001 = "iso27001"
    NIST = "nist"


# ============================================================
# Taxonomy Registry
# ============================================================

TAXONOMIES = {
    "agent_type": {
        "name": "Agent Type",
        "description": "Classification of agent types",
        "values": {
            "assistant": {"description": "AI assistant", "risk": "low"},
            "autonomous": {"description": "Autonomous agent", "risk": "medium"},
            "delegate": {"description": "Delegate agent", "risk": "medium"},
            "copilot": {"description": "Copilot agent", "risk": "low"},
            "analyzer": {"description": "Analysis agent", "risk": "low"},
            "orchestrator": {"description": "Orchestration agent", "risk": "high"},
        }
    },
    "agent_capability": {
        "name": "Agent Capability",
        "description": "What agent can do",
        "values": {
            "reasoning": {"description": "Logical reasoning"},
            "execution": {"description": "Task execution"},
            "discovery": {"description": "Information discovery"},
            "communication": {"description": "Communication"},
            "analysis": {"description": "Data analysis"},
            "generation": {"description": "Content generation"},
            "orchestration": {"description": "Multi-agent orchestration"},
            "monitoring": {"description": "System monitoring"},
        }
    },
    "task_type": {
        "name": "Task Type",
        "description": "Classification of tasks",
        "values": {
            "analysis": {"description": "Analysis task"},
            "research": {"description": "Research task"},
            "execution": {"description": "Execution task"},
            "creation": {"description": "Content creation"},
            "orchestration": {"description": "Orchestration task"},
            "monitoring": {"description": "Monitoring task"},
            "automation": {"description": "Automation task"},
            "decision": {"description": "Decision task"},
        }
    },
    "industry": {
        "name": "Industry",
        "description": "Industry classification",
        "values": {
            "technology": {"description": "Technology"},
            "finance": {"description": "Finance"},
            "healthcare": {"description": "Healthcare"},
            "retail": {"description": "Retail"},
            "manufacturing": {"description": "Manufacturing"},
            "education": {"description": "Education"},
            "legal": {"description": "Legal"},
            "marketing": {"description": "Marketing"},
        }
    },
    "risk_level": {
        "name": "Risk Level",
        "description": "Risk classification",
        "values": {
            "critical": {"description": "Critical risk", "score": 100},
            "high": {"description": "High risk", "score": 75},
            "medium": {"description": "Medium risk", "score": 50},
            "low": {"description": "Low risk", "score": 25},
            "minimal": {"description": "Minimal risk", "score": 0},
        }
    },
    "compliance": {
        "name": "Compliance Framework",
        "description": "Compliance standards",
        "values": {
            "soc2": {"description": "SOC 2"},
            "hipaa": {"description": "HIPAA"},
            "gdpr": {"description": "GDPR"},
            "pci": {"description": "PCI DSS"},
            "iso27001": {"description": "ISO 27001"},
            "nist": {"description": "NIST"},
        }
    },
    "data_classification": {
        "name": "Data Classification",
        "description": "Data sensitivity",
        "values": {
            "public": {"description": "Public data"},
            "internal": {"description": "Internal data"},
            "confidential": {"description": "Confidential data"},
            "restricted": {"description": "Restricted data"},
            "pii": {"description": "Personal data"},
            "phi": {"description": "Health data"},
        }
    },
    "agent_status": {
        "name": "Agent Status",
        "description": "Agent lifecycle",
        "values": {
            "provisioning": {"description": "Being provisioned"},
            "active": {"description": "Active"},
            "suspended": {"description": "Suspended"},
            "disabled": {"description": "Disabled"},
            "decommissioned": {"description": "Decommissioned"},
        }
    },
}


class TaxonomyRegistry:
    """Taxonomy registry"""
    
    @classmethod
    def get_taxonomy(cls, name: str) -> Dict:
        """Get taxonomy"""
        return TAXONOMIES.get(name)
    
    @classmethod
    def list_taxonomies(cls) -> List[str]:
        """List taxonomies"""
        return list(TAXONOMIES.keys())
    
    @classmethod
    def get_values(cls, taxonomy: str) -> Dict:
        """Get taxonomy values"""
        tax = TAXONOMIES.get(taxonomy)
        return tax.get("values", {}) if tax else {}
    
    @classmethod
    def validate(cls, taxonomy: str, value: str) -> bool:
        """Validate value"""
        values = cls.get_values(taxonomy)
        return value in values
    
    @classmethod
    def get_risk(cls, taxonomy: str, value: str) -> str:
        """Get risk for value"""
        values = cls.get_values(taxonomy)
        spec = values.get(value, {})
        return spec.get("risk", "low")


__all__ = [
    'TAXONOMIES', 'TaxonomyRegistry',
    'AgentTaxonomy', 'AgentCapability', 'TaskTaxonomy', 
    'IndustryTaxonomy', 'RiskLevel', 'ComplianceFramework'
]