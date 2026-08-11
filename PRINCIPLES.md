# Overseer Framework Architecture Principles

**Version**: 1.0.0  
**Date**: 2026-08-10  
**Purpose**: Define the fundamental architectural principles for true agnosticism in the Overseer Framework

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

When Overseer blocks an action, it creates a bypass menu for the user, allowing them to override the block when needed.

**Interaction Model**

Overseer uses a hybrid approach: automatic enforcement with interactive options for violations. Most decisions are enforced automatically, but users can interact when needed.

**Policy Management**

Users create rules as YAML files with accompanying Python files under the same name. These rules run when hooks are triggered. Examples include running ruff on Python files or forcing frontmatter on .md files.

**Rule Execution**

Rules run synchronously when hooks trigger. Blocks create bypass menus, while other hooks (like post-tool) check files for encoding and run tools like ruff.

**File System Structure**

- `/rules` directory in `/Overseer` contains user rules (initially empty, populated by user)
- Adapters located in `Overseer/Adapters`, named as [ApplicationName]-Adapter.py (e.g., Devin-Adapter.py)
- Python files accompanying rules are in `Overseer/Actions`
- Meta actions in `Overseer/Actions` enforce meta rules for the system itself

**Meta Rules and Actions**

Meta rules serve both purposes:
- Govern how users create their own rules (format, structure, naming)
- Govern the Overseer system itself (hooks, logging, configuration)

Meta actions enforce the meta rules for system compliance and self-governance.

---

## Principle 1: True Agnosticism

**Definition**: The core framework must make ZERO functional assumptions about adapters or environment. The framework should not know, care about, or depend on specific adapter capabilities, CLI-specific behaviors, or tool implementations. However, framework conventions exist for organization and consistency.

**Desired State**:

### 1.1 Zero Hardcoded Event Types
- **Target Behavior**: Framework accepts ANY event type that adapters provide
- **Implementation**: Event types are dynamically registered by adapters, not predefined by framework
- **Example**: If an adapter provides "CustomEventA" and another provides "CustomEventB", framework accepts both without modification
- **Benefit**: Infinite extensibility without framework changes

### 1.2 Framework Conventions for Adapters
- **Target Behavior**: Framework defines adapter location and naming conventions for consistency
- **Implementation**: Adapters located in Overseer/Adapters, named as [ApplicationName]-Adapter.py
- **Example**: Devin-Adapter.py, Cursor-Adapter.py, Claude-Adapter.py
- **Benefit**: Consistent adapter organization while maintaining functional agnosticism

### 1.3 Zero CLI-Specific Assumptions
- **Target Behavior**: Framework is completely CLI-agnostic in code and documentation
- **Implementation**: No references to specific tools, frameworks, or environments
- **Example**: Documentation refers to "adapters" generically, not specific CLI tools
- **Benefit**: Framework works with any tool that implements the adapter contract

### 1.4 Dynamic Adaptation
- **Target Behavior**: Framework adapts to whatever adapters provide
- **Implementation**: Framework discovers adapter capabilities at runtime
- **Example**: Framework learns what events an adapter supports by querying the adapter
- **Benefit**: Self-discovering system that requires no manual configuration

### 1.5 Environment Independence
- **Target Behavior**: Core layers work in ANY environment without modification
- **Implementation**: Core layers are completely environment-independent
- **Example**: The same framework works whether connected to CLI, API, web interface, or any other system
- **Benefit**: Universal applicability across different deployment scenarios

**Success Criteria**:
- Protocol layer contains zero event type definitions
- Overseer layer contains zero adapter-specific logic
- Framework works with ANY adapter that implements the contract
- Adding a new adapter requires ZERO framework code changes
- Documentation contains zero tool-specific references

---

## Principle 2: Overseer-Centric Architecture

**Definition**: Hooks point to overseer.py as the primary integration point. overseer.py is responsible for using adapters to determine available functionality and coordinate governance decisions.

**Desired State**:

### 2.1 Overseer as Integration Point
- **Target Behavior**: Hooks point to overseer.py as the primary integration point
- **Implementation**: overseer.py receives hook events and coordinates with adapters
- **Example**: PreToolUse hook calls overseer.py, which then uses adapters to determine functionality
- **Benefit**: Single integration point for all hooks, centralized governance coordination

### 2.2 Adapter Functionality Discovery
- **Target Behavior**: overseer.py uses adapters to determine available functionality
- **Implementation**: overseer.py queries adapters for capabilities and coordinates decisions
- **Example**: overseer.py asks Devin-Adapter what tools it supports, then applies governance
- **Benefit**: overseer.py coordinates governance while adapters provide application-specific knowledge

### 2.3 Centralized Governance Coordination
- **Target Behavior**: overseer.py coordinates all governance decisions
- **Implementation**: overseer.py integrates with rule system, adapters, and hooks
- **Example**: overseer.py receives hook event, consults rules, uses adapter context, makes decision
- **Benefit**: Consistent governance logic across all hooks and adapters

**Success Criteria**:
- Hooks point to overseer.py as single integration point
- overseer.py coordinates with adapters to determine functionality
- Governance decisions are centralized in overseer.py
- Adapters provide application-specific knowledge to overseer.py
- overseer.py integrates with rule system, adapters, and hooks consistently

---

## Principle 3: Config-Driven Adapter Selection

**Definition**: A config file tells overseer which adapter to use. Events and hooks are based on the adapter selection in the config file. Rules are generic and cross-compatible, linked to different hooks based on adapter.

**Desired State**:

### 3.1 Config-Based Adapter Selection
- **Target Behavior**: Config file specifies which adapter to use
- **Implementation**: overseer.py reads config to determine active adapter
- **Example**: config.json specifies "adapter": "Devin-Adapter.py"
- **Benefit**: Easy switching between different AI agent frameworks

### 3.2 Adapter-Specific Hook Mapping
- **Target Behavior**: Hooks are determined by the selected adapter
- **Implementation**: Adapter defines which hooks it supports, overseer maps rules accordingly
- **Example**: Devin-Adapter supports PreToolUse, PostToolUse; Cursor-Adapter supports different hooks
- **Benefit**: Hook system adapts to adapter capabilities

### 3.3 Generic Cross-Compatible Rules
- **Target Behavior**: Rules are generic and work across different adapters
- **Implementation**: Rules define governance logic that can be applied to multiple hook types
- **Example**: "Prevent file deletion" rule works for any adapter's file operations
- **Benefit**: Write rules once, apply to any adapter

### 3.4 Rule-to-Hook Linking
- **Target Behavior**: Rules are linked to hooks based on adapter configuration
- **Implementation**: Config maps rules to adapter-specific hooks
- **Example**: Security rule linked to Devin-Adapter's PreToolUse hook
- **Benefit**: Flexible rule application across different adapters

**Success Criteria**:
- Config file specifies which adapter to use
- overseer.py reads config to determine active adapter
- Hooks are determined by selected adapter
- Rules are generic and cross-compatible
- Rules are linked to hooks based on adapter configuration

---

## Principle 4: Zero-Assumption Framework

