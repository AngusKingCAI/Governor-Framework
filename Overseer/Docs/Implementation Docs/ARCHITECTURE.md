# Overseer Framework Architecture Principles

**Version**: 4.0.0  
**Date**: 2026-08-11  
**Purpose**: Define the fundamental architectural principles and data flow for the Overseer hook-based AI agent governance system

## Product Summary

**What is Overseer?**

Overseer is a hook-based governance system that intercepts AI agent tool usage and enforces policies. It provides runtime enforcement of governance rules, universal CLI support across different AI agent frameworks, and lightweight portability that can be embedded anywhere.

**What is Overseer trying to achieve?**

Overseer aims to solve three key problems in AI agent governance:

1. **Tool Access Control**: AI agents can access tools and files inappropriately. Overseer enforces boundaries on what agents can do.

2. **Compliance and Auditing**: Organizations need compliance, audit trails, and governance for AI agent actions. Overseer provides tamper-evident audit trails and comprehensive logging.

3. **Cross-Framework Standardization**: Different AI agent frameworks and CLIs have different governance approaches. Overseer standardizes governance across all frameworks through a universal hook-based system.

**Target Users**

Overseer serves both hobbyists and enterprise users equally:
- **Hobbyists**: Individual developers who want basic tool usage oversight and policy enforcement
- **Enterprise**: Teams needing compliance, audit trails, and strict policy enforcement at scale

**Differentiation**

Overseer is unique because it provides:
- **Runtime Enforcement**: Hook-based enforcement at the moment of action, unlike dashboard-only tools
- **Universal CLI Support**: CLI-agnostic design works with any AI agent framework
- **Lightweight and Portable**: Zero-dependency design allows embedding in any environment

**Success Definition**

Overseer succeeds when:
- Users trust their AI agents are properly governed (trust and safety)
- Overseer can be easily embedded in any environment (universal embeddability)
- Overseer scales from individual developers to enterprise teams (scalable adoption)

**Deployment Model**

Overseer is designed for local installation - users install it locally and it hooks into their AI agent tools.

**Default Behavior**

When Overseer blocks an action based on policy, it creates a bypass menu for the user, allowing them to override the block when needed. System errors fail-closed without bypass menus.

---

## Architecture and Data Flow

### File Structure

```
Overseer/
├── Core/
│   ├── overseer.py              # Central entry point and orchestrator
│   ├── protocol/                # Protocol module - canonical data models
│   │   ├── __init__.py
│   │   ├── models.py            # Canonical payload definitions
│   │   ├── validators.py        # Schema validation
│   │   └── transformers.py      # Data transformation utilities
│   ├── engine/                  # Engine module - policy evaluation
│   │   ├── __init__.py
│   │   ├── evaluator.py         # Policy evaluation logic
│   │   ├── conflict_resolver.py # Conflict resolution strategies
│   │   └── policy_loader.py     # Policy loading and hot-reload
│   ├── state_machine/           # State Machine module - governance state
│   │   ├── __init__.py
│   │   ├── base.py              # Base state machine classes
│   │   ├── emergency.py         # Emergency control states
│   │   └── workflow.py          # Workflow orchestration states
│   └── hook_handler/            # Hook Handler - single dynamic dispatcher
│       ├── __init__.py
│       └── dispatcher.py        # Dynamic hook dispatcher
├── Adapter/
│   ├── __init__.py
│   ├── base.py                  # BaseAdapter class
│   └── [AppName]-Adapter.py     # Framework-specific adapters (devin, claude, cursor, vscode)
├── Config/
│   └── config.json              # Configuration and adapter selection
├── Actions/
│   ├── __init__.py
│   ├── base.py                  # BaseAction class
│   ├── [PolicyName].py         # User policy execution logic
│   └── Meta-Actions/
│       └── [MetaRuleName].py    # Meta rule enforcement
├── Rules/
│   ├── [PolicyName].json        # User policy definitions
│   └── Meta-Rules/
│       └── [MetaRuleName].json  # Meta rule definitions
├── Logs/                        # Layer-specific JSONL log files
└── Tests/                       # Test suites
```

### Data Flow

**Complete request flow from hook to action:**

```
1. Hook fires (e.g., Devin CLI PreToolUse)
   ↓
2. Overseer/overseer.py (entry point)
   - Receives hook event name and event data
   - Logs initialization
   ↓
3. Config/config.json
   - Reads adapter name (e.g., "devin")
   - Logs configuration loaded
   ↓
4. Adapter/[AppName]-Adapter.py (dynamically loaded)
   - Adapter loaded based on config
   - Adapter provides: capabilities, transformations, hook support
   - Logs adapter loaded
   ↓
5. Core/protocol/models.py
   - Adapter transforms event to CanonicalPayload
   - Protocol validates canonical structure
   - Logs transformation and validation
   ↓
6. Core/engine/evaluator.py
   - Engine evaluates policies against canonical payload
   - Conflict resolver composes multiple policy decisions
   - Logs policy evaluation and conflict resolution
   ↓
7. Core/state_machine/emergency.py
   - State machine checks emergency halt status
   - If emergency active, returns deny immediately
   - Logs state check
   ↓
8. Core/hook_handler/dispatcher.py
   - Single dynamic dispatcher coordinates hook execution
   - Dispatcher parses input once, routes to appropriate handlers
   - Logs hook dispatch
   ↓
9. Rules/[PolicyName].json
   - Hook handler checks rules from rule files
   - Determines if any rule is triggered
   - Logs rule evaluation
   ↓
10. Actions/[PolicyName].py
    - If rule triggered, execute corresponding action
    - Action performs: Block, Warn, or Direct agent
    - Logs action execution
    ↓
11. Return decision to CLI
    - Block: exit code 2 with reason
    - Allow: exit code 0 with reason
```

