# Validation Checklists for Governor Framework

**Version**: 1.0.0
**Date**: 2026-08-12
**Purpose**: Comprehensive validation checklists for architecture, security, compliance, code quality, test coverage, documentation, configuration, and policy reviews aligned with industry standards and Governor Framework requirements.

## 1. Architecture Validation Checklist

### Document Control
- [ ] Version and change history show active maintenance
- [ ] Authors and contributors are named
- [ ] Classification is set and appropriate to content
- [ ] Document index in AGENTS.md is current

### Executive Summary
- [ ] Solution overview is understandable to non-technical readers
- [ ] Business drivers are specific (what, when, consequence of inaction)
- [ ] Strategic alignment is credible - not boilerplate
- [ ] Scope boundaries are clear (in / out / related)
- [ ] Criticality tier is justified, not defaulted

### Stakeholders & Concerns
- [ ] Business owner is named
- [ ] Security considerations are listed
- [ ] Operational requirements are documented
- [ ] Regulatory context is declared (ISO 42001, NIST AI RMF, EU AI Act, GDPR)

### Architectural Principles
- [ ] True Agnosticism (Principle 1): Zero CLI-specific assumptions in core
- [ ] Modular Architecture (Principle 2): Layer independence with minimal coupling
- [ ] Small Reusable Kernel (Principle 3): Core contains only essential governance logic
- [ ] Rule-Based Governance (Principle 4): Declarative policies with versioning
- [ ] In-Path Fail-Closed Enforcement (Principle 5): Hooks block before execution
- [ ] Deterministic Discrete Verdicts (Principle 6): Allow/deny/modify outcomes
- [ ] Stateless and Idempotent Enforcement (Principle 7): Independent hook decisions
- [ ] Standardized Hook Payloads (Principle 8): Canonical data models
- [ ] Audit Trail and Observability (Principle 9): Tamper-evident logging
- [ ] Emergency Controls (Principle 10): Kill switch and circuit breaker
- [ ] Zero External Dependencies (Principle 11): Core uses only Python stdlib
- [ ] Universal Adapter Interface (Principle 12): Well-defined adapter SDK
- [ ] Capability-Based Orchestration (Principle 13): Framework adapts to adapter capabilities
- [ ] Data Minimization (Principle 14): Only collect necessary data
- [ ] Emergency State Management (Principle 15): Emergency halt with file-system persistence
- [ ] Human-in-the-Loop Escalation (Principle 16): Approval gates for high-risk actions
- [ ] Policy Conflict Resolution (Principle 17): Compose multiple policy decisions
- [ ] Governance Decision Explainability (Principle 18): Rationale for all decisions
- [ ] Configuration Integrity (Principle 19): Tamper-evident configuration with hot-reload
- [ ] Audit Trail Integrity (Principle 20): Hash-verified tamper-evident logging

### Component Decomposition
- [ ] Components are decomposed meaningfully (not just "backend" and "frontend")
- [ ] Each component has a named owner
- [ ] Technology choices are specific (name + version where relevant)
- [ ] Design patterns have rationale
- [ ] Layer boundaries are explicit (Adapter, Protocol, Engine, State Machine, Hook Handler)

### Integration & Data Flow
- [ ] Every internal interface is documented (protocol, auth, direction, encryption)
- [ ] Every external integration is documented
- [ ] Synchronous vs asynchronous patterns are specified
- [ ] Error handling at boundaries is defined
- [ ] Data flow diagram matches implementation

---

## 2. Security Validation Checklist

### Input Validation (ARCHITECTURE.md Principle 23)
- [ ] All external inputs are validated before processing
- [ ] Strict allow-lists used instead of block-lists
- [ ] Prompt injection defenses implemented
- [ ] Structural separation between control and data
- [ ] No eval() or dynamic code execution from untrusted sources

### Authentication & Authorization
- [ ] Principle of Least Privilege enforced (Principle 25)
- [ ] Zero Trust model: verify explicitly, assume breach
- [ ] Subagent isolation with scoped delegation tokens (Principle 27)
- [ ] No automatic permission inheritance
- [ ] Access controls are at appropriate granularity

### Cryptographic Implementation
- [ ] Secrets are never logged or exposed (Principle 21)
- [ ] Secret detection patterns are appropriate (not overly broad)
- [ ] Configuration integrity verification implemented (Principle 20)
- [ ] Hash chaining for tamper-evident audit trails (Principle 9)
- [ ] Cryptographic operations use approved algorithms

### Defense in Depth (Principle 24)
- [ ] Multiple overlapping security layers implemented
- [ ] Fail-closed enforcement throughout (Principle 5)
- [ ] Emergency controls for incident response (Principle 15)
- [ ] Kill switch functionality verified
- [ ] No single point of failure in security controls

