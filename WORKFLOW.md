# Overseer Framework Development Workflow

This document defines the optimized governance workflow used for all Overseer Framework development tasks to ensure enterprise compliance and auditability. The workflow leverages Devin CLI subagent capabilities for parallel execution and complex orchestration.

## Workflow Architecture

The workflow uses a **hybrid pattern** combining:
- **Parallel execution** using background subagents for independent tasks
- **Sequential core** for dependent phases with clear dependencies
- **Iteration loops** at evaluation gates for quality enforcement
- **DAG structure** for explicit dependency tracking and audit reconstruction

## Critical Requirements

### TDD Compliance (MANDATORY)
**ALL implementations MUST follow Test-Driven Development (TDD) as explicitly required by SOFTWARE_ENGINEERING_PRINCIPLES.md and AGENTS.md:**

**SOFTWARE_ENGINEERING_PRINCIPLES.md - Test Principles (Lines 141-197):**
- "Follow TDD approach: write failing test, implement code, refactor (Red-Green-Refactor)"
- "Write tests **before** writing functional code"
- "Test list approach: plan tests first, then implement one at a time"
- "Build comprehensive automated test suites"
- "Single command execution of all tests"
- "Confidence that passing tests means code is working"

**AGENTS.md - Critical Rules:**
- "Testing-First: Never implement without a test plan. Test in order: implement → test → verify → fix"

**Workflow Compliance:**
- Step 12 (CREATE_TEST_PLAN) is MANDATORY before implementation
- Step 18 (RUN_TESTS) is MANDATORY after implementation
- ALL tests MUST pass before completion
- Implementation CANNOT proceed without test plan approval
- Task CANNOT complete if any test fails

**Violations:**
- Skipping test plan creation = WORKFLOW VIOLATION
- Implementing without tests = WORKFLOW VIOLATION
- Proceeding with failing tests = WORKFLOW VIOLATION
- Completing task without test verification = WORKFLOW VIOLATION

**Workflow Enforcement:**
The workflow now explicitly includes TDD requirements in steps 12, 18, 19, and 20 to prevent workflow deviations.

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
Automated quality checks on plan (aligned with ARCHITECTURE.md principles):
- **Completeness**: Are all required components addressed?
- **Feasibility**: Is the plan technically achievable?
- **Risk alignment**: Does the plan match the risk classification?
- **Dependency validation**: Are dependencies explicit and achievable?
- **Modularity**: Does the plan maintain proper separation of concerns and correct dependency direction? (ARCHITECTURE.md Principle 2)
- **Extensibility**: Does the plan support future growth and plugin architecture? (ARCHITECTURE.md Principle 3)
- **True Agnosticism**: Does the core system make ZERO assumptions about adapters or environment? (ARCHITECTURE.md Principle 1)
  - No hardcoded event types (must be dynamically registered by adapters)
  - No hardcoded naming conventions (must be configurable)
  - No CLI-specific assumptions in documentation or code
  - Adapters should be the ONLY flexible component
  - Core system must adapt to whatever adapters provide
  - Protocol/Overseer layers must be completely environment-independent
- **Security Alignment**: Does the plan follow security principles? (ARCHITECTURE.md Principles 23-27)
  - Input validation and prompt injection defense
  - Defense in depth with layered security
  - Least privilege and zero trust enforcement
  - Reversibility-weighted risk enforcement
  - Subagent isolation and delegation boundaries

**Iteration Loop**: If evaluation gate fails, loop back to step 9 (PLAN) with specific feedback. Maximum 3 iterations to prevent runaway loops.

### 11. VERIFY_PLAN
Present implementation plan for user approval with evaluation results. Use ask_user_question tool for structured approval process. User must approve before implementation.

## Implementation Phase

### 12. CREATE_TEST_PLAN (CRITICAL - TDD Compliance)
**MANDATORY**: Create comprehensive test plan BEFORE implementation following SOFTWARE_ENGINEERING_PRINCIPLES.md Test Principles:
- Write failing tests first (Red-Green-Refactor TDD approach)
- Plan unit tests for each component in isolation
- Plan integration tests for end-to-end functionality
- Plan security tests for input validation, secret redaction, configuration tampering
- Plan performance tests for latency targets
- Test strategy must be documented and approved before implementation

**TDD Requirement**: SOFTWARE_ENGINEERING_PRINCIPLES.md explicitly states:
- "Follow TDD approach: write failing test, implement code, refactor"
- "Write tests before writing functional code"
- "Test list approach: plan tests first, then implement one at a time"
- AGENTS.md Critical Rule: "Testing-First: Never implement without a test plan. Test in order: implement → test → verify → fix"

**Exit Condition**: Test plan created and approved by user. Implementation CANNOT proceed without test plan approval.

### 13. IMPLEMENT
Execute implementation based on approved plan with version control. All changes must be tracked.
For implementations requiring refactoring of existing code:
- Update dependency imports and cross-file references
- Maintain backward compatibility during migration
- Document refactoring changes in commit messages
- Test refactored code paths before proceeding

**TDD Compliance**: Implementation must follow test plan created in step 12. Code should make tests pass (Green phase of TDD).

