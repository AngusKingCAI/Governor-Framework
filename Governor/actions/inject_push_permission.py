"""
Inject Push Permission Action - Allow git push when explicitly requested
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class InjectPushPermissionAction(RuleAction):
    """Action to inject push permission when user explicitly requests git push."""
    
    @property
    def name(self) -> str:
        return "inject_push_permission"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the push permission injection action."""
        # UserPromptSubmit payload uses 'prompt' field, not 'user_prompt'
        user_prompt = payload.get("prompt", payload.get("user_prompt", "")).lower()
        
        # Check if prompt contains push-related keywords (more specific to git)
        push_keywords = ["push to git", "git push", "push to", "git push to", "push"]
        has_push_request = any(keyword in user_prompt for keyword in push_keywords)
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("inject_push_permission_action", {
            "has_push_request": has_push_request,
            "prompt_length": len(user_prompt),
            "matched_keywords": [kw for kw in push_keywords if kw in user_prompt]
        })
        
        if has_push_request:
            guidance = """

=== GIT PUSH PERMISSION GRANTED ===
The user has explicitly requested git push operations. You are authorized to:
- Run git push commands
- Push commits to remote repositories
- Proceed with git operations as requested

This explicit user request overrides the default "no auto-push" behavior.
"""
            return ActionResult(
                decision="allow",
                reason="Git push explicitly requested by user",
                additional_context=guidance
            )
        else:
            return ActionResult(
                decision="allow",
                reason="No explicit git push request detected"
            )
