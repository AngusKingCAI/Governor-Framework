"""
Overseer.py - Layer 1 Entry Point

Layer 1: Entry point. Own logging. No imports from other Overseer files.
CLI/program agnostic layer that communicates with hook files,
routes events to correct place, and logs actions to /logs.

This module provides the main entry point for the Overseer Framework,
handling hook communication events in a CLI/program agnostic manner
using the Event Adapter Pattern.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod

# Get Overseer package root
OVERSEER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Config file path
CONFIG_PATH = os.path.join(OVERSEER_ROOT, "Config", "config.json")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json.
    
    Returns:
        Configuration dictionary with adapter settings
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log_execution("config", {"event": "config_not_found", "fallback": "devin"})
        return {"adapter": "devin", "default_handler_behavior": "allow"}
    except json.JSONDecodeError as e:
        log_execution("config", {"event": "config_invalid", "error": str(e), "fallback": "devin"})
        return {"adapter": "devin", "default_handler_behavior": "allow"}


def get_adapter(adapter_name: str):
    """
    Dynamically load adapter based on configuration.
    
    Args:
        adapter_name: Name of the adapter to load (e.g., "devin")
        
    Returns:
        Adapter instance
    """
    try:
        # Add both current directory and Overseer directory to path for imports
        current_dir = os.path.dirname(OVERSEER_ROOT)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if OVERSEER_ROOT not in sys.path:
            sys.path.insert(0, OVERSEER_ROOT)
        
        # Import adapter from Adapter directory
        if adapter_name == "devin":
            from Overseer.Adapter.devin_adapter import DevinAdapter
            return DevinAdapter()
        else:
            # Try to dynamically load adapter
            module_name = f"{adapter_name}_adapter"
            adapter_class_name = f"{adapter_name.capitalize()}Adapter"
            
            # Add adapter path to sys.path
            adapter_path = os.path.join(OVERSEER_ROOT, "Adapter")
            if adapter_path not in sys.path:
                sys.path.insert(0, adapter_path)
            
            module = __import__(module_name)
            adapter_class = getattr(module, adapter_class_name)
            return adapter_class()
    except ImportError as e:
        log_execution("adapter", {"event": "adapter_load_failed", "adapter": adapter_name, "error": str(e)})
        raise ValueError(f"Failed to load adapter '{adapter_name}': {e}")


def log_execution(component: str, data: Dict[str, Any]):
    """
    Write to daily JSONL log file - isolated to overseer.py.
    
    Modular logging approach: each module has its own logging function
    for fault isolation. If logging fails in one module, others continue working.
    
    Args:
        component: Component name for log identification
        data: Data to log as JSON
    """
    try:
        log_dir = os.path.join(OVERSEER_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Overseer-Log-{today}.jsonl")

        entry = {
            "File": "overseer.py",
            "component": component,
            "Time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "trace_id": data.get("trace_id", str(uuid.uuid4())),
            "data": data,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    except Exception as e:
        # Silent failure - logging errors shouldn't crash the system
        # Modular logging ensures other modules continue working
        try:
            # Fallback: attempt to write to stderr as last resort
            print(f"Logging failed in overseer.py: {e}", file=sys.stderr)
        except Exception:
            # Ultimate fallback - silently fail
            pass


class StandardEvent:
    """
    Standardized event format for CLI/program agnostic processing.
    
    Transport-specific adapters convert their native format to this
    standard format for unified processing.
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
        self.event_type = event_type  # e.g., "pre_tool_use", "post_tool_use", "permission_request"
        self.source = source  # e.g., "devin", "claude", "cursor"
        self.timestamp = timestamp
        self.data = data  # The original payload data
        self.metadata = metadata or {}
        self.trace_id = trace_id or str(uuid.uuid4())
    
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


