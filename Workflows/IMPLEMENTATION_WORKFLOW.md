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
- Implementation Phase Step 12 (CREATE_TEST_PLAN) is MANDATORY before implementation
- Implementation Phase Step 18 (RUN_TESTS) is MANDATORY after implementation
- ALL tests MUST pass before completion
- Implementation CANNOT proceed without test plan approval
- Task CANNOT complete if any test fails

**Violations:**
- Skipping test plan creation = WORKFLOW VIOLATION
- Implementing without tests = WORKFLOW VIOLATION
- Proceeding with failing tests = WORKFLOW VIOLATION
- Completing task without test verification = WORKFLOW VIOLATION

**Workflow Enforcement:**
The workflow explicitly includes TDD requirements in steps 12, 18, 19, and 20 to prevent workflow deviations.

---

## Implementation Workflow

### Phase 1: Pre-Planning

#### 1. USER_PROMPT
Starting point from user request. All development tasks begin with a clear user prompt defining the requirements.

#### 2. RESEARCH_BEST_PRACTICES
Research industry best practices, architectural patterns, and implementation approaches relevant to the implementation type.

**Research Scope:**
- Domain-specific architectural patterns and design principles
- Industry standards and conventions for the implementation type
- Security and performance considerations
- Modularity and maintainability best practices
- File structure and organization patterns

#### 3. CLARIFY_INTENT
Ensure complete understanding of requirements before proceeding. Use ask_user_question tool for structured clarification.

**Exit Condition**: User explicitly confirms all requirements are clear and understood.

#### 4. PARALLEL_INITIALIZATION (Background Subagents)
Spawn parallel initialization subagents for independent research tasks:
- **Subagent A**: Technical research - best practices, patterns, implementation approaches
- **Subagent B**: Compliance research - regulatory requirements, security standards
- **Subagent C**: Risk assessment - potential risks, mitigation strategies

**Parallel Execution**: All initialization subagents run simultaneously.

#### 5. SYNTHESIZE_INITIALIZATION
Parent agent synthesizes initialization results:
- Combine findings from all initialization subagents
- Identify common themes and conflicting findings
- Create unified initialization report

#### 6. RISK_CLASSIFICATION
Classify implementation risk based on synthesized research:
- **Low**: Low complexity, well-understood patterns, minimal compliance impact
- **Medium**: Moderate complexity, some compliance considerations
- **High**: High complexity, significant compliance requirements, security-sensitive

**Exit Condition**: Risk classification determined and documented.

#### 7. GOVERNANCE_BOUNDARIES
Define governance boundaries for the implementation:
- What data can be accessed/modified
- What operations are allowed/blocked
- What verification steps are required
- What approval processes are needed

**Exit Condition**: Governance boundaries defined and approved by user.

#### 8. SYNTHESIZE_PLAN
Present synthesized initialization, risk classification, and governance boundaries for user approval.

**Exit Condition**: User approves plan to proceed.

---

### Phase 2: Planning

#### 9. PARALLEL_RESEARCH (Background Subagents)
Spawn parallel research subagents for detailed investigation:
- **Subagent A**: Technical research - specific patterns, libraries, implementation details
- **Subagent B**: Compliance research - specific regulations, standards, requirements
- **Subagent C**: Security research - specific threats, vulnerabilities, mitigations

**Parallel Execution**: All research subagents run simultaneously.

#### 10. CROSS_REFERENCE_FINDINGS
Cross-reference research findings against repository documents:
- ARCHITECTURE.md principles
- IMPLEMENTATION.md patterns
- ORGANIZATIONAL_GUIDE.md compliance requirements
- SOFTWARE_ENGINEERING_PRINCIPLES.md engineering standards

**Exit Condition**: Findings cross-referenced and documented.

#### 11. SYNTHESIZE_RESEARCH
Present synthesized research findings for user approval.

**Exit Condition**: User approves research to proceed.

#### 12. CREATE_IMPLEMENTATION_PLAN (CRITICAL - TDD Compliance)
**MANDATORY**: Create comprehensive test plan BEFORE implementation following SOFTWARE_ENGINEERING_PRINCIPLES.md Test Principles:
- Write failing tests first (Red-Green-Refactor TDD approach)
- Plan unit tests for each component in isolation
- Plan integration tests for end-to-end functionality
- Plan security tests for input validation, secret redaction, configuration tampering
- Plan performance tests for latency targets

**TDD Requirement**: SOFTWARE_ENGINEERING_PRINCIPLES.md explicitly states:
- "Follow TDD approach: write failing test, implement code, refactor"
- "Write tests **before** writing functional code"
- "Test list approach: plan tests first, then implement one at a time"
- AGENTS.md Critical Rule: "Testing-First: Never implement without a test plan. Test in order: implement → test → verify → fix"

**Exit Condition**: Test plan created and approved by user. Implementation CANNOT proceed without test plan approval.

#### 13. VERIFY_PLAN
Present implementation plan for user approval with evaluation results. Use ask_user_question tool for structured approval process. User must approve before implementation.

---

### Phase 3: Implementation

#### 14. IMPLEMENT
Execute implementation based on approved plan with version control.

**Implementation Requirements**:
- Follow SOFTWARE_ENGINEERING_PRINCIPLES.md
- Maintain zero external dependencies for core
- Update dependency imports and cross-file references
- Add comprehensive logging to layer-specific JSONL files
- Document changes in commit messages

