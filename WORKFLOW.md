# Overseer Framework Development Workflow

This document defines the optimized governance workflow used for all Overseer Framework development tasks to ensure enterprise compliance and auditability. The workflow leverages Devin CLI subagent capabilities for parallel execution and complex orchestration.

## Workflow Architecture

The workflow uses a **hybrid pattern** combining:
- **Parallel execution** using background subagents for independent tasks
- **Sequential core** for dependent phases with clear dependencies
- **Iteration loops** at evaluation gates for quality enforcement
- **DAG structure** for explicit dependency tracking and audit reconstruction

## Pre-Planning Phase

### 1. USER_PROMPT
Starting point from user request. All development tasks begin with a clear user prompt defining the requirements.

### 2. RESEARCH_BEST_PRACTICES
Research industry best practices, architectural patterns, and implementation approaches relevant to the implementation type. This research provides context for informed clarification questions.

**Research Scope:**
- Domain-specific architectural patterns and design principles
- Industry standards and conventions for the implementation type
- Security and performance considerations
- Modularity and maintainability best practices
- File structure and organization patterns

**Research Method:**
- Use web search to find current best practices
- Reference established design patterns and architectural principles
- Consider project-specific constraints and requirements
- Document key findings to inform clarification process

### 3. CLARIFY_INTENT
Ensure complete understanding of requirements before proceeding. The agent must iteratively ask pertinent questions until the user is 100% satisfied with clarity on all aspects of the implementation.

**Iterative Clarification Process:**
- Use ask_user_question tool for structured clarification with multiple-choice options
- Ask questions relevant to requirements, scope, approach, dependencies, and constraints
- Use research findings to inform question formulation and provide context for decisions
- Continue asking questions until user explicitly confirms satisfaction
- Address gaps, ambiguities, and uncertainties through targeted questioning
- Document key decisions and clarifications for reference in subsequent steps

**Exit Condition:**
- User explicitly confirms all requirements are clear and understood
- No remaining ambiguities or uncertainties
- Implementation scope and approach are fully defined

### 4. PARALLEL_INITIALIZATION (Background Subagents)
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

### 5. SYNTHESIZE_INITIALIZATION
Parent agent synthesizes results from both parallel subagents:
- Combine risk classification with boundary definitions
- Ensure boundaries are appropriate for risk level
- Present combined initialization for user approval using ask_user_question tool for structured feedback

## Planning Phase

### 6. PARALLEL_RESEARCH (Background Subagents)
Spawn parallel research subagents for different research aspects:
- **Subagent A**: Technical research - Existing solutions, best practices, technical feasibility, domain-specific architectural patterns
- **Subagent B**: Compliance research - Regulatory requirements, industry standards, legal considerations, implementation-specific standards
- **Subagent C**: Risk analysis - Security implications, data handling, third-party dependencies, domain-specific security considerations

**Parallel Execution**: All research subagents run simultaneously, each focused on specific domain.

### 7. SYNTHESIZE_RESEARCH
Parent agent synthesizes research findings:
- Combine results from all research subagents
- Identify conflicts or gaps in research
- Create unified research summary with evidence

### 8. VERIFY_RESEARCH
Present synthesized research findings for user approval with supporting evidence. Use ask_user_question tool for structured approval process. User must approve before proceeding.

### 9. PLAN
Create implementation strategy based on approved research. Plan must be detailed and actionable with explicit dependencies.

### 10. EVALUATION_GATE (Iteration Loop)
Automated quality checks on plan:
- **Completeness**: Are all required components addressed?
- **Feasibility**: Is the plan technically achievable?
- **Risk alignment**: Does the plan match the risk classification?
- **Dependency validation**: Are dependencies explicit and achievable?
- **Modularity**: Does the plan maintain proper separation of concerns and correct dependency direction?
- **Extensibility**: Does the plan support future growth and plugin architecture?
- **True Agnosticism**: Does the core system make ZERO assumptions about adapters or environment?
  - No hardcoded event types (must be dynamically registered by adapters)
  - No hardcoded naming conventions (must be configurable)
  - No CLI-specific assumptions in documentation or code
  - Adapters should be the ONLY flexible component
  - Core system must adapt to whatever adapters provide
  - Protocol/Overseer layers must be completely environment-independent

