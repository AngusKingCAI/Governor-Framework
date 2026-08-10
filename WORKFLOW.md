# Governor Framework Development Workflow

This document defines the optimized governance workflow used for all Governor Framework development tasks to ensure enterprise compliance and auditability. The workflow leverages Devin CLI subagent capabilities for parallel execution and complex orchestration.

## Workflow Architecture

The workflow uses a **hybrid pattern** combining:
- **Parallel execution** using background subagents for independent tasks
- **Sequential core** for dependent phases with clear dependencies
- **Iteration loops** at evaluation gates for quality enforcement
- **DAG structure** for explicit dependency tracking and audit reconstruction

## Pre-Planning Phase

### 1. USER_PROMPT
Starting point from user request. All development tasks begin with a clear user prompt defining the requirements.

### 2. CLARIFY_INTENT
Ensure understanding of requirements before proceeding. The agent must confirm it understands what is being requested.

### 3. PARALLEL_INITIALIZATION (Background Subagents)
Spawn parallel background subagents for independent analysis:
- **Subagent A**: RISK_CLASSIFICATION - Classify task risk level (Low/Medium/Critical) based on:
  - Data access requirements (PII, production data, customer data)
  - System impact (infrastructure, deployment pipelines, security systems)
  - Tool access needed (file system, APIs, external systems)
  - Potential blast radius if something goes wrong
- **Subagent B**: DEFINE_BOUNDARIES - Explicitly define governance boundaries:
  - File access: What files can be read/write
  - Tool usage: Which tools can be used
  - Data access: What data access is permitted
  - Approval requirements: Actions requiring human approval
  - Blocked actions: Actions completely blocked
  - Scope boundaries: Systems out of scope

**Parallel Execution**: Both subagents run simultaneously, parent agent collects results when both complete.

### 4. SYNTHESIZE_INITIALIZATION
Parent agent synthesizes results from both parallel subagents:
- Combine risk classification with boundary definitions
- Ensure boundaries are appropriate for risk level
- Present combined initialization for user approval

## Planning Phase

### 5. PARALLEL_RESEARCH (Background Subagents)
Spawn parallel research subagents for different research aspects:
- **Subagent A**: Technical research - Existing solutions, best practices, technical feasibility
- **Subagent B**: Compliance research - Regulatory requirements, industry standards, legal considerations
- **Subagent C**: Risk analysis - Security implications, data handling, third-party dependencies

**Parallel Execution**: All research subagents run simultaneously, each focused on specific domain.

### 6. SYNTHESIZE_RESEARCH
Parent agent synthesizes research findings:
- Combine results from all research subagents
- Identify conflicts or gaps in research
- Create unified research summary with evidence

### 7. VERIFY_RESEARCH
Present synthesized research findings for user approval with supporting evidence. User must approve before proceeding.

### 8. PLAN
Create implementation strategy based on approved research. Plan must be detailed and actionable with explicit dependencies.

### 9. EVALUATION_GATE (Iteration Loop)
Automated quality checks on plan:
- **Completeness**: Are all required components addressed?
- **Feasibility**: Is the plan technically achievable?
- **Risk alignment**: Does the plan match the risk classification?
- **Dependency validation**: Are dependencies explicit and achievable?

**Iteration Loop**: If evaluation gate fails, loop back to step 8 (PLAN) with specific feedback. Maximum 3 iterations to prevent runaway loops.

### 10. VERIFY_PLAN
Present implementation plan for user approval with evaluation results. User must approve before implementation.

## Implementation Phase

### 11. IMPLEMENT
Execute implementation based on approved plan with version control. All changes must be tracked.

### 12. PARALLEL_VALIDATION (Background Subagents)
Spawn parallel validation subagents:
- **Subagent A**: Code quality validation - Standards compliance, formatting, best practices
- **Subagent B**: Compliance validation - Governance rules, boundary adherence, security requirements
- **Subagent C**: Dependency validation - Import correctness, package compatibility, version conflicts

**Parallel Execution**: All validation subagents run simultaneously, each focused on specific validation domain.

### 13. SYNTHESIZE_VALIDATION
Parent agent synthesizes validation results:
- Combine findings from all validation subagents
- Identify critical issues vs. warnings
- Create unified validation report

### 14. SUMMARIZE_IMPLEMENTATION
Present implementation changes and validation synthesis for user verification. User must review and approve changes.

### 15. EVALUATION_GATE (Iteration Loop)
Automated quality checks on implementation:
- **Code quality**: Does code meet standards?
- **Compliance**: Are governance rules followed?
- **Security**: Are security requirements met?
- **Validation synthesis**: Are all validation results acceptable?

**Iteration Loop**: If evaluation gate fails, loop back to step 11 (IMPLEMENT) with specific feedback. Maximum 3 iterations.

## Testing Phase

### 16. PARALLEL_TESTING (Background Subagents)
Spawn parallel testing subagents:
- **Subagent A**: Unit testing - Individual component testing
- **Subagent B**: Integration testing - Component interaction testing
- **Subagent C**: Security testing - Vulnerability scanning, penetration testing
- **Subagent D**: Performance testing - Load testing, response time validation

