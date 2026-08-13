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
- Initialize module-level logging with standardized JSONL format
- Provide convenient imports for common classes
- Set up module-level state if needed
- Implement consistent initialization pattern across all modules

**NOT Job:**
- Does NOT contain business logic
- Does NOT make governance decisions
- Does NOT evaluate policies

**Key Interfaces:**
- Located in: Every module directory (Core/, Core/protocol/, Core/engine/, Core/state_machine/, Core/hook_handler/, Adapter/, Actions/)
- Used by: Python import system

**Required Functions (Base Pattern):**
```python
def initialize_module(module_name: str) -> None:
    """Initialize module with logging setup.
    
    Args:
        module_name: Name of the module for logging purposes
        
    Sets up module-specific logger with JSONL format per ARCHITECTURE.md Principle 9.
    Implements graceful degradation - non-critical failures log but don't block import.
    Critical failures block import with error logging.
    """

def get_module_version() -> str:
    """Return module version string.
    
    Returns:
        Version string (e.g., "1.0.0") for debugging and compliance tracking.
    """

def get_public_api() -> dict:
    """Return dictionary of public API exports.
    
    Returns:
        Dictionary mapping public names to their implementations.
        Used for __all__ export list and API documentation.
    """
```

**Optional Functions (Module-Specific):**
- Modules can add additional initialization functions as needed
- Example: Adapter module may have `register_hooks()` function
- Example: Engine module may have `initialize_policy_cache()` function

**Logging Requirements:**
Per ARCHITECTURE.md Principle 9.1, logging is required for governance decisions and operations, not all module initializations:

- **Governance Operations** (REQUIRED logging):
  - Policy evaluation and enforcement decisions
  - Hook execution and results
  - State machine transitions
  - Governance decision outputs
  - Use standardized JSONL format: `{"File": "__init__.py", "component": module_name, "Time": timestamp, "data": {...}}`
  - Log to corresponding module log file (e.g., `Logs/Overseer-Log-DATE.jsonl` for Core/__init__.py)

- **Schema Definitions** (OPTIONAL logging):
  - Data structure definitions (e.g., Core/protocol/models.py)
  - Type definitions and interfaces
  - Configuration schemas
  - Module imports and exports
  - May log initialization for debugging but not required for governance compliance