### 14. PARALLEL_VALIDATION (Background Subagents)
Spawn parallel validation subagents:
- **Subagent A**: Code quality validation - Standards compliance, formatting, best practices, architectural consistency
- **Subagent B**: Compliance validation - Governance rules, boundary adherence, security requirements, implementation-specific compliance
- **Subagent C**: Dependency validation - Import correctness, package compatibility, version conflicts, cross-component dependency verification

**Parallel Execution**: All validation subagents run simultaneously, each focused on specific validation domain.

### 15. SYNTHESIZE_VALIDATION
Parent agent synthesizes validation results:
- Combine findings from all validation subagents
- Identify critical issues vs. warnings
- Create unified validation report

### 16. SUMMARIZE_IMPLEMENTATION
Present implementation changes and validation synthesis for user verification. Use ask_user_question tool for structured review and approval process. User must review and approve changes.

### 17. EVALUATION_GATE (Iteration Loop)
Automated quality checks on implementation (aligned with ARCHITECTURE.md and IMPLEMENTATION.md):
- **Code quality**: Does code meet standards? (SOFTWARE_ENGINEERING_PRINCIPLES.md)
- **Compliance**: Are governance rules followed? (ARCHITECTURE.md Principle 4)
- **Security**: Are security requirements met? (ARCHITECTURE.md Principles 23-27)
- **Validation synthesis**: Are all validation results acceptable?
- **Modularity**: Does implementation maintain proper separation of concerns and correct dependency direction? (ARCHITECTURE.md Principle 2)
- **Consistency**: Does implementation follow established code patterns and naming conventions? (IMPLEMENTATION.md)
- **True Agnosticism**: Does implementation make ZERO assumptions about adapters or environment? (ARCHITECTURE.md Principle 1)
  - No hardcoded event types or registry (must be dynamic)
  - No hardcoded naming conventions (must be configurable)
  - No CLI-specific references in code or documentation
  - Core layers must work with ANY adapter structure
- **Zero Dependencies**: Does core maintain zero external dependencies? (IMPLEMENTATION.md - JSON instead of pyyaml)
- **Performance**: Does implementation avoid anti-patterns like synchronous file I/O? (IMPLEMENTATION.md - policy caching)

**Iteration Loop**: If evaluation gate fails, loop back to step 13 (IMPLEMENT) with specific feedback. Maximum 3 iterations.

## Testing Phase

### 18. RUN_TESTS (CRITICAL - TDD Compliance)
**MANDATORY**: Run all tests created in step 12. All tests MUST pass before implementation is considered complete.

**Test Execution Requirements**:
- Run unit tests: `python -m unittest discover -s Overseer/Tests -p "test_*.py" -v`
- Run integration tests: Execute integration test suite
- Run security tests: Execute security test suite
- Run performance tests: Execute performance test suite
- Verify test coverage: All critical paths must be covered

**TDD Requirement**: SOFTWARE_ENGINEERING_PRINCIPLES.md explicitly states:
- "Build comprehensive automated test suites"
- "Single command execution of all tests"
- "Confidence that passing tests means code is working"
- AGENTS.md Critical Rule: "Test in order: implement → test → verify → fix"

**Exit Condition**: ALL tests pass. Implementation CANNOT proceed to completion if any test fails.

### 19. FIX_TEST_FAILURES (Iteration Loop)
If any tests fail:
- Analyze test failure root cause
- Fix implementation to make tests pass
- Re-run tests to verify fix
- Maximum 3 iterations per test failure to prevent runaway loops

**Iteration Loop**: If tests fail after 3 iterations, escalate to user for guidance.

### 20. VERIFY_COMPLIANCE
Verify implementation compliance with all architectural principles and project requirements:
- Cross-reference implementation against ARCHITECTURE.md principles
- Verify compliance with IMPLEMENTATION.md patterns
- Verify compliance with SOFTWARE_ENGINEERING_PRINCIPLES.md
- Verify compliance with ORGANIZATIONAL_GUIDE.md (if applicable)
- Document compliance status

**Exit Condition**: All compliance requirements verified and documented.

### 21. PARALLEL_TESTING (Background Subagents - Optional Enhancement)
For comprehensive validation, spawn parallel testing subagents:
- **Subagent A**: Unit testing - Individual component testing, conformance testing (type validation, schema validation, interface validation)
- **Subagent B**: Integration testing - Component interaction testing, dependency testing (import verification, compatibility testing)
- **Subagent C**: Security testing - Vulnerability scanning, penetration testing, domain-specific security testing
- **Subagent D**: Performance testing - Load testing, response time validation, regression testing for refactored code

**Note**: This step is optional enhancement. Step 18 (RUN_TESTS) is MANDATORY and must pass before completion.

**Testing Best Practices:**
- **Layered Testing Strategy**: Unit tests → Contract tests → Integration tests → End-to-end tests
- **Test Pyramid Pattern**: Many fast unit tests, some integration tests, few end-to-end tests
- **Arrange-Act-Assert Structure**: Set up test data, call method under test, assert expected results
- **Security Testing**: Validate allowlists, check input validation, test secret redaction
- **Performance Testing**: Verify latency targets (< 100ms for hooks, < 500ms for policy evaluation)