**Definition**: The core framework makes no assumptions about the environment, adapters, or event structures. It provides generic mechanisms that adapt to whatever is provided.

**Desired State**:

### 4.1 Generic Container Pattern
- **Target Behavior**: Framework is a generic container
- **Implementation**: Framework provides generic interfaces that work with any data structure
- **Example**: Framework provides "process data" interface, not "process tool use" interface
- **Benefit**: Universal applicability across different use cases

### 4.2 Metadata-Driven Processing
- **Target Behavior**: Framework processes based on metadata, not field names
- **Implementation**: Framework uses metadata to determine how to process events
- **Example**: Framework checks event metadata for "type" and "handler" fields, not hardcoded field names
- **Benefit**: Structure-agnostic processing

### 4.3 Configuration-Driven Behavior
- **Target Behavior**: Framework behavior is driven by configuration
- **Implementation**: All framework behavior parameters are externalized to config
- **Example**: Adapter discovery patterns, event routing rules, logging behavior all configurable
- **Benefit**: Behavior changes without code modifications

### 4.4 Extensibility Without Modification
- **Target Behavior**: Framework is extensible through configuration and plugins
- **Implementation**: New capabilities added through config, not code
- **Example**: New adapter types, event processors, or routing rules added via config
- **Benefit**: Infinite extensibility without touching framework code

**Success Criteria**:
- Framework code contains zero business logic for specific use cases
- All behavior is configurable
- Framework works with any data structure through metadata
- New capabilities added without code changes
- Framework can be extended through configuration only

---

## Principle 5: Plugin SDK Pattern

**Definition**: Adapters compile against a Plugin SDK, not against framework internals. The SDK provides a stable interface that isolates adapters from framework implementation details.

**Desired State**:

### 5.1 Stable Plugin Interface
- **Target Behavior**: Adapters depend only on Plugin SDK
- **Implementation**: Create Plugin SDK with stable, versioned interface
- **Example**: Adapters import from `overseer_sdk`, not framework internals
- **Benefit**: Adapter development independent of framework implementation

### 5.2 Framework Isolation
- **Target Behavior**: Adapters are isolated from framework implementation
- **Implementation**: Adapters interact only through SDK, no direct framework access
- **Example**: Adapters use SDK methods, never import framework modules directly
- **Benefit**: Framework internals can change without breaking adapters

### 5.3 Version Compatibility
- **Target Behavior**: SDK maintains backward compatibility
- **Implementation**: SDK versioning, deprecation policies, migration guides
- **Example**: Framework v2.0 might change internals, but SDK v1.x still works for existing adapters
- **Benefit**: Adapter stability across framework evolution

### 5.4 Self-Contained Development
- **Target Behavior**: Adapters are developable with only SDK
- **Implementation**: SDK provides mock/stub framework for adapter development
- **Example**: Developers can write adapters using only SDK, no need to run full framework
- **Benefit**: Simplified adapter development and testing

**Success Criteria**:
- Adapters depend only on SDK, not framework internals
- SDK provides complete interface for adapter development
- Framework changes don't break existing adapters
- Adapters can be developed and tested with SDK only
- SDK versioning is independent of framework versioning

---

## Principle 6: Capability-Based Ports

**Definition**: Framework and adapters communicate through capability-based ports with open string identifiers, not hardcoded type definitions. The registry boundary uses open strings that can be extended without modification.

**Desired State**:

### 6.1 Open String Identifiers
- **Target Behavior**: All identifiers are open strings
- **Implementation**: No predefined type lists, any string is valid
- **Example**: "tool_use", "custom_event", "anything" - all valid event type identifiers
- **Benefit**: Infinite identifier space without framework changes

### 6.2 Dynamic Capability Discovery
- **Target Behavior**: Framework discovers capabilities dynamically
- **Implementation**: Adapters declare capabilities, framework queries and adapts
- **Example**: Adapter declares "I can handle X, Y, Z", framework routes accordingly
- **Benefit**: Self-discovering capability system

### 6.3 Capability-Based Routing
- **Target Behavior**: Routing is based on declared capabilities
- **Implementation**: Framework routes events to adapters that declare capability
- **Example**: Event "X" routes to any adapter that declares capability for "X"
- **Benefit**: Dynamic routing based on actual capabilities

### 6.4 Extensible Capability Set
- **Target Behavior**: Capability set is infinitely extensible
- **Implementation**: No predefined capability lists, entirely dynamic
- **Example**: New capabilities added by adapters without framework modification
- **Benefit**: Unlimited extensibility without framework changes

**Success Criteria**:
- No hardcoded capability or event type lists
- Any string identifier is valid
- Framework discovers capabilities at runtime
- New capabilities added without framework changes
- Routing is entirely capability-based

---

## Principle 7: Layer Independence

**Definition**: Each layer must be completely independent with zero coupling to other layers. Dependencies must flow in one direction only, and layers must be replaceable without affecting others.

**Desired State**:

### 7.1 Unidirectional Dependencies
- **Target Behavior**: Dependencies flow in one direction only
- **Implementation**: Define clear dependency hierarchy and enforce it
- **Example**: Adapter → SDK → Framework, never reverse
- **Benefit**: Clean dependency graph with no circular dependencies

### 7.2 Replaceable Layers
- **Target Behavior**: Each layer is independently replaceable
- **Implementation**: Layers communicate through stable interfaces only
- **Example**: SDK could be completely rewritten without breaking adapters
- **Benefit**: System evolution without breaking changes

### 7.3 Zero Cross-Layer Imports
- **Target Behavior**: Layers communicate through interfaces only
- **Implementation**: No direct imports between layers, only interface imports
- **Example**: Adapter imports SDK interface, not framework implementation
- **Benefit**: Layer isolation and loose coupling

### 7.4 Independent Testing
- **Target Behavior**: Each layer is independently testable
- **Implementation**: Layers provide mocks/stubs for dependencies
- **Example**: SDK can be tested without framework, adapters tested without SDK implementation
- **Benefit**: Parallel development and testing

**Success Criteria**:
- Clear dependency hierarchy with no circular dependencies
- Each layer can be replaced without affecting others
- Layers communicate only through stable interfaces
- Each layer can be tested independently
- Dependencies flow in one direction only

---

## Principle 8: Extreme Modularization

**Definition**: Each file must be completely independent with minimal imports. Every file should have extensive logging functions to track everything it does. Connections between files should be minimized to only what's absolutely necessary.

**Desired State**:

### 8.1 File Independence
- **Target Behavior**: Each file is completely self-contained
- **Implementation**: Files import only what they absolutely need, nothing more
- **Example**: A file should work in isolation with only its direct dependencies
- **Benefit**: Files can be understood, tested, and modified independently

### 8.2 Minimal Import Surface
- **Target Behavior**: Each file has the smallest possible import surface
- **Implementation**: Import only directly needed items, avoid wildcard imports
- **Example**: Import specific functions/classes, not entire modules when possible
- **Benefit**: Clear dependency graph, reduced coupling

