"""
Block App Edits Action - Block architect agent from modifying files in App directory
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class BlockAppEditsAction(RuleAction):
    """Action to block architect agent from modifying files in App directory."""
    
    @property
    def name(self) -> str:
        return "block_app_edits"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the block app edits action."""
        tool_name = payload.get("tool_name", "unknown")
        reason = params.get("reason", f"Tool {tool_name} blocked by governance rule")
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("block_app_edits_action", {
            "tool": tool_name,
            "reason": reason
        })
        
        return ActionResult(
            decision="deny",
            reason=reason
        )