### Module Responsibilities

**Overseer (Core/overseer.py)**
- Entry point for all hook events
- Orchestrates between modules
- Dynamic adapter loading based on config
- Coordinates data flow through system
- Logs orchestration events

**Adapter (Adapter/[AppName]-Adapter.py)**
- CLI-specific event transformation
- Capability discovery and declaration
- Provides transformation logic to Protocol
- Dynamically loaded based on config
- Zero CLI-specific assumptions in core (Principle 1)

**Protocol (Core/protocol/)**
- Canonical data model definitions (CanonicalPayload, GovernanceDecision)
- Schema validation for canonical payloads
- Data transformation utilities
- Version management for protocol evolution
- Completely independent of adapter implementations

**Engine (Core/engine/)**
- Policy evaluation logic
- Policy loading and hot-reload
- Conflict resolution strategies (deny_overrides, allow_overrides, priority_first_match)
- Decision composition and attribution
- Stateless and deterministic evaluation

**State Machine (Core/state_machine/)**
- Emergency control states (NORMAL, HALT_NONCRITICAL, HALT_ALL, EMERGENCY)
- Workflow orchestration states
- Session state management
- State transition audit logging
- File-system persistence for emergency state

**Hook Handler (Core/hook_handler/)**
- Single dynamic dispatcher per event type
- Coordinates hook execution
- Priority-based ordering
- Per-hook timeout configuration
- Fail-closed for security, fail-open for observability

**Rules (Rules/[PolicyName].json)**
- Declarative policy definitions
- JSON-based rule conditions and actions
- Versioned policy files
- Meta rules for policy governance

**Actions (Actions/[PolicyName].py)**
- Policy execution logic
- Block, Warn, or Direct agent enforcement
- User policy implementations
- Meta rule enforcement

### Key Architectural Principles

**Modular Independence**
- Each module has single responsibility
- Minimal coupling between modules
- Clear interfaces between layers
- Independent testing possible

**Dynamic Loading**
- Adapters loaded dynamically based on config
- No hardcoded CLI knowledge in core
- Adding new adapters requires config change only
- Core adapts to adapter capabilities

**Zero External Dependencies**
- Core modules use only Python standard library
- Adapter dependencies optional and documented
- No cloud service dependencies
- Local installation and execution

**Fail-Closed Enforcement**
- Emergency state checked before every action
- Governance errors result in deny
- System errors fail-closed without bypass
- Security-first approach

**Comprehensive Logging**
- Every layer logs to layer-specific JSONL files
- Structured log format for machine readability
- Tamper-evident audit trails
- State transition history for reconstruction

---

## Architecture Principles

## Principle 1: True Agnosticism

**Definition**: The core Overseer framework must make zero assumptions about adapters or environments. It must be configurable to work with any CLI or agent framework without hardcoded knowledge.

**Desired State**:

### 1.1 Zero CLI-Specific Assumptions
- **Target Behavior**: Core framework has no hardcoded CLI knowledge
- **Implementation**: All CLI-specific logic lives in adapters, not core
- **Example**: Overseer core doesn't know about Devin, Cursor, or any specific CLI
- **Benefit**: Framework works with any CLI without core changes

### 1.2 Configurable Adapter Selection
- **Target Behavior**: Adapters selected via configuration, not hardcoded
- **Implementation**: Configuration specifies which adapter to load
- **Example**: User configures "devin_adapter" or "cursor_adapter" in config.json
- **Benefit**: Easy addition of new adapters without core changes

### 1.3 Plugin SDK Pattern
- **Target Behavior**: Adapters implement well-defined SDK interface
- **Implementation**: BaseAdapter class with required methods for all adapters
- **Example**: BaseAdapter requires transform_event(), get_capabilities(), register_hooks()
- **Benefit**: Consistent adapter development pattern

### 1.4 Capability-Based Ports
- **Target Behavior**: Adapters expose capabilities via capability discovery
- **Implementation**: Adapters declare supported hooks, event types, and data schemas
- **Example**: Adapter declares support for PreToolUse, PostToolUse hooks
- **Benefit**: Framework adapts to adapter capabilities automatically

**Success Criteria**:
- Core framework has zero CLI-specific code
- Adapters selected via configuration
- All adapters implement SDK interface
- Capabilities discovered dynamically

---

## Principle 2: Modular Architecture

**Definition**: Overseer is composed of independent layers with minimal coupling. Each layer has a single responsibility and well-defined interfaces.

**Desired State**:

### 2.1 Layer Independence
- **Target Behavior**: Each layer operates independently with minimal coupling
- **Implementation**: Loose coupling through interfaces, not direct dependencies
- **Example**: Adapter layer doesn't directly import Overseer core internals
- **Benefit**: Layers can be developed, tested, and deployed independently

### 2.2 Single Responsibility
- **Target Behavior**: Each layer has a single, well-defined responsibility
- **Implementation**: Adapter handles CLI mapping, Protocol handles data, Overseer handles governance
- **Example**: Protocol layer doesn't know about CLI specifics
- **Benefit**: Clear separation of concerns, easier to understand and maintain

