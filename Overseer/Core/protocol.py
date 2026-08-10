"""
Protocol Layer - Event Schema Definitions

This module defines the standardized event schemas for the Overseer Framework.
It serves as the single source of truth for event type definitions across all
Overseer components.

Design Principles:
- Schema definitions only (no runtime validation)
- Static type checking via TypedDict
- Zero runtime overhead
- YAGNI compliance (events only, no response formats initially)
- Layer independence (no imports from other Overseer files)
- CLI-agnostic: Core universal events + extensible for CLI-specific events
- Agent-agnostic: Generic schemas applicable to any agent type

Architecture:
- Core Universal Events: Governance-critical events common across all CLIs
- Extensible Events: CLI-specific events handled via adapter translation
- Adapter Pattern: CLI adapters translate native events to universal format

Core Universal Events (governance-critical, common across CLIs):
- session_start: Session initialization (all CLIs)
- user_prompt_submit: User prompt submission (Devin, Claude, VS Code)
- pre_tool_use: Pre-tool use validation (all CLIs)
- post_tool_use: Post-tool use logging (all CLIs)
- permission_request: Permission request handling (Devin, Claude)
- stop: Session stop event (all CLIs)
- session_end: Session termination (Devin, Claude, Cursor)
- subagent_start: Subagent initialization (Claude, Cursor, VS Code)
- subagent_stop: Subagent termination (Claude, Cursor, VS Code)

Extensible Events (CLI-specific, handled via adapters):
- CLI-specific events like UserPromptExpansion, PostToolUseFailure, etc.
- These are handled by adapters and mapped to universal events where possible
- CLI-specific data preserved in metadata field

Usage:
    from Overseer.Core.protocol import StandardEvent, SessionStartEvent
    
    event = StandardEvent(
        event_type="session_start",
        source="devin",
        timestamp="2024-01-15T10:30:00.000Z",
        data={"session_id": "..."}
    )
    
    # Type checking ensures data matches SessionStartEvent schema
    typed_data: SessionStartEvent = event.data

Dependencies:
- No imports from other Overseer files (Layer Independence)
- Standard library only (typing, json, os, sys, datetime, uuid modules)
"""

from typing import TypedDict, NotRequired, Dict, Any, Optional
import uuid
import json
import os
import sys
from datetime import datetime

# Get protocol module directory for logging
PROTOCOL_DIR = os.path.dirname(os.path.abspath(__file__))
OVERSEER_ROOT = os.path.dirname(PROTOCOL_DIR)


