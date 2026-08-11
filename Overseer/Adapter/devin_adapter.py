"""
Devin-Adapter - CLI-Specific Adapter for Devin CLI

This adapter transforms Devin CLI hook events into canonical payloads
for Overseer governance.

Per ARCHITECTURE.md Principle 1 (True Agnosticism):
- All Devin-specific logic lives in this adapter
- Core Overseer has no knowledge of Devin CLI
- Adapter implements SDK interface from BaseAdapter

Based on Devin CLI Hooks Documentation:
- https://docs.devin.ai/cli/extensibility/hooks/lifecycle-hooks
- https://docs.devin.ai/cli/extensibility/hooks/overview
"""

from datetime import datetime, timezone
from typing import Any, Dict, Set
import sys
from pathlib import Path

# Import BaseAdapter and CanonicalPayload
sys.path.append(str(Path(__file__).parent))
from base import BaseAdapter, AdapterCapabilities
sys.path.append(str(Path(__file__).parent.parent / "Core"))
from overseer import CanonicalPayload, HookResult


class DevinAdapter(BaseAdapter):
    """
    Adapter for Devin CLI hook events.
    
    Transforms Devin-specific hook events (PreToolUse, PostToolUse, etc.)
    into CanonicalPayload for Overseer governance evaluation.
    """
    
    def __init__(self, config: Dict[str, Any], log_dir: str):
        """Initialize Devin adapter with configuration."""
        # Extract adapter-specific config from the full config
        adapter_config = config.get("adapter_specific_settings", {}).get("devin", {}).get("config", {})
        super().__init__(adapter_config, log_dir)
        self.adapter_name = "devin_adapter"
        self.full_config = config
        
        self.logger.info({
            "File": "devin_adapter.py",
            "component": "DevinAdapter",
            "Time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "event": "devin_adapter_initialized",
                "supported_events": ["PreToolUse", "PostToolUse", "PermissionRequest", "UserPromptSubmit", "Stop", "SessionStart", "SessionEnd", "PostCompaction"]
            }
        })
    
    def transform_event(self, event: Dict[str, Any]) -> CanonicalPayload:
        """
        Transform Devin hook event to canonical payload.
        
        Args:
            event: Devin hook event data from stdin
                {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "exec",
                    "tool_input": {...},
                    "session_id": "...",
                    "prompt_id": "..."
                }
                
        Returns:
            CanonicalPayload with standardized structure
            
        Raises:
            ValueError: If event is invalid or missing required fields
        """
        hook_event_name = event.get("hook_event_name")
        
        if not hook_event_name:
            raise ValueError("Missing required field: hook_event_name")
        
        # Map Devin hook events to action types
        action_type = self._map_hook_to_action(hook_event_name)
        
        # Extract agent identity from session or config
        agent_identity = event.get("session_id", "unknown_agent")
        
        # Extract resource (tool_name or derived from context)
        resource = event.get("tool_name", "unknown_resource")
        
        # Determine access level based on event type
        access_level = self._determine_access_level(hook_event_name, event)
        
        # Build audit context with full event data
        audit_context = {
            "original_event": event,
            "adapter": "devin_adapter",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Metadata for additional context
        metadata = {
            "session_id": event.get("session_id"),
            "prompt_id": event.get("prompt_id"),
            "tool_input": event.get("tool_input"),
            "hook_event_name": hook_event_name
        }
        
        return CanonicalPayload(
            action_type=action_type,
            agent_identity=agent_identity,
            resource=resource,
            access_level=access_level,
            audit_context=audit_context,
            metadata=metadata
        )
    
    def _map_hook_to_action(self, hook_event_name: str) -> str:
        """Map Devin hook event names to Overseer action types."""
        mapping = {
            "PreToolUse": "tool_execution_pre",
            "PostToolUse": "tool_execution_post",
            "PermissionRequest": "permission_request",
            "UserPromptSubmit": "user_interaction",
            "Stop": "agent_stop",
            "SessionStart": "session_lifecycle",
            "SessionEnd": "session_lifecycle",
            "PostCompaction": "context_management"
        }
        return mapping.get(hook_event_name, "unknown_action")
    
    def _determine_access_level(self, hook_event_name: str, event: Dict[str, Any]) -> str:
        """Determine access level based on event context."""
        # For tool-related events, determine based on tool type
        if hook_event_name in ["PreToolUse", "PostToolUse", "PermissionRequest"]:
            tool_name = event.get("tool_name", "")
            
            # High-risk tools
            if tool_name in ["exec", "edit", "delete"]:
                return "high"
            # Medium-risk tools
            elif tool_name.startswith("mcp__"):
                return "medium"
            # Low-risk tools
            else:
                return "low"
        
        # Non-tool events
        return "system"
    
    def get_capabilities(self) -> AdapterCapabilities:
        """
        Return Devin adapter capabilities.
        
        Returns:
            AdapterCapabilities with supported hooks, events, and schemas
        """
        return AdapterCapabilities(
            supported_hooks={
                "PreToolUse",
                "PostToolUse",
                "PermissionRequest",
                "UserPromptSubmit",
                "Stop",
                "SessionStart",
                "SessionEnd",
                "PostCompaction"
            },
            supported_events={
                "tool_execution",
                "permission_request",
                "user_interaction",
                "session_lifecycle",
                "context_management"
            },
            input_schema={
                "required": ["hook_event_name"],
                "optional": ["tool_name", "tool_input", "tool_response", "session_id", "prompt_id", "prompt", "source", "reason", "summary"]
            },
            output_schema={
                "action_type": "string",
                "agent_identity": "string",
                "resource": "string",
                "access_level": "string",
                "audit_context": "object",
                "metadata": "object"
            }
        )
    
    def register_hooks(self, hook_registry: Any) -> None:
        """
        Register Devin-specific hooks with the hook registry.
        
        Args:
            hook_registry: HookRegistry instance from Overseer core
        """
        # Register hook handlers for each supported event type
        for hook_type in self.get_capabilities().supported_hooks:
            try:
                hook_registry.register_hook(
                    hook_type=hook_type,
                    hook_func=self._create_hook_handler(hook_type),
                    priority=100  # Default priority
                )
                
                self.logger.info({
                    "File": "devin_adapter.py",
                    "component": "DevinAdapter",
                    "Time": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "event": "hook_registered",
                        "hook_type": hook_type
                    }
                })
            except Exception as e:
                self.logger.error({
                    "File": "devin_adapter.py",
                    "component": "DevinAdapter",
                    "Time": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "event": "hook_registration_failed",
                        "hook_type": hook_type,
                        "error": str(e)
                    }
                })
    
    def _create_hook_handler(self, hook_type: str):
        """Create a hook handler function for the given hook type."""
        def handler(event: Dict[str, Any]) -> Any:
            # Transform event to canonical payload
            payload = self.transform_event(event)
            
            # Log the transformation
            self.logger.info({
                "File": "devin_adapter.py",
                "component": "DevinAdapter",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "event_transformed",
                    "hook_type": hook_type,
                    "action_type": payload.action_type,
                    "resource": payload.resource
                }
            })
            
            # Return payload for governance evaluation
            # Note: In full implementation, this would call Overseer for decision
            # For now, return a simple allow result
            return HookResult(
                decision="allow",
                reason=f"Devin adapter transformed {hook_type} event"
            )
        
        return handler