#### 15. PARALLEL_VALIDATION (Background Subagents)
Spawn parallel validation subagents:
- **Subagent A**: Code quality validation - Standards compliance, formatting, best practices
- **Subagent B**: Compliance validation - Governance rules, boundary adherence, security requirements
- **Subagent C**: Dependency validation - Import correctness, package compatibility, version conflicts

**Parallel Execution**: All validation subagents run simultaneously.

#### 16. SYNTHESIZE_VALIDATION
Parent agent synthesizes validation results:
- Combine findings from all validation subagents
- Identify critical issues vs. warnings
- Create unified validation report

#### 17. SUMMARIZE_IMPLEMENTATION
Present implementation changes and validation synthesis for user verification. Use ask_user_question tool for structured review and approval process. User must review and approve changes.

#### 18. EVALUATION_GATE (Iteration Loop)
Automated quality checks on implementation (aligned with ARCHITECTURE.md and IMPLEMENTATION.md):
- **Code quality**: Does code meet standards? (SOFTWARE_ENGINEERING_PRINCIPLES.md)
- **Compliance**: Are governance rules followed? (ARCHITECTURE.md Principle 4)
- **Security**: Are security requirements met? (ARCHITECTURE.md Principles 23-27)
- **Validation synthesis**: Are all validation results acceptable?
- **Modularity**: Does implementation maintain proper separation of concerns and correct dependency direction? (ARCHITECTURE.md Principle 2)
- **Consistency**: Does implementation follow established code patterns and naming conventions? (IMPLEMENTATION.md)
- **True Agnosticism**: Does implementation make ZERO assumptions about adapters or environment? (ARCHITECTURE.md Principle 1)
- **Zero Dependencies**: Does core maintain zero external dependencies? (IMPLEMENTATION.md)
- **Performance**: Does implementation avoid anti-patterns?

**Iteration Loop**: If evaluation gate fails, loop back to step 14 (IMPLEMENT) with specific feedback. Maximum 3 iterations.

---

### Phase 4: Testing

#### 19. RUN_TESTS (CRITICAL - TDD Compliance)
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

#### 20. FIX_TEST_FAILURES (Iteration Loop)
If any tests fail:
- Analyze test failure root cause
- Fix implementation to make tests pass
- Re-run tests to verify fix
- Maximum 3 iterations per test failure

**Iteration Loop**: If tests fail after 3 iterations, escalate to user for guidance.

#### 21. VERIFY_COMPLIANCE
Verify implementation compliance with all architectural principles and project requirements:
- Cross-reference implementation against ARCHITECTURE.md principles
- Verify compliance with IMPLEMENTATION.md patterns
- Verify compliance with SOFTWARE_ENGINEERING_PRINCIPLES.md
- Verify compliance with ORGANIZATIONAL_GUIDE.md (if applicable)
- Document compliance status

**Exit Condition**: All compliance requirements verified and documented.

#### 22. PARALLEL_TESTING (Background Subagents - Optional Enhancement)
For comprehensive validation, spawn parallel testing subagents:
- **Subagent A**: Unit testing - Individual component testing, conformance testing
- **Subagent B**: Integration testing - Component interaction testing, dependency testing
- **Subagent C**: Security testing - Vulnerability scanning, penetration testing
- **Subagent D**: Performance testing - Load testing, response time validation

**Note**: This step is optional enhancement. Step 19 (RUN_TESTS) is MANDATORY and must pass before completion.

---

### Phase 5: Review

#### 23. COMPREHENSIVE_REVIEW (Managed Devins - Optional)
For complex tasks, spawn managed Devins for specialized review:
- **Managed Devin A**: Architecture review - Design patterns, modularity, scalability
- **Managed Devin B**: Security review - Security posture, vulnerability assessment
- **Managed Devin C**: Compliance review - Regulatory compliance, documentation completeness

**Note**: This step is optional for standard implementations.

#### 24. SYNTHESIZE_REVIEW (Optional)
Parent/coordinator agent synthesizes review findings:
- Combine results from all review agents
- Identify critical issues vs. recommendations
- Create unified review report

#### 25. SUMMARIZE_REVIEW (Optional)
Present synthesized review findings for final user approval.

**Note**: This step is optional for standard implementations.

---

### Phase 6: Completion

#### 26. AUDIT_TRAIL_UPDATE
Update immutable audit trail with full workflow record:
- All workflow steps with timestamps
- Subagent execution details and results
- Evaluation gate iterations and decisions
- User approvals with evidence reviewed
- Proof bundle hash and verification links

#### 27. COMPLETE
Task completion after user approval and test verification.

**Completion Requirements**:
- All tests pass (Step 19 - MANDATORY)
- Implementation verified (Step 21 - MANDATORY)
- Code committed to version control
- Documentation updated if needed

---

## Strict Governance Principles

- **Version control**: Every artifact must be version-controlled with metadata (ARCHITECTURE.md Principle 4)
- **Parallel execution with coordination**: Independent tasks run in parallel with proper result synthesis (SUBAGENT_ORCHESTRATION.md)
- **Evaluation gates with iteration loops**: Must pass before state transitions, with limited iterations (ARCHITECTURE.md Principle 5)
- **Evidence-based approval**: Human approval requires evidence review, not acknowledgment (ARCHITECTURE.md Principle 18)
- **Immutable audit trail**: Audit trail is hash-verified and tamper-evident (ARCHITECTURE.md Principle 9)

---

## For Fix Workflow: Issue Resolution

Use **Workflows/FIX_WORKFLOW.md** for systematic resolution of external review findings, security issues, and quality improvements:
- Research each issue independently
- User decision before implementation
- Fix → Test → Verify cycle
- Full test suite before commit
- Push only after all tests pass