### 2.3 Well-Defined Interfaces
- **Target Behavior**: Layers communicate through well-defined interfaces
- **Implementation**: Abstract base classes and protocol definitions
- **Example**: BaseAdapter, ProtocolPayload, GovernanceDecision interfaces
- **Benefit**: Layers can be swapped or extended without breaking others

**Success Criteria**:
- Layers can be developed independently
- Each layer has single responsibility
- Interfaces clearly defined and stable
- Minimal coupling between layers

---

## Principle 3: Small Reusable Kernel

**Definition**: The core Overseer engine should be small, focused, and reusable. It should contain only essential governance logic, with extensibility through plugins.

**Desired State**:

### 3.1 Minimal Core
- **Target Behavior**: Core contains only essential governance logic
- **Implementation**: Policy evaluation, hook orchestration, decision enforcement in core
- **Example**: CLI adapters, logging backends are plugins, not core
- **Benefit**: Small, focused core is easier to test and maintain

### 3.2 Plugin Extensibility
- **Target Behavior**: Non-essential functionality provided through plugins
- **Implementation**: Plugin system for logging, adapters, policy engines
- **Example**: Different logging backends (file, cloud) as plugins
- **Benefit**: Extensible without bloating core

### 3.3 Reusable Components
- **Target Behavior**: Core components are reusable across different contexts
- **Implementation**: Governance engine can be embedded in different systems
- **Example**: Same core can work in CLI, web, or embedded contexts
- **Benefit**: Overseer can be embedded anywhere

**Success Criteria**:
- Core is small and focused
- Plugin system for extensibility
- Core components reusable in different contexts
- Zero runtime dependencies in core

---

## Principle 4: Rule-Based Governance

**Definition**: Governance decisions are based on declarative rules rather than imperative code. Policies are data-driven and can be versioned, audited, and reasoned about.

**Desired State**:

### 4.1 Declarative Policy Engine
- **Target Behavior**: Policies expressed as declarative rules
- **Implementation**: Support JSON policy definitions with standard patterns
- **Example**: JSON policy defines conditions, actions, and rationales
- **Benefit**: Policies are human-readable and machine-processable

### 4.2 Policy Versioning
- **Target Behavior**: Every policy has a unique version identifier
- **Implementation**: Semantic versioning with timestamp and author
- **Example**: Policy change creates new version: "file-deletion-rule v2.1.0"
- **Benefit**: Reproducible governance decisions linked to specific policy versions

### 4.3 Meta Rules
- **Target Behavior**: Framework supports meta rules for policy governance
- **Implementation**: Meta rules validate policy format, structure, and conflicts
- **Example**: Meta rule prevents contradictory policies from being loaded
- **Benefit**: Policy quality enforced programmatically

**Success Criteria**:
- Policies expressed declaratively
- Policy versioning implemented
- Meta rules for policy governance
- Policy rollback capability

---

## Principle 5: In-Path Fail-Closed Enforcement

**Definition**: Governance enforcement happens in-path, before tool execution, with fail-closed defaults for security. Hooks block actions when governance checks fail.

**Desired State**:

### 5.1 Fail-Closed Default
- **Target Behavior**: Default governance mode is fail-closed (block on failure)
- **Implementation**: Hooks block actions when governance checks fail or error
- **Example**: New installations start in "blocking" mode with deny on errors
- **Benefit**: Security-first approach prevents unauthorized access during failures

### 5.2 Pre-Execution Interception
- **Target Behavior**: Hooks intercept tool calls before execution
- **Implementation**: PreToolUse hook blocks or modifies tool execution
- **Example**: File deletion hook blocks rm command before it executes
- **Benefit**: Prevents unauthorized actions from completing

### 5.3 Immediate Enforcement
- **Target Behavior**: Governance decisions are enforced immediately
- **Implementation**: No delay between decision and enforcement
- **Example**: Deny decision immediately blocks tool execution
- **Benefit**: No window for unauthorized action completion

### 5.4 No Bypass Path
- **Target Behavior**: No path to bypass governance enforcement
- **Implementation**: All tool invocations must pass through governance hooks
- **Example**: Cannot execute tool without passing through Overseer hooks
- **Benefit**: Complete governance coverage

### 5.5 Configurable Strictness
- **Target Behavior**: Strictness levels are configurable
- **Implementation**: Support blocking, advisory, and hybrid modes
- **Example**: Hobbyists use advisory mode, enterprises use blocking mode
- **Benefit**: Scales from casual to critical use cases

**Success Criteria**:
- Default mode is fail-closed (block on failure)
- Enforcement happens before tool execution
- Governance decisions enforced immediately
- No bypass path for tool execution
- Multiple strictness levels supported

---

## Principle 6: Deterministic Discrete Verdicts

**Definition**: Governance produces deterministic verdicts (allow, deny, modify) based on policy evaluation. Decisions are deterministic for a fixed, explicitly recorded decision context.

**Desired State**:

### 6.1 Discrete Verdict Types
- **Target Behavior**: Governance produces allow, deny, or modify verdicts
- **Implementation**: Policy evaluation results in one of three discrete outcomes
- **Example**: Rule evaluation returns "allow", "deny", or "modify with parameters"
- **Benefit**: Clear, bounded decision space

