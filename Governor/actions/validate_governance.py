"""
Validate Governance Action - Validate Governor framework integrity
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class ValidateGovernanceAction(RuleAction):
    """Action to validate Governor framework integrity."""
    
    @property
    def name(self) -> str:
        return "validate_governance"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the governance validation action."""
        scope = params.get("scope", "session_start")
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("validate_governance_action", {
            "scope": scope,
            "action": "governance_validation"
        })
        
        # For session start validation, check critical components
        if scope == "session_start":
            try:
                # Check if critical files exist
                import os
                governor_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                critical_files = [
                    "governor.py",
                    "engine.py", 
                    "state_machine.py",
                    "protocol.py"
                ]
                
                missing_files = []
                for file in critical_files:
                    if not os.path.exists(os.path.join(governor_root, file)):
                        missing_files.append(file)
                
                if missing_files:
                    return ActionResult(
                        decision="allow",
                        reason=f"Governance validation warning: missing critical files {missing_files}",
                        additional_context="Framework may not function correctly. Manual review recommended."
                    )
                
                # Check if actions directory exists and has actions
                actions_dir = os.path.join(governor_root, "actions")
                if not os.path.exists(actions_dir):
                    return ActionResult(
                        decision="allow",
                        reason="Governance validation warning: actions directory missing",
                        additional_context="Framework cannot load governance actions. Manual review recommended."
                    )
                
                # Try to load engine to check rules
                try:
                    from engine import Engine
                    engine = Engine()
                    rule_count = len(engine.rules)
                    log_execution("validate_governance_action", {
                        "validation": "engine_load_success",
                        "rule_count": rule_count
                    })
                except Exception as e:
                    return ActionResult(
                        decision="allow",
                        reason=f"Governance validation warning: engine load failed: {e}",
                        additional_context="Framework rule system may not be functional. Manual review recommended."
                    )
                
                log_execution("validate_governance_action", {
                    "result": "validation_passed"
                })
                
                return ActionResult(
                    decision="allow",
                    reason="Governance framework validation passed"
                )
                
            except Exception as e:
                log_execution("validate_governance_action", {
                    "error": str(e),
                    "result": "validation_error"
                })
                return ActionResult(
                    decision="allow",
                    reason=f"Governance validation error: {e}",
                    additional_context="Framework validation encountered an error. Manual review recommended."
                )
        
        # Default allow for other scopes
        return ActionResult(
            decision="allow",
            reason="Governance validation not applicable for this scope"
        )