class Overseer:
    """
    Main Overseer class for event routing and processing.
    
    Provides CLI-agnostic event processing through handlers.
    Adapters are loaded externally and handle CLI-specific logic.
    """
    
    def __init__(self):
        """Initialize Overseer with handler registry."""
        self.handlers: Dict[str, Callable[[StandardEvent], Dict[str, Any]]] = {}
    
    def register_handler(self, event_type: str, handler: Callable[[StandardEvent], Dict[str, Any]]) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Event type to handle (e.g., "pre_tool_use")
            handler: Callable that processes the event
        
        Raises:
            ValueError: If event_type is empty
        """
        if not event_type or not event_type.strip():
            raise ValueError("Event type cannot be empty")
        
        self.handlers[event_type] = handler
        log_execution("handler_registration", {
            "event_type": event_type,
            "status": "registered"
        })
    
    def handle_event(self, standard_event: StandardEvent) -> Dict[str, Any]:
        """
        Handle a standard event through the Overseer core.
        
        Args:
            standard_event: StandardEvent object with converted event data
            
        Returns:
            Response dictionary from handlers
        """
        trace_id = standard_event.trace_id
        
        log_execution("event_received", {
            "trace_id": trace_id,
            "event_type": standard_event.event_type,
            "source": standard_event.source
        })
        
        try:
            # Route to appropriate handler
            handler = self.handlers.get(standard_event.event_type)
            if not handler:
                log_execution("handler_error", {
                    "trace_id": trace_id,
                    "event_type": standard_event.event_type,
                    "error": "No handler registered for event type"
                })
                return self._build_error_response("No handler for event type", standard_event.source)
            
            # Process event
            handler_response = handler(standard_event)
            
            # Validate handler response structure
            if not isinstance(handler_response, dict):
                log_execution("handler_error", {
                    "trace_id": trace_id,
                    "event_type": standard_event.event_type,
                    "error": "Handler returned non-dict response"
                })
                return self._build_error_response("Handler returned invalid response", standard_event.source)
            
            log_execution("event_processed", {
                "trace_id": trace_id,
                "event_type": standard_event.event_type,
                "decision": handler_response.get("decision", "unknown")
            })
            
            return handler_response
        
        except Exception as e:
            log_execution("processing_error", {
                "trace_id": trace_id,
                "source": standard_event.source,
                "error": str(e)
            })
            return self._build_error_response(f"Processing error: {e}", standard_event.source)
    
    def _build_error_response(self, error_message: str, source: str) -> Dict[str, Any]:
        """Build a standardized error response."""
        return {
            "decision": "deny",
            "reason": error_message,
            "source": source,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        }


def main():
    """
    CLI entry point for Overseer hook handling.
    
    This function allows overseer.py to be called as a CLI script
    by the hooks system, similar to Governor's governor.py.
    
    Usage: python overseer.py <hook_name>
    Reads JSON payload from stdin.
    
    Overseer is CLI-agnostic - all CLI-specific logic is handled by adapters.
    """
    try:
        # Load configuration
        config = load_config()
        adapter_name = config.get("adapter", "devin")
        
        log_execution("config", {
            "event": "config_loaded",
            "adapter": adapter_name,
            "config_file": CONFIG_PATH
        })
        
        # Get hook name from command line argument
        if len(sys.argv) < 2:
            log_execution("error", {"event": "no_hook_name", "error": "No hook name provided"})
            sys.exit(1)
        
        hook_name = sys.argv[1]
        
        # Read JSON payload from stdin
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError as e:
            log_execution("error", {"event": "invalid_json", "error": str(e)})
            sys.exit(1)
        
        trace_id = str(uuid.uuid4())
        
        log_execution(hook_name, {
            "event": "hook_fired",
            "trace_id": trace_id,
            "adapter": adapter_name,
            "payload_keys": list(payload.keys()) if isinstance(payload, dict) else "non_dict"
        })
        
        # Load the appropriate adapter (CLI-specific logic)
        adapter = get_adapter(adapter_name)
        
        log_execution("adapter", {
            "event": "adapter_loaded",
            "adapter": adapter_name,
            "source": adapter.get_source_name()
        })
        
        # Convert hook event to StandardEvent format (adapter handles CLI-specific logic)
        standard_event = adapter.to_standard_event(hook_name, payload)
        
        log_execution("adapter", {
            "event": "event_converted",
            "original_hook": hook_name,
            "standard_event_type": standard_event.event_type,
            "source": standard_event.source
        })
        
        # Create Overseer instance and register handlers
        overseer = Overseer()
        
        # Dynamically register handlers based on adapter's supported events
        # This makes Overseer truly CLI-agnostic - no hardcoded event names
        supported_events = adapter.get_supported_event_types()
        
        for event_type in supported_events:
            overseer.register_handler(event_type, lambda event: {"decision": "allow", "reason": "Default handler - allowing all"})
        
        # Handle the event through Overseer core
        handler_response = overseer.handle_event(standard_event)
        
        log_execution("handler", {
            "event": "handler_response",
            "decision": handler_response.get("decision", "unknown"),
            "reason": handler_response.get("reason", "")
        })
        
        # Convert StandardEvent response back to CLI format (adapter handles CLI-specific logic)
        cli_response = adapter.from_standard_response(handler_response, hook_name)
        
        log_execution(hook_name, {
            "event": "hook_complete",
            "trace_id": trace_id,
            "decision": cli_response.get("decision", "unknown")
        })
        
        print(json.dumps(cli_response, indent=2))
    
    except SystemExit:
        # Re-raise SystemExit to respect exit codes
        raise
    except Exception as e:
        log_execution("error", {
            "event": "cli_error",
            "error": str(e)
        })
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()