### 6.2 Deterministic Evaluation
- **Target Behavior**: Policy evaluation is deterministic for given inputs
- **Implementation**: Same policy and context always produce same verdict
- **Example**: Identical requests to same policy produce identical verdicts
- **Benefit**: Predictable and testable governance

### 6.3 Context Recording
- **Target Behavior**: Decision context is explicitly recorded
- **Implementation**: Audit logs include full context that influenced the decision
- **Example**: Decision log includes all inputs, policy version, system state
- **Benefit**: Complete decision reconstruction for audit

### 6.4 Verdict Composition
- **Target Behavior**: Multiple policy verdicts compose into final decision
- **Implementation**: Policy conflict resolution determines final verdict
- **Example**: Multiple rules evaluate; conflict resolution determines final allow/deny/modify
- **Benefit**: Complex policy sets supported through composition

**Success Criteria**:
- Governance produces allow, deny, or modify verdicts
- Policy evaluation is deterministic
- Decision context explicitly recorded
- Multiple verdicts compose into final decision

---

## Principle 7: Stateless and Idempotent Enforcement

**Definition**: Each hook invocation should be independently decidable (given rule state and action context). Governance checks must be idempotent - the same request evaluated multiple times should produce the same decision.

**Desired State**:

### 7.1 Independent Hook Decisions
- **Target Behavior**: Each hook invocation independently decidable based on provided context
- **Implementation**: Hook decisions based only on current state and context provided
- **Example**: Hook decision doesn't depend on previous hook results
- **Benefit**: Predictable, testable behavior

### 7.2 No Cross-Hook Decision Dependencies
- **Target Behavior**: Hook decisions don't depend on other hooks' decisions
- **Implementation**: Each hook makes its own allow/deny/modify decision based on input
- **Example**: Hook A's decision doesn't depend on whether Hook B allowed or denied
- **Benefit**: Flexible hook ordering, independent testing

### 7.3 Deterministic Re-evaluation
- **Target Behavior**: Re-evaluating the same request produces the same decision
- **Implementation**: Governance decisions based only on request state and policy state
- **Example**: Retrying a blocked action remains blocked unless policy or context changes
- **Benefit**: Consistent behavior across retries and network issues

**Success Criteria**:
- Hook decisions independently decidable
- No cross-hook decision dependencies
- Re-evaluating same request produces same decision
- State changes atomic and reversible

---

## Principle 8: Standardized Hook Payloads

**Definition**: Hook inputs/outputs should map cleanly to a canonical model (action type, agent identity, resource, access level, audit context). Adapters map CLI-specific formats to this canonical model.

**Desired State**:

### 8.1 Canonical Payload Model
- **Target Behavior**: Hook payloads follow canonical model with all necessary context
- **Implementation**: Standard structure for all hook inputs/outputs
- **Example**: All hooks have action_type, agent_identity, resource, access_level
- **Benefit**: Consistent interface across different CLIs

### 8.2 CLI-to-Canonical Mapping
- **Target Behavior**: CLI-specific formats mapped to canonical model
- **Implementation**: Adapters convert CLI events to canonical payloads
- **Example**: Devin CLI tool use mapped to canonical action model
- **Benefit**: Framework works consistently across different CLIs

### 8.3 Payload Extensibility
- **Target Behavior**: Canonical model extensible for new fields
- **Implementation**: Optional fields in canonical model
- **Example**: Can add new audit context fields without breaking existing hooks
- **Benefit**: Future-proof design

**Success Criteria**:
- Hook payloads follow canonical model
- CLI-specific formats mapped to canonical
- Model extensible for new requirements
- Consistent interface across CLIs

---

## Principle 9: Audit Trail and Observability

**Definition**: Governance decisions must be fully auditable with tamper-evident logging. Hooks provide runtime observability into agent behavior for monitoring compliance, cost, and performance.

**Desired State**:

### 9.1 Comprehensive Decision Logging
- **Target Behavior**: Every governance decision is logged with full context
- **Implementation**: Log decision type, triggering policy, input context, and rationale
- **Example**: Decision logged as "DENY by policy X for action Y because Z"
- **Benefit**: Complete audit trail of all governance decisions

### 9.2 Structured Log Format
- **Target Behavior**: All logs follow consistent structured format
- **Implementation**: Use JSONL format with consistent fields
- **Example**: `{"timestamp": "ISO8601", "decision": "deny", "policy": "X", "context": {...}}`
- **Benefit**: Machine-readable logs for analysis and monitoring

### 9.3 Behavioral Monitoring
- **Target Behavior**: Hooks monitor agent behavior patterns
- **Implementation**: Hooks track which tools are called, frequency, and patterns
- **Example**: Hook logs "agent called file_delete 5 times in last hour"
- **Benefit**: Visibility into agent behavior

### 9.4 Tamper-Evident Audit
- **Target Behavior**: Audit trail is tamper-evident
- **Implementation**: Cryptographic signatures or append-only logging
- **Example**: Logs signed or stored in append-only format
- **Benefit**: Audit trail integrity verifiable

**Success Criteria**:
- Every governance decision logged with full context
- Structured log format for machine readability
- Hooks monitor agent behavior
- Audit trail is tamper-evident

---

## Principle 10: Digital Sovereignty

**Definition**: The governance system should be sovereign by construction - portable across providers, inspectable in behavior, and free of hidden dependencies on any single vendor or platform.