**Parallel Execution**: All testing subagents run simultaneously, each focused on specific testing domain.

### 22. SYNTHESIZE_TEST_RESULTS (Optional Enhancement)
Parent agent synthesizes test results from parallel testing subagents:
- Combine results from all testing subagents
- Identify critical failures vs. warnings
- Create unified test report with coverage metrics

**Note**: This step is optional. Step 18 (RUN_TESTS) provides baseline testing coverage.

### 23. SUMMARIZE_TEST_RESULTS (Optional Enhancement)
Present synthesized test outcomes for user verification. Use ask_user_question tool for structured review process. User must review test results.

**Note**: This step is optional. Step 18 (RUN_TESTS) provides baseline test reporting.

### 24. EVALUATION_GATE (Iteration Loop - Optional Enhancement)
Automated quality checks on tests from parallel testing:
- **Coverage**: Do tests cover critical paths?
- **Thresholds**: Do tests meet quality thresholds?
- **Regression**: Do tests prevent regressions?
- **Test synthesis**: Are all test results acceptable?

**Iteration Loop**: If evaluation gate fails, loop back to step 21 (PARALLEL_TESTING) with specific feedback. Maximum 3 iterations.

**Note**: This step is optional. Step 18 (RUN_TESTS) provides mandatory test execution.

## Review Phase

### 25. COMPREHENSIVE_REVIEW (Managed Devins - Optional)
For complex tasks, spawn managed Devins for specialized review:
- **Managed Devin A**: Architecture review - Design patterns, modularity, scalability, layer placement, dependency direction, separation of concerns
- **Managed Devin B**: Security review - Security posture, vulnerability assessment, domain-specific security considerations
- **Managed Devin C**: Compliance review - Regulatory compliance, documentation completeness, industry standard alignment

**Parallel Execution**: Managed Devins work in parallel, coordinator agent synthesizes results.

**Note**: This step is optional for standard implementations.

### 26. SYNTHESIZE_REVIEW (Optional)
Parent/coordinator agent synthesizes review findings:
- Combine results from all review agents
- Identify critical issues vs. recommendations
- Create unified review report

**Note**: This step is optional for standard implementations.

### 27. SUMMARIZE_REVIEW (Optional)
Present synthesized review findings for final user approval. Use ask_user_question tool for structured final approval process. User must approve final work.

**Note**: This step is optional for standard implementations.

### 28. PROOF_BUNDLE_GENERATION (Optional)
Create immutable proof bundle containing:
- **Complete pipeline snapshot**: Versioned configuration, dependency graph
- **All evaluation results**: Every metric score from evaluation gates with iteration history
- **Subagent execution logs**: Parallel execution timeline, resource usage, decision points
- **Approval records**: Who approved, what they reviewed, when, conditions, iteration history
- **Deployment metadata**: Version information, timestamps, environment details
- **Audit trail links**: References to complete audit records with hash verification

Proof bundle enables regulatory compliance and audit reconstruction with full provenance.

**Note**: This step is optional for standard implementations.

## Completion Phase

### 29. AUDIT_TRAIL_UPDATE
Update immutable audit trail with full workflow record:
- All workflow steps with timestamps
- Subagent execution details and results
- Evaluation gate iterations and decisions
- User approvals with evidence reviewed
- Proof bundle hash and verification links

### 30. COMPLETE
Task completion after user approval and test verification. Only then is the task considered complete.

**Completion Requirements**:
- All tests pass (Step 18 - MANDATORY)
- Implementation verified (Step 20 - MANDATORY)
- Code committed to version control
- Documentation updated if needed

## Strict Governance Principles

- **Version control**: Every artifact must be version-controlled with metadata (ARCHITECTURE.md Principle 4)
- **Parallel execution with coordination**: Independent tasks run in parallel with proper result synthesis (SUBAGENT_ORCHESTRATION.md)
- **Evaluation gates with iteration loops**: Must pass before state transitions, with limited iterations (ARCHITECTURE.md Principle 5)
- **Evidence-based approval**: Human approval requires evidence review, not acknowledgment (ARCHITECTURE.md Principle 18)
- **Immutable audit trail**: Audit trail is hash-verified and tamper-evident (ARCHITECTURE.md Principle 9)
- **Proof bundles**: Enable regulatory compliance and audit reconstruction with full provenance
- **Risk-based governance**: Risk classification determines required governance rigor (ARCHITECTURE.md Principle 26)
- **Agent-agnostic design**: Overseer Framework state machine supports different workflows (ARCHITECTURE.md Principle 1)
- **Cost-aware parallelism**: Subagent usage is deliberate and justified by parallel benefits (SUBAGENT_ORCHESTRATION.md)
- **Comprehensive logging**: All implementations must include standardized logging to layer-specific JSONL files with consistent format and silent failure handling (ARCHITECTURE.md Principle 9)
- **Security-first development**: All implementations follow security principles (ARCHITECTURE.md Principles 23-27)
- **Zero external dependencies**: Core framework maintains zero external dependencies (IMPLEMENTATION.md)

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