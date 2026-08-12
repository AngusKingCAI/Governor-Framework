# Overseer Framework Module Specifications

**Version**: 1.0.0  
**Date**: 2026-08-12  
**Purpose**: Define the responsibilities and boundaries of each Overseer module for implementation and validation

---

## Overview

This document provides a comprehensive breakdown of each file/module in the Overseer Framework, specifying:
- **Job**: What the module is responsible for
- **NOT Job**: What the module is NOT responsible for (boundaries)
- **Key Interfaces**: Dependencies and interfaces with other modules
- **Logging Requirements**: What must be logged

This serves as a reference for implementation and validation processes.

---

## Module Initialization Files

### All __init__.py files

**Job:**
- Define module exports and public API
- Initialize module-level logging
- Provide convenient imports for common classes
- Set up module-level state if needed

**NOT Job:**
- Does NOT contain business logic
- Does NOT make governance decisions
- Does NOT evaluate policies

**Key Interfaces:**
- Located in: Every module directory (Core/, Core/protocol/, Core/engine/, Core/state_machine/, Core/hook_handler/, Adapter/, Actions/)
- Used by: Python import system

**Logging Requirements:**
- Log module initialization
- Log file: Corresponding module log file (e.g., `Logs/Overseer-Log-DATE.jsonl` for Core/__init__.py)

---

## Core Layer

### Core/overseer.py

**Job:**
- Entry point for all hook events from CLI frameworks
- Orchestrates between all modules (Adapter, Protocol, Engine, State Machine, Hook Handler)
- Dynamically loads adapter based on config.json
- Cache adapter and supported hooks on first hook execution to temporary file
- Detect config.json changes and invalidate cache when config modified
- Coordinates data flow through the system
- Returns final governance decision to CLI (exit code 0 for allow, 2 for block)
- Logs orchestration events

**NOT Job:**
- Does NOT evaluate policies directly (delegates to Engine)
- Does NOT transform events (delegates to Adapter)
- Does NOT validate canonical structures (delegates to Protocol)
- Does NOT check emergency state (delegates to State Machine)
- Does NOT execute individual hooks (delegates to Hook Handler dispatcher)
- Does NOT manage hook priority ordering (delegates to Hook Handler dispatcher)
- Does NOT aggregate hook results (delegates to Hook Handler dispatcher)
- Does NOT contain CLI-specific logic (Principle 1)

**Key Interfaces:**
- Input: Hook event name (CLI argument), event data (stdin JSON)
- Dependencies: Config/config.json, Adapter/[AppName]-Adapter.py
- Cache file: Temporary cache file for adapter and supported hooks (created on first hook)
- Calls: Adapter.transform_event(), Engine.evaluate(), StateMachine.check_state(), HookHandler.dispatch()
- Output: Governance decision to CLI (stdout JSON, exit code)
- Cache strategy: First hook loads from config.json, subsequent hooks read from cache, invalidate on config change

**Logging Requirements:**
- Log initialization on startup
- Log configuration loaded
- Log adapter loaded
- Log orchestration events (module transitions)
- Log errors with context
- Log file: `Logs/Overseer-Log-DATE.jsonl`

---

### Core/protocol/models.py

**Job:**
- Define canonical data model structures
- Define CanonicalPayload class (action_type, agent_identity, resource, access_level, audit_context, metadata, delegation_chain)
- Define GovernanceDecision class (decision, policy_id, rationale, context, evaluated_rules, timestamp)
- Define ActionType enum (READ, WRITE, DELETE, EXECUTE, MODIFY)
- Define AccessLevel enum (NONE, READ, WRITE, ADMIN)
- Provide extensible metadata field for future growth

**NOT Job:**
- Does NOT validate payloads (delegates to validators.py)
- Does NOT transform data (delegates to transformers.py)
- Does NOT contain CLI-specific structures
- Does NOT depend on adapter implementations
- Does NOT make governance decisions

**Key Interfaces:**
- Used by: Adapter/[AppName]-Adapter.py (returns CanonicalPayload)
- Used by: Engine/evaluator.py (receives CanonicalPayload)
- Used by: All modules (GovernanceDecision)
- Dependencies: Python standard library only (dataclasses, enum, typing)