**Desired State**:

### 10.1 Local Installation
- **Target Behavior**: Overseer runs locally on user's machine
- **Implementation**: No cloud dependency or remote service requirement
- **Example**: Users install Overseer locally like any other CLI tool
- **Benefit**: Full control over governance system

### 10.2 Vendor Independence
- **Target Behavior**: Overseer doesn't depend on any single vendor
- **Implementation**: Zero cloud service dependencies, open-source code
- **Example**: Overseer works offline without any vendor services
- **Benefit**: No vendor lock-in

### 10.3 Inspectable Behavior
- **Target Behavior**: All Overseer behavior is inspectable
- **Implementation**: Open-source code, clear logging, transparent decision-making
- **Example**: Users can inspect how Overseer makes decisions
- **Benefit**: Trust through transparency

**Success Criteria**:
- Overseer runs locally
- No vendor dependencies
- All behavior inspectable
- Open-source code

---

## Principle 11: Hook Composability

**Definition**: Multiple hooks should be composable without conflicts. Users should be able to chain multiple governance hooks together.

**Desired State**:

### 11.1 Hook Chaining
- **Target Behavior**: Multiple hooks can be chained together in configurable order
- **Implementation**: Hooks are called in sequence, with data passing between them
- **Example**: Validation hook → Logging hook → Audit hook
- **Benefit**: Users can combine multiple governance concerns

### 11.2 Hook Isolation
- **Target Behavior**: Hook decisions are independent; one hook cannot force another hook's decision
- **Implementation**: Each hook evaluates independently based on the input it receives
- **Example**: One hook's deny decision doesn't automatically trigger another hook's deny
- **Benefit**: Predictable behavior, easier debugging

### 11.3 Configurable Hook Order
- **Target Behavior**: Hook execution order is configurable
- **Implementation**: Configuration defines hook priority and ordering
- **Example**: Priority configuration determines which hooks run first
- **Benefit**: Flexible governance pipeline composition

**Success Criteria**:
- Multiple hooks can be chained together
- Hook decisions are independent
- Hook execution order is configurable
- Hooks can be composed without conflicts

---

## Principle 12: Bypass Menu Interaction

**Definition**: When governance blocks an action based on policy, users should have a clear mechanism to understand and potentially override the block. This enables user control while maintaining security boundaries.

**Desired State**:

### 12.1 Bypass Menu Creation
- **Target Behavior**: Blocked actions present bypass menu to user
- **Implementation**: Clear UI showing block reason and override options
- **Example**: "Action blocked by policy X. Override? [Yes/No]"
- **Benefit**: User maintains control while security is enforced

### 12.2 Bypass Justification
- **Target Behavior**: User bypass requires justification
- **Implementation**: User must provide reason for override
- **Example**: "Reason for override: _______"
- **Benefit**: Audit trail of bypass decisions

### 12.3 Bypass Limits
- **Target Behavior**: Bypass capability has configurable limits
- **Implementation**: Maximum bypasses per time period, or require approval for certain actions
- **Example**: Max 5 bypasses per hour, or admin approval for production overrides
- **Benefit**: Prevents bypass abuse

**Success Criteria**:
- Blocked actions present bypass menu
- Bypass requires justification
- Bypass capability has limits
- Bypass decisions logged

---

## Principle 13: Configurable Hook Timeouts

**Definition**: Hooks must have configurable timeout boundaries to prevent hung hooks from deadlocking the governed agent.

**Desired State**:

### 13.1 Config-Based Timeout Definition
- **Target Behavior**: Hook timeouts are defined in configuration
- **Implementation**: Configuration specifies timeout values for each hook type
- **Example**: Configuration defines timeout values for each hook type
- **Benefit**: Different adapters can specify appropriate timeout values

### 13.2 Timeout Enforcement
- **Target Behavior**: Hooks are aborted if they exceed timeout
- **Implementation**: Hook execution is terminated after timeout, action blocked
- **Example**: If hook runs longer than timeout, tool execution is denied
- **Benefit**: Prevents hung hooks from deadlocking the agent

**Success Criteria**:
- Hook timeouts defined in configuration
- Hooks are aborted on timeout to prevent deadlocks
- Different hook types can have different timeout values

---

## Principle 14: Data Minimization and Privacy by Design

**Definition**: Governance system must minimize data collection and protect sensitive information by default. Logs should be retained only as long as necessary, and sensitive data should be identified and masked.

**Desired State**:

### 14.1 Configurable Retention
- **Target Behavior**: Log retention periods are configurable
- **Implementation**: Configuration defines how long logs are kept before deletion
- **Example**: Retain logs for 90 days by default, configurable per environment
- **Benefit**: Compliance with data retention requirements

### 14.2 Sensitive Data Identification
- **Target Behavior**: System identifies sensitive data in logs
- **Implementation**: Pattern matching for secrets, PII, and other sensitive data
- **Example**: Detect patterns like "password", "token", "credit_card"
- **Benefit**: Awareness of sensitive data in logs

### 14.3 Configurable Data Masking
- **Target Behavior**: Sensitive data is masked or redacted before log persistence
- **Implementation**: Masking rules applied during log generation or export
- **Example**: Mask "password" field with "*****", redact credit card numbers
- **Benefit**: User control over sensitive data visibility

