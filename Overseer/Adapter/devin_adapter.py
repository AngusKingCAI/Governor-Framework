"""
Devin Adapter - Handles Devin CLI specific event conversion.

This adapter converts Devin-specific hook events to StandardEvent format
and converts StandardEvent responses back to Devin's expected protocol format.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from ..Core.protocol import StandardEvent, BaseAdapter


def log_adapter_event(component: str, data: Dict[str, Any]):
    """
    Write adapter-specific events to daily JSONL log file.
    
    Args:
        component: Adapter component name (e.g., "event_conversion", "response_conversion")
        data: Data to log
    """
    try:
        # Get adapter directory (two levels up from this file)
        adapter_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(adapter_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Adapter-Log-{today}.jsonl")

        entry = {
            "File": "devin_adapter.py",
            "component": component,
            "Time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "data": data,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    except Exception:
        # Silent failure - logging errors shouldn't crash the adapter
        pass


class DevinAdapter(BaseAdapter):
    """
    Adapter for Devin CLI hook system.
    
    Handles Devin-specific event name mapping, payload format conversion,
    and response format conversion. Only handles Devin events.
    """

    def __init__(self):
        """Initialize Devin adapter with Devin-specific event name mappings."""
        self.source_name = "devin"
        
        # Devin hook name to StandardEvent type mapping
        self.event_type_mapping = {
            "SessionStart": "session_start",
            "UserPromptSubmit": "user_prompt_submit", 
            "PreToolUse": "pre_tool_use",
            "PostToolUse": "post_tool_use",
            "PermissionRequest": "permission_request",
            "Stop": "stop",
            "SessionEnd": "session_end",
            "PostCompaction": "post_compaction"
        }
        
        log_adapter_event("adapter_init", {
            "event": "adapter_initialized",
            "source": self.source_name,
            "supported_events": len(self.event_type_mapping)
        })

    def get_source_name(self) -> str:
        """Return the source name this adapter handles."""
        return self.source_name
    
    def get_supported_event_types(self) -> list:
        """
        Return list of event types this adapter can handle.
        
        Returns:
            List of StandardEvent type names (snake_case) for Devin events
        """
        return list(self.event_type_mapping.values())

    def get_standard_event_type(self, hook_name: str) -> str:
        """
        Convert Devin hook name to StandardEvent type.
        
        Args:
            hook_name: Devin hook name (e.g., "PreToolUse")
            
        Returns:
            StandardEvent type (e.g., "pre_tool_use")
        """
        return self.event_type_mapping.get(hook_name, hook_name.lower())

    def to_standard_event(self, hook_name: str, payload: Dict[str, Any]) -> StandardEvent:
        """
        Convert Devin hook event to StandardEvent format.
        
        Args:
            hook_name: Devin hook name (e.g., "PreToolUse")
            payload: JSON payload from stdin
            
        Returns:
            StandardEvent object with converted event data
        """
        event_type = self.get_standard_event_type(hook_name)
        
        log_adapter_event("event_conversion", {
            "event": "converting_to_standard",
            "original_hook": hook_name,
            "standard_event_type": event_type,
            "payload_keys": list(payload.keys()) if isinstance(payload, dict) else "non_dict"
        })
        
        # Convert payload to StandardEvent format
        standard_event = StandardEvent(
            event_type=event_type,
            source=self.source_name,
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            data=payload,
            metadata={
                "original_hook_name": hook_name,
                "cli": "devin"
            }
        )
        
        log_adapter_event("event_conversion", {
            "event": "conversion_complete",
            "original_hook": hook_name,
            "standard_event_type": event_type,
            "success": True
        })
        
        return standard_event

    def from_standard_response(self, response: Dict[str, Any], hook_name: str) -> Dict[str, Any]:
        """
        Convert StandardEvent response to Devin protocol format.
        
        Args:
            response: StandardEvent response from handlers
            hook_name: Original Devin hook name for response formatting
            
        Returns:
            Devin-formatted response for stdout
        """
        log_adapter_event("response_conversion", {
            "event": "converting_from_standard",
            "original_hook": hook_name,
            "decision": response.get("decision", "unknown"),
            "reason": response.get("reason", "")
        })
        
        # Devin expects response in specific format based on Governor's protocol
        # Build response following Governor's protocol format
        devin_response = {
            "decision": response.get("decision", "allow"),
            "reason": response.get("reason", "No reason provided"),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "hook_event_name": hook_name
        }
        
        # Include additional fields if present
        if "updated_input" in response:
            devin_response["updated_input"] = response["updated_input"]
        if "additional_context" in response:
            devin_response["additional_context"] = response["additional_context"]
        
        log_adapter_event("response_conversion", {
            "event": "conversion_complete",
            "original_hook": hook_name,
            "decision": devin_response.get("decision"),
            "success": True
        })
            
        return devin_response