# Complete Entity Schema - Decide (all 127 tables)

## Summary

| Domain | Tables | Files |
|--------|--------|-------|
| Agent | 8 | agent.py |
| Billing | 4 | billing.py |
| Collaboration | 9 | collaboration.py |
| Component | 3 | component.py |
| Control Plane | 15 | control_plane.py |
| Decision | 9 | decision.py |
| Execution Identity | 2 | execution_identity.py |
| Master Data | 12 | master_data.py |
| Memory | 2 | memory.py |
| Prompt/Skill/Goal/Timeline | 13 | prompt_skills_goals_timelines.py |
| Skill | 4 | skill.py |
| Template | 3 | template.py |
| Tenant/Employee | 6 | tenant_employee.py |
| Trace | 4 | trace.py |
| Workflow | 13 | workflow.py |
| Workflow Definition | 8 | workflow_definition.py |
| **Total** | **127** | **16 files** |

---

## 1. Agent (8 tables) - agent.py

| Table | Purpose |
|-------|---------|
| Agent | Main agent |
| AgentIdentity | Agent credentials |
| AgentProfile | Profile data |
| AgentSkill | Skills |
| AgentGovernanceProfile | Governance settings |
| AgentMemoryProfile | Memory config |
| AgentRelationship | Agent-agent relations |
| EmployeeAgentAssignment | User-agent assignments |

---

## 2. Billing (4 tables) - billing.py

| Table | Purpose |
|-------|---------|
| BillingAdapterBinding | Adapter config |
| BillingAccountBinding | Accounts |
| BillingEvent | Usage events |
| MeterDefinition | Meter definitions |

---

## 3. Collaboration (9 tables) - collaboration.py

| Table | Purpose |
|-------|---------|
| Tenant | Multi-tenant org |
| Product | Product |
| Project | Project |
| ProjectGroup | Grouping |
| Team | Team |
| TeamMember | Team membership |
| TeamProject | Project assignment |
| TenantFeature | Features |
| TenantTag | Tags |

---

## 4. Component (3 tables) - component.py

| Table | Purpose |
|-------|---------|
| FlowComponent | LangFlow component |
| ComponentVersion | Versioned component |
| ComponentArtifact | Component files |

---

## 5. Control Plane (15 tables) - control_plane.py

| Table | Purpose |
|-------|---------|
| ExecutionRequest | Execution requests |
| ExecutionResponse | Execution responses |
| DecisionRecord | Decision records |
| RunConfig | Run config |
| ExecutionStatus | Status tracking |
| ExecutionMetrics | Metrics |
| RetryPolicy | Retry rules |
| TimeoutPolicy | Timeout rules |
| RateLimitPolicy | Rate limits |
| ExecutionPolicy | Policies |
| ExecutionLog | Execution logs |
| ExecutionEvent | Events |
| ExecutionWebhook | Webhooks |
| ExecutionGuardrail | Guardrails |
| GuardrailRule | Guardrail rules |

---

## 6. Decision (9 tables) - decision.py ⭐

| Table | Purpose |
|-------|---------|
| Decision | Main decision |
| DecisionAlternative | Alternatives |
| DecisionEvidence | Evidence |
| DecisionCriterion | Criteria |
| DecisionScore | Scores |
| DecisionRecommendation | Recommendations |
| DecisionApprovalStep | Approval workflow |
| DecisionOutcomeReview | Outcome review |
| DecisionEvent | Events |

---

## 7. Execution Identity (2 tables) - execution_identity.py

| Table | Purpose |
|-------|---------|
| Credential | Credentials |
| IdentityToken | Tokens |

---

## 8. Master Data (12 tables) - master_data.py

| Table | Purpose |
|-------|---------|
| SkillDefinition | Skill definitions |
| SkillVersion | Skill versions |
| SkillPromotion | Promotion records |
| PromptDefinition | Prompts |
| PromptVersion | Prompt versions |
| GoalDefinition | Goals |
| GoalMilestone | Goal milestones |
| TimelineDefinition | Timelines |
| TimelineEvent | Timeline events |
| PolicyDefinition | Policies |
| PolicyVersion | Policy versions |
| MasterTag | Tags |

---

## 9. Memory (2 tables) - memory.py

| Table | Purpose |
|-------|---------|
| MemorySpace | Memory space |
| MemoryEntry | Memory entries |

---

## 10. Prompt/Skill/Goal/Timeline (13 tables) - prompt_skills_goals_timelines.py

| Table | Purpose |
|-------|---------|
| PromptTemplate | Prompt templates |
| PromptVariable | Variables |
| PromptVersion | Versioned prompts |
| PromptBinding | Bindings |
| SkillDefinition | Skills |
| SkillVersion | Skill versions |
| SkillBinding | Skill bindings |
| GoalDefinition | Goals |
| GoalCheckin | Check-ins |
| TimelineDefinition | Timelines |
| TimelineMilestone | Milestones |
| TimelineEvent | Events |
| TimelineRecurrence | Recurrence |

---

## 11. Skill (4 tables) - skill.py

| Table | Purpose |
|-------|---------|
| SkillDefinition | Skill definitions |
| SkillVersion | Skill versions |
| SkillBinding | Bindings |
| SkillPromotionRecord | Promotion history |

---

## 12. Template (3 tables) - template.py

| Table | Purpose |
|-------|---------|
| Template | Templates |
| TemplateVersion | Versioned |
| TemplateBinding | Bindings |

---

## 13. Tenant/Employee (6 tables) - tenant_employee.py

| Table | Purpose |
|-------|---------|
| Tenant | Organization |
| Employee | User |
| TenantEmployee | Tenant-user mapping |
| EmployeeRole | Roles |
| TenantRole | Tenant roles |
| TenantEmployeeRole | Role assignment |

---

## 14. Trace (4 tables) - trace.py

| Table | Purpose |
|-------|---------|
| TraceSession | Session |
| TraceSpanRecord | Span |
| TraceLink | Links |
| UsageRecord | Usage |

---

## 15. Workflow (13 tables) - workflow.py

| Table | Purpose |
|-------|---------|
| Task | Task |
| TaskDependency | Dependencies |
| TaskAssignmentHistory | Assignment history |
| Milestone | Milestone |
| MilestoneTask | Task-milestone |
| Deadline | Deadlines |
| Escalation | Escalations |
| Reminder | Reminders |
| TaskComment | Comments |
| TaskAttachment | Attachments |
| TaskCommentAttachment | Comment attachments |
| TaskRating | Ratings |
| TaskFeedback | Feedback |

---

## 16. Workflow Definition (8 tables) - workflow_definition.py

| Table | Purpose |
|-------|---------|
| WorkflowDefinition | Workflow def |
| WorkflowVersion | Versioned |
| WorkflowNode | Nodes |
| WorkflowEdge | Edges |
| WorkflowValidationResult | Validation |
| WorkflowPublishArtifact | Published |
| WorkflowRun | Runs |
| WorkflowRunStep | Run steps |

---

## Kernel Coverage

| Decide Domain | Kernel File | Coverage |
|--------------|-----------|------------|
| Decision (9) | decision.py | ✅ Full |
| Workflow Definition (8) | workflow_db.py + workflow_engine.py | ✅ Full |
| Agent (8) | flow.py + taxonomy.py | Partial |
| Skill (4) | taxonomies.py | ✅ Full |
| Memory (2) | memory.py | ✅ Full |
| Trace (4) | executor.py + telemetry.py | Partial |
| Billing (4) | wallet_manager.py | Partial |

**Missing in Kernel:**
- Collaboration (9)
- Component (3)
- Master Data (12)
- Template (3)
- Tenant/Employee (6)