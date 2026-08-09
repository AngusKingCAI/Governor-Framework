"""
Inject Research Guidance Action - Add research-first guidance for questions
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class InjectResearchGuidanceAction(RuleAction):
    """Action to inject research-first guidance when user asks questions."""
    
    @property
    def name(self) -> str:
        return "inject_research_guidance"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the research guidance injection action."""
        # UserPromptSubmit payload uses 'prompt' field, not 'user_prompt'
        user_prompt = payload.get("prompt", payload.get("user_prompt", ""))
        
        # Check if prompt contains a question mark
        has_question = "?" in user_prompt
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("inject_research_guidance_action", {
            "has_question": has_question,
            "prompt_length": len(user_prompt)
        })
        
        if has_question:
            guidance = """

=== RESEARCH-FIRST APPROACH ===
The user has asked a question (contains "?"). Follow this approach:

1. RESEARCH FIRST: Use web search to find current information and best practices
2. ANSWER-FIRST: Provide a direct answer to the question based on research
3. OFFER IMPLEMENTATION: After answering, offer to implement if appropriate
4. AVOID DIRECT IMPLEMENTATION: Do not implement code until the question is answered

This ensures questions get proper research and answers before any implementation work.
"""
            return ActionResult(
                decision="allow",
                reason="Question detected - research guidance injected",
                additional_context=guidance
            )
        else:
            return ActionResult(
                decision="allow",
                reason="No question detected - normal proceeding"
            )