### Reversibility-Weighted Risk (Principle 26)
- [ ] Lighter oversight for reversible actions
- [ ] Mandatory gates for irreversible actions
- [ ] Risk classification is documented and enforced
- [ ] Human-in-the-loop for high-risk operations

### Error Handling
- [ ] Errors fail-closed without bypass menus
- [ ] Error messages don't expose sensitive information
- [ ] Comprehensive error logging for security events
- [ ] Error recovery procedures documented

### Configuration Security
- [ ] Configuration files have integrity verification
- [ ] No hardcoded credentials or secrets
- [ ] Configuration changes are audited
- [ ] Default configurations are secure

### Audit Trail Security (Principle 9)
- [ ] Tamper-evident audit logging with hash chains
- [ ] Immutable audit trail with hash verification
- [ ] Log retention meets regulatory requirements (90 days for production)
- [ ] Log access is controlled and audited

---

## 3. Compliance Validation Checklist

### ISO 42001 Alignment
- [ ] Clause 4: Context of the Organization
  - [ ] Governance scope defined (agents, tools, environments)
  - [ ] Stakeholder identification documented
  - [ ] AI role defined in value chain
  - [ ] Regulatory requirements mapped (GDPR, EU AI Act, sector-specific)

- [ ] Clause 5: Leadership
  - [ ] Executive sponsorship secured
  - [ ] Resource allocation documented
  - [ ] AI governance board established
  - [ ] AI policy developed and communicated
  - [ ] Roles and responsibilities defined (Governance Lead, Policy Author, Auditor)

- [ ] Clause 6: Planning
  - [ ] Risk assessment process defined
  - [ ] AI system impact assessment process
  - [ ] Risk documentation (likelihood, severity, impact)
  - [ ] Mitigation strategies mapped to Overseer policies

- [ ] Clause 7: Support
  - [ ] Training programs developed
  - [ ] Competence evaluation process
  - [ ] Awareness programs established
  - [ ] Document control procedures

- [ ] Clause 8: Operation
  - [ ] Operational controls documented
  - [ ] Control verification process
  - [ ] Lifecycle controls (development, deployment, operation, monitoring, retirement)

- [ ] Clause 9: Performance Evaluation
  - [ ] Metrics collection (policy violation rate, approval time, governance coverage)
  - [ ] Internal audit schedule
  - [ ] Management review process

- [ ] Clause 10: Improvement
  - [ ] Nonconformity detection process
  - [ ] Root cause analysis methodology
  - [ ] Corrective action timeline
  - [ ] Continual improvement process

### NIST AI RMF Alignment
- [ ] Govern Function
  - [ ] Policies, processes, procedures in place
  - [ ] Legal and regulatory requirements documented
  - [ ] Trustworthy AI characteristics integrated
  - [ ] Risk management culture established

- [ ] Map Function
  - [ ] Context and use cases documented
  - [ ] Risk categories identified
  - [ ] TEVV (Test, Evaluation, Verification, Validation) considerations documented

- [ ] Measure Function
  - [ ] Metrics defined and tracked
  - [ ] Testing and validation processes
  - [ ] Benchmarking implemented
  - [ ] Monitoring and analysis

- [ ] Manage Function
  - [ ] Response procedures
  - [ ] Recovery procedures
  - [ ] Communication procedures
  - [ ] Documentation and knowledge management

### EU AI Act Alignment
- [ ] Article 10: Transparency
  - [ ] Decision explainability implemented (Principle 22)
  - [ ] Policies tagged with EU AI Act references
  - [ ] User-facing transparency information

- [ ] Article 11: Human Oversight
  - [ ] Human-in-the-loop escalation gates (Principle 18)
  - [ ] Human approval for high-risk actions
  - [ ] Override capability documentation

- [ ] Log Retention
  - [ ] 6-month minimum log retention
  - [ ] Production: 90-day retention
  - [ ] Staging: 30-day retention
  - [ ] Development: 7-day retention

### GDPR Alignment
- [ ] Article 25: Data Protection by Design
  - [ ] Data minimization (Principle 14)
  - [ ] Secrets protection (Principle 21)
  - [ ] Retention periods configured
  - [ ] Data masking implemented

- [ ] Article 32: Security of Processing
  - [ ] Configuration integrity (Principle 20)
  - [ ] Tamper-evident audit (Principle 9)
  - [ ] Access controls
  - [ ] Regular security testing

---

## 4. Code Quality Validation Checklist

