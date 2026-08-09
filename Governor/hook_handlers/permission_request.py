"""
PermissionRequest Handler - Custom permission logic
Layer 2: Handler. Imports _base.py ONLY.
"""

import json
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration
FAIL_CLOSED = os.getenv("GOVERNOR_FAIL_CLOSED", "true").lower() == "true"


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to permission_request.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "permission_request.py",
            "component": component,
            "Time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "data": data,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    except Exception:
        # Silent failure - logging errors shouldn't crash the system
        pass


try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class PermissionRequestHandler(HookHandler):
    """Handler for PermissionRequest hook events."""

    @property
    def hook_name(self) -> str:
        return "PermissionRequest"

    @property
    def can_block(self) -> bool:
        return True

    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the PermissionRequest handler logic."""
        tool_name = payload.get("tool_name", "unknown")

        log_execution(
            "PermissionRequest", {"event": "permission_request", "tool": tool_name}
        )

        try:
            # Evaluate rules via engine (engine handles ActionContext creation)
            if engine:
                rule_results = engine.evaluate_rules(
                    "PermissionRequest", payload, state_machine
                )

                for result in rule_results:
                    if result.decision == "deny":
                        if result.permission_decision == "ask":
                            return self._build_response(
                                internal_decision="deny",
                                reason=result.reason,
                                permission_decision="ask",
                                permission_decision_reason=result.permission_decision_reason
                                or result.reason,
                            )
                        return self._build_deny_response(
                            reason=f"Rule blocked: {result.reason}"
                        )

            # No Governor rule matched - return None to let normal permissions handle it
            log_execution(
                "PermissionRequest", {"event": "no_rule_match", "action": "return_none"}
            )
            return None

        except Exception as e:
            # Log the exception
            log_execution(
                "PermissionRequest",
                {
                    "event": "handler_error",
                    "error": str(e),
                    "fail_closed": FAIL_CLOSED,
                    "tool": tool_name,
                },
            )
            traceback.print_exc(file=sys.stderr)

            # Apply fail-closed logic
            if FAIL_CLOSED:
                # Fail-closed: deny on error to maintain security guarantees
                log_execution(
                    "PermissionRequest",
                    {"event": "fail_closed_deny", "error": str(e), "tool": tool_name},
                )
                return self._build_deny_response(
                    reason=f"Governor error in PermissionRequest handler: {e} (fail-closed mode active)"
                )
            else:
                # Fail-open: allow on error for availability (legacy behavior)
                log_execution(
                    "PermissionRequest",
                    {"event": "fail_open_allow", "error": str(e), "tool": tool_name},
                )
                # Return None to let normal permissions handle it
                return None
