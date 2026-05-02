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
            "insurance": {"description": "Insurance"},
            "realestate": {"description": "Real Estate"},
            "government": {"description": "Government"},
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
            "ferpa": {"description": "FERPA"},
            "coppa": {"description": "COPPA"},
            "sox": {"description": "SOX"},
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
            "spi": {"description": "Sensitive personal data"},
            "classified": {"description": "Classified data"},
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
    
    # NEW TAXONOMIES
    
    "runtime": {
        "name": "Runtime",
        "description": "Agent runtime environment",
        "values": {
            "openai": {"description": "OpenAI"},
            "anthropic": {"description": "Anthropic"},
            "google": {"description": "Google AI"},
            "cohere": {"description": "Cohere"},
            "local": {"description": "Local model"},
            "hybrid": {"description": "Hybrid"},
        }
    },
    "framework": {
        "name": "Framework",
        "description": "Agent framework",
        "values": {
            "langchain": {"description": "LangChain"},
            "llamaindex": {"description": "LlamaIndex"},
            "crewai": {"description": "CrewAI"},
            "autogen": {"description": "AutoGen"},
            "pydanticai": {"description": "PydanticAI"},
            "mastra": {"description": "Mastra"},
            "custom": {"description": "Custom"},
        }
    },
    "model_provider": {
        "name": "Model Provider",
        "description": "LLM provider",
        "values": {
            "openai": {"description": "OpenAI"},
            "anthropic": {"description": "Anthropic"},
            "google": {"description": "Google"},
            "cohere": {"description": "Cohere"},
            "mistral": {"description": "Mistral"},
            "meta": {"description": "Meta"},
            "aws": {"description": "AWS"},
            "azure": {"description": "Azure OpenAI"},
            "local": {"description": "Local/huggingface"},
        }
    },
    "model_size": {
        "name": "Model Size",
        "description": "Model size category",
        "values": {
            "small": {"description": "<1B parameters"},
            "medium": {"description": "1-10B parameters"},
            "large": {"description": "10-100B parameters"},
            "xlarge": {"description": ">100B parameters"},
        }
    },
    "auth_method": {
        "name": "Auth Method",
        "description": "Authentication method",
        "values": {
            "password": {"description": "Password"},
            "oauth": {"description": "OAuth"},
            "api_key": {"description": "API Key"},
            "jwt": {"description": "JWT"},
            "saml": {"description": "SAML"},
            "mfa": {"description": "Multi-factor"},
            "passkey": {"description": "Passkey/WebAuthn"},
            "did": {"description": "DID/Decentralized"},
        }
    },
    "authorization": {
        "name": "Authorization",
        "description": "Authorization model",
        "values": {
            "rbac": {"description": "Role-based"},
            "abac": {"description": "Attribute-based"},
            "fga": {"description": "Fine-grained (Zanzibar)"},
            "policy": {"description": "Policy-based"},
            "capability": {"description": "Capability-based"},
        }
    },
    "scope": {
        "name": "Scope",
        "description": "Permission scope",
        "values": {
            "read": {"description": "Read access"},
            "write": {"description": "Write access"},
            "execute": {"description": "Execute access"},
            "admin": {"description": "Admin access"},
            "delegate": {"description": "Delegate access"},
            "audit": {"description": "Audit access"},
        }
    },
    "action_status": {
        "name": "Action Status",
        "description": "Status of an action",
        "values": {
            "PotentialActionStatus": {"description": "Not yet started"},
            "ActiveActionStatus": {"description": "In progress"},
            "CompletedActionStatus": {"description": "Completed"},
            "FailedActionStatus": {"description": "Failed"},
            "AbandonedActionStatus": {"description": "Abandoned"},
        }
    },
    "deployment": {
        "name": "Deployment",
        "description": "Deployment environment",
        "values": {
            "development": {"description": "Development"},
            "staging": {"description": "Staging"},
            "production": {"description": "Production"},
            "dr": {"description": "Disaster recovery"},
            "edge": {"description": "Edge"},
        }
    },
    "cloud": {
        "name": "Cloud Provider",
        "description": "Cloud infrastructure",
        "values": {
            "aws": {"description": "AWS"},
            "gcp": {"description": "Google Cloud"},
            "azure": {"description": "Azure"},
            "private": {"description": "Private cloud"},
            "onprem": {"description": "On-premise"},
            "hybrid": {"description": "Hybrid"},
        }
    },
    "event_type": {
        "name": "Event Type",
        "description": "Event classification",
        "values": {
            "start": {"description": "Start event"},
            "stop": {"description": "Stop event"},
            "complete": {"description": "Completion event"},
            "error": {"description": "Error event"},
            "timeout": {"description": "Timeout event"},
            "rate_limit": {"description": "Rate limit event"},
            "auth_failure": {"description": "Auth failure"},
            "health_check": {"description": "Health check"},
        }
    },
    "log_level": {
        "name": "Log Level",
        "description": "Logging level",
        "values": {
            "trace": {"description": "Trace"},
            "debug": {"description": "Debug"},
            "info": {"description": "Info"},
            "warning": {"description": "Warning"},
            "error": {"description": "Error"},
            "critical": {"description": "Critical"},
        }
    },
    "metric_type": {
        "name": "Metric Type",
        "description": "Metric classification",
        "values": {
            "counter": {"description": "Counter"},
            "gauge": {"description": "Gauge"},
            "histogram": {"description": "Histogram"},
            "summary": {"description": "Summary"},
        }
    },
    "memory_type": {
        "name": "Memory Type",
        "description": "Agent memory architecture",
        "values": {
            "episodic": {"description": "Episodic memory"},
            "semantic": {"description": "Semantic memory"},
            "procedural": {"description": "Procedural memory"},
            "working": {"description": "Working memory"},
            "context": {"description": "Context window"},
            "vector": {"description": "Vector embeddings"},
            "knowledge_graph": {"description": "Knowledge graph"},
            "hybrid": {"description": "Hybrid memory"},
        }
    },
    "tool_type": {
        "name": "Tool Type",
        "description": "Tool/function classification",
        "values": {
            "function": {"description": "Function call"},
            "api": {"description": "API call"},
            "search": {"description": "Search tool"},
            "browser": {"description": "Browser automation"},
            "code_executor": {"description": "Code execution"},
            "database": {"description": "Database query"},
            "file": {"description": "File operation"},
            "http": {"description": "HTTP request"},
            "mcp": {"description": "MCP tool"},
            "agent": {"description": "Sub-agent"},
            "webhook": {"description": "Webhook"},
            "stream": {"description": "Stream processor"},
        }
    },
    "category": {
        "name": "Category",
        "description": "Content/organization category",
        "values": {
            "news": {"description": "News"},
            "blog": {"description": "Blog post"},
            "document": {"description": "Document"},
            "product": {"description": "Product"},
            "service": {"description": "Service"},
            "user": {"description": "User content"},
            "system": {"description": "System content"},
            "faq": {"description": "FAQ"},
            "tutorial": {"description": "Tutorial"},
            "reference": {"description": "Reference"},
            "api_doc": {"description": "API documentation"},
            "changelog": {"description": "Changelog"},
        }
    },
    "topics": {
        "name": "Topics",
        "description": "Subject matter topics",
        "values": {
            "artificial_intelligence": {"description": "AI"},
            "machine_learning": {"description": "Machine Learning"},
            "data_science": {"description": "Data Science"},
            "programming": {"description": "Programming"},
            "security": {"description": "Security"},
            "cloud_computing": {"description": "Cloud"},
            "devops": {"description": "DevOps"},
            "blockchain": {"description": "Blockchain"},
            "iot": {"description": "IoT"},
            "robotics": {"description": "Robotics"},
            "quantum": {"description": "Quantum computing"},
            "biotech": {"description": "Biotech"},
            "finance": {"description": "Finance"},
            "healthcare": {"description": "Healthcare"},
            "education": {"description": "Education"},
            "marketing": {"description": "Marketing"},
        }
    },
    "tags": {
        "name": "Tags",
        "description": "Flexible tagging system",
        "values": {
            "featured": {"description": "Featured"},
            "trending": {"description": "Trending"},
            "popular": {"description": "Popular"},
            "new": {"description": "New"},
            "recommended": {"description": "Recommended"},
            "verified": {"description": "Verified"},
            "premium": {"description": "Premium"},
            "beta": {"description": "Beta"},
            "deprecated": {"description": "Deprecated"},
            "experimental": {"description": "Experimental"},
        }
    },
    "place_type": {
        "name": "Place Type",
        "description": "Type of place/location",
        "values": {
            "country": {"description": "Country"},
            "region": {"description": "Region/State"},
            "city": {"description": "City"},
            "address": {"description": "Street address"},
            "virtual": {"description": "Virtual location"},
            "datacenter": {"description": "Data center"},
            "edge": {"description": "Edge location"},
            "office": {"description": "Office"},
            "home": {"description": "Home"},
            "mobile": {"description": "Mobile"},
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