### Layer 1: Mechanical (Automated)
- [ ] Code formatted correctly (PEP 8 for Python)
- [ ] Unnecessary whitespace removed
- [ ] Linting passes (flake8, pylint, etc.)
- [ ] Type hints used where appropriate
- [ ] Unit tests pass
- [ ] Invalid inputs validated
- [ ] Inputs sanitized

### Layer 2: Structural (Requires Understanding)
#### Architecture & Design
- [ ] Follows ARCHITECTURE.md principles
- [ ] Maintains layer independence (Principle 2)
- [ ] True agnosticism maintained (Principle 1)
- [ ] Zero external dependencies in core
- [ ] Separation of concerns followed
- [ ] Single Responsibility Principle (SOLID)
- [ ] Open/Closed Principle (extensible without modification)
- [ ] Dependency Inversion Principle (depend on abstractions)

#### Security
- [ ] Follows security principles (Principles 23-27)
- [ ] Input validation comprehensive
- [ ] No hardcoded secrets
- [ ] Error handling doesn't expose sensitive information
- [ ] Least privilege enforced

#### Error Handling & Logging
- [ ] Comprehensive logging to layer-specific JSONL files
- [ ] Structured log format: {"File": "filename", "component": "component_name", "Time": "timestamp", "data": {...}}
- [ ] Errors are logged with context
- [ ] Silent failure for logging errors
- [ ] Different errors handled correctly
- [ ] Magic values avoided

#### Testing
- [ ] Edge cases tested
- [ ] Security tests implemented
- [ ] Performance tests implemented
- [ ] Integration tests implemented
- [ ] Test coverage adequate

#### Performance
- [ ] Code performance acceptable
- [ ] No obvious performance anti-patterns
- [ ] Caching used where appropriate
- [ ] Expensive operations optimized

#### Readability
- [ ] Code is easy to read
- [ ] DRY principle followed (no repetition)
- [ ] Method/class not too long
- [ ] Naming is descriptive
- [ ] Minimal nesting used
- [ ] Comments for "why" and complex "how", not obvious code

### Layer 3: Narrative (Context)
#### Requirements & Context
- [ ] Requirements met
- [ ] Stakeholder approval obtained
- [ ] Business value clear

#### Documentation & Reasoning
- [ ] Sufficient documentation
- [ ] README.md up to date
- [ ] Implementation rationale documented
- [ ] Architectural decisions recorded (ADRs if applicable)

#### Implementation Standards (SOFTWARE_ENGINEERING_PRINCIPLES.md)
- [ ] Component modularity maintained
- [ ] Standardization across files
- [ ] KISS principle followed
- [ ] YAGNI compliance (no premature generalization)
- [ ] Test principles followed (TDD, test pyramid, isolation)

---

## 5. AI Agent Governance Validation Checklist

### Identity & Provenance (OASB-1)
- [ ] Agent identity is verified and authenticated
- [ ] Agent provenance is tracked (origin, version, author)
- [ ] Agent capabilities are declared and bounded
- [ ] Agent behavior is predictable within bounds
- [ ] Agent-to-agent identity verification

### Capability & Authorization (OASB-1)
- [ ] Agent capabilities are explicitly declared
- [ ] Authorization scopes are defined per agent
- [ ] Tool access is controlled per policy
- [ ] Agent cannot exceed authorized capabilities
- [ ] Delegation tokens are scoped and time-limited (Principle 27)

### Input Security (OASB-1)
- [ ] All agent inputs are validated (Principle 23)
- [ ] Prompt injection defenses implemented
- [ ] Input sanitization for agent commands
- [ ] Input size limits enforced
- [ ] Malicious input detection

### Output Security (OASB-1)
- [ ] Agent outputs are filtered/redacted
- [ ] Sensitive data not exposed in outputs
- [ ] Output size limits enforced
- [ ] Output integrity verification
- [ ] Unsafe output detection

### Credential Protection (OASB-1)
- [ ] Secrets never passed to agents (Principle 21)
- [ ] Credential vault for agent access
- [ ] Credential rotation process
- [ ] No hardcoded credentials in agent code
- [ ] Credential usage audited

### Supply Chain Integrity (OASB-1)
- [ ] Agent dependencies are vetted
- [ ] Agent code is signed/verified
- [ ] Agent updates are controlled
- [ ] Third-party agent risk assessment
- [ ] Agent version control

### Agent-to-Agent Security (OASB-1)
- [ ] Agent communication is authenticated
- [ ] Agent communication is authorized
- [ ] Agent-to-agent delegation is scoped
- [ ] No automatic permission inheritance (Principle 27)
- [ ] Agent interaction audit trail