**Success Criteria**:
- Retention periods configurable
- Sensitive data identified and masked
- Access controls enforced
- Logging balanced with data minimization

---

## Principle 15: Emergency Controls and Kill Switch

**Definition**: The governance system must support immediate halting of agent sessions and workflows for emergency response.

**Desired State**:

### 15.1 Immediate Halt Capability
- **Target Behavior**: System can immediately halt agent sessions and workflows
- **Implementation**: Emergency flag checked in hot path, blocks all actions when set
- **Example**: Set emergency flag, all subsequent tool calls blocked
- **Benefit**: Instant response to critical incidents

### 15.2 Multiple Control Scopes
- **Target Behavior**: Emergency controls support multiple scopes (global, tenant, agent, tool)
- **Implementation**: Emergency flags can be set at different granularity
- **Example**: Global halt stops all agents; agent-specific halt stops one agent
- **Benefit**: Flexible emergency response with appropriate blast radius

### 15.3 Audit Logging
- **Target Behavior**: All emergency actions logged with reason and authorizer
- **Implementation**: Emergency flag changes logged with who authorized and why
- **Example**: Emergency halt logged as "user@example.com halted all agents due to incident X"
- **Benefit**: Complete audit trail of emergency interventions

**Success Criteria**:
- Immediate halt capability implemented
- Multiple control scopes supported
- Emergency actions logged
- Authorization matrix defined

---

## Principle 16: Agent Identity and Authentication

**Definition**: Governance decisions should consider agent identity. Agents must be authenticated and their identity used in policy evaluation.

**Desired State**:

### 16.1 Agent Identity
- **Target Behavior**: Each agent has a unique identity
- **Implementation**: Agent identity passed through governance context
- **Example**: Agent identity: "researcher-agent-001"
- **Benefit**: Policies can differentiate between agents

### 16.2 Authentication
- **Target Behavior**: Agent identity is authenticated
- **Implementation**: Authentication mechanism to verify agent identity
- **Example**: API keys, certificates, or other authentication
- **Benefit**: Prevents agent identity spoofing

### 16.3 Identity-Based Policies
- **Target Behavior**: Policies can reference agent identity
- **Implementation**: Policy conditions can include agent identity
- **Example**: "IF agent == 'researcher-agent' THEN allow read-only"
- **Benefit**: Fine-grained agent-specific governance

**Success Criteria**:
- Each agent has unique identity
- Agent identity authenticated
- Policies can reference agent identity
- Identity spoofing prevented

---

## Principle 17: Delegation Chain Accountability

**Definition**: When agents delegate tasks to other agents or systems, the delegation chain must be tracked and accountable. Governance should understand the full delegation hierarchy.

**Desired State**:

### 17.1 Delegation Tracking
- **Target Behavior**: Delegation chains are tracked
- **Implementation**: Each delegation includes parent agent identity and delegation scope
- **Example**: Agent A delegates to Agent B for task X, scope limited to file Y
- **Benefit**: Full visibility into delegation hierarchy

### 17.2 Delegation Scope
- **Target Behavior**: Delegations have explicit scope limits
- **Implementation**: Delegation tokens encode permissions and time limits
- **Example**: Delegation token allows "read file X" for 10 minutes
- **Benefit**: Delegations are bounded and time-limited

### 17.3 Delegation Accountability
- **Target Behavior**: Delegation chains are accountable
- **Implementation**: Audit trail includes full delegation chain for each action
- **Example**: Action logged with delegation chain: A→B→C
- **Benefit**: Full accountability for delegated actions

**Success Criteria**:
- Delegation chains tracked
- Delegations have explicit scope
- Delegation chains logged
- Full accountability for delegated actions

---

## Principle 18: Human-in-the-Loop Escalation Gates

**Definition**: High-risk or ambiguous governance decisions should require human oversight. The framework should support escalation to human reviewers for approval or guidance.

**Desired State**:

### 18.1 Risk-Based Escalation
- **Target Behavior**: High-risk actions require human approval
- **Implementation**: Policy defines risk levels and corresponding escalation requirements
- **Example**: Production deployment requires human approval; file read does not
- **Benefit**: Human oversight for critical decisions

### 18.2 Escalation Workflow
- **Target Behavior**: Clear workflow for human escalation
- **Implementation**: Defined process for requesting, receiving, and acting on human approval
- **Example**: Agent requests approval, human reviews, approves or denies
- **Benefit**: Predictable escalation process

### 18.3 Approval Tracking
- **Target Behavior**: Human approvals are tracked and audited
- **Implementation**: Approval records include approver identity, reason, and timestamp
- **Example**: Approval logged as "user@example.com approved action X at time T"
- **Benefit**: Audit trail of human decisions

**Success Criteria**:
- High-risk actions require human approval
- Clear escalation workflow defined
- Human approvals tracked and audited
- Approval timeout and expiry

---

## Principle 19: Policy Conflict Resolution

**Definition**: When multiple policies produce conflicting verdicts, the framework must have a deterministic resolution strategy.

**Desired State**:

### 19.1 Conflict Detection
- **Target Behavior**: Framework detects policy conflicts
- **Implementation**: Conflict detection identifies contradictory policy verdicts
- **Example**: Policy A says "allow", Policy B says "deny" for same action
- **Benefit**: Awareness of policy conflicts