**Logging Requirements:**
- Log module initialization
- Log when data structures are imported/used
- Log any structural errors or validation issues
- Log file: `Logs/Protocol-Log-DATE.jsonl`

---

### Core/protocol/validators.py

**Job:**
- Validate canonical payload structures
- Check required fields (action_type, agent_identity, resource, access_level, audit_context)
- Validate field types and formats
- Validate enum values (ActionType, AccessLevel)
- Validate data structure integrity
- Return validation result (valid/invalid with reason)

**NOT Job:**
- Does NOT transform data (delegates to transformers.py)
- Does NOT make governance decisions
- Does NOT depend on adapter implementations
- Does NOT contain business logic
- Does NOT modify input data

**Key Interfaces:**
- Input: CanonicalPayload from models.py
- Used by: Core/overseer.py, Hook Handler
- Dependencies: Core/protocol/models.py
- Output: Boolean validation result with reason

**Logging Requirements:**
- Log validation failures with context
- Log validation passes (debug level)
- Log file: `Logs/Protocol-Log-DATE.jsonl`

---

### Core/protocol/transformers.py

**Job:**
- Provide data transformation utilities
- Convert between canonical payload and other formats if needed
- Support protocol version evolution (version compatibility checks)
- Provide helper functions for data normalization
- Handle backward/forward compatibility