- **General Requirements**:
  - Implement silent failure for logging errors (logging failures shouldn't crash system)
  - All governance decisions must be logged with full context per Principle 9.1

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

**Class Structure:**
```python
class Overseer:
    """Central governance orchestrator following coordinator pattern."""
    
    def __init__(self, config_path: str = "Overseer/Config/config.json"):
        """Initialize Overseer with configuration.
        
        Args:
            config_path: Path to configuration file
            
        Sets up logging, loads config, initializes module references.
        Implements graceful degradation for non-critical initialization failures.
        """
    
    def handle_hook_event(self, hook_name: str, event_data: Dict[str, Any]) -> GovernanceDecision:
        """Process hook event and return governance decision.
        
        Args:
            hook_name: Name of the hook event (e.g., "PreToolUse")
            event_data: Raw event data from CLI as dictionary
            
        Returns:
            GovernanceDecision object with decision, rationale, and context
            
        Orchestrates: Adapter → Protocol → Engine → State Machine → Hook Handler
        Implements classified error handling for security and observability.
        """
```

**Required Functions:**
```python
def load_adapter(config_path: str) -> BaseAdapter:
    """Dynamically load adapter based on configuration.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        BaseAdapter instance loaded from configured adapter class
        
    Uses importlib for dynamic loading.
    Caches loaded adapter to temporary file for performance.
    Detects config changes via file modification time comparison.
    Raises: ConfigurationError if adapter loading fails.
    """

def load_config(config_path: str) -> Dict[str, Any]:
    """Load and validate configuration with integrity verification.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated configuration dictionary
        
    Validates JSON structure and required fields.
    Implements integrity verification per ARCHITECTURE.md Principle 20.
    Raises: ConfigurationError if validation fails.
    """
```

**Error Handling Classification:**
```python
class GovernanceError(Exception):
    """Governance-related errors that should fail-closed (deny)."""
    # Policy evaluation failures, validation failures, etc.

class SystemError(Exception):
    """System-related errors that should fail-open (allow with logging)."""
    # Logging failures, temporary I/O issues, etc.

class ConfigurationError(Exception):
    """Configuration-related errors that should fail-closed (deny)."""
    # Invalid config, missing required fields, etc.
```

**Error Handling Behavior:**
- GovernanceError → Return deny decision with error rationale
- SystemError → Return allow decision with error logging (fail-open for observability)
- ConfigurationError → Return deny decision with error rationale (fail-closed for security)

**CLI Interface:**
```python
def main(hook_name: str, event_data_json: str) -> int:
    """CLI entry point wrapper.
    
    Args:
        hook_name: Hook event name from CLI argument
        event_data_json: Event data as JSON string from stdin
        
    Returns:
        Exit code (0 for allow, 2 for block)
        
    Handles JSON parsing, calls handle_hook_event(), outputs decision as JSON.
    Wrapper separates business logic from CLI mechanics.
    """
```

**Logging Requirements:**
- Log initialization on startup with configuration status
- Log configuration loaded with integrity verification result
- Log adapter loaded with caching status
- Log orchestration events (module transitions) with timestamps
- Log errors with context and classification (governance vs system)
- Use standardized JSONL format: `{"File": "overseer.py", "component": "Overseer", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Overseer-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Data Structures:**
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

class ActionType(str, Enum):
    """Enumeration of possible action types."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    MODIFY = "modify"

class AccessLevel(str, Enum):
    """Enumeration of access levels."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

@dataclass
class CanonicalPayload:
    """Canonical payload structure for universal data representation.
    
    This dataclass provides the universal data format that all adapters
    must transform their CLI-specific events into. It follows ARCHITECTURE.md
    Principle 8 (Standardized Hook Payloads).
    """
    action_type: ActionType
    agent_identity: str
    resource: str
    access_level: AccessLevel
    audit_context: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    delegation_chain: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum to string conversion.
        
        Returns:
            Dictionary representation with enums as strings
        """
        data = {
            "action_type": self.action_type.value,
            "agent_identity": self.agent_identity,
            "resource": self.resource,
            "access_level": self.access_level.value,
            "audit_context": self.audit_context,
        }
        if self.metadata is not None:
            data["metadata"] = self.metadata
        if self.delegation_chain is not None:
            data["delegation_chain"] = self.delegation_chain
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanonicalPayload':
        """Create from dictionary with string to enum conversion.
        
        Args:
            data: Dictionary representation
            
        Returns:
            CanonicalPayload instance with enums converted from strings
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        return cls(
            action_type=ActionType(data["action_type"]),
            agent_identity=data["agent_identity"],
            resource=data["resource"],
            access_level=AccessLevel(data["access_level"]),
            audit_context=data["audit_context"],
            metadata=data.get("metadata"),
            delegation_chain=data.get("delegation_chain")
        )

@dataclass
class GovernanceDecision:
    """Governance decision with complete audit context.
    
    This dataclass captures not just the decision but also the complete
    context for audit trails and compliance requirements per ARCHITECTURE.md
    Principle 6 (Deterministic Discrete Verdicts) and Principle 9 (Audit Trail).
    """
    decision: str  # "allow", "deny", "modify"
    policy_id: str
    rationale: str
    context: Dict[str, Any]
    evaluated_rules: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with datetime serialization.
        
        Returns:
            Dictionary representation with ISO format timestamp
        """
        return {
            "decision": self.decision,
            "policy_id": self.policy_id,
            "rationale": self.rationale,
            "context": self.context,
            "evaluated_rules": self.evaluated_rules,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GovernanceDecision':
        """Create from dictionary with datetime deserialization.
        
        Args:
            data: Dictionary representation
            
        Returns:
            GovernanceDecision instance with datetime parsed from ISO format
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        return cls(
            decision=data["decision"],
            policy_id=data["policy_id"],
            rationale=data["rationale"],
            context=data["context"],
            evaluated_rules=data["evaluated_rules"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
```

**Logging Requirements:**
- Log module initialization with data structure registration
- Log when data structures are instantiated/used (debug level)
- Log any structural errors or validation issues with context
- Use standardized JSONL format: `{"File": "models.py", "component": "Protocol", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Protocol-Log-DATE.jsonl`
- Implement silent failure for logging errors

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
- Input: CanonicalPayload from models.py or dict
- Used by: Core/overseer.py, Hook Handler
- Dependencies: Core/protocol/models.py
- Output: ValidationResult with detailed error information

**Data Structures:**
```python
from dataclasses import dataclass
from typing import List, Union, Dict, Any

@dataclass
class ValidationError:
    """Structured validation error with field path and message."""
    field_path: str  # Dot-separated path to invalid field (e.g., "action_type")
    message: str     # Human-readable error message
    severity: str    # "error" or "warning"

@dataclass
class ValidationResult:
    """Structured validation result with errors and warnings."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def add_error(self, field_path: str, message: str) -> None:
        """Add an error to the validation result."""
        self.errors.append(ValidationError(field_path=field_path, message=message, severity="error"))
        self.is_valid = False
    
    def add_warning(self, field_path: str, message: str) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(ValidationError(field_path=field_path, message=message, severity="warning"))
```

**Required Functions:**
```python
def validate_payload(payload: Union[Dict[str, Any], CanonicalPayload]) -> ValidationResult:
    """Validate canonical payload structure and field values.
    
    Args:
        payload: Either a dictionary or CanonicalPayload instance to validate
        
    Returns:
        ValidationResult with is_valid flag, errors list, and warnings list
        
    Validates:
    - Required fields presence
    - Field types (string, dict, etc.)
    - Enum values (ActionType, AccessLevel)
    - String constraints (non-empty, max length)
    - Data structure integrity
    
    Field-specific validation rules:
    - action_type: Must be valid ActionType enum value
    - agent_identity: Non-empty string, max 256 characters
    - resource: Non-empty string, max 1024 characters
    - access_level: Must be valid AccessLevel enum value
    - audit_context: Must be dict with required sub-fields
    - metadata: Optional dict if present
    - delegation_chain: Optional list if present
    """
```

**Field-Level Validation Logic:**
```python
def _validate_action_type(value: Any, result: ValidationResult) -> None:
    """Validate action_type field."""
    if not isinstance(value, str):
        result.add_error("action_type", f"Must be string, got {type(value).__name__}")
        return
    try:
        ActionType(value)  # Will raise ValueError if invalid
    except ValueError:
        valid_values = [e.value for e in ActionType]
        result.add_error("action_type", f"Must be one of {valid_values}, got '{value}'")

def _validate_agent_identity(value: Any, result: ValidationResult) -> None:
    """Validate agent_identity field."""
    if not isinstance(value, str):
        result.add_error("agent_identity", f"Must be string, got {type(value).__name__}")
        return
    if not value.strip():
        result.add_error("agent_identity", "Cannot be empty")
    elif len(value) > 256:
        result.add_warning("agent_identity", f"Length {len(value)} exceeds recommended maximum of 256")

def _validate_resource(value: Any, result: ValidationResult) -> None:
    """Validate resource field."""
    if not isinstance(value, str):
        result.add_error("resource", f"Must be string, got {type(value).__name__}")
        return
    if not value.strip():
        result.add_error("resource", "Cannot be empty")
    elif len(value) > 1024:
        result.add_warning("resource", f"Length {len(value)} exceeds recommended maximum of 1024")

def _validate_access_level(value: Any, result: ValidationResult) -> None:
    """Validate access_level field."""
    if not isinstance(value, str):
        result.add_error("access_level", f"Must be string, got {type(value).__name__}")
        return
    try:
        AccessLevel(value)  # Will raise ValueError if invalid
    except ValueError:
        valid_values = [e.value for e in AccessLevel]
        result.add_error("access_level", f"Must be one of {valid_values}, got '{value}'")

def _validate_audit_context(value: Any, result: ValidationResult) -> None:
    """Validate audit_context field."""
    if not isinstance(value, dict):
        result.add_error("audit_context", f"Must be dict, got {type(value).__name__}")
        return
    if not value:
        result.add_warning("audit_context", "Empty audit context may not provide sufficient audit trail")
```

**Logging Requirements:**
- Log validation failures with field paths and error messages
- Log validation passes at debug level
- Log validation warnings with context
- Use standardized JSONL format: `{"File": "validators.py", "component": "Protocol", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Protocol-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Required Functions:**
```python
def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize payload data to consistent format.
    
    Args:
        payload: Raw payload dictionary to normalize
        
    Returns:
        Normalized payload dictionary
        
    Applies field-specific normalization:
    - Trims whitespace from string fields
    - Converts empty strings to None for optional fields
    - Normalizes list formats
    - Standardizes dictionary key formats
    """

def merge_metadata(base: Dict[str, Any], additional: Dict[str, Any]) -> Dict[str, Any]:
    """Merge metadata dictionaries with conflict resolution.
    
    Args:
        base: Base metadata dictionary
        additional: Additional metadata to merge
        
    Returns:
        Merged metadata dictionary
        
    Conflict resolution: additional values override base values.
    Nested dictionaries are merged recursively.
    """

def safe_get_field(data: Dict[str, Any], field_path: str, default: Any = None) -> Any:
    """Safely get nested field from dictionary using dot notation.
    
    Args:
        data: Source dictionary
        field_path: Dot-separated field path (e.g., "audit_context.original_event")
        default: Default value if field not found
        
    Returns:
        Field value or default if not found
        
    Example: safe_get_field(payload, "audit_context.adapter") returns adapter value.
    """

def convert_timestamp_format(timestamp: Any, target_format: str = "iso") -> str:
    """Convert timestamp to standardized format.
    
    Args:
        timestamp: Input timestamp (various formats)
        target_format: Target format ("iso", "unix", etc.)
        
    Returns:
        Formatted timestamp string
        
    Handles various input formats (datetime objects, Unix timestamps, ISO strings).
    """

def convert_payload_version(payload: Dict[str, Any], target_version: str) -> Dict[str, Any]:
    """Convert payload between protocol versions.
    
    Args:
        payload: Source payload with version field
        target_version: Target protocol version (semantic version)
        
    Returns:
        Converted payload for target version
        
    Raises:
        ValueError: If version conversion is not supported
        
    Converts between compatible protocol versions using defined conversion rules.
    """

def is_version_compatible(version1: str, version2: str) -> bool:
    """Check if two protocol versions are compatible.
    
    Args:
        version1: First protocol version (semantic version)
        version2: Second protocol version (semantic version)
        
    Returns:
        True if versions are compatible, False otherwise
        
    Compatibility rules:
    - Same major version: Compatible
    - Different major version: Incompatible
    - Minor/patch differences: Compatible if same major
    """
```

**Data Normalization Functions:**
```python
def normalize_string_fields(data: Dict[str, Any], fields: List[str], 
                          trim: bool = True, lowercase: bool = False) -> Dict[str, Any]:
    """Normalize string fields in payload.
    
    Args:
        data: Payload dictionary to normalize
        fields: List of field names to normalize
        trim: Whether to trim whitespace
        lowercase: Whether to convert to lowercase
        
    Returns:
        Payload with normalized string fields
    """

def normalize_optional_fields(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Normalize optional fields by converting empty values to None.
    
    Args:
        data: Payload dictionary to normalize
        fields: List of optional field names
        
    Returns:
        Payload with normalized optional fields
        
    Converts empty strings, empty lists, empty dicts to None for specified fields.
    """

def normalize_lists(data: Dict[str, Any], field_names: List[str]) -> Dict[str, Any]:
    """Normalize list fields to consistent format.
    
    Args:
        data: Payload dictionary to normalize
        field_names: List of field names that should be lists
        
    Returns:
        Payload with normalized list fields
        
    Ensures specified fields are lists (converts single values to single-item lists).
    """

def normalize_dict_keys(data: Dict[str, Any], field_names: List[str], 
                       key_case: str = "lower") -> Dict[str, Any]:
    """Normalize dictionary key formats.
    
    Args:
        data: Payload dictionary to normalize
        field_names: List of field names containing dicts to normalize
        key_case: Target key case ("lower", "upper", "original")
        
    Returns:
        Payload with normalized dictionary keys
        
    Standardizes key case in nested dictionaries for specified fields.
    """
```

**Version Management:**
```python
CURRENT_PROTOCOL_VERSION = "1.0.0"

def get_protocol_version() -> str:
    """Return current protocol version."""
    return CURRENT_PROTOCOL_VERSION

def validate_payload_version(payload: Dict[str, Any]) -> bool:
    """Validate that payload version is compatible with current version.
    
    Args:
        payload: Payload dictionary with version field
        
    Returns:
        True if compatible, False otherwise
        
    Logs compatibility check result.
    """
```

**Logging Requirements:**
- Log transformation operations with input/output summaries
- Log version compatibility checks with versions compared
- Log normalization operations with fields affected
- Use standardized JSONL format: `{"File": "transformers.py", "component": "Protocol", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Protocol-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
class PolicyEvaluator:
    """Stateless policy evaluator following deterministic evaluation principles.
    
    This class implements ARCHITECTURE.md Principle 6 (Deterministic Discrete Verdicts)
    and Principle 7 (Stateless and Idempotent Enforcement). Evaluation is deterministic
    based only on input payload and policy state.
    """
    
    def __init__(self, policies: Dict[str, Dict[str, Any]]):
        """Initialize evaluator with loaded policies.
        
        Args:
            policies: Dictionary of policy_id -> policy_definition from policy_loader
            
        Policies are loaded once at initialization; evaluation is stateless.
        """
    
    def evaluate(self, payload: CanonicalPayload) -> GovernanceDecision:
        """Evaluate policies against payload and return governance decision.
        
        Args:
            payload: CanonicalPayload to evaluate
            
        Returns:
            GovernanceDecision with decision, rationale, and complete context
            
        Evaluation process:
        1. Track all policies evaluated
        2. Match policies against payload conditions
        3. Collect individual policy decisions
        4. Compose final decision (delegates to conflict_resolver if needed)
        5. Build complete decision context for audit trail
        
        Stateless: Same payload + same policies always produces same decision.
        """
    
    def get_evaluated_policies(self) -> List[str]:
        """Return list of policy IDs evaluated in last evaluation.
        
        Returns:
            List of policy IDs that were evaluated
            
        Used for audit trail and debugging.
        """
```

**Required Functions:**
```python
def match_policy_condition(condition: str, payload: CanonicalPayload) -> bool:
    """Evaluate single policy condition against payload using restricted evaluation.
    
    Args:
        condition: Policy condition expression (e.g., "action_type == 'DELETE'")
        payload: CanonicalPayload to evaluate against
        
    Returns:
        True if condition matches, False otherwise
        
    Security: Uses restricted evaluation with whitelisted operations only.
    Prevents code injection per ARCHITECTURE.md Principle 23.
    
    Allowed operations:
    - Field access: payload.action_type, payload.resource, etc.
    - Comparisons: ==, !=, <, >, <=, >=
    - Logical: and, or, not
    - String methods: startswith, endswith, contains, in
    - Safe arithmetic: +, -, *, / (no complex expressions)
    """

def get_matching_policies(policies: Dict[str, Dict[str, Any]], 
                         payload: CanonicalPayload) -> List[Dict[str, Any]]:
    """Get all policies whose conditions match the payload.
    
    Args:
        policies: Dictionary of policy_id -> policy_definition
        payload: CanonicalPayload to evaluate against
        
    Returns:
        List of policy definitions that match the payload
        
    Evaluates each policy's condition and returns matching policies
    in priority order if specified.
    """

def evaluate_single_policy(policy: Dict[str, Any], 
                         payload: CanonicalPayload) -> str:
    """Evaluate single policy and return its decision.
    
    Args:
        policy: Policy definition with rules and actions
        payload: CanonicalPayload to evaluate against
        
    Returns:
        Policy decision: "allow", "deny", or "modify"
        
    Evaluates policy rules and returns the action specified by matching rules.
    If multiple rules match, uses policy-defined conflict resolution.
    """

def build_decision_context(payload: CanonicalPayload, 
                         evaluated_policies: List[str],
                         matching_policies: List[str],
                         individual_decisions: Dict[str, str]) -> Dict[str, Any]:
    """Build complete decision context for audit trail.
    
    Args:
        payload: Original CanonicalPayload evaluated
        evaluated_policies: List of all policy IDs evaluated
        matching_policies: List of policy IDs that matched
        individual_decisions: Dictionary of policy_id -> decision
        
    Returns:
        Complete decision context dictionary
        
    Context includes:
    - Payload summary (without sensitive data)
    - Evaluation timestamp
    - Policies evaluated count
    - Policies matched count
    - Individual policy decisions
    - Evaluation metadata
    """
```

**Security-Safe Expression Evaluation:**
```python
class RestrictedExpressionEvaluator:
    """Security-restricted expression evaluator for policy conditions.
    
    Implements ARCHITECTURE.md Principle 23 (Input Validation and Prompt
    Injection Defense) by only allowing whitelisted operations and field access.
    """
    
    ALLOWED_OPERATIONS = {
        # Comparisons
        '==', '!=', '<', '>', '<=', '>=',
        # Logical
        'and', 'or', 'not',
        # String operations
        'in', 'not in',
        # Arithmetic
        '+', '-', '*', '/', '%',
    }
    
    ALLOWED_METHODS = {
        'str': ['startswith', 'endswith', 'contains', 'lower', 'upper', 'strip'],
        'list': ['__contains__', '__len__'],
    }
    
    def evaluate(self, expression: str, context: Dict[str, Any]) -> bool:
        """Evaluate expression with restricted operations.
        
        Args:
            expression: Expression string to evaluate
            context: Context dictionary (typically payload fields)
            
        Returns:
            Boolean result of evaluation
            
        Raises:
            SecurityError: If expression contains disallowed operations
            ValueError: If expression is syntactically invalid
            
        Security measures:
        - No function calls except whitelisted methods
        - No module imports
        - No attribute access except on context objects
        - No dunder methods except whitelisted ones
        - Limited recursion depth
        """
```

**Decision Composition:**
```python
def compose_decisions(individual_decisions: Dict[str, str],
                     conflict_strategy: str = "deny_overrides") -> str:
    """Compose multiple policy decisions into single decision.
    
    Args:
        individual_decisions: Dictionary of policy_id -> decision
        conflict_strategy: Strategy for resolving conflicts
        
    Returns:
        Composed decision: "allow", "deny", or "modify"
        
    Conflict strategies:
    - deny_overrides: Any deny → deny (default, security-first)
    - allow_overrides: Any allow → allow
    - priority_first_match: Use highest priority matching policy
    - most_specific_wins: Most specific condition wins
    
    Note: This is a simple composition. Complex composition delegates
    to conflict_resolver.py per architecture.
    """
```

**Logging Requirements:**
- Log policy evaluation start with payload summary
- Log each policy evaluated with result
- Log matching policies with conditions
- Log final decision with rationale
- Log evaluation performance (duration if available)
- Use standardized JSONL format: `{"File": "evaluator.py", "component": "Engine", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Engine-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
class ConflictResolver:
    """Resolves conflicts between multiple policy decisions.
    
    Implements ARCHITECTURE.md Principle 19 (Conflict Resolution) with
    multiple strategies to support different security postures and
    governance requirements.
    """
    
    DEFAULT_STRATEGY = "deny_overrides"
    
    def __init__(self, default_strategy: str = DEFAULT_STRATEGY):
        """Initialize conflict resolver with default strategy.
        
        Args:
            default_strategy: Default conflict resolution strategy
            
        Validates strategy is supported; raises ValueError if not.
        """
    
    def resolve(self, decisions: List[GovernanceDecision], 
                strategy: str = None) -> GovernanceDecision:
        """Resolve conflicts between multiple governance decisions.
        
        Args:
            decisions: List of GovernanceDecision objects from policy evaluation
            strategy: Conflict resolution strategy (uses default if None)
            
        Returns:
            Single GovernanceDecision with composed decision and attribution
            
        Resolution process:
        1. Detect conflicts (different decisions from different policies)
        2. Apply specified resolution strategy
        3. Build attribution context (which policies prevailed)
        4. Return composed decision with complete audit trail
        """
    
    def get_supported_strategies(self) -> List[str]:
        """Return list of supported conflict resolution strategies.
        
        Returns:
            List of strategy names
        """
```

**Required Functions:**
```python
def resolve_deny_overrides(decisions: List[GovernanceDecision]) -> GovernanceDecision:
    """Resolve conflicts using deny-overrides strategy (security-first).
    
    Args:
        decisions: List of GovernanceDecision objects
        
    Returns:
        GovernanceDecision with deny if any deny exists, else modify if any modify, else allow
        
    Resolution rules:
    - If any decision is "deny" → final decision is "deny"
    - Else if any decision is "modify" → final decision is "modify"
    - Else final decision is "allow"
    
    This is the default security-first strategy per ARCHITECTURE.md Principle 5.
    """

def resolve_allow_overrides(decisions: List[GovernanceDecision]) -> GovernanceDecision:
    """Resolve conflicts using allow-overrides strategy (permissive).
    
    Args:
        decisions: List of GovernanceDecision objects
        
    Returns:
        GovernanceDecision with allow if any allow exists, else modify if any modify, else deny
        
    Resolution rules:
    - If any decision is "allow" → final decision is "allow"
    - Else if any decision is "modify" → final decision is "modify"
    - Else final decision is "deny"
    
    This is a permissive strategy for development environments.
    """

def resolve_priority_first_match(decisions: List[GovernanceDecision]) -> GovernanceDecision:
    """Resolve conflicts using priority-first-match strategy.
    
    Args:
        decisions: List of GovernanceDecision objects with priority metadata
        
    Returns:
        GovernanceDecision from highest priority matching policy
        
    Resolution rules:
    - Sort decisions by priority (highest first)
    - Return decision from first (highest priority) policy
    - Priority is specified in policy definition
    
    This strategy allows explicit policy ordering.
    """

def resolve_most_specific_wins(decisions: List[GovernanceDecision]) -> GovernanceDecision:
    """Resolve conflicts using most-specific-wins strategy.
    
    Args:
        decisions: List of GovernanceDecision objects with condition specificity
        
    Returns:
        GovernanceDecision from most specific matching policy
        
    Resolution rules:
    - Calculate specificity score for each policy condition
    - Higher specificity = more specific condition (more constraints)
    - Return decision from most specific policy
    
    Specificity calculation:
    - More field references = higher specificity
    - More specific operators (== vs in) = higher specificity
    - Longer strings/paths = higher specificity
    """

def build_attribution_context(decisions: List[GovernanceDecision],
                             final_decision: GovernanceDecision,
                             strategy: str) -> Dict[str, Any]:
    """Build attribution context for audit trail.
    
    Args:
        decisions: List of all GovernanceDecision objects
        final_decision: Final composed GovernanceDecision
        strategy: Resolution strategy used
        
    Returns:
        Attribution context dictionary
        
    Context includes:
    - conflicting_policies: List of policies with different decisions
    - prevailing_policy: Policy that determined final decision
    - resolution_strategy: Strategy used for resolution
    - resolution_rationale: Why this decision was reached
    - decision_count: Number of decisions considered
    """
```

**Strategy Validation:**
```python
VALID_STRATEGIES = {
    "deny_overrides": resolve_deny_overrides,
    "allow_overrides": resolve_allow_overrides,
    "priority_first_match": resolve_priority_first_match,
    "most_specific_wins": resolve_most_specific_wins,
}

def validate_strategy(strategy: str) -> bool:
    """Validate that strategy is supported.
    
    Args:
        strategy: Strategy name to validate
        
    Returns:
        True if strategy is supported, False otherwise
        
    Raises:
        ValueError: If strategy is not supported
    """
```

**Specificity Calculation:**
```python
def calculate_condition_specificity(condition: str) -> int:
    """Calculate specificity score for policy condition.
    
    Args:
        condition: Policy condition expression
        
    Returns:
        Specificity score (higher = more specific)
        
    Specificity factors:
    - Number of field references: +1 per field
    - Number of operators: +1 per operator
    - String literals: +length of literal
    - Nested conditions: +2 per nesting level
    - Specific operators (==, in): +2 vs general operators
    
    Example specificity scores:
    - "action_type == 'DELETE'" → 8 points
    - "action_type == 'DELETE' and resource.startswith('/etc')" → 20 points
    """
```

**Logging Requirements:**
- Log conflicts detected with conflicting policy IDs
- Log resolution strategy applied
- Log prevailing policy and rationale
- Log final composed decision
- Use standardized JSONL format: `{"File": "conflict_resolver.py", "component": "Engine", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Engine-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
class PolicyLoader:
    """Loads and manages policy definitions with hot-reload support.
    
    Implements ARCHITECTURE.md Principle 4 (Policy Versioning) and
    supports hot-reload for policy updates without system restart.
    """
    
    def __init__(self, rules_directory: str = "Overseer/Rules",
                 poll_interval: int = 30):
        """Initialize policy loader with directory and polling config.
        
        Args:
            rules_directory: Directory containing policy JSON files
            poll_interval: Seconds between change detection polls
            
        Sets up file tracking, loads initial policies, configures polling.
        """
    
    def load_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load all policies from rules directory.
        
        Returns:
            Dictionary of policy_id -> policy_definition
            
        Process:
        1. Scan directory for .json files
        2. Validate each policy file
        3. Load valid policies into cache
        4. Track file modification times
        5. Return loaded policies
        
        Raises: PolicyLoadError if critical policies fail to load.
        """
    
    def reload_policies(self) -> Dict[str, Dict[str, Any]]:
        """Reload policies if changes detected.
        
        Returns:
            Dictionary of policy_id -> policy_definition (updated if changed)
            
        Process:
        1. Check file modification times
        2. Reload changed policies
        3. Validate reloaded policies
        4. Atomically update cache
        5. Return updated policies
        
        Uses atomic reload pattern for consistency.
        """
    
    def check_for_changes(self) -> bool:
        """Check if any policy files have changed.
        
        Returns:
            True if changes detected, False otherwise
            
        Polls file modification times and compares with cached times.
        """
    
    def get_policy_version(self, policy_id: str) -> str:
        """Get version of specific policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy version string
            
        Raises: KeyError if policy not found.
        """
```

**Required Functions:**
```python
def validate_policy_file(file_path: str) -> ValidationResult:
    """Validate policy file format and structure.
    
    Args:
        file_path: Path to policy JSON file
        
    Returns:
        ValidationResult with is_valid flag and error/warning messages
        
    Validation checks:
    - JSON syntax validity
    - Required fields: version, name, description, rules
    - Field data types: version (string), name (string), description (string), rules (list)
    - Rule structure: each rule must have id, condition, action, rationale
    - Policy version format: semantic versioning (major.minor.patch)
    - No duplicate rule IDs within policy
    - Referenced fields in conditions exist
    """

def scan_policy_directory(directory: str) -> List[str]:
    """Scan directory for policy JSON files.
    
    Args:
        directory: Directory path to scan
        
    Returns:
        List of file paths to .json files
        
    Excludes files that:
    - Don't end with .json extension
    - Are in subdirectories (only top-level for now)
    - Are hidden files (starting with .)
    """

def load_single_policy(file_path: str) -> Dict[str, Any]:
    """Load and parse single policy file.
    
    Args:
        file_path: Path to policy JSON file
        
    Returns:
        Parsed policy dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        JSONDecodeError: If JSON is invalid
        PolicyValidationError: If validation fails
    """

def get_file_modification_time(file_path: str) -> float:
    """Get file modification time for change detection.
    
    Args:
        file_path: Path to file
        
    Returns:
        Modification time as Unix timestamp
        
    Used for polling-based change detection.
    """

def atomic_policy_reload(new_policies: Dict[str, Dict[str, Any]],
                        current_policies: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Atomically reload policies with consistency guarantees.
    
    Args:
        new_policies: Newly loaded policies
        current_policies: Currently active policies
        
    Returns:
        Updated policy dictionary
        
    Atomic reload pattern:
    1. Validate new policies completely
    2. If validation fails, keep current policies
    3. If validation succeeds, swap references atomically
    4. Ensure no inconsistent state is visible
    """
```

**Policy Validation Schema:**
```python
REQUIRED_POLICY_FIELDS = {
    "version": str,
    "name": str,
    "description": str,
    "rules": list,
}

REQUIRED_RULE_FIELDS = {
    "id": str,
    "condition": str,
    "action": str,
    "rationale": str,
}

VALID_ACTIONS = ["allow", "deny", "modify", "warn"]

def validate_policy_structure(policy: Dict[str, Any]) -> ValidationResult:
    """Validate policy structure against schema.
    
    Args:
        policy: Policy dictionary to validate
        
    Returns:
        ValidationResult with structural validation results
        
    Validates:
    - Required fields present
    - Field types correct
    - Rule structure valid
    - Actions in allowed set
    - No duplicate rule IDs
    """
```

**Caching Strategy:**
```python
class PolicyCache:
    """Cache for loaded policies with change tracking."""
    
    def __init__(self):
        """Initialize empty policy cache."""
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.modification_times: Dict[str, float] = {}
        self.policy_versions: Dict[str, str] = {}
    
    def update(self, policy_id: str, policy: Dict[str, Any], 
              mod_time: float) -> None:
        """Update cache entry for policy.
        
        Args:
            policy_id: Policy identifier
            policy: Policy definition
            mod_time: File modification time
        """
    
    def get(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy from cache.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy definition or None if not found
        """
    
    def is_modified(self, policy_id: str, current_mod_time: float) -> bool:
        """Check if policy file has been modified.
        
        Args:
            policy_id: Policy identifier
            current_mod_time: Current file modification time
            
        Returns:
            True if modified, False otherwise
        """
```

**Logging Requirements:**
- Log policy load events with file paths and versions
- Log policy reload events with changed policy IDs
- Log validation failures with specific error messages
- Log cache hit/miss statistics
- Use standardized JSONL format: `{"File": "policy_loader.py", "component": "Engine", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Engine-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque

class StateMachine(ABC):
    """Abstract base class for state machine implementations.
    
    Provides generic state machine functionality including transition validation,
    history tracking, and logging patterns. Concrete implementations (emergency.py,
    workflow.py) define specific states and business logic.
    """
    
    def __init__(self, initial_state: str, max_history_size: int = 100):
        """Initialize state machine with initial state and history config.
        
        Args:
            initial_state: Starting state for the state machine
            max_history_size: Maximum number of transitions to track in history
            
        Sets up state tracking, history buffer, and logging.
        """
    
    @abstractmethod
    def get_allowed_transitions(self) -> Dict[str, List[str]]:
        """Return allowed transitions table.
        
        Returns:
            Dictionary mapping from_state -> list of valid to_states
            
        Must be implemented by concrete classes to define their specific
        transition rules.
        """
    
    def validate_transition(self, from_state: str, to_state: str) -> bool:
        """Validate that state transition is allowed.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is allowed, False otherwise
            
        Checks against ALLOWED_TRANSITIONS table.
        """
    
    def transition(self, to_state: str, reason: str = "", 
                  authorization: str = "") -> bool:
        """Execute state transition with validation and logging.
        
        Args:
            to_state: Target state
            reason: Reason for transition
            authorization: Authorization context (who/what authorized)
            
        Returns:
            True if transition succeeded, False if validation failed
            
        Process:
        1. Validate transition is allowed
        2. Update current state
        3. Record transition in history
        4. Log transition with full context
        """
    
    def get_current_state(self) -> str:
        """Return current state.
        
        Returns:
            Current state string
        """
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Return state transition history.
        
        Returns:
            List of transition records (oldest first)
            
        Each record contains:
        - timestamp: ISO format timestamp
        - from_state: Previous state
        - to_state: New state
        - reason: Transition reason
        - authorization: Authorization context
        """
    
    def clear_history(self) -> None:
        """Clear state transition history."""
```

**Required Functions:**
```python
def log_transition(from_state: str, to_state: str, reason: str, 
                  authorization: str) -> None:
    """Log state transition with standardized format.
    
    Args:
        from_state: Previous state
        to_state: New state
        reason: Transition reason
        authorization: Authorization context
        
    Logs in standardized JSONL format per ARCHITECTURE.md Principle 9.
    """
```

**State History Implementation:**
```python
class StateHistory:
    """Circular buffer for state transition history."""
    
    def __init__(self, max_size: int = 100):
        """Initialize circular buffer with max size.
        
        Args:
            max_size: Maximum number of transitions to store
            
        When buffer is full, oldest entries are overwritten.
        """
        self.history: deque = deque(maxlen=max_size)
    
    def add_transition(self, from_state: str, to_state: str, reason: str,
                     authorization: str) -> None:
        """Add transition to history.
        
        Args:
            from_state: Previous state
            to_state: New state
            reason: Transition reason
            authorization: Authorization context
            
        Automatically removes oldest entry if buffer is full.
        """
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get transition history as list.
        
        Returns:
            List of transition records (oldest first)
        """
    
    def clear(self) -> None:
        """Clear all history entries."""
```

**Transition Validation:**
```python
def get_valid_transitions(current_state: str, 
                        allowed_transitions: Dict[str, List[str]]) -> List[str]:
    """Get valid next states from current state.
    
    Args:
        current_state: Current state
        allowed_transitions: Transition table
        
    Returns:
        List of valid next states
        
    Returns empty list if current_state not in transition table.
    """

def is_transition_allowed(from_state: str, to_state: str,
                         allowed_transitions: Dict[str, List[str]]) -> bool:
    """Check if specific transition is allowed.
    
    Args:
        from_state: Current state
        to_state: Target state
        allowed_transitions: Transition table
        
    Returns:
        True if transition is allowed, False otherwise
    """
```

**Logging Requirements:**
- Log state transitions with from_state, to_state, reason, authorization
- Log transition validation failures
- Log history buffer operations (clear, overflow)
- Use standardized JSONL format: `{"File": "base.py", "component": "StateMachine", "Time": timestamp, "data": {...}}`
- Log file: `Logs/StateMachine-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
from enum import Enum
from typing import Dict, List, Optional

class EmergencyState(str, Enum):
    """Emergency control states with graduated security implications."""
    NORMAL = "NORMAL"                  # Normal operation, no restrictions
    HALT_NONCRITICAL = "HALT_NONCRITICAL"  # Block non-critical actions (write/delete/execute)
    HALT_ALL = "HALT_ALL"             # Block all actions
    EMERGENCY = "EMERGENCY"           # Complete system shutdown

class AuthorizationLevel(str, Enum):
    """Authorization levels for emergency state transitions."""
    ADMIN = "ADMIN"                   # Standard admin authorization
    ELEVATED = "ELEVATED"            # Elevated privileges (security team)
    BREAK_GLASS = "BREAK_GLASS"      # Multi-factor or break-glass procedure

class EmergencyStateMachine(StateMachine):
    """Emergency control state machine with persistence and authorization.
    
    Implements ARCHITECTURE.md Principle 15 (Emergency Controls) with
    graduated response levels and strict authorization requirements.
    """
    
    DEFAULT_STATE = EmergencyState.NORMAL
    STATE_FILE = "Overseer/Config/emergency_state.json"
    
    def __init__(self, state_file: str = STATE_FILE):
        """Initialize emergency state machine with persistence.
        
        Args:
            state_file: Path to emergency state persistence file
            
        Loads persisted state if available, otherwise uses default.
        Sets up authorization requirements.
        """
    
    def get_allowed_transitions(self) -> Dict[str, List[str]]:
        """Return allowed emergency state transitions.
        
        Returns:
            Transition table mapping current states to valid next states
            
        Transition rules:
        - NORMAL → HALT_NONCRITICAL, HALT_ALL, EMERGENCY
        - HALT_NONCRITICAL → HALT_ALL, EMERGENCY, NORMAL
        - HALT_ALL → EMERGENCY, NORMAL
        - EMERGENCY → NORMAL (recovery procedure only)
        """
    
    def check_emergency_state(self) -> EmergencyState:
        """Check current emergency state for action blocking.
        
        Returns:
            Current emergency state
            
        Called before every action to determine if action should be blocked.
        """
    
    def should_block_action(self, action_type: ActionType) -> bool:
        """Determine if action should be blocked based on emergency state.
        
        Args:
            action_type: Type of action being attempted
            
        Returns:
            True if action should be blocked, False otherwise
            
        Blocking rules:
        - NORMAL: No blocking
        - HALT_NONCRITICAL: Block WRITE, DELETE, EXECUTE, MODIFY (allow READ)
        - HALT_ALL: Block all actions
        - EMERGENCY: Block all actions (system shutdown)
        """
    
    def set_emergency_state(self, new_state: EmergencyState, 
                          authorization: AuthorizationLevel,
                          reason: str) -> bool:
        """Set emergency state with authorization validation.
        
        Args:
            new_state: Target emergency state
            authorization: Authorization level of requester
            reason: Reason for state change
            
        Returns:
            True if transition succeeded, False if authorization failed
            
        Process:
        1. Validate authorization is sufficient for transition
        2. Execute state transition
        3. Persist new state to file
        4. Log transition with full context
        """
```

**Authorization Requirements:**
```python
AUTHORIZATION_REQUIREMENTS = {
    # Transitions and required authorization levels
    (EmergencyState.NORMAL, EmergencyState.HALT_NONCRITICAL): AuthorizationLevel.ADMIN,
    (EmergencyState.NORMAL, EmergencyState.HALT_ALL): AuthorizationLevel.ELEVATED,
    (EmergencyState.NORMAL, EmergencyState.EMERGENCY): AuthorizationLevel.BREAK_GLASS,
    (EmergencyState.HALT_NONCRITICAL, EmergencyState.HALT_ALL): AuthorizationLevel.ELEVATED,
    (EmergencyState.HALT_NONCRITICAL, EmergencyState.EMERGENCY): AuthorizationLevel.BREAK_GLASS,
    (EmergencyState.HALT_NONCRITICAL, EmergencyState.NORMAL): AuthorizationLevel.ADMIN,
    (EmergencyState.HALT_ALL, EmergencyState.EMERGENCY): AuthorizationLevel.BREAK_GLASS,
    (EmergencyState.HALT_ALL, EmergencyState.NORMAL): AuthorizationLevel.ELEVATED,
    (EmergencyState.EMERGENCY, EmergencyState.NORMAL): AuthorizationLevel.BREAK_GLASS,
}

def validate_authorization(from_state: EmergencyState, to_state: EmergencyState,
                         provided_auth: AuthorizationLevel) -> bool:
    """Validate that authorization is sufficient for transition.
    
    Args:
        from_state: Current emergency state
        to_state: Target emergency state
        provided_auth: Authorization level provided
        
    Returns:
        True if authorization is sufficient, False otherwise
        
    Checks against AUTHORIZATION_REQUIREMENTS table.
    """
```

**Persistence Implementation:**
```python
def save_state(state: EmergencyState, state_file: str) -> None:
    """Persist emergency state to file with atomic write.
    
    Args:
        state: Current emergency state
        state_file: Path to state persistence file
        
    Uses atomic write pattern:
    1. Write to temporary file
    2. Validate write succeeded
    3. Rename temp file to target file (atomic)
    
    Raises: IOError if write fails
    """

def load_state(state_file: str) -> EmergencyState:
    """Load emergency state from file with fallback.
    
    Args:
        state_file: Path to state persistence file
        
    Returns:
        Loaded emergency state or NORMAL if file is corrupted/missing
        
    Fallback to NORMAL if:
    - File doesn't exist (first run)
    - File is corrupted (recovery)
    - State value is invalid (unknown state)
    """
```

**Multi-Scope Support:**
```python
class EmergencyScope(str, Enum):
    """Scopes for emergency control."""
    GLOBAL = "GLOBAL"           # Entire system
    TENANT = "TENANT"           # Specific tenant
    AGENT = "AGENT"             # Specific agent
    TOOL = "TOOL"               # Specific tool

class ScopedEmergencyState:
    """Emergency state with scope support."""
    
    def __init__(self, scope: EmergencyScope, scope_id: str = ""):
        """Initialize scoped emergency state.
        
        Args:
            scope: Scope of emergency control
            scope_id: Identifier for scope (tenant ID, agent ID, etc.)
            
        GLOBAL scope has no scope_id.
        """
    
    def get_effective_state(self, global_state: EmergencyState) -> EmergencyState:
        """Get effective emergency state considering scope hierarchy.
        
        Args:
            global_state: Global emergency state
            
        Returns:
            Effective emergency state for this scope
            
        Hierarchy: GLOBAL > TENANT > AGENT > TOOL
        More specific scopes inherit from broader scopes unless overridden.
        """
```

**Logging Requirements:**
- Log every emergency state transition with full context
- Log emergency state checks with action type and result
- Log authorization validation results
- Log persistence operations (save/load)
- Log scope-specific state changes
- Use standardized JSONL format: `{"File": "emergency.py", "component": "StateMachine", "Time": timestamp, "data": {...}}`
- Log file: `Logs/StateMachine-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
from enum import Enum
from typing import Dict, List, Optional, Callable

class WorkflowPhase(str, Enum):
    """Workflow orchestration phases for subagent coordination."""
    INITIALIZATION = "INITIALIZATION"   # Setup and configuration
    RESEARCH = "RESEARCH"              # Research and documentation
    IMPLEMENTATION = "IMPLEMENTATION" # Code implementation
    VALIDATION = "VALIDATION"          # Testing and verification
    COMPLETION = "COMPLETION"          # Finalization and delivery

class WorkflowStateMachine(StateMachine):
    """Workflow state machine for subagent orchestration.
    
    Implements SUBAGENT_ORCHESTRATION.md requirements for structured
    workflow management with iteration limits and evaluation gates.
    """
    
    DEFAULT_PHASE = WorkflowPhase.INITIALIZATION
    MAX_ITERATIONS_PER_PHASE = 3
    
    def __init__(self, workflow_id: str = "default"):
        """Initialize workflow state machine with tracking.
        
        Args:
            workflow_id: Identifier for this workflow instance
            
        Sets up phase tracking, iteration counters, and evaluation gates.
        """
    
    def get_allowed_transitions(self) -> Dict[str, List[str]]:
        """Return allowed workflow phase transitions.
        
        Returns:
            Transition table mapping current phases to valid next phases
            
        Transition rules:
        - INITIALIZATION → RESEARCH
        - RESEARCH → IMPLEMENTATION, back to RESEARCH (iteration)
        - IMPLEMENTATION → VALIDATION, back to IMPLEMENTATION (iteration)
        - VALIDATION → COMPLETION, back to RESEARCH (major issues), back to IMPLEMENTATION (fixes)
        - COMPLETION → terminal state
        """
    
    def advance_phase(self, to_phase: WorkflowPhase, reason: str = "") -> bool:
        """Advance to next workflow phase with gate validation.
        
        Args:
            to_phase: Target workflow phase
            reason: Reason for phase transition
            
        Returns:
            True if transition succeeded, False if gate validation failed
            
        Process:
        1. Check evaluation gate for transition
        2. Validate transition is allowed
        3. Reset iteration counter for new phase
        4. Execute transition
        5. Log transition with gate result
        """
    
    def track_iteration(self) -> int:
        """Track iteration within current phase.
        
        Returns:
            Current iteration count (after increment)
            
        Increments iteration counter for current phase.
        """
    
    def check_iteration_limit(self) -> bool:
        """Check if iteration limit has been reached.
        
        Returns:
            True if limit reached, False otherwise
            
        When limit reached (3 iterations), escalates to human review.
        """
    
    def check_evaluation_gate(self, from_phase: WorkflowPhase, 
                           to_phase: WorkflowPhase) -> bool:
        """Check evaluation gate for phase transition.
        
        Args:
            from_phase: Current workflow phase
            to_phase: Target workflow phase
            
        Returns:
            True if gate criteria met, False otherwise
            
        Validates phase-specific gate criteria before allowing transition.
        """
```

**Iteration Tracking:**
```python
class PhaseIterationTracker:
    """Track iterations per workflow phase."""
    
    def __init__(self, max_iterations: int = 3):
        """Initialize iteration tracker with limits.
        
        Args:
            max_iterations: Maximum iterations per phase
        """
        self.iterations: Dict[WorkflowPhase, int] = {}
        self.max_iterations = max_iterations
    
    def increment(self, phase: WorkflowPhase) -> int:
        """Increment iteration count for phase.
        
        Args:
            phase: Current workflow phase
            
        Returns:
            New iteration count
            
        Raises: IterationLimitExceeded if max iterations reached
        """
    
    def reset(self, phase: WorkflowPhase) -> None:
        """Reset iteration count for phase.
        
        Args:
            phase: Phase to reset
            
        Called when transitioning to a new phase.
        """
    
    def get_count(self, phase: WorkflowPhase) -> int:
        """Get current iteration count for phase.
        
        Args:
            phase: Workflow phase
            
        Returns:
            Current iteration count
        """
```

**Evaluation Gate Management:**
```python
class EvaluationGate:
    """Evaluation gate for phase transitions."""
    
    def __init__(self, from_phase: WorkflowPhase, to_phase: WorkflowPhase,
                 criteria: Callable[[], bool]):
        """Initialize evaluation gate.
        
        Args:
            from_phase: Source phase
            to_phase: Target phase
            criteria: Function that returns True if gate criteria met
        """
    
    def check(self) -> bool:
        """Check if gate criteria are met.
        
        Returns:
            True if criteria met, False otherwise
            
        Executes criteria function and returns result.
        """

class GateManager:
    """Manage evaluation gates for workflow transitions."""
    
    def __init__(self):
        """Initialize gate manager with predefined gates."""
        self.gates: Dict[tuple, EvaluationGate] = {}
        self.gate_history: List[Dict[str, Any]] = []
    
    def register_gate(self, from_phase: WorkflowPhase, to_phase: WorkflowPhase,
                    criteria: Callable[[], bool]) -> None:
        """Register evaluation gate for phase transition.
        
        Args:
            from_phase: Source phase
            to_phase: Target phase
            criteria: Gate criteria function
        """
    
    def check_gate(self, from_phase: WorkflowPhase, to_phase: WorkflowPhase) -> bool:
        """Check gate for phase transition.
        
        Args:
            from_phase: Source phase
            to_phase: Target phase
            
        Returns:
            True if gate passed or no gate exists, False if gate failed
            
        Records gate result in history.
        """
    
    def get_gate_history(self) -> List[Dict[str, Any]]:
        """Get gate check history.
        
        Returns:
            List of gate check results (oldest first)
            
        Each entry includes: from_phase, to_phase, passed, timestamp, details.
        """
```

**Gate Criteria Examples:**
```python
def research_gate_criteria() -> bool:
    """Criteria for RESEARCH → IMPLEMENTATION transition."""
    # Check if documentation is complete
    # Check if research findings are approved
    # Check if implementation plan is defined
    return True  # Placeholder for actual criteria

def implementation_gate_criteria() -> bool:
    """Criteria for IMPLEMENTATION → VALIDATION transition."""
    # Check if code is implemented
    # Check if basic tests pass
    # Check if code follows conventions
    return True  # Placeholder for actual criteria

def validation_gate_criteria() -> bool:
    """Criteria for VALIDATION → COMPLETION transition."""
    # Check if all tests pass
    # Check if coverage requirements met
    # Check if security requirements met
    return True  # Placeholder for actual criteria
```

**Session State Management:**
```python
class WorkflowSession:
    """Manage session state for workflow execution."""
    
    def __init__(self, workflow_id: str):
        """Initialize workflow session.
        
        Args:
            workflow_id: Workflow identifier
        """
        self.workflow_id = workflow_id
        self.session_data: Dict[str, Any] = {}
        self.start_time: datetime = datetime.utcnow()
    
    def set_session_data(self, key: str, value: Any) -> None:
        """Set session data key-value pair.
        
        Args:
            key: Data key
            value: Data value
        """
    
    def get_session_data(self, key: str) -> Optional[Any]:
        """Get session data value.
        
        Args:
            key: Data key
            
        Returns:
            Data value or None if not found
        """
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary.
        
        Returns:
            Dictionary with session metadata and key data
        """
```

**Logging Requirements:**
- Log workflow phase transitions with gate results
- Log iteration tracking and limit escalations
- Log evaluation gate checks with criteria and results
- Log session state changes
- Use standardized JSONL format: `{"File": "workflow.py", "component": "StateMachine", "Time": timestamp, "data": {...}}`
- Log file: `Logs/StateMachine-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import signal
from contextlib import contextmanager

class HookType(str, Enum):
    """Hook types that can be dispatched."""
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    ON_ERROR = "OnError"

class TimeoutBehavior(str, Enum):
    """Timeout behavior for different hook types."""
    FAIL_CLOSED = "FAIL_CLOSED"      # Return DENY on timeout (security-first)
    FAIL_OPEN = "FAIL_OPEN"        # Return ALLOW with logging (observability)

@dataclass
class RegisteredHandler:
    """Registered hook handler with metadata."""
    handler: Callable
    priority: int
    hook_type: HookType
    timeout_behavior: TimeoutBehavior

class HookDispatcher:
    """Single dynamic dispatcher for hook coordination.
    
    Implements "parse once, shared work" pattern for performance with
    priority-based handler ordering and timeout configuration.
    """
    
    DEFAULT_PRIORITY = 50
    DEFAULT_TIMEOUTS = {
        HookType.PRE_TOOL_USE: 10,   # Fast path for synchronous governance
        HookType.POST_TOOL_USE: 5,   # Allow more time for comprehensive logging
        HookType.ON_ERROR: 5,        # Error handling timeout
    }
    
    def __init__(self, state_machine, engine):
        """Initialize dispatcher with dependencies.
        
        Args:
            state_machine: Emergency state machine instance
            engine: Policy engine instance
            
        Sets up handler registry and timeout configuration.
        """
    
    def register_handler(self, hook_type: HookType, handler: Callable, 
                        priority: int = DEFAULT_PRIORITY,
                        timeout_behavior: TimeoutBehavior = TimeoutBehavior.FAIL_CLOSED) -> None:
        """Register handler for specific hook type with priority.
        
        Args:
            hook_type: Type of hook event
            handler: Handler function
            priority: Handler priority (higher numbers first)
            timeout_behavior: Behavior on handler timeout
            
        Handlers are sorted by priority after registration.
        """
    
    def dispatch(self, hook_type: HookType, event_data: Dict[str, Any]) -> str:
        """Dispatch hook event through registered handlers.
        
        Args:
            hook_type: Type of hook event
            event_data: Raw event data from adapter
            
        Returns:
            Governance decision ("allow", "deny", "modify")
            
        Process:
        1. Parse input once
        2. Check emergency state first
        3. Execute handlers in priority order
        4. Short-circuit on DENY
        5. Handle timeouts with configured behavior
        6. Return final decision
        """
    
    def _parse_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and normalize event data once.
        
        Args:
            event_data: Raw event data
            
        Returns:
            Parsed event data
            
        Centralized parsing for performance optimization.
        """
    
    def _check_emergency_state(self) -> Optional[str]:
        """Check emergency state before hook execution.
        
        Returns:
            DENY if emergency state requires blocking, None otherwise
            
        Emergency state check per ARCHITECTURE.md Principle 15.
        """
```

**Required Functions:**
```python
def execute_with_timeout(handler: Callable, event_data: Dict[str, Any],
                       timeout: int, timeout_behavior: TimeoutBehavior) -> str:
    """Execute handler with timeout and configured behavior.
    
    Args:
        handler: Handler function to execute
        event_data: Parsed event data
        timeout: Timeout in seconds
        timeout_behavior: Behavior on timeout
        
    Returns:
        Handler decision or timeout decision based on behavior
        
    Uses signal-based timeout or threading with timeout.
    On timeout: return DENY if FAIL_CLOSED, ALLOW if FAIL_OPEN.
    """

@contextmanager
def timeout_context(seconds: int):
    """Context manager for timeout handling.
    
    Args:
        seconds: Timeout in seconds
        
    Yields:
        None
        
    Raises:
        TimeoutError if timeout exceeded
        
    Uses signal.alarm() for Unix or threading for cross-platform.
    """

def aggregate_handler_results(results: List[str]) -> str:
    """Aggregate multiple handler results into final decision.
    
    Args:
        results: List of individual handler decisions
        
    Returns:
        Final governance decision
        
    Aggregation rules:
    - If any DENY → DENY (security-first)
    - Else if any MODIFY → MODIFY
    - Else ALLOW
    """
```

**Handler Registration:**
```python
class HandlerRegistry:
    """Registry for hook handlers with priority management."""
    
    def __init__(self):
        """Initialize empty handler registry."""
        self.handlers: Dict[HookType, List[RegisteredHandler]] = {}
    
    def add(self, handler: RegisteredHandler) -> None:
        """Add handler to registry.
        
        Args:
            handler: RegisteredHandler instance
            
        Automatically sorts handlers by priority after addition.
        """
    
    def get_handlers(self, hook_type: HookType) -> List[RegisteredHandler]:
        """Get handlers for specific hook type.
        
        Args:
            hook_type: Type of hook
            
        Returns:
            List of handlers sorted by priority (highest first)
        """
    
    def remove(self, hook_type: HookType, handler: Callable) -> bool:
        """Remove handler from registry.
        
        Args:
            hook_type: Type of hook
            handler: Handler function to remove
            
        Returns:
            True if removed, False if not found
        """
```

**Timeout Configuration:**
```python
class TimeoutConfig:
    """Timeout configuration for hook types."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize timeout configuration.
        
        Args:
            config: Configuration dictionary with timeout settings
            
        Falls back to defaults if config not provided.
        """
    
    def get_timeout(self, hook_type: HookType) -> int:
        """Get timeout for specific hook type.
        
        Args:
            hook_type: Type of hook
            
        Returns:
            Timeout in seconds
        """
    
    def get_timeout_behavior(self, hook_type: HookType) -> TimeoutBehavior:
        """Get timeout behavior for specific hook type.
        
        Args:
            hook_type: Type of hook
            
        Returns:
            Timeout behavior (FAIL_CLOSED or FAIL_OPEN)
        """
```

**Logging Requirements:**
- Log hook dispatch events with hook type and handler count
- Log priority ordering with handler priorities
- Log timeout behavior with handler and timeout duration
- Log emergency state checks with state and decision
- Log individual handler execution results
- Use standardized JSONL format: `{"File": "dispatcher.py", "component": "HookHandler", "Time": timestamp, "data": {...}}`
- Log file: `Logs/HookHandler-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Class Structure:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from Overseer.Core.protocol.models import CanonicalPayload

class BaseAdapter(ABC):
    """Abstract base class for all framework adapters.
    
    Enforces consistent adapter interface per ARCHITECTURE.md Principle 1
    (True Agnosticism) and SOFTWARE_ENGINEERING_PRINCIPLES.md (Standardization).
    """
    
    @abstractmethod
    def transform_event(self, event: Dict[str, Any]) -> CanonicalPayload:
        """Transform framework-specific event to canonical payload.
        
        Args:
            event: Framework-specific event data from CLI
            
        Returns:
            CanonicalPayload in standard format
            
        Must convert CLI-specific event format to CanonicalPayload structure.
        Must handle all required fields: action_type, agent_identity, resource,
        access_level, audit_context.
        """
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Declare adapter capabilities dynamically.
        
        Returns:
            Dictionary of adapter capabilities
            
        Capability structure:
        {
            "supported_hooks": ["PreToolUse", "PostToolUse", ...],
            "event_types": ["tool_use", "file_edit", ...],
            "data_schema": {...},
            "adapter_features": {...}
        }
        
        Supports ARCHITECTURE.md Principle 1 (Capability-Based Ports).
        """
    
    @abstractmethod
    def register_hooks(self, overseer) -> None:
        """Register CLI-specific hooks with Overseer.
        
        Args:
            overseer: Overseer instance to register hooks with
            
        Registers adapter-specific hook functions for governance processing.
        Establishes connection between CLI events and governance pipeline.
        """
    
    def validate_event(self, event: Dict[str, Any]) -> bool:
        """Validate event structure before transformation.
        
        Args:
            event: Framework-specific event data
            
        Returns:
            True if event is valid, False otherwise
            
        Optional method with default implementation.
        Override for adapter-specific validation.
        """
    
    def get_adapter_info(self) -> Dict[str, str]:
        """Return adapter metadata.
        
        Returns:
            Dictionary with adapter information
            
        Information: name, version, supported_cli, compatibility_notes.
        """
```

**Required Methods Implementation Guidance:**
```python
def transform_event(self, event: Dict[str, Any]) -> CanonicalPayload:
    """Transform event implementation template.
    
    Implementation template:
    1. Extract CLI-specific fields from event
    2. Map to CanonicalPayload fields:
       - action_type: Map to ActionType enum
       - agent_identity: Extract agent ID
       - resource: Extract target resource
       - access_level: Determine access level
       - audit_context: Include original event and adapter info
    3. Return CanonicalPayload instance
    
    Must handle edge cases: missing fields, invalid values, etc.
    """

def get_capabilities(self) -> Dict[str, Any]:
    """Capabilities declaration template.
    
    Implementation template:
    {
        "supported_hooks": ["PreToolUse", "PostToolUse"],
        "event_types": ["edit", "read", "delete", "execute"],
        "data_schema": {
            "tool_name": "string",
            "parameters": "object",
            "agent_id": "string"
        },
        "adapter_features": {
            "file_operations": True,
            "api_calls": False,
            "custom_actions": []
        }
    }
    """

def register_hooks(self, overseer) -> None:
    """Hook registration template.
    
    Implementation template:
    1. Define adapter-specific hook functions
    2. Register with overseer.hook_handler.register_handler()
    3. Set appropriate priorities and timeout behaviors
    4. Log successful registration
    
    Example:
    overseer.hook_handler.register_handler(
        HookType.PRE_TOOL_USE,
        self.pre_tool_use_hook,
        priority=60,
        timeout_behavior=TimeoutBehavior.FAIL_CLOSED
    )
    """
```

**Capability Schema:**
```python
CAPABILITY_SCHEMA = {
    "supported_hooks": {
        "type": "list",
        "required": True,
        "description": "List of hook types adapter supports"
    },
    "event_types": {
        "type": "list", 
        "required": True,
        "description": "List of event types adapter can handle"
    },
    "data_schema": {
        "type": "dict",
        "required": True,
        "description": "Schema of event data adapter expects"
    },
    "adapter_features": {
        "type": "dict",
        "required": False,
        "description": "Adapter-specific features and capabilities"
    }
}

def validate_capabilities(capabilities: Dict[str, Any]) -> ValidationResult:
    """Validate adapter capabilities against schema.
    
    Args:
        capabilities: Capabilities dictionary from get_capabilities()
        
    Returns:
        ValidationResult with validation results
        
    Ensures capabilities match expected schema for consistency.
    """
```

**Logging Requirements:**
- Log base class initialization
- Log when adapter interface methods are called
- Log adapter registration events
- Log transformation operations with input/output summaries
- Use standardized JSONL format: `{"File": "base.py", "component": "Adapter", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Adapter-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Implementation Pattern:**
```python
from Overseer.Adapter.base import BaseAdapter
from Overseer.Core.protocol.models import CanonicalPayload, ActionType, AccessLevel
from typing import Dict, Any

class DevinAdapter(BaseAdapter):
    """Adapter for Devin CLI framework.
    
    Implements BaseAdapter interface with Devin-specific event transformation
    and hook registration. Follows consistent adapter implementation pattern.
    """
    
    def __init__(self):
        """Initialize Devin adapter with configuration."""
        self.adapter_name = "devin"
        self.adapter_version = "1.0.0"
    
    def transform_event(self, event: Dict[str, Any]) -> CanonicalPayload:
        """Transform Devin CLI event to canonical payload.
        
        Args:
            event: Devin CLI event data
            
        Returns:
            CanonicalPayload in standard format
            
        Mapping logic:
        - tool_name → ActionType enum
        - parameters.path → resource
        - agent_id → agent_identity
        - access_level → determined from action type
        - audit_context → includes original event and adapter info
        """
        # Extract CLI-specific fields
        tool_name = event.get("tool_name", "")
        parameters = event.get("parameters", {})
        agent_id = event.get("agent_id", "unknown")
        
        # Map to CanonicalPayload fields
        action_type = self._map_tool_to_action(tool_name)
        resource = parameters.get("path", "")
        access_level = self._determine_access_level(action_type, parameters)
        
        # Create CanonicalPayload
        return CanonicalPayload(
            action_type=action_type,
            agent_identity=agent_id,
            resource=resource,
            access_level=access_level,
            audit_context={
                "original_event": event,
                "adapter": self.adapter_name,
                "adapter_version": self.adapter_version
            }
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Declare Devin adapter capabilities.
        
        Returns:
            Dictionary of adapter capabilities
            
        Devin-specific capabilities:
        - supported_hooks: PreToolUse, PostToolUse, OnError
        - event_types: tool_use, file_edit, file_read, shell_command
        - data_schema: Devin event structure
        - adapter_features: file operations, API calls, etc.
        """
        return {
            "supported_hooks": ["PreToolUse", "PostToolUse", "OnError"],
            "event_types": ["tool_use", "file_edit", "file_read", "shell_command"],
            "data_schema": {
                "tool_name": "string",
                "parameters": "object",
                "agent_id": "string"
            },
            "adapter_features": {
                "file_operations": True,
                "api_calls": True,
                "custom_actions": []
            }
        }
    
    def register_hooks(self, overseer) -> None:
        """Register Devin-specific hooks with Overseer.
        
        Args:
            overseer: Overseer instance to register hooks with
            
        Registers pre_tool_use_hook, post_tool_use_hook, on_error_hook
        with appropriate priorities and timeout behaviors.
        """
        from Overseer.Core.hook_handler.dispatcher import HookType, TimeoutBehavior
        
        # Register pre-tool use hook (high priority, fail-closed)
        overseer.hook_handler.register_handler(
            HookType.PRE_TOOL_USE,
            self.pre_tool_use_hook,
            priority=60,
            timeout_behavior=TimeoutBehavior.FAIL_CLOSED
        )
        
        # Register post-tool use hook (medium priority, fail-open for observability)
        overseer.hook_handler.register_handler(
            HookType.POST_TOOL_USE,
            self.post_tool_use_hook,
            priority=50,
            timeout_behavior=TimeoutBehavior.FAIL_OPEN
        )
        
        # Register error hook (low priority, fail-open)
        overseer.hook_handler.register_handler(
            HookType.ON_ERROR,
            self.on_error_hook,
            priority=40,
            timeout_behavior=TimeoutBehavior.FAIL_OPEN
        )
    
    def _map_tool_to_action(self, tool_name: str) -> ActionType:
        """Map Devin tool name to ActionType enum.
        
        Args:
            tool_name: Devin tool name
            
        Returns:
            ActionType enum value
            
        Mapping: edit→WRITE, read→READ, delete→DELETE, execute→EXECUTE, etc.
        """
        tool_mapping = {
            "edit": ActionType.WRITE,
            "read": ActionType.READ,
            "delete": ActionType.DELETE,
            "execute": ActionType.EXECUTE,
            "modify": ActionType.MODIFY,
        }
        return tool_mapping.get(tool_name, ActionType.READ)
    
    def _determine_access_level(self, action_type: ActionType, 
                            parameters: Dict[str, Any]) -> AccessLevel:
        """Determine access level from action type and parameters.
        
        Args:
            action_type: Mapped action type
            parameters: Tool parameters
            
        Returns:
            AccessLevel enum value
            
        Logic: WRITE/DELETE/EXECUTE → WRITE, READ → READ, etc.
        """
        if action_type in [ActionType.WRITE, ActionType.DELETE, ActionType.EXECUTE]:
            return AccessLevel.WRITE
        return AccessLevel.READ
    
    def pre_tool_use_hook(self, event: Dict[str, Any]) -> str:
        """Pre-tool use hook for Devin CLI.
        
        Args:
            event: Devin CLI event data
            
        Returns:
            Governance decision
            
        Transforms event and passes to Overseer governance pipeline.
        """
        # Transform event to canonical payload
        canonical = self.transform_event(event)
        
        # Pass to Overseer governance pipeline
        # (Implementation depends on Overseer interface)
        return "allow"  # Placeholder
    
    def post_tool_use_hook(self, event: Dict[str, Any]) -> str:
        """Post-tool use hook for Devin CLI.
        
        Args:
            event: Devin CLI event data
            
        Returns:
            Governance decision
            
        For observability and logging after tool execution.
        """
        return "allow"  # Placeholder
    
    def on_error_hook(self, event: Dict[str, Any]) -> str:
        """Error hook for Devin CLI.
        
        Args:
            event: Devin CLI event data
            
        Returns:
            Governance decision
            
        For error handling and logging.
        """
        return "allow"  # Placeholder
```

**Adapter Implementation Requirements:**
```python
# Each adapter must:
1. Extend BaseAdapter class
2. Implement transform_event() with CLI-specific field mapping
3. Implement get_capabilities() with accurate capability declaration
4. Implement register_hooks() with CLI-specific hook functions
5. Follow the BaseAdapter implementation templates
6. Handle CLI-specific edge cases and error conditions
7. Log adapter-specific operations

# Naming convention:
# Adapter files: [AppName]-Adapter.py (e.g., Devin-Adapter.py, Cursor-Adapter.py)
# Adapter classes: [AppName]Adapter (e.g., DevinAdapter, CursorAdapter)
```

**Field Mapping Guidelines:**
```python
# Common field mappings across adapters:
action_type: Derived from tool_name, operation, or action type
agent_identity: Derived from agent_id, user_id, or session_id  
resource: Derived from path, target, url, or resource identifier
access_level: Derived from action type or explicit permission level
audit_context: Always include original_event, adapter_name, adapter_version

# Access level determination:
WRITE, DELETE, EXECUTE → AccessLevel.WRITE
READ → AccessLevel.READ
ADMIN operations → AccessLevel.ADMIN
```

**Logging Requirements:**
- Log adapter initialization with adapter name and version
- Log transformation events with input/output summaries
- Log capability discovery results
- Log hook registration events with hook types and priorities
- Log hook execution results
- Use standardized JSONL format: `{"File": "[AppName]-Adapter.py", "component": "Adapter", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Adapter-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Configuration Schema:**
```json
{
  "version": "1.0.0",
  "integrity_hash": "sha256_hash_of_config_content",
  "adapters": {
    "devin": {
      "enabled": true,
      "class": "Adapter.devin_adapter.DevinAdapter",
      "config": {
        "timeout": 10,
        "custom_settings": {}
      }
    },
    "cursor": {
      "enabled": false,
      "class": "Adapter.cursor_adapter.CursorAdapter"
    }
  },
  "governance": {
    "default_mode": "blocking",
    "conflict_resolution": "deny_overrides",
    "emergency_halt": false,
    "emergency_state_file": "Overseer/Config/emergency_state.json"
  },
  "logging": {
    "level": "INFO",
    "format": "jsonl",
    "retention_days": 90,
    "log_directory": "Overseer/Logs"
  },
  "timeouts": {
    "PreToolUse": 10,
    "PostToolUse": 5,
    "OnError": 5
  }
}
```

**Configuration Schema Definition:**
```python
CONFIG_SCHEMA = {
    "version": {
        "type": "string",
        "required": True,
        "description": "Configuration version for compatibility"
    },
    "integrity_hash": {
        "type": "string",
        "required": False,
        "description": "SHA-256 hash for tamper detection (Principle 20)"
    },
    "adapters": {
        "type": "dict",
        "required": True,
        "description": "Adapter configuration for dynamic loading"
    },
    "governance": {
        "type": "dict",
        "required": True,
        "description": "Governance settings and modes"
    },
    "logging": {
        "type": "dict",
        "required": True,
        "description": "Logging configuration"
    },
    "timeouts": {
        "type": "dict",
        "required": True,
        "description": "Per-hook timeout configuration"
    }
}

ADAPTER_CONFIG_SCHEMA = {
    "enabled": {
        "type": "boolean",
        "required": True,
        "description": "Whether this adapter is enabled"
    },
    "class": {
        "type": "string",
        "required": True,
        "description": "Python class path for dynamic loading"
    },
    "config": {
        "type": "dict",
        "required": False,
        "description": "Adapter-specific configuration parameters"
    }
}

GOVERNANCE_CONFIG_SCHEMA = {
    "default_mode": {
        "type": "string",
        "required": True,
        "enum": ["blocking", "advisory", "hybrid"],
        "description": "Default governance mode"
    },
    "conflict_resolution": {
        "type": "string",
        "required": True,
        "enum": ["deny_overrides", "allow_overrides", "priority_first_match", "most_specific_wins"],
        "description": "Default conflict resolution strategy"
    },
    "emergency_halt": {
        "type": "boolean",
        "required": True,
        "description": "Whether emergency halt is active"
    },
    "emergency_state_file": {
        "type": "string",
        "required": True,
        "description": "Path to emergency state persistence file"
    }
}

LOGGING_CONFIG_SCHEMA = {
    "level": {
        "type": "string",
        "required": True,
        "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "description": "Logging level"
    },
    "format": {
        "type": "string",
        "required": True,
        "enum": ["jsonl", "text"],
        "description": "Log format"
    },
    "retention_days": {
        "type": "integer",
        "required": True,
        "minimum": 1,
        "description": "Log retention period in days"
    },
    "log_directory": {
        "type": "string",
        "required": True,
        "description": "Directory for log files"
    }
}

TIMEOUTS_CONFIG_SCHEMA = {
    "PreToolUse": {
        "type": "integer",
        "required": True,
        "minimum": 1,
        "description": "Timeout for PreToolUse hooks in seconds"
    },
    "PostToolUse": {
        "type": "integer",
        "required": True,
        "minimum": 1,
        "description": "Timeout for PostToolUse hooks in seconds"
    },
    "OnError": {
        "type": "integer",
        "required": True,
        "minimum": 1,
        "description": "Timeout for OnError hooks in seconds"
    }
}
```

**Configuration Validation:**
```python
def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate configuration against schema.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        ValidationResult with validation results
        
    Validates:
    - Required fields present
    - Field types match schema
    - Enum values are valid
    - Numeric values within ranges
    - Exactly one adapter is enabled
    - File paths are valid
    """
    
def validate_adapter_config(adapter_config: Dict[str, Any]) -> ValidationResult:
    """Validate adapter-specific configuration.
    
    Args:
        adapter_config: Adapter configuration dictionary
        
    Returns:
        ValidationResult with validation results
        
    Validates adapter configuration against ADAPTER_CONFIG_SCHEMA.
    """

def calculate_integrity_hash(config: Dict[str, Any]) -> str:
    """Calculate SHA-256 hash of configuration content.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        SHA-256 hash string
        
    Used for tamper detection per ARCHITECTURE.md Principle 20.
    Excludes integrity_hash field from calculation itself.
    """

def verify_integrity(config: Dict[str, Any]) -> bool:
    """Verify configuration integrity using hash.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if integrity verified, False if tampering detected
        
    Compares stored integrity_hash with calculated hash.
    Returns True if no integrity_hash field (backward compatibility).
    """
```

**Configuration Loading:**
```python
def load_config(config_path: str) -> Dict[str, Any]:
    """Load and validate configuration with integrity verification.
    
    Args:
        config_path: Path to config.json file
        
    Returns:
        Validated configuration dictionary
        
    Process:
    1. Load JSON from file
    2. Validate schema
    3. Verify integrity hash
    4. Check that exactly one adapter is enabled
    5. Return validated config
        
    Raises: ConfigurationError if validation fails.
    """

def get_enabled_adapter(config: Dict[str, Any]) -> tuple:
    """Get enabled adapter from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (adapter_name, adapter_config)
        
    Raises: ConfigurationError if no adapter or multiple adapters enabled.
    """
```

**Default Configuration:**
```python
DEFAULT_CONFIG = {
    "version": "1.0.0",
    "adapters": {
        "devin": {
            "enabled": True,
            "class": "Adapter.devin_adapter.DevinAdapter",
            "config": {}
        }
    },
    "governance": {
        "default_mode": "blocking",
        "conflict_resolution": "deny_overrides",
        "emergency_halt": False,
        "emergency_state_file": "Overseer/Config/emergency_state.json"
    },
    "logging": {
        "level": "INFO",
        "format": "jsonl",
        "retention_days": 90,
        "log_directory": "Overseer/Logs"
    },
    "timeouts": {
        "PreToolUse": 10,
        "PostToolUse": 5,
        "OnError": 5
    }
}
```

**Logging Requirements:**
- None (configuration file only, overseer.py logs when loaded)
- Overseer.py logs configuration loading with validation results
- Overseer.py logs integrity verification results
- Overseer.py logs adapter selection

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

**Class Structure:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from functools import lru_cache

class BaseAction(ABC):
    """Abstract base class for all policy action implementations.
    
    Enforces consistent action interface per SOFTWARE_ENGINEERING_PRINCIPLES.md
    (Standardization) and IMPLEMENTATION.md patterns.
    """
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> str:
        """Execute policy action and return result.
        
        Args:
            context: Context from hook handler with governance information
            
        Returns:
            Action result: "block", "warn", "direct", or "allow"
            
        Must implement policy-specific logic for governance enforcement.
        """
    
    @lru_cache(maxsize=1)
    def _load_policy(self) -> Dict[str, Any]:
        """Load and cache policy configuration (called once at startup).
        
        Returns:
            Policy configuration dictionary
            
        Loads policy from corresponding JSON file in Rules/ directory.
        Uses LRU cache for performance optimization.
        """
        # Implementation pattern from IMPLEMENTATION.md
        pass
    
    def invalidate_cache(self) -> None:
        """Invalidate policy cache for hot-reload support.
        
        Clears cached policy to force reload on next execution.
        Called when policy file changes.
        """
        self._load_policy.cache_clear()
    
    def get_action_info(self) -> Dict[str, str]:
        """Return action metadata.
        
        Returns:
            Dictionary with action information
            
        Information: name, version, policy_file, enforcement_type.
        """
```

**Required Methods Implementation Guidance:**
```python
def execute(self, context: Dict[str, Any]) -> str:
    """Execute policy action implementation template.
    
    Implementation template:
    1. Load policy configuration (cached)
    2. Extract relevant context information
    3. Evaluate conditions against policy rules
    4. Return appropriate action result
    
    Action results:
    - "block": Block the action with deny decision
    - "warn": Allow action but warn user
    - "direct": Direct agent to specific behavior
    - "allow": Allow action without restriction
    """

def _load_policy(self) -> Dict[str, Any]:
    """Policy loading implementation template.
    
    Implementation template:
    1. Determine policy file path from action class name
    2. Load JSON from Rules/[PolicyName].json
    3. Validate policy structure
    4. Return policy dictionary
    
    Called once at startup due to @lru_cache(maxsize=1).
    """

def invalidate_cache(self) -> None:
    """Cache invalidation for hot-reload.
    
    Implementation template:
    1. Clear LRU cache using _load_policy.cache_clear()
    2. Log cache invalidation
    3. Next execute() will reload policy
    
    Called when policy file changes.
    """
```

**Action Result Semantics:**
```python
ACTION_RESULTS = {
    "block": {
        "description": "Block the action with deny decision",
        "governance_implication": "Returns deny decision to governance pipeline",
        "user_experience": "Action blocked with explanation"
    },
    "warn": {
        "description": "Allow action but warn user",
        "governance_implication": "Returns allow decision with warning in context",
        "user_experience": "Action proceeds with warning message"
    },
    "direct": {
        "description": "Direct agent to specific behavior",
        "governance_implication": "Returns allow with modification instructions",
        "user_experience": "Agent receives specific guidance"
    },
    "allow": {
        "description": "Allow action without restriction",
        "governance_implication": "Returns allow decision normally",
        "user_experience": "Action proceeds normally"
    }
}
```

**Logging Requirements:**
- Log base class initialization
- Log when action interface methods are called
- Log policy loading and cache operations
- Log action execution results
- Use standardized JSONL format: `{"File": "base.py", "component": "Actions", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Actions-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Implementation Pattern:**
```python
from Overseer.Actions.base import BaseAction
from typing import Dict, Any
import json
import os

class FileDeletionProtection(BaseAction):
    """Policy action for file deletion protection.
    
    Implements BaseAction interface with policy-specific logic for
    protecting critical files from deletion.
    """
    
    def __init__(self):
        """Initialize file deletion protection action."""
        self.policy_file = "Overseer/Rules/file-deletion-protection.json"
        self.action_name = "file-deletion-protection"
    
    @lru_cache(maxsize=1)
    def _load_policy(self) -> Dict[str, Any]:
        """Load and cache policy configuration.
        
        Returns:
            Policy configuration dictionary
            
        Loads from Rules/file-deletion-protection.json.
        """
        with open(self.policy_file, 'r') as f:
            return json.load(f)
    
    def execute(self, context: Dict[str, Any]) -> str:
        """Execute file deletion protection logic.
        
        Args:
            context: Context from hook handler with governance information
            
        Returns:
            Action result: "block", "warn", "direct", or "allow"
            
        Process:
        1. Load policy configuration (cached)
        2. Extract context information
        3. Evaluate policy conditions
        4. Return appropriate action result
        """
        try:
            # Load policy configuration
            policy = self._load_policy()
            
            # Extract context information
            action_type = context.get("action_type", "")
            resource = context.get("resource", "")
            agent_identity = context.get("agent_identity", "")
            
            # Evaluate policy conditions
            if self._should_block_deletion(policy, action_type, resource):
                return "block"
            elif self._should_warn_deletion(policy, action_type, resource):
                return "warn"
            elif self._should_direct_deletion(policy, action_type, resource):
                return "direct"
            else:
                return "allow"
                
        except Exception as e:
            # Fail-closed: block on errors for security-critical policy
            self._log_error(f"Policy execution error: {e}")
            return "block"
    
    def _should_block_deletion(self, policy: Dict[str, Any], 
                             action_type: str, resource: str) -> bool:
        """Check if deletion should be blocked.
        
        Args:
            policy: Policy configuration
            action_type: Action type from context
            resource: Resource path from context
            
        Returns:
            True if should block, False otherwise
            
        Evaluates block conditions from policy rules.
        """
        # Implementation based on policy structure
        block_rules = policy.get("block_rules", [])
        for rule in block_rules:
            if self._matches_condition(rule, action_type, resource):
                return True
        return False
    
    def _should_warn_deletion(self, policy: Dict[str, Any],
                            action_type: str, resource: str) -> bool:
        """Check if deletion should trigger warning.
        
        Args:
            policy: Policy configuration
            action_type: Action type from context
            resource: Resource path from context
            
        Returns:
            True if should warn, False otherwise
        """
        warn_rules = policy.get("warn_rules", [])
        for rule in warn_rules:
            if self._matches_condition(rule, action_type, resource):
                return True
        return False
    
    def _should_direct_deletion(self, policy: Dict[str, Any],
                              action_type: str, resource: str) -> bool:
        """Check if deletion should be directed.
        
        Args:
            policy: Policy configuration
            action_type: Action type from context
            resource: Resource path from context
            
        Returns:
            True if should direct, False otherwise
        """
        direct_rules = policy.get("direct_rules", [])
        for rule in direct_rules:
            if self._matches_condition(rule, action_type, resource):
                return True
        return False
    
    def _matches_condition(self, rule: Dict[str, Any],
                          action_type: str, resource: str) -> bool:
        """Check if context matches rule condition.
        
        Args:
            rule: Policy rule with conditions
            action_type: Action type from context
            resource: Resource path from context
            
        Returns:
            True if condition matches, False otherwise
        """
        # Extract condition from rule
        condition = rule.get("condition", {})
        
        # Check action type match
        if "action_type" in condition:
            if action_type != condition["action_type"]:
                return False
        
        # Check resource pattern match
        if "resource_pattern" in condition:
            import re
            pattern = condition["resource_pattern"]
            if not re.match(pattern, resource):
                return False
        
        return True
    
    def _log_error(self, message: str) -> None:
        """Log error message.
        
        Args:
            message: Error message to log
        """
        # Implementation using standardized logging
        pass
```

**Policy Action Implementation Requirements:**
```python
# Each policy action must:
1. Extend BaseAction class
2. Implement _load_policy() with @lru_cache(maxsize=1)
3. Implement execute() with context-aware logic
4. Implement helper methods for condition evaluation
5. Implement fail-closed error handling
6. Log all operations
7. Follow base.py implementation templates

# Naming convention:
# Action files: [policy-name].py (e.g., file-deletion-protection.py)
# Action classes: [PolicyName]Action (e.g., FileDeletionProtection)
# Policy files: Rules/[policy-name].json (must match action name)
```

**Context Extraction Pattern:**
```python
# Standard context fields to extract:
action_type: Context["action_type"] (e.g., "DELETE", "WRITE")
resource: Context["resource"] (e.g., file path, URL)
agent_identity: Context["agent_identity"] (e.g., agent ID)
access_level: Context["access_level"] (e.g., "WRITE", "READ")
audit_context: Context["audit_context"] (original event metadata)

# Example context extraction:
action_type = context.get("action_type", "")
resource = context.get("resource", "")
agent_identity = context.get("agent_identity", "")
access_level = context.get("access_level", "")
```

**Error Handling Strategy:**
```python
# Error handling hierarchy:
try:
    # Execute policy logic
    pass
except FileNotFoundError:
    # Policy file missing → block (security-critical)
    return "block"
except json.JSONDecodeError:
    # Policy file corrupted → block (security-critical)
    return "block"
except KeyError:
    # Context field missing → block with logging
    self._log_error(f"Missing context field: {e}")
    return "block"
except Exception as e:
    # Unexpected error → block for security policies, allow for observability
    self._log_error(f"Unexpected error: {e}")
    return "block"  # or "allow" for observability policies
```

**Logging Requirements:**
- Log action execution with context summary
- Log action result with decision rationale
- Log policy loading events
- Log cache operations (load, invalidate)
- Log error handling with error details
- Use standardized JSONL format: `{"File": "[PolicyName].py", "component": "Actions", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Actions-Log-DATE.jsonl`
- Implement silent failure for logging errors

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

**Implementation Pattern:**
```python
from Overseer.Actions.base import BaseAction
from typing import Dict, Any, List
import json
import os

class PolicyFormatValidator(BaseAction):
    """Meta-action for policy format validation.
    
    Implements BaseAction interface with meta-rule logic for validating
    policy definitions per ARCHITECTURE.md Principle 4 (Meta Rules).
    """
    
    def __init__(self):
        """Initialize policy format validator meta-action."""
        self.meta_rule_file = "Overseer/Rules/Meta-Rules/policy-format-validator.json"
        self.rules_directory = "Overseer/Rules"
    
    @lru_cache(maxsize=1)
    def _load_policy(self) -> Dict[str, Any]:
        """Load and cache meta-rule configuration.
        
        Returns:
            Meta-rule configuration dictionary
            
        Loads from Rules/Meta-Rules/policy-format-validator.json.
        """
        with open(self.meta_rule_file, 'r') as f:
            return json.load(f)
    
    def execute(self, context: Dict[str, Any]) -> str:
        """Execute policy format validation meta-rule.
        
        Args:
            context: Context with policy definitions or validation trigger
            
        Returns:
            Action result: "block", "warn", or "allow"
            
        Process:
        1. Load meta-rule configuration (cached)
        2. Scan Rules/ directory for policy JSON files
        3. Load and validate each policy definition
        4. Apply meta-rule checks (consistency, completeness, conflicts)
        5. Return validation result
        """
        try:
            # Load meta-rule configuration
            meta_rule = self._load_policy()
            
            # Scan rules directory for policy files
            policy_files = self._scan_policy_directory()
            
            # Load and validate policy definitions
            validation_results = []
            for policy_file in policy_files:
                result = self._validate_policy_file(policy_file, meta_rule)
                validation_results.append(result)
            
            # Aggregate validation results
            if self._has_critical_issues(validation_results):
                return "block"
            elif self._has_warnings(validation_results):
                return "warn"
            else:
                return "allow"
                
        except Exception as e:
            # Fail-closed: block on meta-rule errors
            self._log_error(f"Meta-rule execution error: {e}")
            return "block"
    
    def _scan_policy_directory(self) -> List[str]:
        """Scan Rules/ directory for policy JSON files.
        
        Returns:
            List of policy file paths
            
        Excludes Meta-Rules subdirectory.
        """
        policy_files = []
        for filename in os.listdir(self.rules_directory):
            if filename.endswith('.json') and filename != 'Meta-Rules':
                policy_files.append(os.path.join(self.rules_directory, filename))
        return policy_files
    
    def _validate_policy_file(self, policy_file: str, 
                            meta_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single policy file against meta-rule.
        
        Args:
            policy_file: Path to policy JSON file
            meta_rule: Meta-rule configuration
            
        Returns:
            Validation result dictionary
            
        Validates policy structure, required fields, and rule consistency.
        """
        with open(policy_file, 'r') as f:
            policy = json.load(f)
        
        # Apply meta-rule checks
        checks = meta_rule.get("checks", {})
        results = {}
        
        # Check required fields
        if "required_fields" in checks:
            results["required_fields"] = self._check_required_fields(
                policy, checks["required_fields"]
            )
        
        # Check rule consistency
        if "rule_consistency" in checks:
            results["rule_consistency"] = self._check_rule_consistency(
                policy, checks["rule_consistency"]
            )
        
        # Check naming conventions
        if "naming_conventions" in checks:
            results["naming_conventions"] = self._check_naming_conventions(
                policy, checks["naming_conventions"]
            )
        
        return {
            "policy_file": policy_file,
            "results": results,
            "valid": all(results.values())
        }
    
    def _check_required_fields(self, policy: Dict[str, Any],
                              required_fields: List[str]) -> bool:
        """Check if policy has all required fields.
        
        Args:
            policy: Policy dictionary
            required_fields: List of required field names
            
        Returns:
            True if all required fields present, False otherwise
        """
        for field in required_fields:
            if field not in policy:
                return False
        return True
    
    def _check_rule_consistency(self, policy: Dict[str, Any],
                               consistency_rules: Dict[str, Any]) -> bool:
        """Check if policy rules are consistent.
        
        Args:
            policy: Policy dictionary
            consistency_rules: Consistency rule configuration
            
        Returns:
            True if rules are consistent, False otherwise
        """
        # Check for conflicting rules, duplicate IDs, etc.
        rules = policy.get("rules", [])
        rule_ids = [rule.get("id") for rule in rules]
        
        # Check for duplicate rule IDs
        if len(rule_ids) != len(set(rule_ids)):
            return False
        
        return True
    
    def _check_naming_conventions(self, policy: Dict[str, Any],
                                 naming_rules: Dict[str, Any]) -> bool:
        """Check if policy follows naming conventions.
        
        Args:
            policy: Policy dictionary
            naming_rules: Naming convention configuration
            
        Returns:
            True if naming conventions followed, False otherwise
        """
        # Check policy name, rule IDs, etc. against conventions
        return True  # Placeholder
    
    def _has_critical_issues(self, validation_results: List[Dict[str, Any]]) -> bool:
        """Check if any validation results have critical issues.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            True if critical issues found, False otherwise
        """
        for result in validation_results:
            if not result["valid"]:
                return True
        return False
    
    def _has_warnings(self, validation_results: List[Dict[str, Any]]) -> bool:
        """Check if any validation results have warnings.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            True if warnings found, False otherwise
        """
        # Implement warning detection logic
        return False
    
    def _log_error(self, message: str) -> None:
        """Log error message.
        
        Args:
            message: Error message to log
        """
        # Implementation using standardized logging
        pass
```

**Meta-Action Implementation Requirements:**
```python
# Each meta-action must:
1. Extend BaseAction class
2. Implement _load_policy() with @lru_cache(maxsize=1) from Rules/Meta-Rules/
3. Implement execute() with policy validation logic (not user context)
4. Implement policy directory scanning and loading
5. Implement meta-rule checks (consistency, completeness, conflicts)
6. Implement fail-closed error handling
7. Log all validation operations
8. Follow base.py implementation templates

# Naming convention:
# Meta-action files: Meta-Actions/[meta-rule-name].py (e.g., policy-format-validator.py)
# Meta-action classes: [MetaRuleName]Action (e.g., PolicyFormatValidator)
# Meta-rule files: Rules/Meta-Rules/[meta-rule-name].json
```

**Meta-Action Invocation Points:**
```python
# Invocation triggers for meta-actions:
1. Policy Load:
   - Triggered by policy_loader.load_policies()
   - Validates policies before they are loaded into system
   - Blocks invalid policies from being loaded

2. Configuration Change:
   - Triggered by config watcher on config.json changes
   - Validates policy configuration consistency
   - Warns on configuration issues

3. Manual Invocation:
   - Triggered by CLI command or API call
   - On-demand policy validation
   - Useful for policy development and testing

# Configuration for invocation timing:
# In config.json:
{
  "meta_actions": {
    "policy_format_validator": {
      "enabled": true,
      "triggers": ["policy_load", "config_change", "manual"]
    }
  }
}
```

**Meta-Rule Checks Examples:**
```python
# Common meta-rule checks:
- Required fields: version, name, description, rules present
- Rule consistency: no duplicate rule IDs, no conflicting conditions
- Naming conventions: policy names follow pattern, rule IDs follow pattern
- Policy completeness: all rules have conditions and actions
- Conflict detection: no contradictory rules (allow and deny same condition)
- Version compatibility: policy versions compatible with framework version
```

**Logging Requirements:**
- Log meta-rule execution with validation trigger
- Log policy directory scanning results
- Log individual policy validation results
- Log meta-rule check results (consistency, completeness, conflicts)
- Log validation aggregation results
- Use standardized JSONL format: `{"File": "[MetaRuleName].py", "component": "Actions", "Time": timestamp, "data": {...}}`
- Log file: `Logs/Actions-Log-DATE.jsonl`
- Implement silent failure for logging errors
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
- Does NOT execute code (code is in Actions/)
- Does NOT evaluate logic (evaluation is in Engine)
- Does NOT contain CLI-specific information

**Key Interfaces:**
- Loaded by: Core/engine/policy_loader.py
- Used by: Actions/[PolicyName].py
- Schema: Defined below

**Policy JSON Schema:**
```json
{
  "version": "1.0.0",
  "name": "file-deletion-protection",
  "description": "Protects critical system files from deletion",
  "metadata": {
    "author": "Security Team",
    "created": "2024-01-01",
    "category": "security"
  },
  "enforcement_type": "blocking",
  "rules": [
    {
      "id": "block-etc-deletion",
      "condition": "action_type == 'DELETE' AND resource.contains('/etc/')",
      "action": "deny",
      "rationale": "Prevent deletion of system configuration files",
      "priority": 100,
      "scope": "global"
    },
    {
      "id": "warn-bin-deletion",
      "condition": "action_type == 'DELETE' AND resource.contains('/bin/')",
      "action": "warn",
      "rationale": "Warn before deleting system binaries",
      "priority": 80,
      "scope": "global"
    }
  ]
}
```

**Policy Schema Definition:**
```python
POLICY_SCHEMA = {
    "version": {
        "type": "string",
        "required": True,
        "description": "Semantic versioning (major.minor.patch)",
        "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "name": {
        "type": "string",
        "required": True,
        "description": "Policy identifier (matches action file name)"
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Human-readable policy description"
    },
    "metadata": {
        "type": "object",
        "required": False,
        "description": "Policy metadata (author, created, category, etc.)"
    },
    "enforcement_type": {
        "type": "string",
        "required": False,
        "enum": ["blocking", "advisory", "hybrid"],
        "description": "Policy enforcement mode"
    },
    "rules": {
        "type": "array",
        "required": True,
        "description": "List of rule definitions"
    }
}
```

**Rule Schema Definition:**
```python
RULE_SCHEMA = {
    "id": {
        "type": "string",
        "required": True,
        "description": "Unique rule identifier within policy"
    },
    "condition": {
        "type": "string",
        "required": True,
        "description": "Evaluation logic using condition syntax"
    },
    "action": {
        "type": "string",
        "required": True,
        "enum": ["allow", "deny", "modify", "warn"],
        "description": "Action to take when condition matches"
    },
    "rationale": {
        "type": "string",
        "required": True,
        "description": "Human-readable explanation of rule purpose"
    },
    "priority": {
        "type": "integer",
        "required": False,
        "description": "Rule priority for conflict resolution (higher = more important)"
    },
    "scope": {
        "type": "string",
        "required": False,
        "enum": ["global", "tenant", "agent", "tool"],
        "description": "Rule scope for targeted enforcement"
    },
    "metadata": {
        "type": "object",
        "required": False,
        "description": "Rule-specific metadata"
    }
}
```

**Condition Syntax:**
```python
# Supported condition syntax:
# Field comparisons:
action_type == 'DELETE'
action_type != 'READ'
resource == '/etc/passwd'
resource.contains('/etc/')
resource.startswith('/etc/')
resource.endswith('.conf')

# Logical operators:
AND: "action_type == 'DELETE' AND resource.contains('/etc/')"
OR: "action_type == 'DELETE' OR action_type == 'MODIFY'"
NOT: "NOT resource.contains('/home/')"

# Pattern matching (regex):
resource.matches('^/etc/.*\\.conf$')

# Nested conditions:
"(action_type == 'DELETE' OR action_type == 'MODIFY') AND resource.contains('/etc/')"

# Membership:
agent_identity in ['admin', 'security-team']

# Numeric comparisons:
priority > 50
priority >= 50
priority < 100
priority <= 100

# Available fields in conditions:
action_type: ActionType enum value (READ, WRITE, DELETE, EXECUTE, MODIFY)
resource: Resource identifier (file path, URL, etc.)
agent_identity: Agent identifier (agent ID, user ID, etc.)
access_level: Access level (READ, WRITE, ADMIN)
priority: Rule priority (if evaluating meta-rules)
```

**Condition Syntax Constraints:**
```python
# Restricted evaluation constraints (aligned with evaluator):
# ALLOWED:
- Field comparisons (==, !=, >, <, >=, <=)
- Logical operators (AND, OR, NOT)
- String methods (contains, startswith, endswith, matches for regex)
- Membership (in operator)
- Nested parentheses for grouping

# NOT ALLOWED:
- Import statements
- Arbitrary function calls
- Dunder methods (__import__, __class__, etc.)
- Unsafe attribute access
- Excessive recursion

# All conditions must be compatible with evaluator's restricted expression evaluation.
```

**Policy Naming Convention:**
```python
# Policy file naming:
# Format: [policy-name].json (lowercase, hyphen-separated)
# Examples:
# - file-deletion-protection.json
# - api-rate-limiting.json
# - data-exfiltration-prevention.json

# Policy name field must match file name (without .json extension)
# Example: file-deletion-protection.json → name: "file-deletion-protection"
```

**Rule ID Conventions:**
```python
# Rule ID naming:
# Format: [action]-[scope]-[description] (lowercase, hyphen-separated)
# Examples:
# - block-etc-deletion
# - warn-bin-modification
# - allow-home-read

# Rule IDs must be unique within a policy
# Rule IDs should be descriptive and indicate the action and scope
```

**Example Policy: File Deletion Protection**
```json
{
  "version": "1.0.0",
  "name": "file-deletion-protection",
  "description": "Protects critical system files from deletion",
  "metadata": {
    "author": "Security Team",
    "created": "2024-01-01",
    "category": "security"
  },
  "enforcement_type": "blocking",
  "rules": [
    {
      "id": "block-etc-deletion",
      "condition": "action_type == 'DELETE' AND resource.contains('/etc/')",
      "action": "deny",
      "rationale": "Prevent deletion of system configuration files",
      "priority": 100,
      "scope": "global"
    },
    {
      "id": "block-bin-deletion",
      "condition": "action_type == 'DELETE' AND resource.contains('/bin/')",
      "action": "deny",
      "rationale": "Prevent deletion of system binaries",
      "priority": 100,
      "scope": "global"
    },
    {
      "id": "warn-var-deletion",
      "condition": "action_type == 'DELETE' AND resource.contains('/var/')",
      "action": "warn",
      "rationale": "Warn before deleting variable data files",
      "priority": 80,
      "scope": "global"
    },
    {
      "id": "allow-home-deletion",
      "condition": "action_type == 'DELETE' AND resource.contains('/home/') AND agent_identity == 'admin'",
      "action": "allow",
      "rationale": "Allow admin to delete home directory files",
      "priority": 60,
      "scope": "global"
    }
  ]
}
```

**Validation Requirements:**
- Policy files must validate against POLICY_SCHEMA
- Rules must validate against RULE_SCHEMA
- Rule IDs must be unique within policy
- Condition syntax must be valid and compatible with evaluator
- Version must follow semantic versioning
- Name must match file name
- All required fields must be present

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

**Meta-Rule JSON Schema:**
```json
{
  "version": "1.0.0",
  "name": "policy-format-validator",
  "description": "Validates policy format and structure",
  "checks": [
    {
      "type": "required_fields",
      "parameters": {
        "fields": ["version", "name", "description", "rules"]
      },
      "severity": "critical",
      "description": "Ensures all required policy fields are present"
    },
    {
      "type": "rule_consistency",
      "parameters": {
        "check_duplicate_ids": true,
        "check_conflicting_actions": true
      },
      "severity": "critical",
      "description": "Ensures rules are consistent and not conflicting"
    },
    {
      "type": "naming_conventions",
      "parameters": {
        "policy_name_pattern": "^[a-z-]+$",
        "rule_id_pattern": "^[a-z-]+$"
      },
      "severity": "warning",
      "description": "Ensures policy and rule names follow conventions"
    },
    {
      "type": "conflict_detection",
      "parameters": {
        "check_allow_deny_conflicts": true,
        "check_condition_overlap": true
      },
      "severity": "critical",
      "description": "Detects conflicting rules within policy"
    }
  ]
}
```

**Meta-Rule Schema Definition:**
```python
META_RULE_SCHEMA = {
    "version": {
        "type": "string",
        "required": True,
        "description": "Semantic versioning (major.minor.patch)",
        "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "name": {
        "type": "string",
        "required": True,
        "description": "Meta-rule identifier (matches meta-action file name)"
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Human-readable meta-rule description"
    },
    "checks": {
        "type": "array",
        "required": True,
        "description": "List of validation check definitions"
    }
}
```

**Check Schema Definition:**
```python
CHECK_SCHEMA = {
    "type": {
        "type": "string",
        "required": True,
        "enum": ["required_fields", "rule_consistency", "naming_conventions", "conflict_detection"],
        "description": "Check type defining validation logic"
    },
    "parameters": {
        "type": "object",
        "required": True,
        "description": "Check-specific parameters"
    },
    "severity": {
        "type": "string",
        "required": True,
        "enum": ["critical", "warning"],
        "description": "Severity level for validation failures"
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Human-readable explanation of check purpose"
    }
}
```

**Check Type Parameter Structures:**
```python
# required_fields check parameters:
{
  "fields": ["version", "name", "description", "rules"]
}
# - fields: List of required field names to check

# rule_consistency check parameters:
{
  "check_duplicate_ids": true,
  "check_conflicting_actions": true
}
# - check_duplicate_ids: Check for duplicate rule IDs
# - check_conflicting_actions: Check for conflicting actions on same condition

# naming_conventions check parameters:
{
  "policy_name_pattern": "^[a-z-]+$",
  "rule_id_pattern": "^[a-z-]+$"
}
# - policy_name_pattern: Regex pattern for policy name validation
# - rule_id_pattern: Regex pattern for rule ID validation

# conflict_detection check parameters:
{
  "check_allow_deny_conflicts": true,
  "check_condition_overlap": true
}
# - check_allow_deny_conflicts: Check for allow/deny conflicts
# - check_condition_overlap: Check for overlapping conditions
```

**Meta-Rule Naming Convention:**
```python
# Meta-rule file naming:
# Format: [meta-rule-name].json (lowercase, hyphen-separated)
# Examples:
# - policy-format-validator.json
# - conflict-detector.json
# - completeness-checker.json

# Meta-rule name field must match file name (without .json extension)
# Example: policy-format-validator.json → name: "policy-format-validator"
```

**Example Meta-Rule: Policy Format Validator**
```json
{
  "version": "1.0.0",
  "name": "policy-format-validator",
  "description": "Validates policy format and structure",
  "checks": [
    {
      "type": "required_fields",
      "parameters": {
        "fields": ["version", "name", "description", "rules"]
      },
      "severity": "critical",
      "description": "Ensures all required policy fields are present"
    },
    {
      "type": "rule_consistency",
      "parameters": {
        "check_duplicate_ids": true,
        "check_conflicting_actions": true
      },
      "severity": "critical",
      "description": "Ensures rules are consistent and not conflicting"
    },
    {
      "type": "naming_conventions",
      "parameters": {
        "policy_name_pattern": "^[a-z-]+$",
        "rule_id_pattern": "^[a-z-]+$"
      },
      "severity": "warning",
      "description": "Ensures policy and rule names follow conventions"
    },
    {
      "type": "conflict_detection",
      "parameters": {
        "check_allow_deny_conflicts": true,
        "check_condition_overlap": true
      },
      "severity": "critical",
      "description": "Detects conflicting rules within policy"
    }
  ]
}
```

**Validation Requirements:**
- Meta-rule files must validate against META_RULE_SCHEMA
- Checks must validate against CHECK_SCHEMA
- Check parameters must match check type requirements
- Severity must be either "critical" or "warning"
- Version must follow semantic versioning
- Name must match file name
- All required fields must be present

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
