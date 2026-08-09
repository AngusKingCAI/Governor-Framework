"""
SessionEnd Handler - Final logging and cleanup
Layer 2: Handler. Imports _base.py ONLY.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to session_end.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "session_end.py",
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


class SessionEndHandler(HookHandler):
    """Handler for SessionEnd hook events."""

    @property
    def hook_name(self) -> str:
        return "SessionEnd"

    @property
    def can_block(self) -> bool:
        return False

    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the SessionEnd handler logic."""
        log_execution("SessionEnd", {"event": "session_end"})

        # Note: current_agent is NOT cleared here to allow it to persist
        # It will be re-set at the next SessionStart if needed

        current_phase = state_machine.get_phase()
        exec_count = state_machine.get_counter("exec")
        validate_count = state_machine.get_counter("validate")
        violations = state_machine.get_violations()

        compliance_report = f"""
Session Summary:
- Final Phase: {current_phase}
- Executions: {exec_count}
- Validations: {validate_count}
- Violations: {len(violations)}

Compliance Status: {"COMPLIANT" if len(violations) == 0 else "NON-COMPLIANT"}
"""

        return self._build_allow_response(
            reason=f"Session ended. Phase: {current_phase}, Executions: {exec_count}",
            additional_context=compliance_report,
        )