**NOT Job:**
- Does NOT contain CLI-specific transformation logic (that's in Adapter)
- Does NOT validate payloads (delegates to validators.py)
- Does NOT make governance decisions
- Does NOT depend on adapter implementations

**Key Interfaces:**
- Used by: All modules that need data transformation
- Dependencies: Core/protocol/models.py
- Helper functions for canonical operations

**Logging Requirements:**
- Log transformation operations
- Log version compatibility checks
- Log file: `Logs/Protocol-Log-DATE.jsonl`

---

### Core/engine/evaluator.py

**Job:**
- Evaluate policies against canonical payload
- Execute policy evaluation logic
- Return deterministic governance decisions (allow/deny/modify)
- Track which policies were evaluated
- Provide decision context and rationale
- Stateless evaluation (no wall-clock, random, or network calls during evaluation)

**NOT Job:**
- Does NOT load policies (delegates to policy_loader.py)
- Does NOT resolve conflicts (delegates to conflict_resolver.py)
- Does NOT transform events (delegates to Adapter/Protocol)
- Does NOT check emergency state (delegates to State Machine)
- Does NOT execute actions (delegates to Actions)
- Does NOT depend on CLI-specific logic

**Key Interfaces:**
- Input: CanonicalPayload from Protocol
- Dependencies: Core/engine/policy_loader.py, Core/engine/conflict_resolver.py
- Used by: Core/overseer.py, Hook Handler
- Output: GovernanceDecision

**Logging Requirements:**
- Log policy evaluation results
- Log which policies were evaluated
- Log decision rationale
- Log file: `Logs/Engine-Log-DATE.jsonl`

---

### Core/engine/conflict_resolver.py

**Job:**
- Resolve conflicts when multiple policies produce different verdicts
- Implement conflict resolution strategies (deny_overrides, allow_overrides, priority_first_match, most_specific_wins)
- Compose multiple policy decisions into final decision
- Apply default deny-wins strategy if no policy matches
- Log conflict resolution process

**NOT Job:**
- Does NOT evaluate policies (delegates to evaluator.py)
- Does NOT load policies (delegates to policy_loader.py)
- Does NOT make governance decisions independently
- Does NOT depend on CLI-specific logic

**Key Interfaces:**
- Input: List of GovernanceDecision from evaluator.py
- Dependencies: Core/protocol/models.py
- Used by: Core/engine/evaluator.py
- Output: Single GovernanceDecision

**Logging Requirements:**
- Log conflicts detected
- Log resolution strategy applied
- Log final composed decision
- Log file: `Logs/Engine-Log-DATE.jsonl`

---

### Core/engine/policy_loader.py

**Job:**
- Load policy definitions from Rules/[PolicyName].json
- Support hot-reload of policies without restart
- Validate policy format before loading
- Provide policy versioning and metadata
- Cache loaded policies for performance
- Detect policy changes via ETag or file watching

**NOT Job:**
- Does NOT evaluate policies (delegates to evaluator.py)
- Does NOT resolve conflicts (delegates to conflict_resolver.py)
- Does NOT make governance decisions
- Does NOT depend on CLI-specific logic

**Key Interfaces:**
- Input: Policy file paths from Rules/ directory
- Dependencies: Rules/[PolicyName].json
- Used by: Core/engine/evaluator.py
- Output: Loaded policy objects

**Logging Requirements:**
- Log policy load events
- Log policy reload events
- Log validation failures
- Log file: `Logs/Engine-Log-DATE.jsonl`

---

### Core/state_machine/base.py

**Job:**
- Define base state machine classes
- Provide state transition validation
- Implement generic state machine logic (transitions, history tracking)
- Define state transition logging pattern
- Provide enum-based state definitions

**NOT Job:**
- Does NOT contain specific state definitions (delegates to emergency.py, workflow.py)
- Does NOT implement business logic
- Does NOT depend on CLI-specific logic

**Key Interfaces:**
- Base class for: emergency.py, workflow.py
- Dependencies: Python standard library only (enum, typing)
- Used by: All state machine implementations

**Logging Requirements:**
- Log state transitions (base pattern)
- Log file: `Logs/StateMachine-Log-DATE.jsonl`

---

### Core/state_machine/emergency.py

**Job:**
- Define emergency control states (NORMAL, HALT_NONCRITICAL, HALT_ALL, EMERGENCY)
- Check emergency state before every action
- Implement state transitions for emergency controls
- Persist emergency state to file-system (survives process restart)
- Log all emergency state changes with authorization
- Support multiple control scopes (global, tenant, agent, tool)

**NOT Job:**
- Does NOT evaluate policies (delegates to Engine)
- Does NOT execute actions (delegates to Actions)
- Does NOT contain workflow logic (delegates to workflow.py)
- Does NOT depend on CLI-specific logic

**Key Interfaces:**
- Used by: Core/overseer.py, Hook Handler
- Dependencies: Core/state_machine/base.py
- State file: `Overseer/Config/emergency_state.json`

**Logging Requirements:**
- Log every state transition
- Log emergency state checks
- Log authorization for state changes
- Log file: `Logs/StateMachine-Log-DATE.jsonl`

---

### Core/state_machine/workflow.py

**Job:**
- Define workflow orchestration states
- Track workflow phase transitions
- Manage session state (if needed)
- Log workflow state changes
- Support iteration limits and evaluation gates

**NOT Job:**
- Does NOT handle emergency controls (delegates to emergency.py)
- Does NOT evaluate policies (delegates to Engine)
- Does NOT execute actions (delegates to Actions)
- Does NOT depend on CLI-specific logic

**Key Interfaces:**
- Used by: Core/overseer.py, subagent orchestration
- Dependencies: Core/state_machine/base.py
- Future enhancement for workflow orchestration

**Logging Requirements:**
- Log workflow state transitions
- Log evaluation gate checks
- Log file: `Logs/StateMachine-Log-DATE.jsonl`

---

### Core/hook_handler/dispatcher.py

**Job:**
- Single dynamic dispatcher for hook coordination
- Parse input once (performance optimization)
- Route to appropriate handlers based on hook type
- Coordinate hook execution with priority ordering
- Check emergency state before hook execution
- Handle per-hook timeout configuration
- Aggregate hook results and return final decision
- Support fail-closed for security, fail-open for observability

**NOT Job:**
- Does NOT contain CLI-specific logic
- Does NOT evaluate policies (delegates to Engine)
- Does NOT check rules (delegates to Rules/)
- Does NOT execute actions (delegates to Actions)
- Does NOT transform events (delegates to Adapter/Protocol)

**Key Interfaces:**
- Input: Hook type, event data
- Dependencies: Core/engine/evaluator.py, Core/state_machine/emergency.py
- Used by: Core/overseer.py
- Routes to: Registered hook handlers
- Output: Aggregated hook results
- Note: Engine.evaluate() and StateMachine.check_state() are called by overseer.py before dispatcher

**Logging Requirements:**
- Log hook dispatch events
- Log priority ordering
- Log timeout behavior
- Log emergency state checks
- Log file: `Logs/HookHandler-Log-DATE.jsonl`

---

## Adapter Layer

### Adapter/base.py

**Job:**
- Define BaseAdapter abstract base class
- Define adapter interface (transform_event, get_capabilities, register_hooks)
- Provide common adapter functionality
- Enforce adapter implementation requirements

**NOT Job:**
- Does NOT contain CLI-specific implementation
- Does NOT make governance decisions
- Does NOT evaluate policies

**Key Interfaces:**
- Abstract methods: transform_event(), get_capabilities(), register_hooks()
- Used by: All adapter implementations (Devin-Adapter, Cursor-Adapter, etc.)

**Logging Requirements:**
- Log base class initialization
- Log when adapter interface methods are called
- Log file: `Logs/Adapter-Log-DATE.jsonl`

---

### Adapter/[AppName]-Adapter.py (e.g., Devin-Adapter.py)

**Job:**
- CLI-specific event transformation
- Transform CLI-specific event format to CanonicalPayload
- Declare capabilities (supported hooks, event types, data schemas)
- Provide CLI-specific transformation logic to Protocol
- Implement BaseAdapter interface
- Log adapter-specific events

**NOT Job:**
- Does NOT evaluate policies (delegates to Engine)
- Does NOT check emergency state (delegates to State Machine)
- Does NOT execute actions (delegates to Actions)
- Does NOT contain governance logic
- Does NOT assume other CLI frameworks exist

**Key Interfaces:**
- Implements: BaseAdapter
- Input: CLI-specific event format
- Output: CanonicalPayload
- Dependencies: Core/protocol/models.py

**Logging Requirements:**
- Log adapter initialization
- Log transformation events
- Log capability discovery
- Log file: `Logs/Adapter-Log-DATE.jsonl`

---

## Configuration Layer

### Config/config.json

**Job:**
- Store Overseer configuration
- Specify which adapter to load (adapter selection)
- Define adapter-specific settings
- Define governance settings (default_mode, conflict_resolution, emergency_halt)
- Define logging settings (level, format, retention)
- Define hook timeout settings

**NOT Job:**
- Does NOT contain governance logic
- Does NOT contain policy definitions (those are in Rules/)
- Does NOT execute code

**Key Interfaces:**
- Read by: Core/overseer.py
- Used by: All modules for configuration

**Logging Requirements:**
- None (configuration file only, overseer.py logs when loaded)

---

## Actions Layer

### Actions/base.py

**Job:**
- Define BaseAction abstract base class
- Define action interface (execute)
- Provide common action functionality
- Enforce action implementation requirements
- Log base class initialization and method calls

**NOT Job:**
- Does NOT contain policy-specific implementation
- Does NOT evaluate rules (that's in Hook Handler checking Rules/)

**Key Interfaces:**
- Abstract methods: execute()
- Used by: All action implementations

**Logging Requirements:**
- Log base class initialization
- Log when action interface methods are called
- Log file: `Logs/Actions-Log-DATE.jsonl`

---

### Actions/[PolicyName].py (e.g., file-deletion-protection.py)

**Job:**
- Execute policy-specific logic when rule is triggered
- Implement governance actions (Block, Warn, Direct agent)
- Load corresponding policy definition from Rules/[PolicyName].json
- Return action result (block/warn/direct with reason)
- Log action execution

**NOT Job:**
- Does NOT check if rule is triggered (that's in Hook Handler)
- Does NOT evaluate policies (that's in Engine)
- Does NOT transform events (that's in Adapter/Protocol)
- Does NOT contain CLI-specific logic

**Key Interfaces:**
- Implements: BaseAction
- Input: Context from Hook Handler
- Dependencies: Rules/[PolicyName].json
- Used by: Core/hook_handler/dispatcher.py

**Logging Requirements:**
- Log action execution
- Log action result
- Log file: `Logs/Actions-Log-DATE.jsonl`

---

### Actions/Meta-Actions/[MetaRuleName].py (e.g., policy-format-validator.py)

**Job:**
- Execute meta rule enforcement logic
- Validate policy format, structure, and conflicts
- Prevent contradictory policies from being loaded
- Enforce policy quality programmatically
- Log meta rule enforcement results

**NOT Job:**
- Does NOT evaluate user policies (that's in Engine)
- Does NOT execute user actions (that's in Actions/[PolicyName].py)
- Does NOT contain CLI-specific logic

**Key Interfaces:**
- Implements: BaseAction
- Input: Policy definitions for validation
- Dependencies: Rules/Meta-Rules/[MetaRuleName].json
- Used by: Core/engine/policy_loader.py

**Logging Requirements:**
- Log meta rule validation
- Log policy format violations
- Log conflict detection
- Log file: `Logs/Actions-Log-DATE.jsonl`

---

## Rules Layer

### Rules/[PolicyName].json (e.g., file-deletion-protection.json)

**Job:**
- Define declarative policy rules
- Specify rule conditions, actions, and rationales
- Define protected paths, resource types, etc.
- Versioned policy definitions
- Human-readable and machine-processable

**NOT Job:**
- Does NOT contain execution logic (that's in Actions/)
- Does NOT contain transformation logic
- Does NOT execute code

**Key Interfaces:**
- Read by: Actions/[PolicyName].py
- Read by: Core/engine/policy_loader.py

**Logging Requirements:**
- None (data file only, loader logs when loaded)

---

### Rules/Meta-Rules/[MetaRuleName].json (e.g., policy-format-validator.json)

**Job:**
- Define meta rule definitions for policy governance
- Specify policy format requirements
- Define conflict detection rules
- Define policy structure validation
- Human-readable and machine-processable

**NOT Job:**
- Does NOT contain execution logic (that's in Actions/Meta-Actions/)
- Does NOT contain user policy definitions

**Key Interfaces:**
- Read by: Actions/Meta-Actions/[MetaRuleName].py
- Read by: Core/engine/policy_loader.py

**Logging Requirements:**
- None (data file only, loader logs when loaded)

---

## Logging Layer

### Logs/ (Directory)

**Job:**
- Store layer-specific JSONL log files
- Provide structured logging for all modules
- Enable audit trail reconstruction
- Support tamper-evident logging

**NOT Job:**
- Does NOT contain logic (log files only)

**Log Files:**
- `Logs/Overseer-Log-DATE.jsonl` - Orchestration events
- `Logs/Protocol-Log-DATE.jsonl` - Protocol validation/transformation
- `Logs/Engine-Log-DATE.jsonl` - Policy evaluation
- `Logs/StateMachine-Log-DATE.jsonl` - State transitions
- `Logs/HookHandler-Log-DATE.jsonl` - Hook dispatch
- `Logs/Adapter-Log-DATE.jsonl` - Adapter events
- `Logs/Actions-Log-DATE.jsonl` - Action execution

---

## Tests Layer

### Tests/ (Directory)

**Job:**
- Test suite for all modules
- Unit tests for individual components
- Integration tests for end-to-end flows
- Performance tests for latency requirements
- Security tests for validation and fail-closed behavior

**NOT Job:**
- Does NOT contain production code

**Test Files:**
- `Tests/test_overseer.py` - Core tests
- `Tests/test_adapter.py` - Adapter tests
- `Tests/test_protocol.py` - Protocol tests
- `Tests/test_engine.py` - Engine tests
- `Tests/test_state_machine.py` - State machine tests
- `Tests/test_hook_handler.py` - Hook handler tests
- `Tests/test_actions.py` - Actions tests

---

## Summary of Module Independence

Each module has a single, well-defined responsibility:
- **Overseer**: Orchestration and entry point
- **Protocol**: Data structures and validation
- **Engine**: Policy evaluation
- **State Machine**: Governance state
- **Hook Handler**: Hook coordination
- **Adapter**: CLI-specific transformation
- **Actions**: Policy execution
- **Rules**: Declarative policy definitions

This modular architecture enables:
- Independent development and testing
- Clear separation of concerns
- Easy addition of new adapters
- Zero CLI-specific assumptions in core (Principle 1)
- Fail-closed enforcement (Principle 5)
