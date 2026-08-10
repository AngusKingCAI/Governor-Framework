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
import importlib
from datetime import datetime
from typing import TypedDict, NotRequired, Dict, Any, Optional, Callable

# Handle both module import and direct script execution
try:
    from .protocol import StandardEvent, HandlerResponse
except ImportError:
    # When run as script, add the Governor Framework root to path
    # This allows importing Overseer as a package when run as: python Overseer/Core/overseer.py
    framework_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if framework_root not in sys.path:
        sys.path.insert(0, framework_root)
    from Overseer.Core.protocol import StandardEvent, HandlerResponse

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
        # Load allowlist from config for true adapter-agnostic behavior
        config = load_config()
        ALLOWED_ADAPTERS = set(config.get("allowed_adapters", ["devin"]))
        
        # Validate adapter name against allowlist
        if adapter_name not in ALLOWED_ADAPTERS:
            log_execution("adapter", {"event": "adapter_not_allowed", "adapter": adapter_name})
            raise ValueError(f"Adapter '{adapter_name}' is not in the allowlist")
        
        # Import adapter from Adapter directory using consistent dynamic loading
        module_name = f"Overseer.Adapter.{adapter_name}_adapter"
        adapter_class_name = f"{adapter_name.capitalize()}Adapter"
        
        # Use importlib instead of __import__ for security
        module = importlib.import_module(module_name)
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

class Overseer:
    """
    Main Overseer class for event routing and processing.
    
    Provides CLI-agnostic event processing through handlers.
    Adapters are loaded externally and handle CLI-specific logic.
    
    Handler Response Contract:
        All handlers must return HandlerResponse TypedDict with:
        - decision: "allow" or "deny"
        - reason: Explanation for the decision
        - timestamp: ISO 8601 timestamp
        - source: Source system identifier
    """
    
    def __init__(self):
        """Initialize Overseer with handler registry."""
        self.handlers: Dict[str, Callable[[StandardEvent], HandlerResponse]] = {}
    
    def register_handler(self, event_type: str, handler: Callable[[StandardEvent], HandlerResponse]) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Event type to handle (e.g., "pre_tool_use")
            handler: Callable that processes the event and returns HandlerResponse
        
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
    
    def handle_event(self, standard_event: StandardEvent) -> HandlerResponse:
        """
        Handle a standard event through the Overseer core.
        
        Args:
            standard_event: StandardEvent object with converted event data
            
        Returns:
            HandlerResponse from handlers
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
    
    def _build_error_response(self, error_message: str, source: str) -> HandlerResponse:
        """Build a standardized error response following HandlerResponse contract."""
        return {
            "decision": "deny",
            "reason": error_message,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "source": source
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
        
        # Check if stdin contains valid hook JSON before consuming it
        # This preserves TTY for interactive tools that need stdin
        try:
            stdin_content = sys.stdin.read()
            if not stdin_content.strip():
                # Empty stdin - not a hook event, don't process
                sys.exit(0)
            
            payload = json.loads(stdin_content)
            
            # Validate that this looks like hook data by checking for expected fields
            if not isinstance(payload, dict):
                # Not a valid hook payload, don't process
                sys.exit(0)
                
        except json.JSONDecodeError:
            # Invalid JSON - not a hook event, don't process
            sys.exit(0)
        
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
            overseer.register_handler(event_type, lambda event: {
                "decision": "allow",
                "reason": "Default handler - allowing all",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                "source": adapter.get_source_name()
            })
        
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