**Iteration Loop**: If evaluation gate fails, loop back to step 9 (PLAN) with specific feedback. Maximum 3 iterations to prevent runaway loops.

### 11. VERIFY_PLAN
Present implementation plan for user approval with evaluation results. Use ask_user_question tool for structured approval process. User must approve before implementation.

## Implementation Phase

### 12. IMPLEMENT
Execute implementation based on approved plan with version control. All changes must be tracked. 
For implementations requiring refactoring of existing code:
- Update dependency imports and cross-file references
- Maintain backward compatibility during migration
- Document refactoring changes in commit messages
- Test refactored code paths before proceeding

### 13. PARALLEL_VALIDATION (Background Subagents)
Spawn parallel validation subagents:
- **Subagent A**: Code quality validation - Standards compliance, formatting, best practices, architectural consistency
- **Subagent B**: Compliance validation - Governance rules, boundary adherence, security requirements, implementation-specific compliance
- **Subagent C**: Dependency validation - Import correctness, package compatibility, version conflicts, cross-component dependency verification

**Parallel Execution**: All validation subagents run simultaneously, each focused on specific validation domain.

### 14. SYNTHESIZE_VALIDATION
Parent agent synthesizes validation results:
- Combine findings from all validation subagents
- Identify critical issues vs. warnings
- Create unified validation report

### 15. SUMMARIZE_IMPLEMENTATION
Present implementation changes and validation synthesis for user verification. Use ask_user_question tool for structured review and approval process. User must review and approve changes.

### 16. EVALUATION_GATE (Iteration Loop)
Automated quality checks on implementation:
- **Code quality**: Does code meet standards?
- **Compliance**: Are governance rules followed?
- **Security**: Are security requirements met?
- **Validation synthesis**: Are all validation results acceptable?
- **Modularity**: Does implementation maintain proper separation of concerns and correct dependency direction?
- **Consistency**: Does implementation follow established code patterns and naming conventions?
- **True Agnosticism**: Does implementation make ZERO assumptions about adapters or environment?
  - No hardcoded event types or registry (must be dynamic)
  - No hardcoded naming conventions (must be configurable)
  - No CLI-specific references in code or documentation
  - Core layers must work with ANY adapter structure

**Iteration Loop**: If evaluation gate fails, loop back to step 12 (IMPLEMENT) with specific feedback. Maximum 3 iterations.

## Testing Phase

### 17. PARALLEL_TESTING (Background Subagents)
Spawn parallel testing subagents:
- **Subagent A**: Unit testing - Individual component testing, conformance testing (type validation, schema validation, interface validation)
- **Subagent B**: Integration testing - Component interaction testing, dependency testing (import verification, compatibility testing)
- **Subagent C**: Security testing - Vulnerability scanning, penetration testing, domain-specific security testing
- **Subagent D**: Performance testing - Load testing, response time validation, regression testing for refactored code

**Testing Best Practices for Protocol Layers:**
- **Layered Testing Strategy**: Unit tests → Contract tests → Integration tests → End-to-end tests
- **Schema Validation Testing**: Schema unit checks, protocol contract tests, handler unit tests
- **Test Pyramid Pattern**: Many fast unit tests, some integration tests, few end-to-end tests
- **Arrange-Act-Assert Structure**: Set up test data, call method under test, assert expected results
- **Contract Testing**: Verify published schema matches handler behavior, catch registration/serialization drift
- **Regression Testing**: Ensure refactoring preserves behavior, test import paths and compatibility
- **Security Testing**: Validate allowlists, check dynamic imports, test input validation
- **Performance Testing**: Verify no performance regression from refactoring, test critical paths

**Protocol-Specific Test Coverage:**
- Schema validation for all event types
- Contract testing for protocol surface
- Import path verification (module vs script execution)
- Adapter translation testing (CLI-specific to universal events)
- Backward compatibility testing
- Extensibility testing (ExtensibleEvent schema)
- Security validation (dynamic imports, allowlists)
- Integration testing with hook system

**Parallel Execution**: All testing subagents run simultaneously, each focused on specific testing domain.

