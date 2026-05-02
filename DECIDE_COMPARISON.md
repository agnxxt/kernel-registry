# Decide vs Kernel Comparison

## Feature-by-Feature

| Feature | Decide | Kernel | Winner |
|---------|--------|--------|--------|
| **LangFlow adapter** | component.py | framework_adapter.py | Tie (both) |
| **Decision chaining** | 8 SQLAlchemy models | flow.py (code primitives) | Kernel (flexible) |
| **Multi-layer memory** | 8 Python modules | memory.py + personality.py | Kernel (unified API) |
| **Skill/Tool registry** | skill.py + SQLAlchemy | taxonomies.py (35 systems) | Kernel (more taxonomies) |
| **Nodes/Edges** | DB tables | code primitives | Kernel (executable) |
| **Framework support** | 7 frameworks | 7 frameworks | Tie |

## Detailed Comparison

### 1. LangFlow Integration

**Decide**: `component.py` + `langflow_components/` folder
- Custom LangFlow components
- Import/export workflows
- LangFlow registry

**Kernel**: `framework_adapter.py`
- LangChain, CrewAI, AutoGen, LlamaIndex, Mastra, PydanticAI
- UnifiedGraph for interop
- Flow ↔ framework conversion

**Verdict**: Tie - both have adapters

### 2. Decision Chaining

**Decide**: `decision.py` (8 models)
- Decision alternatives
- Evidence tracking
- Criteria/scores
- Approval workflows
- Recommendations
- Outcome reviews
- Events

**Kernel**: `flow.py` + `executor.py`
- FlowGraph with 15 node types
- 6 edge types
- Execution states
- FlowBuilder DSL
- Branch/loop execution

**Verdict**: Kernel - more flexible, executable

### 3. Memory

**Decide**: 8 separate modules
- episodic_memory.py
- working_memory.py
- semantic_memory.py
- cortex.py
- checkpoints.py
- compaction.py
- types.py
- __init__.py

**Kernel**: `memory.py` + `personality.py` (unified)
- Working memory (bounded)
- Episodic memory
- Semantic memory (facts)
- Procedural memory (skills)
- Context window
- Vector memory (embeddings)
- Knowledge graph
- Personality (traits, style, tone)

**Verdict**: Kernel - unified API

### 4. Skill/Tool Resolution

**Decide**: 
- `skill.py` API + `skill.py` model
- SQLAlchemy tables for skills/bindings
- Version management

**Kernel**: `taxonomies.py`
- 35 taxonomy systems
- 400+ values
- agent_type, task_type, framework, model_provider, tool_type, etc.

**Verdict**: Kernel - more comprehensive

### 5. Flow Nodes/Edges

**Decide**: DB tables
- WorkflowNode (stored in PostgreSQL)
- WorkflowEdge (stored in PostgreSQL)
- Version tracking

**Kernel**: Code primitives
- Node, Edge as Python classes
- FlowGraph, FlowBuilder
- Executable (not just stored)

**Verdict**: Kernel - executable, not just stored

## Architecture

### Decide (DB-first)
```
Workflow → Nodes (DB) → Edges (DB) → Execute
```

### Kernel (Code-first)
```
FlowGraph → FlowBuilder → Execute
```

## Integration

Decide can use Kernel as backend:
- Use Kernel taxonomies instead of local
- Use Kernel memory API
- Use Kernel framework adapters
- Convert Decide workflows → Kernel flow before execution

## Summary

| Aspect | Decide | Kernel |
|--------|--------|--------|
| **Storage-first** | ✅ DB | ⚠️ Memory |
| **Code-first** | ⚠️ Basic | ✅ Flow |
| **Flexible** | ⚠️ | ✅ |
| **Executable** | ⚠️ | ✅ |
| **Integrates with Runner** | ⚠️ | ✅ |

**Conclusion**: Use Kernel for execution, Decide for UI/workflows → convert to Kernel flow before run.