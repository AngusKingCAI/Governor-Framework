"""
Block Edit Test Action - Block editing of Edit test.md for testing
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class BlockEditTestAction(RuleAction):
    """Action to block editing of Edit test.md for testing rule firing."""
    
    @property
    def name(self) -> str:
        return "block_edit_test"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the block edit test action."""
        tool_name = payload.get("tool_name", "unknown")
        reason = params.get("reason", f"Tool {tool_name} blocked by governance rule")
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("block_edit_test_action", {
            "tool": tool_name,
            "reason": reason
        })
        
        return ActionResult(
            decision="deny",
            reason=reason
        )