### 8.3 Self-Contained Functionality
- **Target Behavior**: Each file contains all the functionality it needs
- **Implementation**: Files should not rely on helper functions in other files
- **Example**: If a file needs logging, it has its own logging function
- **Benefit**: Files can be moved, copied, or reused without breaking

### 8.4 Explicit Dependencies
- **Target Behavior**: All dependencies are explicit and documented
- **Implementation**: No implicit dependencies through shared state or side effects
- **Example**: Dependencies are declared in imports, not assumed through environment
- **Benefit**: Clear understanding of what each file needs

**Success Criteria**:
- Each file can be understood without reading other files
- Import statements are minimal and specific
- Files can be moved without breaking dependencies
- No implicit dependencies between files
- Each file contains its own utility functions

---

## Principle 9: Comprehensive Logging

**Definition**: Each file must have extensive, extremely verbose logging functions that track everything the file does. Logging should be comprehensive enough to reconstruct the complete execution flow of any operation.

**Desired State**:

### 9.1 File-Specific Logging
- **Target Behavior**: Each file has its own comprehensive logging function
- **Implementation**: Each file implements its own logging function with layer-specific log files
- **Example**: protocol.py logs to Protocol-Log-DATE.jsonl, overseer.py to Overseer-Log-DATE.jsonl
- **Benefit**: Complete visibility into each file's execution

### 9.2 Extremely Verbose Logging
- **Target Behavior**: Log every significant operation, state change, and decision point
- **Implementation**: Log function entry/exit, parameter values, decision logic, errors, state changes
- **Example**: Log "Entering function X with parameters: {...}", "Decision made: Y because Z", "Function X returned: {...}"
- **Benefit**: Complete execution trace for debugging and monitoring

### 9.3 Structured Log Format
- **Target Behavior**: All logs follow consistent structured format
- **Implementation**: Use JSONL format with consistent fields: File, component, Time, trace_id, data
- **Example**: `{"File": "filename.py", "component": "function_name", "Time": "ISO8601", "trace_id": "uuid", "data": {...}}`
- **Benefit**: Machine-readable logs for analysis and monitoring

### 9.4 Silent Failure Pattern
- **Target Behavior**: Logging failures don't crash the system
- **Implementation**: Multi-layer fallback: try logging, try stderr, finally silent fail
- **Example**: Try file logging, on fail try stderr, on fail silently continue
- **Benefit**: System continues working even if logging fails

**Success Criteria**:
- Every file has its own logging function
- All significant operations are logged
- Logs are extremely verbose and detailed
- Logging failures don't crash the system
- Log format is consistent across all files

---

## Principle 10: KISS Principle (Keep It Simple, Stupid)

**Definition**: Favor simple solutions over complex ones. Build the simplest solution that correctly solves the problem. Avoid complexity unless genuinely necessary.

**Desired State**:

### 10.1 Simplicity Over Complexity
- **Target Behavior**: Choose simple solutions whenever possible
- **Implementation**: Evaluate complexity vs. benefit, prefer simpler approaches
- **Example**: Use straightforward data structures instead of complex abstractions
- **Benefit**: Easier to understand, maintain, and debug

### 10.2 Small Focused Functions
- **Target Behavior**: Functions and classes are small and focused
- **Implementation**: Each function does one thing well, keep under 50 lines when possible
- **Example**: Split complex operations into multiple smaller functions
- **Benefit**: Easier to test, understand, and reuse

### 10.3 Remove Dead Code
- **Target Behavior**: Eliminate unused code and features
- **Implementation**: Regularly remove unused imports, functions, and code
- **Example**: Delete commented-out code, rely on version control instead
- **Benefit**: Cleaner codebase, reduced cognitive load

### 10.4 YAGNI Compliance
- **Target Behavior**: Don't implement features for hypothetical futures
- **Implementation**: Build what you need now, not what you might need later
- **Example**: Avoid "just in case" functionality
- **Benefit**: Focus on actual requirements, avoid over-engineering

**Success Criteria**:
- Solutions are as simple as possible while solving the problem
- Functions are small and focused
- No dead or unused code
- No premature abstractions
- Features are implemented based on actual needs

---

## Principle 11: SOLID Principles

**Definition**: Follow SOLID principles for object-oriented design to create maintainable, scalable software.

**Desired State**:

### 11.1 Single Responsibility Principle
- **Target Behavior**: Each class has only one reason to change
- **Implementation**: Classes should have one primary responsibility
- **Example**: StandardEvent handles event encapsulation only, not conversion or validation
- **Benefit**: Easier to understand, test, and modify

### 11.2 Open/Closed Principle
- **Target Behavior**: Classes are extensible without requiring modification
- **Implementation**: Use interfaces and abstractions, allow extension through composition
- **Example**: New adapters can be added without modifying core framework code
- **Benefit**: System can grow without breaking existing code

### 11.3 Liskov Substitution Principle
- **Target Behavior**: Subtypes must be substitutable for their base types
- **Implementation**: Ensure derived classes honor base class contracts
- **Example**: Any adapter can be used wherever BaseAdapter is expected
- **Benefit**: Polymorphism works correctly, no surprising behavior

### 11.4 Interface Segregation Principle
- **Target Behavior**: Client-specific, fine-grained interfaces
- **Implementation**: Create focused interfaces rather than large general-purpose ones
- **Example**: Separate interfaces for different adapter capabilities
- **Benefit**: Clients depend only on what they actually use

### 11.5 Dependency Inversion Principle
- **Target Behavior**: Depend on abstractions, not concretions
- **Implementation**: High-level modules depend on abstractions, low-level modules implement them
- **Example**: Overseer depends on BaseAdapter interface, not specific adapter implementations
- **Benefit**: Loose coupling, easier to change implementations

**Success Criteria**:
- Each class has one clear responsibility
- New functionality can be added without modifying existing code
- Subtypes can be substituted for their base types
- Interfaces are focused and client-specific
- Dependencies flow from high-level to low-level abstractions

---

## Principle 12: Component Modularity

**Definition**: Components must be loosely coupled with clear contracts, single responsibilities, and independent replaceability.

**Desired State**:

### 12.1 Loose Coupling
- **Target Behavior**: Components have minimal dependencies on other components
- **Implementation**: Communicate through well-defined interfaces rather than shared internals
- **Example**: Components use interfaces to communicate, not direct class references
- **Benefit**: Changes to one component don't cascade to others

### 12.2 Clear Contracts
- **Target Behavior**: Each component defines explicit contracts
- **Implementation**: Define operations, guarantees, and error behavior explicitly
- **Example**: Interfaces document what methods do, what they return, and what errors they raise
- **Benefit**: Clear expectations and predictable behavior

### 12.3 Single Responsibility
- **Target Behavior**: Each component owns a specific slice of behavior and data
- **Implementation**: Clear boundaries around component responsibilities
- **Example**: Protocol layer handles schema definition only, not event processing
- **Benefit**: Focused, maintainable components

### 12.4 Independent Replaceability
- **Target Behavior**: Components are independently replaceable and upgradeable
- **Implementation**: Components preserve existing contracts during upgrades
- **Example**: SDK can be upgraded without breaking adapters
- **Benefit**: System can evolve without coordination between components