def log_protocol_event(component: str, data: Dict[str, Any]):
    """
    Write protocol-specific events to daily JSONL log file.
    
    Modular logging approach: protocol module has its own logging function
    for fault isolation. If logging fails here, other modules continue working.
    
    Args:
        component: Protocol component name (e.g., "protocol_init", "event_creation")
        data: Data to log as JSON
    """
    try:
        log_dir = os.path.join(OVERSEER_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Protocol-Log-{today}.jsonl")

        entry = {
            "File": "protocol.py",
            "component": component,
            "Time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "trace_id": data.get("trace_id", str(uuid.uuid4())),
            "data": data,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    except Exception as e:
        # Silent failure - logging errors shouldn't crash the protocol module
        # Modular logging ensures other modules continue working
        try:
            # Fallback: attempt to write to stderr as last resort
            print(f"Logging failed in protocol.py: {e}", file=sys.stderr)
        except Exception:
            # Ultimate fallback - silently fail
            pass


# =============================================================================
# SECTION 1: StandardEvent Class
# =============================================================================

class StandardEvent:
    """
    Standardized event format for CLI/program agnostic processing.
    
    Transport-specific adapters convert their native format to this
    standard format for unified processing.
    
    Attributes:
        event_type: Type of event (e.g., "pre_tool_use", "post_tool_use")
        source: Source system (e.g., "devin", "claude", "cursor")
        timestamp: ISO 8601 timestamp when event occurred
        data: Original payload data (should match event-specific schema)
        metadata: Optional metadata for additional context
        trace_id: Unique identifier for event tracing
    """
    
    def __init__(
        self,
        event_type: str,
        source: str,
        timestamp: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ):
        self.event_type = event_type
        self.source = source
        self.timestamp = timestamp
        self.data = data
        self.metadata = metadata or {}
        self.trace_id = trace_id or str(uuid.uuid4())
        
        # Log event creation
        log_protocol_event("event_creation", {
            "event_type": event_type,
            "source": source,
            "trace_id": self.trace_id,
            "data_keys": list(data.keys()) if isinstance(data, dict) else "non_dict"
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata,
            "trace_id": self.trace_id
        }


# =============================================================================
# SECTION 2: Event Schema Definitions (TypedDict)
# =============================================================================

class SessionStartEvent(TypedDict):
    """
    Schema for session_start event type.
    
    This event signals the start of a new session and provides initialization
    context for the governance system.
    
    Required Fields:
        session_id: Unique identifier for the session (UUID format)
        timestamp: ISO 8601 timestamp when session started
    
    Optional Fields:
        user_id: User identifier if available
        agent_type: Type of agent (e.g., "architect", "coder")
        environment: Environment context (e.g., "development", "production")
    
    Example:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-15T10:30:00.000Z",
            "user_id": "user_123",
            "agent_type": "architect"
        }
    
    Notes:
        - This event is non-blocking (cannot deny session start)
        - Used to initialize governance state machine
        - Triggers phase initialization to EXECUTE
    """
    session_id: str
    timestamp: str
    user_id: NotRequired[str]
    agent_type: NotRequired[str]
    environment: NotRequired[str]


class UserPromptSubmitEvent(TypedDict):
    """
    Schema for user_prompt_submit event type.
    
    This event represents a user submitting a prompt to the agent.
    
    Required Fields:
        prompt: The user's prompt text
        timestamp: ISO 8601 timestamp when prompt was submitted
        session_id: Session identifier
    
    Optional Fields:
        prompt_id: Unique identifier for this prompt
        context: Additional context about the prompt
        metadata: Extra metadata about the submission
    
    Example:
        {
            "prompt": "Help me implement a feature",
            "timestamp": "2024-01-15T10:31:00.000Z",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "prompt_id": "prompt_456"
        }
    
    Notes:
        - Used to track user interactions
        - May trigger governance checks for sensitive operations
    """
    prompt: str
    timestamp: str
    session_id: str
    prompt_id: NotRequired[str]
    context: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class PreToolUseEvent(TypedDict):
    """
    Schema for pre_tool_use event type.
    
    This event represents a tool being about to be used by the agent.
    This is a governance checkpoint where the system can approve or deny
    the tool usage.
    
    Required Fields:
        tool_name: Name of the tool being used (e.g., "read", "write", "exec")
        tool_args: Arguments passed to the tool
        timestamp: ISO 8601 timestamp when tool use was initiated
        session_id: Session identifier
    
    Optional Fields:
        tool_input: Complete tool input payload
        trace_id: Unique identifier for this tool use
        metadata: Additional metadata about the tool use
    
    Example:
        {
            "tool_name": "read",
            "tool_args": {"file_path": "/path/to/file.txt"},
            "timestamp": "2024-01-15T10:32:00.000Z",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "trace_id": "trace_789"
        }
    
    Notes:
        - This is a blocking event (can deny tool usage)
        - Primary governance checkpoint for tool access control
        - Decision must be returned before tool executes
    """
    tool_name: str
    tool_args: Dict[str, Any]
    timestamp: str
    session_id: str
    tool_input: NotRequired[Dict[str, Any]]
    trace_id: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class PostToolUseEvent(TypedDict):
    """
    Schema for post_tool_use event type.
    
    This event represents a tool that has been used and its results.
    This is primarily for logging and audit purposes.
    
    Required Fields:
        tool_name: Name of the tool that was used
        tool_args: Arguments passed to the tool
        result: Result returned by the tool
        timestamp: ISO 8601 timestamp when tool use completed
        session_id: Session identifier
    
    Optional Fields:
        execution_time: Time taken to execute the tool (milliseconds)
        error: Error message if tool execution failed
        trace_id: Unique identifier for this tool use
        metadata: Additional metadata about the tool use
    
    Example:
        {
            "tool_name": "read",
            "tool_args": {"file_path": "/path/to/file.txt"},
            "result": {"content": "file contents", "success": true},
            "timestamp": "2024-01-15T10:33:00.000Z",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "execution_time": 150
        }
    
    Notes:
        - This is a non-blocking event (for logging only)
        - Used for audit trail and compliance
        - Cannot deny tool usage (already executed)
    """
    tool_name: str
    tool_args: Dict[str, Any]
    result: Dict[str, Any]
    timestamp: str
    session_id: str
    execution_time: NotRequired[int]
    error: NotRequired[str]
    trace_id: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class PermissionRequestEvent(TypedDict):
    """
    Schema for permission_request event type.
    
    This event represents a request for permission to perform an action.
    This is a governance checkpoint for human approval requirements.
    
    Required Fields:
        action: Action being requested (e.g., "file_write", "api_call")
        resource: Resource being accessed (e.g., file path, API endpoint)
        timestamp: ISO 8601 timestamp when permission was requested
        session_id: Session identifier
    
    Optional Fields:
        action_id: Unique identifier for this action
        context: Additional context about the action
        requester: Information about who is requesting permission
        metadata: Additional metadata about the request
    
    Example:
        {
            "action": "file_write",
            "resource": "/path/to/file.txt",
            "timestamp": "2024-01-15T10:34:00.000Z",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "action_id": "action_012"
        }
    
    Notes:
        - This is a blocking event (can deny permission)
        - Used for human-in-the-loop governance
        - Decision must be returned before action proceeds
    """
    action: str
    resource: str
    timestamp: str
    session_id: str
    action_id: NotRequired[str]
    context: NotRequired[str]
    requester: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class StopEvent(TypedDict):
    """
    Schema for stop event type.
    
    This event represents a session being stopped (graceful shutdown).
    
    Required Fields:
        session_id: Session identifier
        timestamp: ISO 8601 timestamp when stop was requested
        reason: Reason for stopping the session
    
    Optional Fields:
        stop_type: Type of stop (e.g., "user_requested", "error", "timeout")
        metadata: Additional metadata about the stop
    
    Example:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-15T10:35:00.000Z",
            "reason": "User requested stop",
            "stop_type": "user_requested"
        }
    
    Notes:
        - This is a non-blocking event (session is already stopping)
        - Used for cleanup and finalization
        - Triggers phase transition to TERMINATED
    """
    session_id: str
    timestamp: str
    reason: str
    stop_type: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class SessionEndEvent(TypedDict):
    """
    Schema for session_end event type.
    
    This event represents the final termination of a session.
    
    Required Fields:
        session_id: Session identifier
        timestamp: ISO 8601 timestamp when session ended
        duration: Total session duration in seconds
    
    Optional Fields:
        end_reason: Reason for session end
        statistics: Session statistics (e.g., tools used, events processed)
        metadata: Additional metadata about the session
    
    Example:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-15T10:36:00.000Z",
            "duration": 3600,
            "end_reason": "normal_completion"
        }
    
    Notes:
        - This is a non-blocking event (session is already ended)
        - Used for final audit trail generation
        - Marks final state transition to COMPLETE
    """
    session_id: str
    timestamp: str
    duration: int
    end_reason: NotRequired[str]
    statistics: NotRequired[Dict[str, Any]]
    metadata: NotRequired[Dict[str, Any]]


class PostCompactionEvent(TypedDict):
    """
    Schema for post_compaction event type.
    
    This event represents the completion of a compaction operation
    (e.g., message history compaction in conversational agents).
    
    Required Fields:
        session_id: Session identifier
        timestamp: ISO 8601 timestamp when compaction completed
        compaction_type: Type of compaction performed
    
    Optional Fields:
        messages_before: Number of messages before compaction
        messages_after: Number of messages after compaction
        compression_ratio: Ratio of compression achieved
        metadata: Additional metadata about the compaction
    
    Example:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-15T10:37:00.000Z",
            "compaction_type": "message_history",
            "messages_before": 1000,
            "messages_after": 500,
            "compression_ratio": 0.5
        }
    
    Notes:
        - This is a non-blocking event (compaction already completed)
        - Used for logging and optimization tracking
        - Typically occurs after long conversations
    """
    session_id: str
    timestamp: str
    compaction_type: str
    messages_before: NotRequired[int]
    messages_after: NotRequired[int]
    compression_ratio: NotRequired[float]
    metadata: NotRequired[Dict[str, Any]]


class SubagentStartEvent(TypedDict):
    """
    Schema for subagent_start event type.
    
    This event represents the initialization of a subagent (background agent).
    Common across Claude, Cursor, and VS Code.
    
    Required Fields:
        session_id: Session identifier
        subagent_id: Unique identifier for the subagent
        timestamp: ISO 8601 timestamp when subagent started
        subagent_type: Type of subagent (e.g., "explore", "general")
    
    Optional Fields:
        task: Task description for the subagent
        parent_agent_id: Parent agent identifier
        metadata: Additional metadata about the subagent
    
    Example:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "subagent_id": "subagent_123",
            "timestamp": "2024-01-15T10:38:00.000Z",
            "subagent_type": "explore",
            "task": "Research best practices"
        }
    
    Notes:
        - This is a non-blocking event (subagent already started)
        - Used for tracking parallel execution
        - Governance may track subagent resource usage
    """
    session_id: str
    subagent_id: str
    timestamp: str
    subagent_type: str
    task: NotRequired[str]
    parent_agent_id: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class SubagentStopEvent(TypedDict):
    """
    Schema for subagent_stop event type.
    
    This event represents the termination of a subagent.
    Common across Claude, Cursor, and VS Code.
    
    Required Fields:
        session_id: Session identifier
        subagent_id: Unique identifier for the subagent
        timestamp: ISO 8601 timestamp when subagent stopped
        status: Final status (e.g., "completed", "failed", "cancelled")
    
    Optional Fields:
        result: Result data if subagent completed successfully
        error: Error message if subagent failed
        duration: Duration of subagent execution in seconds
        metadata: Additional metadata about the subagent
    
    Example:
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "subagent_id": "subagent_123",
            "timestamp": "2024-01-15T10:39:00.000Z",
            "status": "completed",
            "duration": 120
        }
    
    Notes:
        - This is a non-blocking event (subagent already stopped)
        - Used for tracking parallel execution completion
        - May trigger cleanup or result processing
    """
    session_id: str
    subagent_id: str
    timestamp: str
    status: str
    result: NotRequired[Dict[str, Any]]
    error: NotRequired[str]
    duration: NotRequired[int]
    metadata: NotRequired[Dict[str, Any]]


class ExtensibleEvent(TypedDict):
    """
    Generic schema for CLI-specific events that don't map to universal events.
    
    This schema provides flexibility for CLI-specific events while maintaining
    the ability to govern them through the Overseer Framework.
    
    Required Fields:
        event_type: Original CLI-specific event type name
        source: CLI source (e.g., "claude", "cursor", "vscode")
        timestamp: ISO 8601 timestamp when event occurred
        session_id: Session identifier
    
    Optional Fields:
        original_event_name: Original CLI event name before translation
        cli_specific_data: CLI-specific data that doesn't map to universal schema
        mapped_universal_event: Universal event type if mapping exists
        metadata: Additional metadata about the event
    
    Example:
        {
            "event_type": "UserPromptExpansion",
            "source": "claude",
            "timestamp": "2024-01-15T10:40:00.000Z",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "original_event_name": "UserPromptExpansion",
            "cli_specific_data": {"expanded_prompt": "..."}
        }
    
    Notes:
        - Provides extensibility for CLI-specific events
        - Adapters can preserve CLI-specific data in cli_specific_data
        - Governance can still apply basic rules to extensible events
        - Future: May evolve into specific universal events as patterns emerge
    """
    event_type: str
    source: str
    timestamp: str
    session_id: str
    original_event_name: NotRequired[str]
    cli_specific_data: NotRequired[Dict[str, Any]]
    mapped_universal_event: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


# =============================================================================
# SECTION 3: Event Type Registry
# =============================================================================

EVENT_TYPES = {
    # Core Universal Events (governance-critical, common across CLIs)
    "session_start": SessionStartEvent,
    "user_prompt_submit": UserPromptSubmitEvent,
    "pre_tool_use": PreToolUseEvent,
    "post_tool_use": PostToolUseEvent,
    "permission_request": PermissionRequestEvent,
    "stop": StopEvent,
    "session_end": SessionEndEvent,
    "post_compaction": PostCompactionEvent,
    "subagent_start": SubagentStartEvent,
    "subagent_stop": SubagentStopEvent,
    
    # Extensible Event (for CLI-specific events)
    "extensible": ExtensibleEvent,
}

# Log protocol initialization
log_protocol_event("protocol_init", {
    "event": "protocol_layer_initialized",
    "event_types_count": len(EVENT_TYPES),
    "event_types": list(EVENT_TYPES.keys())
})


# =============================================================================
# SECTION 4: Public API
# =============================================================================

__all__ = [
    "StandardEvent",
    # Core Universal Events
    "SessionStartEvent",
    "UserPromptSubmitEvent",
    "PreToolUseEvent",
    "PostToolUseEvent",
    "PermissionRequestEvent",
    "StopEvent",
    "SessionEndEvent",
    "PostCompactionEvent",
    "SubagentStartEvent",
    "SubagentStopEvent",
    # Extensible Event
    "ExtensibleEvent",
    # Registry
    "EVENT_TYPES",
]