### Memory & Context Integrity (OASB-1)
- [ ] Agent memory is bounded
- [ ] Context injection protection
- [ ] Context isolation between agents
- [ ] Memory retention policies
- [ ] Context sanitization

### Operational Security (OASB-1)
- [ ] Agent deployment is controlled
- [ ] Agent execution is monitored
- [ ] Agent termination procedures
- [ ] Agent resource limits
- [ ] Agent operational logs

### Monitoring & Response (OASB-1)
- [ ] Agent behavior monitoring
- [ ] Anomaly detection for agent actions
- [ ] Agent incident response procedures
- [ ] Agent performance metrics
- [ ] Agent audit trail (Principle 9)

### Human Oversight (Singapore MGF)
- [ ] Human-in-the-loop for high-risk actions (Principle 18)
- [ ] Human override capability
- [ ] Human approval workflows
- [ ] Human-AI configuration documentation
- [ ] Balance between oversight and scale

### Accountability (Singapore MGF)
- [ ] Agent actions are attributable
- [ ] Agent decision logging
- [ ] Agent responsibility assignment
- [ ] Agent liability framework
- [ ] Agent governance board oversight

---

## 6. Cross-Document Validation Checklist

### Document Hierarchy
- [ ] Authority order defined (AGENTS.md > ARCHITECTURE.md > IMPLEMENTATION.md > SOFTWARE_ENGINEERING_PRINCIPLES.md > ORGANIZATIONAL_GUIDE.md > WORKFLOW documents)
- [ ] All cross-references resolve correctly
- [ ] No broken links between documents
- [ ] Principle numbers match across documents
- [ ] File paths in references are correct
- [ ] Section references are accurate

### Identity Drift
- [ ] Terminology is consistent across documents
- [ ] Component names match (Adapter, Protocol, Engine, etc.)
- [ ] Principle names match
- [ ] File structure references match
- [ ] No synonym confusion

### Quantifier Consistency
- [ ] Numbers match across documents (27 principles, 44 tests, etc.)
- [ ] Versions match (v4.0.0, v1.0.0, etc.)
- [ ] Dates match
- [ ] Counts match (layers, modules, etc.)
- [ ] Percentages match

### Causal Ordering
- [ ] Workflow steps are in logical order
- [ ] Dependencies are correctly ordered
- [ ] Prerequisites are listed before dependents
- [ ] No circular dependencies
- [ ] Temporal sequences make sense

### I/O Coherence
- [ ] Input specifications match across documents
- [ ] Output specifications match across documents
- [ ] Data structures match
- [ ] API contracts match
- [ ] Interfaces match

### Completeness
- [ ] All principles in ARCHITECTURE.md are referenced elsewhere
- [ ] All workflow steps are documented
- [ ] All file structures are documented
- [ ] All roles are defined
- [ ] No orphans (mentioned in one doc, not defined)

### Contradiction Detection
- [ ] No contradictory requirements
- [ ] No contradictory workflows
- [ ] No contradictory principles
- [ ] No contradictory procedures
- [ ] Conflicts are resolved or documented

### Boundary Drift
- [ ] Scope boundaries are consistent
- [ ] In-scope/out-of-scope is consistent
- [ ] Responsibility boundaries are clear
- [ ] Layer boundaries are consistent
- [ ] No scope creep

### Self-Reference
- [ ] Documents don't contradict themselves
- [ ] Internal consistency within each document
- [ ] Sections within documents are consistent
- [ ] No internal circular references
- [ ] Self-consistent terminology

### Realism
- [ ] Claims are achievable
- [ ] Timelines are realistic
- [ ] Resource requirements are realistic
- [ ] Technical claims are verified
- [ ] No unfounded assertions

---

## 7. Test Coverage Validation Checklist

### Unit Tests
- [ ] Individual component testing
- [ ] Conformance testing
- [ ] Edge case coverage
- [ ] Error path coverage
- [ ] Mock external dependencies

### Integration Tests
- [ ] Component interaction testing
- [ ] Dependency testing
- [ ] Interface contract testing
- [ ] End-to-end workflow testing
- [ ] Multi-component scenarios

### Security Tests
- [ ] Input validation testing
- [ ] Secret redaction testing
- [ ] Configuration tampering testing
- [ ] Prompt injection testing
- [ ] Access control testing

### Performance Tests
- [ ] Load testing
- [ ] Response time validation
- [ ] Latency target verification
- [ ] Resource usage testing
- [ ] Scalability testing

### Test Stability
- [ ] Test stability ≥ 99.5%
- [ ] No flaky tests
- [ ] Test isolation (no interdependence)
- [ ] Deterministic test results
- [ ] Test reproducibility