**Success Criteria**:
- Components have minimal dependencies
- Clear contracts between components
- Each component has a single clear responsibility
- Components can be replaced independently
- Changes don't cascade between components

---

## Success Metrics

**Framework achieves true agnosticism when**:
1. Adding a new adapter requires ZERO framework code changes
2. Framework works with ANY adapter that implements the SDK contract
3. Adding a new event type requires ZERO framework code changes
4. Framework code contains ZERO tool-specific references
5. Each layer can be replaced without affecting others
6. Adapters can be developed with only the SDK
7. All identifiers are open strings, no hardcoded types
8. Framework behavior is entirely configuration-driven

**Framework achieves extreme modularization when**:
1. Each file can be understood without reading other files
2. Import statements are minimal and specific
3. Files can be moved without breaking dependencies
4. No implicit dependencies between files
5. Each file contains its own utility functions

**Framework achieves comprehensive logging when**:
1. Every file has its own logging function
2. All significant operations are logged
3. Logs are extremely verbose and detailed
4. Logging failures don't crash the system
5. Log format is consistent across all files

**Framework achieves simplicity when**:
1. Solutions are as simple as possible while solving the problem
2. Functions are small and focused
3. No dead or unused code
4. No premature abstractions
5. Features are implemented based on actual needs

**Framework achieves hook performance when**:
1. Hook execution <0.1ms p50 for allow path
2. Hook execution <0.5ms p99 for deny path
3. Linear scaling with concurrent load
4. Minimal memory footprint
5. <1% CPU overhead for typical workloads

**Framework achieves hook reliability when**:
1. Hook failures never crash the governed system
2. Hook failures are isolated to specific components
3. Hook behavior is deterministic and reproducible
4. Circuit breaker prevents cascading failures
5. System degrades gracefully under failure

**Framework achieves scalability when**:
1. Works for hobbyists with minimal setup
2. Scales to enterprise workloads
3. Provides configurable strictness levels
4. Works in resource-constrained environments
5. Supports multiple deployment scenarios

---

## Principle 13: Rule-Based Governance System

**Definition**: Governance is implemented through YAML rule files with accompanying Python execution files. Users define policies as YAML files, and Python files execute the logic when hooks are triggered.

**Desired State**:

### 13.1 YAML Rule Definition
- **Target Behavior**: Users define governance rules in YAML files
- **Implementation**: YAML files specify rule conditions, actions, and metadata
- **Example**: rule.yaml defines "prevent deleting important files" with Python execution logic
- **Benefit**: Human-readable policy definition, easy to version control

### 13.2 Python Execution Files
- **Target Behavior**: Each YAML rule has a corresponding Python file with execution logic
- **Implementation**: Python files execute when hooks trigger, implementing rule logic
- **Example**: rule.yaml has rule.py that checks file importance and blocks deletion
- **Benefit**: Complex logic in Python, simple configuration in YAML

### 13.3 Synchronous Hook Triggering
- **Target Behavior**: Rules run synchronously when hooks trigger
- **Implementation**: Hook calls rule execution immediately, blocking tool execution until complete
- **Example**: PreToolUse hook triggers rule.py synchronously before tool executes
- **Benefit**: Governance decisions happen before tool execution

### 13.4 Rule File Location
- **Target Behavior**: User rules live in /rules directory in /Overseer
- **Implementation**: /rules directory initially empty, populated by user with their rules
- **Example**: User adds security_rules.yaml and security_rules.py to /rules/
- **Benefit**: Clear separation of system rules and user rules

**Success Criteria**:
- Users can define rules in YAML format
- Python files implement rule execution logic
- Rules run synchronously on hook trigger
- User rules stored in /rules directory
- YAML and Python files follow naming convention

---

## Principle 14: Meta Rules and Actions

**Definition**: The system includes meta rules that govern both user rule creation and system behavior. Meta actions enforce meta rules for system compliance and self-governance.

**Desired State**:

### 14.1 Meta Rule Governance
- **Target Behavior**: Meta rules govern how users create their own rules
- **Implementation**: Meta rules define rule format, structure, naming conventions
- **Example**: Meta rules require rule.yaml to have specific required fields
- **Benefit**: Consistent rule structure across user rules

### 14.2 System Self-Governance
- **Target Behavior**: Meta rules govern the Overseer system itself
- **Implementation**: Meta rules define system behavior for hooks, logging, configuration
- **Example**: Meta rules ensure all system hooks follow logging principles
- **Benefit**: System follows its own architectural principles

### 14.3 Meta Actions Execution
- **Target Behavior**: Meta actions in Overseer/Actions enforce meta rules
- **Implementation**: Meta actions validate system compliance during operation
- **Example**: Meta action checks that new rule files follow naming convention
- **Benefit**: System self-enforces architectural compliance

### 14.4 Dual Purpose Meta Rules
- **Target Behavior**: Meta rules serve both user rule governance and system governance
- **Implementation**: Meta rules apply to both user-created rules and system components
- **Example**: Same meta rule enforces logging format for user rules and system hooks
- **Benefit**: Consistent governance across entire system

**Success Criteria**:
- Meta rules govern user rule creation
- Meta rules govern system behavior
- Meta actions enforce meta rules
- Meta rules have dual purpose
- System self-governs using meta rules

---

## Principle 15: Bypass Menu Interaction

**Definition**: When Overseer blocks an action, it creates a bypass menu for the user. This provides flexibility while maintaining governance control.

**Desired State**:

### 15.1 Bypass Menu Creation
- **Target Behavior**: Blocks create interactive bypass menus for users
- **Implementation**: When a rule blocks an action, present user with override options
- **Example**: Block displays "Allow this action", "Allow for this session", "Permanently allow"
- **Benefit**: Users maintain control while governance provides safety

### 15.2 User Override Options
- **Target Behavior**: Users can override blocks with different scope
- **Implementation**: Bypass menu offers temporary, session, or permanent override options
- **Example**: User can choose to allow once, allow for session, or permanently allow
- **Benefit**: Flexibility for edge cases and urgent situations

### 15.3 Override Logging
- **Target Behavior**: All bypass actions are logged with justification
- **Implementation**: Bypass menu actions logged with user ID, reason, and scope
- **Example**: Override logged as "User X overrode block Y with reason Z"
- **Benefit**: Audit trail for override decisions

### 15.4 Configurable Bypass Behavior
- **Target Behavior**: Bypass menu behavior is configurable
- **Implementation**: Configuration controls when bypass menu appears and what options are available
- **Example**: Enterprise can disable bypass menu for critical environments
- **Benefit**: Strictness levels configurable for different use cases

**Success Criteria**:
- Blocks create bypass menus for users
- Multiple override scope options available
- All bypass actions are logged
- Bypass behavior is configurable
- Override decisions are auditable

---

## Principle 16: Action Organization

**Definition**: Python execution files are organized in Overseer/Actions directory, with meta actions for system governance and regular actions for user rules.

**Desired State**:

### 16.1 Actions Directory Structure
- **Target Behavior**: Python execution files live in Overseer/Actions
- **Implementation**: Both meta actions and regular actions stored in Overseer/Actions
- **Example**: security_check.py and encoding_check.py in Overseer/Actions
- **Benefit**: Clear separation of system logic and user rule logic

### 16.2 Meta Actions Isolation
- **Target Behavior**: Meta actions for system governance are clearly identified
- **Implementation**: Meta actions prefixed or organized separately in Overseer/Actions
- **Example**: meta_rule_validator.py clearly marked as meta action
- **Benefit**: Clear distinction between system and user actions

### 16.3 Action Naming Convention
- **Target Behavior**: Actions follow naming convention matching their YAML files
- **Implementation**: rule.yaml has rule.py in Overseer/Actions
- **Example**: encoding_rules.yaml has encoding_rules.py
- **Benefit**: Clear mapping between YAML rules and Python actions

### 16.4 Action Registration
- **Target Behavior**: Actions are registered with the system when files are added
- **Implementation**: System discovers new actions in Overseer/Actions and registers them
- **Example**: Adding new .py file to Overseer/Actions automatically registers it
- **Benefit**: Easy to add new actions without configuration changes

**Success Criteria**:
- Actions stored in Overseer/Actions directory
- Meta actions clearly identified
- Actions follow naming convention with YAML files
- New actions automatically registered
- Clear separation of system and user actions

---

## Principle 17: Small Reusable Kernel

**Definition**: Governance should be a small reusable kernel that work embeds, not a platform that work runs on. The kernel should be minimal, portable, and embeddable in any environment.

**Desired State**:

### 13.1 Kernel Minimality
- **Target Behavior**: Core governance kernel is as small as possible
- **Implementation**: Only essential governance logic in kernel, everything else in adapters
- **Example**: Kernel only contains event routing and policy enforcement, not domain-specific logic
- **Benefit**: Easy to embed, understand, and maintain

### 13.2 Embeddability
- **Target Behavior**: Kernel can be embedded in any environment
- **Implementation**: Zero runtime dependencies, stdlib-only when possible
- **Example**: Kernel can be embedded in CLI, web service, or any application
- **Benefit**: Universal applicability across deployment scenarios

### 13.3 Domain Neutrality
- **Target Behavior**: Kernel contains no domain-specific logic
- **Implementation**: All domain-specific logic lives in adapters
- **Example**: Kernel doesn't know about "Devin" or "Claude", only about "events" and "policies"
- **Benefit**: Same kernel can govern different domains

### 13.4 Portable Governance
- **Target Behavior**: Governance decisions are portable and verifiable
- **Implementation**: Decisions are self-contained and can be verified independently
- **Example**: Governance decisions can be audited without access to the original system
- **Benefit**: Compliance verification and auditability

**Success Criteria**:
- Kernel has minimal code footprint
- Kernel can be embedded without dependencies
- Kernel contains zero domain-specific logic
- Governance decisions are portable and verifiable
- Kernel works in any environment

---

## Principle 18: Hook Performance and Efficiency

**Definition**: Hook-based governance must add minimal performance overhead. Hooks are called synchronously during execution, so they must be extremely fast and efficient.

**Desired State**:

### 14.1 Sub-Millisecond Hook Execution
- **Target Behavior**: Hook execution completes in sub-millisecond time
- **Implementation**: Optimize hot paths, minimize allocations, use efficient data structures
- **Example**: Hook completes in <0.1ms for allow path, <0.5ms for deny path
- **Benefit**: Governance overhead is negligible compared to tool execution time

### 14.2 Linear Scaling
- **Target Behavior**: Performance scales linearly with load
- **Implementation**: No O(n²) or worse algorithms in hot paths
- **Example**: 1000 concurrent agents maintain consistent per-hook latency
- **Benefit**: Predictable performance under load

### 14.3 Zero Allocations in Hot Paths
- **Target Behavior**: Hot paths avoid memory allocations
- **Implementation**: Reuse objects, use efficient data structures, avoid boxing
- **Example**: Pre-allocate log buffers, reuse event objects
- **Benefit**: Reduced GC pressure, consistent latency

### 14.4 Efficient Resource Usage
- **Target Behavior**: Minimal CPU and memory footprint
- **Implementation**: Lazy loading, efficient algorithms, resource pooling
- **Example**: Governance adds <1% CPU overhead for typical workloads
- **Benefit**: Suitable for resource-constrained environments

**Success Criteria**:
- Hook execution <0.1ms p50 for allow path
- Hook execution <0.5ms p99 for deny path
- Linear scaling with concurrent load
- Minimal memory footprint
- <1% CPU overhead for typical workloads

---

## Principle 19: Hook Reliability and Resilience

**Definition**: Hook-based governance must be extremely reliable. Hook failures should not break the system being governed.

**Desired State**:

### 19.1 Graceful Degradation
- **Target Behavior**: Hook failures don't crash the governed system
- **Implementation**: Hooks use failure-safe pattern, fallback to deny on errors
- **Example**: If hook fails, default to "deny" with error logging
- **Benefit**: System remains secure even if governance fails

### 19.2 Hook Isolation
- **Target Behavior**: Hook failures don't affect other hooks
- **Implementation**: Each hook is isolated with its own error handling
- **Example**: One adapter's hook failure doesn't prevent other adapters from working
- **Benefit**: Partial failure doesn't cause system-wide failure

### 19.3 Deterministic Hook Behavior
- **Target Behavior**: Same inputs always produce same outputs
- **Implementation**: No randomness, no state-dependent behavior in hot paths
- **Example**: Same event always produces same governance decision
- **Benefit**: Reproducible behavior, easier debugging and testing

### 19.4 Circuit Breaker Pattern
- **Target Behavior**: Failing hooks are temporarily disabled
- **Implementation**: Circuit breaker disables hooks after repeated failures
- **Example**: If a hook fails 3 times in a row, disable it for 1 minute
- **Benefit**: System recovers from transient failures automatically

**Success Criteria**:
- Hook failures never crash the governed system
- Hook failures are isolated to specific components
- Hook behavior is deterministic and reproducible
- Circuit breaker prevents cascading failures
- System degrades gracefully under failure

---

## Principle 20: Fail-Closed by Default, Configurable Strictness

**Definition**: Governance should be fail-closed by default for security, with configurable strictness levels to balance usability for hobbyists with control for enterprises.

**Desired State**:

### 20.1 Fail-Closed Default
- **Target Behavior**: Default governance mode is fail-closed (block on failure)
- **Implementation**: Hooks block actions when governance checks fail
- **Example**: New installations start in "blocking" mode with deny on errors
- **Benefit**: Security-first approach prevents unauthorized access during failures

### 20.2 Configurable Strictness
- **Target Behavior**: Strictness levels are configurable
- **Implementation**: Support blocking, advisory, and hybrid modes
- **Example**: Hobbyists use advisory mode, enterprises use blocking mode
- **Benefit**: Scales from casual to critical use cases

### 20.3 Progressive Enforcement
- **Target Behavior**: Users can progressively increase strictness
- **Implementation**: Start with advisory, allow gradual tightening to blocking
- **Example**: Start with logging, move to warnings, then to blocking
- **Benefit**: Users can adapt governance to their needs gradually