### 19.2 Resolution Strategy
- **Target Behavior**: Framework has deterministic conflict resolution
- **Implementation**: Default deny-wins strategy with configurable alternatives
- **Example**: Default: deny verdicts always take precedence over allow
- **Benefit**: Predictable conflict resolution

### 19.3 Configurable Strategies
- **Target Behavior**: Conflict resolution strategy is configurable
- **Implementation**: Support deny-wins, allow-wins, or custom strategies
- **Example**: Organizations can choose their conflict resolution approach
- **Benefit**: Flexible conflict resolution

**Success Criteria**:
- Policy conflicts detected
- Deterministic resolution strategy implemented
- Conflict resolution configurable
- Conflict resolution decisions logged

---

## Principle 20: Configuration Integrity and Change Control

**Definition**: Governance configuration must be tamper-evident and change-controlled. Configuration changes should be logged, authorized, and reversible.

**Desired State**:

### 20.1 Configuration Integrity
- **Target Behavior**: Configuration integrity is verifiable
- **Implementation**: Configuration checksums or signatures
- **Example**: Configuration file has SHA256 hash verified on load
- **Benefit**: Detects configuration tampering

### 20.2 Change Logging
- **Target Behavior**: All configuration changes are logged
- **Implementation**: Change log includes who changed what and when
- **Example**: Configuration change logged as "user@example.com changed policy X at time T"
- **Benefit**: Audit trail of configuration changes

### 20.3 Change Authorization
- **Target Behavior**: Configuration changes require authorization
- **Implementation**: Role-based access control for configuration modifications
- **Example**: Only admins can modify governance configuration
- **Benefit**: Prevents unauthorized configuration changes

**Success Criteria**:
- Configuration integrity verifiable
- Configuration changes logged
- Configuration changes authorized
- Configuration rollback capability

---

## Principle 21: Secrets Protection via Meta Rules

**Definition**: Secrets (API keys, passwords, tokens) must be protected from exposure in logs, audit trails, and error messages. Meta rules should detect and redact secrets.

**Desired State**:

### 21.1 Secret Detection
- **Target Behavior**: Meta rules detect secrets in data
- **Implementation**: Pattern matching for common secret formats
- **Example**: Detect API keys, passwords, tokens
- **Benefit**: Awareness of secrets in data

### 21.2 Secret Redaction
- **Target Behavior**: Secrets are redacted from logs and outputs
- **Implementation**: Replace secrets with placeholders before logging
- **Example**: "API_KEY: sk-abc123" → "API_KEY: [REDACTED]"
- **Benefit**: Prevents secret exposure

### 21.3 Secret Storage
- **Target Behavior**: Secrets stored securely
- **Implementation**: Encrypted storage or secure secret management
- **Example**: Secrets stored in encrypted format or secret manager
- **Benefit**: Secure secret storage

**Success Criteria**:
- Secrets detected in data
- Secrets redacted from logs
- Secrets stored securely
- Secret exposure prevented

---

## Principle 22: Governance Decision Explainability

**Definition**: Governance decisions should be explainable. Users should understand why a decision was made, which policies were evaluated, and what context influenced the decision.

**Desired State**:

### 22.1 Decision Rationale
- **Target Behavior**: Governance decisions include rationale
- **Implementation**: Decision logs include explanation of why decision was made
- **Example**: Decision logged as "DENY because file is in protected paths"
- **Benefit**: Users understand decision logic

### 22.2 Policy Attribution
- **Target Behavior**: Decisions attribute which policies triggered them
- **Implementation**: Decision logs include policy IDs and rule IDs
- **Example**: Decision logged as "DENY by policy file-deletion-protection rule 1"
- **Benefit**: Users know which policies caused decisions

### 22.3 Context Factors
- **Target Behavior**: Decisions include context factors
- **Implementation**: Decision logs include relevant context that influenced decision
- **Example**: Decision logged with "resource: /etc/passwd, agent: researcher-agent"
- **Benefit**: Users understand decision context

**Success Criteria**:
- Decisions include rationale
- Decisions attribute policies
- Decisions include context factors
- Decision explanations machine-readable

---

## Principle 23: Input Validation and Prompt Injection Defense

**Definition**: The governance framework must treat all external data as untrusted and implement structural separation between trusted control flow and untrusted data processing to prevent prompt injection attacks.

**Desired State**:

### 23.1 Untrusted Data Handling
- **Target Behavior**: All external data treated as untrusted
- **Implementation**: Structural separation between trusted control flow and untrusted data
- **Example**: External documents parsed and validated before inclusion in agent context
- **Benefit**: Prevents indirect prompt injection through data poisoning

### 23.2 Input Sanitization
- **Target Behavior**: External content sanitized before inclusion in agent context
- **Implementation**: Content filtering for known injection patterns, delimiters
- **Example**: Sanitize tool outputs before passing to agent reasoning
- **Benefit**: Reduces attack surface for prompt injection

### 23.3 Origin-Aware Policy Enforcement
- **Target Behavior**: Policy enforcement at tool-call boundary with origin tracking
- **Implementation**: Values tagged with origin (trusted/untrusted) and policies enforced based on origin
- **Example**: Tool parameters from untrusted sources require additional validation
- **Benefit**: Prevents data-flow attacks manipulating tool arguments

**Success Criteria**:
- All external data treated as untrusted
- Input sanitization implemented before context inclusion
- Origin-aware policy enforcement at tool-call boundary
- Output validation before action execution