### Test Coverage
- [ ] Test coverage ≥ 80%
- [ ] Critical paths covered
- [ ] Public API covered
- [ ] Error paths covered
- [ ] Security paths covered

---

## 8. Configuration Validation Checklist

### Configuration Structure
- [ ] Configuration files are valid JSON
- [ ] All required fields present
- [ ] Field types correct
- [ ] Schema validation passes
- [ ] No syntax errors

### Configuration Integrity
- [ ] Configuration tampering detection
- [ ] Hash-based verification
- [ ] Immutable configuration history
- [ ] Configuration backup procedures
- [ ] Configuration rollback capability

### Configuration Security
- [ ] No hardcoded credentials
- [ ] Secure defaults (fail-closed)
- [ ] Least privilege defaults
- [ ] Configuration access controlled
- [ ] Configuration changes audited

### Adapter Configuration
- [ ] Adapter capability declarations accurate
- [ ] Hook registration correct
- [ ] Adapter-specific config valid
- [ ] Adapter selection exactly one enabled
- [ ] Adapter timeouts configured

### Governance Settings
- [ ] Strictness levels appropriate
- [ ] Default mode configured
- [ ] Conflict resolution strategy configured
- [ ] Emergency halt configured
- [ ] Emergency state file path configured

### Logging Configuration
- [ ] Log level configured
- [ ] Log format configured (JSONL)
- [ ] Log retention configured
- [ ] Log directory configured
- [ ] Log rotation configured

### Timeout Configuration
- [ ] PreToolUse timeout configured
- [ ] PostToolUse timeout configured
- [ ] OnError timeout configured
- [ ] Timeouts appropriate for operations
- [ ] Timeout enforcement tested

---

## 9. Policy Validation Checklist

### Policy Structure
- [ ] Policy files are valid JSON
- [ ] Version field present (semantic versioning)
- [ ] Name field present
- [ ] Description field present
- [ ] Rules array present
- [ ] Required fields present

### Rule Structure
- [ ] Rule ID unique within policy
- [ ] Condition field present
- [ ] Action field present
- [ ] Rationale field present
- [ ] Condition syntax valid
- [ ] Action in allowed values (allow, deny, modify, warn)

### Policy Versioning
- [ ] Semantic versioning used (major.minor.patch)
- [ ] Timestamp present
- [ ] Author present
- [ ] Version history maintained
- [ ] Rollback capability functional

### Meta Rules
- [ ] Meta rules implemented
- [ ] Policy format validation functional
- [ ] Conflict prevention functional
- [ ] Meta rule checks executed
- [ ] Meta rule violations detected

### Conflict Resolution
- [ ] Conflict resolution strategy configured (per ARCHITECTURE.md Principle 19)
- [ ] Strategy is one of allowed values (deny_overrides, allow_overrides, priority_first_match)
- [ ] deny_overrides implemented
- [ ] allow_overrides implemented
- [ ] priority_first_match implemented
- [ ] Conflicts resolvable

### Policy Naming
- [ ] Policy name matches file name
- [ ] Policy naming convention followed
- [ ] Rule ID naming convention followed
- [ ] Names descriptive
- [ ] Names consistent

### Policy Quality
- [ ] Conditions evaluate correctly
- [ ] Actions are appropriate
- [ ] Rationales are clear
- [ ] Priorities are set correctly
- [ ] Scopes are set correctly

---

## Checklist Creation Process

### Phase 1: Draft Creation
1. Start with industry standards (ISO 42030, OWASP, NIST AI RMF, ISO 42001)
2. Map to Governor Framework specifics (ARCHITECTURE.md principles)
3. Organize by layer (Architecture, Security, Compliance, Code Quality)
4. Include both automated and manual checks

### Phase 2: Expert Review
1. Review with security architect
2. Review with compliance officer
3. Review with software engineering lead
4. Review with AI governance board
5. Revise based on feedback

### Phase 3: Field Testing
1. Test with real reviews (use EXTERNAL_REVIEW_PROMPT.md)
2. Test with different reviewers (varying expertise)
3. Test on different document types (architecture, code, compliance)
4. Track time to complete checklist
5. Revise based on field testing

### Phase 4: Integration
1. Integrate into IMPLEMENTATION_WORKFLOW.md
2. Integrate into FIX_WORKFLOW.md
3. Add evaluation gates at appropriate points
4. Document checklist usage in training materials

### Phase 5: Maintenance
1. Schedule quarterly review
2. Update based on new standards/requirements
3. Update based on lessons learned
4. Track checklist effectiveness (findings missed vs caught)