### 20.4 Local Override Capability
- **Target Behavior**: Users can override governance locally when needed
- **Implementation**: Provide local escape hatch for emergencies
- **Example**: Local file can temporarily disable specific rules
- **Benefit**: Flexibility for urgent situations without breaking governance

**Success Criteria**:
- Default mode is fail-closed (block on failure)
- Multiple strictness levels supported
- Progressive enforcement path available
- Local override capability for emergencies
- System degrades gracefully without breaking security
- No breaking changes when moving between modes

---

## Principle 21: Managed Dependency Portability

**Definition**: The governance system should have minimal runtime dependencies. Dependencies that are required must be auto-installed via a script or bat file to ensure maximum portability and reduce supply chain attack surface.

**Desired State**:

### 21.1 Auto-Install Dependencies
- **Target Behavior**: Required dependencies are auto-installed via script or bat file
- **Implementation**: Installation script handles all dependency setup automatically
- **Example**: install.bat or install.sh automatically installs required packages
- **Benefit**: One-click setup, no manual dependency management

### 21.2 Minimal Dependency Set
- **Target Behavior**: Use minimal necessary dependencies
- **Implementation**: Only dependencies that provide essential functionality are included
- **Example**: Core governance uses stdlib, optional features have optional dependencies
- **Benefit**: Reduced attack surface, faster installation

### 21.3 Dependency Transparency
- **Target Behavior**: All dependencies are clearly documented and approved
- **Implementation**: Dependencies listed in requirements.txt with version pinning
- **Example**: Clear list of required packages with specific versions
- **Benefit**: Reproducible installations, security transparency

### 21.4 Supply Chain Security
- **Target Behavior**: Dependencies follow security best practices
- **Implementation**: Use packages published at least 7 days ago, verify integrity
- **Example**: Avoid latest/unbounded ranges, use specific version numbers
- **Benefit**: Reduced supply chain attack risk

**Success Criteria**:
- Required dependencies auto-installed via script or bat file
- Minimal dependency set used
- All dependencies clearly documented with version pinning
- Dependencies follow security best practices
- Reproducible and secure installation process

---

## Principle 22: Tamper-Evident Audit

**Definition**: Governance decisions should be tamper-evident by default. Any modification to audit logs should be detectable, ensuring compliance and accountability.

**Desired State**:

### 18.1 Hash Chain Verification
- **Target Behavior**: Audit logs use hash chain for tamper detection
- **Implementation**: Each log entry includes hash of previous entry
- **Example**: Merkle tree or hash chain for log integrity
- **Benefit**: Any modification to logs is detectable

### 18.2 Cryptographic Signatures
- **Target Behavior**: Critical decisions are cryptographically signed
- **Implementation**: Governance decisions include cryptographic signatures
- **Example**: Denial decisions signed with private key, verifiable with public key
- **Benefit**: Decision authenticity and non-repudiation

### 18.3 Immutable Audit Trail
- **Target Behavior**: Audit trail is append-only
- **Implementation**: Once written, audit entries cannot be modified
- **Example**: Log files are append-only, deletion prohibited
- **Benefit**: Immutable evidence for compliance

### 18.4 Offline Verification
- **Target Behavior**: Audit can be verified without system access
- **Implementation**: Audit verification works with only log files and public keys
- **Example**: External auditor can verify logs without accessing running system
- **Benefit**: Independent compliance verification

**Success Criteria**:
- Audit logs use hash chain for integrity
- Critical decisions are cryptographically signed
- Audit trail is append-only
- Verification works offline
- Any modification is detectable

---

## Principle 23: Digital Sovereignty

**Definition**: The governance system should be sovereign by construction - portable across providers, inspectable in behavior, and free of hidden dependencies on any single vendor or platform.

**Desired State**:

### 19.1 Provider Portability
- **Target Behavior**: System works across different providers/platforms
- **Implementation**: No provider-specific dependencies or lock-in
- **Example**: Works on AWS, Azure, GCP, or on-premise equally
- **Benefit**: No vendor lock-in, deployment flexibility

### 19.2 Behavioral Inspectability
- **Target Behavior**: System behavior is fully inspectable
- **Implementation**: Open source, clear code, comprehensive logging
- **Example**: All decisions can be audited and explained
- **Benefit**: Trust through transparency

### 19.3 No Hidden Dependencies
- **Target Behavior**: No hidden dependencies on single vendor/platform
- **Implementation**: All dependencies are explicit and documented
- **Example**: No proprietary services or cloud-specific features
- **Benefit**: Full control over deployment and operation

### 19.4 Data Sovereignty
- **Target Behavior**: User controls where data is stored and processed
- **Implementation**: All data processing happens in user-controlled environment
- **Example**: Logs, policies, and audit data stay in user's infrastructure
- **Benefit**: Compliance with data residency requirements

**Success Criteria**:
- Works across multiple providers/platforms
- System behavior is fully inspectable
- No hidden vendor dependencies
- User controls data location
- No vendor lock-in

---

## Principle 35: Configurable Hook Timeouts

**Definition**: Hooks must have configurable timeout boundaries defined in the config.json where the adapter is selected. This prevents hung hooks from deadlocking the governed agent and allows different adapters to specify appropriate timeout values.

**Desired State**:

### 35.1 Config-Based Timeout Definition
- **Target Behavior**: Hook timeouts are defined in config.json alongside adapter selection
- **Implementation**: config.json specifies timeout values for each hook type
- **Example**: config.json defines "pre_tool_use_timeout": 10, "post_tool_use_timeout": 5
- **Benefit**: Different adapters can specify appropriate timeout values

### 35.2 Timeout Default Behavior
- **Target Behavior**: Hooks have default timeout when not specified in config
- **Implementation**: Default timeout of 10 seconds for governance checks
- **Example**: If config doesn't specify timeout, use 10-second default
- **Benefit**: Reasonable default for simple governance checks

### 35.3 Timeout Enforcement
- **Target Behavior**: Hooks are aborted if they exceed timeout
- **Implementation**: Hook execution is terminated after timeout, action blocked
- **Example**: If hook runs longer than timeout, tool execution is denied
- **Benefit**: Prevents hung hooks from deadlocking the agent

### 35.4 Per-Hook Type Configuration
- **Target Behavior**: Different hook types can have different timeout values
- **Implementation**: config.json can specify timeouts per hook type
- **Example**: PreToolUse: 10s, PostToolUse: 5s, complex checks: 30s
- **Benefit**: Simple checks run faster, complex checks have more time

**Success Criteria**:
- Hook timeouts defined in config.json alongside adapter selection
- Default timeout of 10 seconds for unspecified hooks
- Hooks are aborted on timeout to prevent deadlocks
- Different hook types can have different timeout values
- Timeout values are adaptable per adapter requirements

---

## Principle 24: Hook Composability

**Definition**: Multiple hooks should be composable without conflicts. Users should be able to chain multiple governance hooks together.

**Desired State**:

### 24.1 Hook Chaining
- **Target Behavior**: Multiple hooks can be chained together
- **Implementation**: Hooks are called in configurable order, pass-through pattern
- **Example**: Validation hook → Logging hook → Audit hook
- **Benefit**: Users can combine multiple governance concerns

### 24.2 Hook Isolation
- **Target Behavior**: Hooks don't interfere with each other
- **Implementation**: Each hook operates on independent data or copy of data
- **Example**: One hook can't modify data that affects another hook
- **Benefit**: Predictable behavior, easier debugging

### 24.3 Configurable Hook Order
- **Target Behavior**: Hook execution order is configurable
- **Implementation**: Configuration defines hook priority and ordering
- **Example**: User can specify which hooks run first
- **Benefit**: Flexibility in governance pipeline construction

### 24.4 Hook Composition APIs
- **Target Behavior**: Easy to compose hooks from smaller pieces
- **Implementation**: Provide composable hook primitives
- **Example**: Combine validation, logging, and audit into single composite hook
- **Benefit**: Reusable hook components

**Success Criteria**:
- Multiple hooks can be chained
- Hooks don't interfere with each other
- Hook order is configurable
- Easy to compose hooks from primitives
- Complex governance pipelines can be built

---

## Market-Derived Principles

These principles are based on competitive analysis of governance systems (Agent Control Standard, SkillGuard, ThumbGate, SteerPlane, Microsoft Agent Governance Toolkit) and regulatory frameworks (NIST COSAiS, CAISI, Singapore's IMDA Model AI Governance Framework).

## Principle 25: Determinism Over Probability

**Definition**: Governance layer produces binary allow/deny/modify verdicts based on state and rule matching, not learned confidence scores. The system uses declarative policy engines that evaluate structured authorization requests against explicit rules.

**Desired State**:

### 25.1 Binary Governance Decisions
- **Target Behavior**: Governance produces binary outcomes (allow/deny/modify)
- **Implementation**: Rule evaluation returns clear deterministic results
- **Example**: "Block file deletion" returns deny, not "95% confidence to block"
- **Benefit**: Verifiable, predictable governance decisions

### 25.2 State-Based Rule Matching
- **Target Behavior**: Rules match against explicit state, not probabilistic analysis
- **Implementation**: Rules evaluate current state against defined conditions
- **Example**: Rule checks "if file in protected directory" not "if file looks important"
- **Benefit**: Deterministic, auditable rule evaluation

### 25.3 Declarative Policy Engine
- **Target Behavior**: Policy defined declaratively, not procedurally
- **Implementation**: YAML/DSL defines what should happen, not how
- **Example**: "Block sensitive file access" rather than "Check file, if sensitive, block"
- **Benefit**: Policy intent clear, implementation details abstracted

**Success Criteria**:
- Governance decisions are binary and deterministic
- Rules match against explicit state conditions
- Policy is defined declaratively
- No confidence scores or probabilistic judgments
- Outcomes are verifiable and reproducible

---

## Principle 26: In-Path Enforcement (Fail-Closed)

**Definition**: Governance controls must be in-path (checked before the action executes), not forensic-only (reconstructed after failure). This aligns with fail-closed philosophy.

**Desired State**:

### 26.1 Pre-Execution Validation
- **Target Behavior**: Governance checks happen before action execution
- **Implementation**: Hooks intercept actions before they execute
- **Example**: PreToolUse hook validates before tool executes
- **Benefit**: Prevents damage rather than detecting after fact

### 26.2 Fail-Closed Default
- **Target Behavior**: System fails closed by default, blocks unknown actions
- **Implementation**: If governance check fails, action is blocked
- **Example**: If rule evaluation fails, tool use is denied
- **Benefit**: Security-first approach, prevents unauthorized actions

### 26.3 Immediate Enforcement
- **Target Behavior**: Governance decisions are enforced immediately
- **Implementation**: No delay between decision and enforcement
- **Example**: Block decision immediately stops tool execution
- **Benefit**: Prevents race conditions and timing attacks

**Success Criteria**:
- Governance checks happen before action execution
- System fails closed by default
- Enforcement is immediate
- No forensic-only governance
- Actions blocked before damage occurs

---

## Principle 27: Declarative Policy Over Hardcoded Rules

**Definition**: Declarative policy languages provide the governance layer that hooks need to be operationally viable at scale. Policy language matters more than implementation—allow for Cedar, OPA, or similar engines plugging in.

**Desired State**:

### 27.1 Declarative Policy Language
- **Target Behavior**: Policies defined in declarative language
- **Implementation**: Support multiple policy engines (Cedar, OPA, custom)
- **Example**: YAML rules can be processed by different policy engines
- **Benefit**: Policy portability across implementations

### 27.2 Policy Engine Pluggability
- **Target Behavior**: Different policy engines can be plugged in
- **Implementation**: Abstract policy evaluation interface
- **Example**: Switch between Cedar and OPA without changing rules
- **Benefit**: Flexibility in policy implementation choice

### 27.3 Scale-Ready Policy Format
- **Target Behavior**: Policy format suitable for enterprise scale
- **Implementation**: Hierarchical, composable policy structure
- **Example**: Policies can be organized, inherited, and composed
- **Benefit**: Manages hundreds of agents and rules effectively

**Success Criteria**:
- Policies defined declaratively
- Multiple policy engines supported
- Policy evaluation abstracted
- Format suitable for enterprise scale
- Policy logic independent of implementation

---

## Principle 28: Runtime Observability Through Hooks

**Definition**: The same interception points used for permission checks can support runtime behavioral monitoring, cost tracking, compliance auditing, and performance profiling.

**Desired State**:

### 28.1 Behavioral Monitoring
- **Target Behavior**: Hooks monitor anomalous action sequences
- **Implementation**: Logging and analysis of action patterns
- **Example**: Detect repeated failed access attempts
- **Benefit**: Runtime security monitoring

### 28.2 Cost Tracking
- **Target Behavior**: Hooks track token and time consumption per skill
- **Implementation**: Metrics collection through hook interception
- **Example**: Log token usage per tool call
- **Benefit**: Cost optimization and budgeting

### 28.3 Compliance Auditing
- **Target Behavior**: Hooks record data access and policy application
- **Implementation**: Comprehensive audit trail through hooks
- **Example**: Log which files accessed under which policy
- **Benefit**: Compliance reporting and verification

### 28.4 Performance Profiling
- **Target Behavior**: Hooks measure per-skill latency
- **Implementation**: Performance metrics through hook timing
- **Example**: Measure governance overhead per tool call
- **Benefit**: Performance optimization and SLA monitoring

**Success Criteria**:
- Hooks support behavioral monitoring
- Cost tracking available through hooks
- Compliance auditing through hook logs
- Performance profiling via hook metrics
- Single interception point serves multiple observability needs

---

## Principle 29: Governance Before Deployment (Risk Bounding)

**Definition**: Organizations must assess and bound new agent risks before deployment, increase human accountability for agent oversight, implement technical controls limiting agent authority, and enable end-users to understand and manage risks.

**Desired State**:

### 29.1 Pre-Deployment Risk Assessment
- **Target Behavior**: Agent risks assessed before deployment
- **Implementation**: Risk evaluation framework for new agents
- **Example**: Agent capabilities analyzed for potential risks
- **Benefit**: Proactive risk management

### 29.2 Human Accountability
- **Target Behavior**: Human oversight required for agent deployment
- **Implementation**: Approval workflow for agent deployment
- **Example**: Human reviews and approves agent configuration
- **Benefit**: Clear accountability chain

### 29.3 Technical Authority Limits
- **Target Behavior**: Technical controls limit agent authority
- **Implementation**: Capability restrictions and scope limitations
- **Example**: Agent cannot access certain resources without approval
- **Benefit**: Bounded agent authority

### 29.4 User Risk Understanding
- **Target Behavior**: End-users understand and can manage risks
- **Implementation**: Clear risk communication and user controls
- **Example**: Users see what risks agent poses and can configure limits
- **Benefit**: Informed risk management

**Success Criteria**:
- Risk assessment before deployment
- Human accountability in approval chain
- Technical controls limit agent authority
- Users understand and can manage risks
- Proactive rather than reactive risk management

---

## Principle 30: Delegation Chain Accountability

**Definition**: When an orchestrator agent delegates to a sub-agent which calls an API which modifies a database, the accountability chain spans multiple layers. The system needs explicit role propagation and delegation bounds.

**Desired State**:

### 30.1 Role Propagation
- **Target Behavior**: User roles propagate through delegation chain
- **Implementation**: Role information passed through all delegation levels
- **Example**: Orchestrator → Sub-agent → API carries original user role
- **Benefit**: Accountability maintained across delegation

### 30.2 Delegation Bounds
- **Target Behavior**: Delegation has explicit boundaries and limits
- **Implementation**: Defined scope and duration for delegation
- **Example**: Sub-agent can only access specific resources for limited time
- **Benefit**: Controlled delegation prevents privilege escalation

### 30.3 Chain of Custody
- **Target Behavior**: Complete chain of custody tracked
- **Implementation**: Audit trail records all delegation steps
- **Example**: Every delegation step logged with context
- **Benefit**: Complete accountability traceability

**Success Criteria**:
- Roles propagate through delegation chain
- Delegation has explicit boundaries
- Chain of custody tracked completely
- Accountability maintained across all delegation levels
- Clear audit trail of delegation flow

---

## Principle 31: No Silent Failures

**Definition**: If a hook denies an action, the agent and operator must know immediately. Logging is not notification; fail-fast and surface denials in context.

**Desired State**:

### 31.1 Immediate Denial Notification
- **Target Behavior**: Denials are immediately surfaced to user
- **Implementation**: Clear error messages and context on denial
- **Example**: "Access denied: File in protected directory" shown immediately
- **Benefit**: User knows exactly what was blocked and why

### 31.2 Contextual Error Messages
- **Target Behavior**: Denials include relevant context
- **Implementation**: Error messages include rule name, resource, reason
- **Example**: "Denied by security rule: Cannot delete production files"
- **Benefit**: User can understand and respond appropriately

### 31.3 Fail-Fast Behavior
- **Target Behavior**: System fails fast on governance violations
- **Implementation**: No silent failures or background processing
- **Example**: Tool use immediately blocked, not queued for later
- **Benefit**: Clear, immediate feedback

**Success Criteria**:
- Denials immediately surfaced to user
- Error messages include relevant context
- System fails fast on violations
- No silent failures
- User understands what was blocked and why

---

## Principle 32: Minimal Context Passing

**Definition**: Pass only what the enforcement rule needs. Don't pollute the hook with ambient state. This reduces cognitive load and attack surface.

**Desired State**:

### 32.1 Targeted Context Passing
- **Target Behavior**: Only relevant context passed to hooks
- **Implementation**: Hooks receive minimal necessary information
- **Example**: File deletion hook only gets file path, not full system state
- **Benefit**: Reduced cognitive load and attack surface

### 32.2 Explicit Context Definition
- **Target Behavior**: Context requirements explicitly defined
- **Implementation**: Hook contracts specify required context
- **Example**: Hook interface defines "requires: file_path, user_id"
- **Benefit**: Clear context requirements, no over-passing

### 32.3 State Isolation
- **Target Behavior**: Hooks operate on isolated context
- **Implementation**: No ambient state access, only provided context
- **Example**: Hook cannot access global state beyond provided parameters
- **Benefit**: Reduced attack surface, predictable behavior

**Success Criteria**:
- Hooks receive minimal necessary context
- Context requirements explicitly defined
- Hooks isolated from ambient state
- No unnecessary state passing
- Reduced cognitive load and attack surface

---

## Principle 33: Stateless Enforcement

**Definition**: Each hook invocation should be independently decidable (given rule state and action context). Avoid cross-hook dependencies or temporal state that makes race conditions possible.

**Desired State**:

### 33.1 Independent Hook Decisions
- **Target Behavior**: Each hook invocation independently decidable
- **Implementation**: Hook decisions based only on current state and context
- **Example**: Hook decision doesn't depend on previous hook results
- **Benefit**: Predictable, testable behavior

### 33.2 No Cross-Hook Dependencies
- **Target Behavior**: Hooks don't depend on each other's state
- **Implementation**: Each hook self-contained, no shared state
- **Example**: Hook A doesn't require Hook B to have run first
- **Benefit**: Flexible hook ordering, easier testing

### 33.3 Race Condition Prevention
- **Target Behavior**: Temporal state dependencies avoided
- **Implementation**: No state that changes between hook invocations
- **Example**: Hook decisions don't depend on timing or order
- **Benefit**: Eliminates race conditions, improves reliability

**Success Criteria**:
- Hook decisions independently decidable
- No cross-hook dependencies
- No temporal state dependencies
- Race conditions eliminated
- Hooks self-contained and isolated

---

## Principle 34: Standardized Hook Payloads

**Definition**: Even if the CLI changes, hook inputs/outputs should map cleanly to a canonical model (action type, agent identity, resource, access level, audit context).

**Desired State**:

### 34.1 Canonical Payload Model
- **Target Behavior**: Hook payloads follow canonical model
- **Implementation**: Standard structure for all hook inputs/outputs
- **Example**: All hooks have action_type, agent_identity, resource, access_level
- **Benefit**: Consistent interface across different CLIs

### 34.2 CLI-to-Canonical Mapping
- **Target Behavior**: CLI-specific formats mapped to canonical model
- **Implementation**: Adapters convert CLI events to canonical payloads
- **Example**: Devin CLI tool use mapped to canonical action model
- **Benefit**: Framework works consistently across different CLIs

### 34.3 Payload Extensibility
- **Target Behavior**: Canonical model extensible for new fields
- **Implementation**: Optional fields in canonical model
- **Example**: Can add new audit context fields without breaking existing hooks
- **Benefit**: Future-proof design

**Success Criteria**:
- Hook payloads follow canonical model
- CLI-specific formats mapped to canonical
- Model extensible for new requirements
- Consistent interface across CLIs
- Framework works with any CLI that can map to canonical model