### 18. SYNTHESIZE_TEST_RESULTS
Parent agent synthesizes test results:
- Combine results from all testing subagents
- Identify critical failures vs. warnings
- Create unified test report with coverage metrics

### 19. SUMMARIZE_TEST_RESULTS
Present synthesized test outcomes for user verification. Use ask_user_question tool for structured review process. User must review test results.

### 20. EVALUATION_GATE (Iteration Loop)
Automated quality checks on tests:
- **Coverage**: Do tests cover critical paths?
- **Thresholds**: Do tests meet quality thresholds?
- **Regression**: Do tests prevent regressions?
- **Test synthesis**: Are all test results acceptable?

**Iteration Loop**: If evaluation gate fails, loop back to step 17 (PARALLEL_TESTING) with specific feedback. Maximum 3 iterations.

## Review Phase

### 21. COMPREHENSIVE_REVIEW (Managed Devins)
For complex tasks, spawn managed Devins for specialized review:
- **Managed Devin A**: Architecture review - Design patterns, modularity, scalability, layer placement, dependency direction, separation of concerns
- **Managed Devin B**: Security review - Security posture, vulnerability assessment, domain-specific security considerations
- **Managed Devin C**: Compliance review - Regulatory compliance, documentation completeness, industry standard alignment

**Parallel Execution**: Managed Devins work in parallel, coordinator agent synthesizes results.

### 22. SYNTHESIZE_REVIEW
Parent/coordinator agent synthesizes review findings:
- Combine results from all review agents
- Identify critical issues vs. recommendations
- Create unified review report

### 23. SUMMARIZE_REVIEW
Present synthesized review findings for final user approval. Use ask_user_question tool for structured final approval process. User must approve final work.

### 24. PROOF_BUNDLE_GENERATION
Create immutable proof bundle containing:
- **Complete pipeline snapshot**: Versioned configuration, dependency graph
- **All evaluation results**: Every metric score from evaluation gates with iteration history
- **Subagent execution logs**: Parallel execution timeline, resource usage, decision points
- **Approval records**: Who approved, what they reviewed, when, conditions, iteration history
- **Deployment metadata**: Version information, timestamps, environment details
- **Audit trail links**: References to complete audit records with hash verification

Proof bundle enables regulatory compliance and audit reconstruction with full provenance.

## Completion Phase

### 25. AUDIT_TRAIL_UPDATE
Update immutable audit trail with full workflow record:
- All workflow steps with timestamps
- Subagent execution details and results
- Evaluation gate iterations and decisions
- User approvals with evidence reviewed
- Proof bundle hash and verification links

### 26. COMPLETE
Task completion after user approval and proof bundle verification. Only then is the task considered complete.

## Strict Governance Principles

- **Version control**: Every artifact must be version-controlled with metadata
- **Parallel execution with coordination**: Independent tasks run in parallel with proper result synthesis
- **Evaluation gates with iteration loops**: Must pass before state transitions, with limited iterations
- **Evidence-based approval**: Human approval requires evidence review, not acknowledgment
- **Immutable audit trail**: Audit trail is hash-verified and tamper-evident
- **Proof bundles**: Enable regulatory compliance and audit reconstruction with full provenance
- **Risk-based governance**: Risk classification determines required governance rigor
- **Agent-agnostic design**: Overseer Framework state machine supports different workflows
- **Cost-aware parallelism**: Subagent usage is deliberate and justified by parallel benefits
- **Comprehensive logging**: All implementations must include standardized logging to layer-specific JSONL files with consistent format and silent failure handling

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
- **Overseer Framework hooks** for enforcement at critical transition points

## Enforcement Mechanism

The existing Overseer Framework is used to enforce adherence to this workflow through:
- Hook-based interception at critical transition points
- State machine tracking of workflow phase progression with subagent coordination
- Automatic validation of evaluation gate requirements and iteration limits
- Audit trail generation for all workflow steps including subagent execution
- Proof bundle generation and verification with parallel execution provenance
- Cost monitoring and alerting for subagent usage

This creates a self-governing system where the current Overseer enforces the improved workflow for building the next version of Overseer, leveraging modern parallel execution capabilities while maintaining strict compliance.