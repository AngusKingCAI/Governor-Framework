"""
Complete Before Proceed Action - Check state machine compliance before allowing edits
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Any, Dict, List

from ._base import ActionContext, ActionResult, RuleAction


class CompleteBeforeProceedAction(RuleAction):
    """Action to check compliance state before allowing tool execution."""

    @property
    def name(self) -> str:
        return "complete_before_proceed"

    def get_required_params(self) -> List[str]:
        return []

    def evaluate(
        self, payload: Dict[str, Any], params: Dict[str, Any], context: ActionContext
    ) -> ActionResult:
        """Evaluate the compliance state check action."""
        # Get state machine from context
        state_machine = context.state_machine

        if not state_machine:
            return ActionResult(
                decision="allow",
                reason="State machine not available - allowing operation",
            )

        # Get compliance status
        compliance_status = state_machine.get_compliance_status()
        current_state = compliance_status.get("state", "testing_in_progress")
        can_proceed = compliance_status.get("can_proceed", False)
        blocked_reason = compliance_status.get("blocked_reason")

        # Log action evaluation
        from ._base import log_execution

        log_execution(
            "complete_before_proceed_action",
            {
                "current_state": current_state,
                "can_proceed": can_proceed,
                "blocked_reason": blocked_reason,
                "evidence_count": compliance_status.get("evidence_count", 0),
            },
        )

        # If state is ready_to_proceed, allow the operation
        if can_proceed:
            return ActionResult(
                decision="allow",
                reason="Compliance state is ready_to_proceed - operation allowed",
            )

        # If state is blocked, deny with reason
        if current_state == "blocked":
            reason = blocked_reason or "Compliance state is blocked"
            return ActionResult(decision="deny", reason=f"Compliance blocked: {reason}")

        # If state is testing_in_progress or testing_complete, deny with guidance
        guidance = f"""
=== COMPLIANCE CHECK FAILED ===
Current compliance state: {current_state}
This operation requires compliance state to be: ready_to_proceed

To proceed:
1. Complete testing of current changes
2. Add compliance evidence using state machine
3. Set compliance state to testing_complete
4. Set compliance state to ready_to_proceed

Example commands:
- state_machine.set_compliance_state(\"testing_complete\")
- state_machine.add_compliance_evidence(\"test_results\", {{\"tests_passed\": True}})
- state_machine.set_compliance_state(\"ready_to_proceed\")

Current evidence count: {compliance_status.get("evidence_count", 0)}
Last verification: {compliance_status.get("last_verification", "None")}
"""
        return ActionResult(
            decision="deny",
            reason=f"Compliance state '{current_state}' does not allow this operation",
            additional_context=guidance,
        )