**Parallel Execution**: All testing subagents run simultaneously, each focused on specific testing domain.

### 17. SYNTHESIZE_TEST_RESULTS
Parent agent synthesizes test results:
- Combine results from all testing subagents
- Identify critical failures vs. warnings
- Create unified test report with coverage metrics

### 18. SUMMARIZE_TEST_RESULTS
Present synthesized test outcomes for user verification. User must review test results.

### 19. EVALUATION_GATE (Iteration Loop)
Automated quality checks on tests:
- **Coverage**: Do tests cover critical paths?
- **Thresholds**: Do tests meet quality thresholds?
- **Regression**: Do tests prevent regressions?
- **Test synthesis**: Are all test results acceptable?

**Iteration Loop**: If evaluation gate fails, loop back to step 16 (PARALLEL_TESTING) with specific feedback. Maximum 3 iterations.

## Review Phase

### 20. COMPREHENSIVE_REVIEW (Managed Devins)
For complex tasks, spawn managed Devins for specialized review:
- **Managed Devin A**: Architecture review - Design patterns, modularity, scalability
- **Managed Devin B**: Security review - Security posture, vulnerability assessment
- **Managed Devin C**: Compliance review - Regulatory compliance, documentation completeness

**Parallel Execution**: Managed Devins work in parallel, coordinator agent synthesizes results.

### 21. SYNTHESIZE_REVIEW
Parent/coordinator agent synthesizes review findings:
- Combine results from all review agents
- Identify critical issues vs. recommendations
- Create unified review report

### 22. SUMMARIZE_REVIEW
Present synthesized review findings for final user approval. User must approve final work.

### 23. PROOF_BUNDLE_GENERATION
Create immutable proof bundle containing:
- **Complete pipeline snapshot**: Versioned configuration, dependency graph
- **All evaluation results**: Every metric score from evaluation gates with iteration history
- **Subagent execution logs**: Parallel execution timeline, resource usage, decision points
- **Approval records**: Who approved, what they reviewed, when, conditions, iteration history
- **Deployment metadata**: Version information, timestamps, environment details
- **Audit trail links**: References to complete audit records with hash verification

Proof bundle enables regulatory compliance and audit reconstruction with full provenance.

## Completion Phase

### 24. AUDIT_TRAIL_UPDATE
Update immutable audit trail with full workflow record:
- All workflow steps with timestamps
- Subagent execution details and results
- Evaluation gate iterations and decisions
- User approvals with evidence reviewed
- Proof bundle hash and verification links

### 25. COMPLETE
Task completion after user approval and proof bundle verification. Only then is the task considered complete.

## Strict Governance Principles

- **Version control**: Every artifact must be version-controlled with metadata
- **Parallel execution with coordination**: Independent tasks run in parallel with proper result synthesis
- **Evaluation gates with iteration loops**: Must pass before state transitions, with limited iterations
- **Evidence-based approval**: Human approval requires evidence review, not acknowledgment
- **Immutable audit trail**: Audit trail is hash-verified and tamper-evident
- **Proof bundles**: Enable regulatory compliance and audit reconstruction with full provenance
- **Risk-based governance**: Risk classification determines required governance rigor
- **Agent-agnostic design**: Governor Framework state machine supports different workflows
- **Cost-aware parallelism**: Subagent usage is deliberate and justified by parallel benefits

## Risk-Based Controls

- **Low Risk**: Standard workflow with basic parallel execution (2-3 subagents)
- **Medium Risk**: Enhanced parallel execution (4-6 subagents), additional evaluation gates
- **Critical Risk**: Maximum parallel execution (7+ subagents + managed Devins), multi-stage approvals, comprehensive audit trail

## Iteration Loop Safeguards

- **Maximum iterations**: Each evaluation gate has maximum 3 iterations to prevent runaway loops
- **Hard stop conditions**: Workflow terminates if maximum iterations exceeded without success
- **Progressive escalation**: Failed iterations escalate to higher-level review
- **Cost monitoring**: Parallel execution is cost-monitored to prevent excessive spend

## Implementation

The workflow leverages modern AI agent capabilities:
- **Background subagents** for parallel execution of independent tasks
- **Skill orchestration** for workflow coordination and decision logic
- **Custom subagent profiles** for specialized analysis (risk, compliance, security)
- **Managed agents** for complex parallel review workflows
- **Iteration loops** implemented through skill orchestration logic
- **Governor Framework hooks** for enforcement at critical transition points

## Enforcement Mechanism

The existing Governor Framework is used to enforce adherence to this workflow through:
- Hook-based interception at critical transition points
- State machine tracking of workflow phase progression with subagent coordination
- Automatic validation of evaluation gate requirements and iteration limits
- Audit trail generation for all workflow steps including subagent execution
- Proof bundle generation and verification with parallel execution provenance
- Cost monitoring and alerting for subagent usage

This creates a self-governing system where the current Governor enforces the improved workflow for building the next version of Governor, leveraging modern parallel execution capabilities while maintaining strict compliance.