---

## Principle 24: Defense in Depth with Layered Security

**Definition**: The governance framework must implement multiple overlapping security layers using different techniques. No single layer is sufficient for agent security.

**Desired State**:

### 24.1 Layered Security Architecture
- **Target Behavior**: Multiple security layers implemented using different techniques
- **Implementation**: Execution sandboxing, intent verification, zero-trust authorization, audit logging
- **Example**: Four-layer governance: sandboxing (L1), intent verification (L2), zero-trust auth (L3), audit (L4)
- **Benefit**: Defense in depth - if one layer fails, others provide protection

### 24.2 Execution Sandboxing
- **Target Behavior**: Agent execution isolated from governance system
- **Implementation**: Agents cannot modify governance configuration or access enforcement logic
- **Example**: Agent processes run with restricted permissions, cannot access Overseer config files
- **Benefit**: Prevents agents from subverting their own governance

### 24.3 Intent Verification
- **Target Behavior**: Agent intent verified before action execution
- **Implementation**: Separate validation layer checks agent intent against policy
- **Example**: Agent tool calls validated for intent before execution
- **Benefit**: Detects malicious intent even if individual tool calls appear legitimate

**Success Criteria**:
- Multiple security layers implemented
- Execution sandboxing prevents agent access to governance
- Intent verification before action execution
- Zero-trust authorization at action level

---

## Principle 25: Least Privilege and Zero Trust Enforcement

**Definition**: Every agent action must be verified explicitly with minimum necessary permissions. Credentials scoped per-task, not per-session. Zero-trust assumption: no agent is trusted by default.

**Desired State**:

### 25.1 Per-Task Credential Scoping
- **Target Behavior**: Credentials scoped to specific task, not entire session
- **Implementation**: Short-lived tokens with minimal necessary permissions for each task
- **Example**: Agent receives token for "read specific file" not "read all files"
- **Benefit**: Limits blast radius of compromised credentials

### 25.2 Explicit Verification
- **Target Behavior**: Every action verified explicitly, no implicit trust
- **Implementation**: Action-level authorization for every tool call
- **Example**: Each tool call validated against user permissions, no implicit agent permissions
- **Benefit**: Zero-trust enforcement prevents privilege escalation

### 25.3 Permission Boundary Enforcement
- **Target Behavior**: Agent permissions bounded by explicit authorization
- **Implementation**: Delegation tokens encode only delegated permissions
- **Example**: Agent cannot exceed permissions delegated by user
- **Benefit**: Prevents unauthorized action scope expansion

**Success Criteria**:
- Credentials scoped per-task
- Every action explicitly verified
- Permission boundaries enforced
- Trust validated continuously

---

## Principle 26: Reversibility-Weighted Risk Enforcement

**Definition**: Governance enforcement intensity weighted by action reversibility. Read-only and reversible actions require lighter oversight; irreversible actions require mandatory human gates.

**Desired State**:

### 26.1 Action Reversibility Classification
- **Target Behavior**: Actions classified by reversibility (read-only, reversible, irreversible)
- **Implementation**: Policy defines reversibility levels for different action types
- **Example**: File read = reversible, file write = reversible, file delete = irreversible
- **Benefit**: Risk-based enforcement proportional to action impact

### 26.2 Light Oversight for Reversible Actions
- **Target Behavior**: Read-only and reversible actions can proceed autonomously
- **Implementation**: Automated enforcement for low-risk reversible actions
- **Example**: File read operations proceed without human approval
- **Benefit**: Reduces friction for low-risk actions

### 26.3 Mandatory Gates for Irreversible Actions
- **Target Behavior**: Irreversible actions require human confirmation
- **Implementation**: Human-in-the-loop gates for destructive or externally visible actions
- **Example**: File deletion, production deployment require human approval
- **Benefit**: Prevents irreversible damage from autonomous decisions

**Success Criteria**:
- Actions classified by reversibility
- Light oversight for reversible actions
- Mandatory gates for irreversible actions
- Configurable risk thresholds

---

## Principle 27: Subagent Isolation and Delegation Boundaries

**Definition**: Subagents must not inherit parent permissions automatically. Each delegation requires independent verification and scoped credentials. Orchestrator agents treated as untrusted input.

**Desired State**:

### 27.1 No Automatic Permission Inheritance
- **Target Behavior**: Subagents do not automatically inherit parent agent permissions
- **Implementation**: Each delegation requires explicit authorization and scoped credentials
- **Example**: Orchestrator agent cannot delegate to subagent without explicit user authorization
- **Benefit**: Prevents privilege escalation through delegation chains

### 27.2 Scoped Delegation
- **Target Behavior**: Delegation tokens scoped to specific task and duration
- **Implementation**: Delegation includes task scope, time limit, and usage caps
- **Example**: Subagent receives token for "analyze specific file" not "analyze all files"
- **Benefit**: Limits delegation blast radius

### 27.3 Independent Verification
- **Target Behavior**: Each delegation independently verified
- **Implementation**: Governance checks applied at each delegation boundary
- **Example**: Subagent tool calls validated independently of parent agent context
- **Benefit**: Prevents compromised orchestrator from bypassing governance

**Success Criteria**:
- No automatic permission inheritance
- Delegation scoped to task and duration
- Each delegation independently verified
- Orchestrator treated as untrusted input

---

## Principle Count: 27
