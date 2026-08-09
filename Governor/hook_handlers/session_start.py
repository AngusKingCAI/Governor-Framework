"""
SessionStart Handler - Initialize session
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
    """Log execution to daily JSONL file - isolated to session_start.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "session_start.py",
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


class SessionStartHandler(HookHandler):
    """Handler for SessionStart hook events."""

    @property
    def hook_name(self) -> str:
        return "SessionStart"

    @property
    def can_block(self) -> bool:
        return False

    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the SessionStart handler logic."""
        log_execution(
            "SessionStart",
            {"event": "session_start", "session_id": payload.get("session_id", "")},
        )

        try:
            # Evaluate rules via engine (engine handles ActionContext creation)
            if engine:
                rule_results = engine.evaluate_rules(
                    "SessionStart", payload, state_machine
                )

                # Log rule evaluation results (SessionStart is non-blocking)
                for result in rule_results:
                    log_execution(
                        "SessionStart",
                        {
                            "action": "rule_evaluated",
                            "rule_result": result.decision,
                            "rule_reason": result.reason,
                        },
                    )

            # Initialize phase to EXECUTE
            state_machine.set_phase("EXECUTE")

            # Reset counters
            state_machine.set_counter("exec", 0)
            state_machine.set_counter("validate", 0)

            # Detect and set current agent from environment or default to architect
            active_agent = os.environ.get("ACTIVE_AGENT", "architect")
            state_machine.set_current_agent(active_agent)

            log_execution(
                "SessionStart",
                {
                    "action": "agent_detection",
                    "detected_agent": active_agent,
                    "source": "environment",
                },
            )

            # Load environment bypasses
            bypass_env = os.environ.get("GOVERNOR_BYPASSES", "")
            if bypass_env:
                for bypass_key in bypass_env.split(","):
                    bypass_key = bypass_key.strip()
                    if bypass_key:
                        parts = bypass_key.split(":")
                        if len(parts) >= 2:
                            rule_id = parts[0]
                            tool_name = parts[1]
                        else:
                            rule_id = bypass_key
                            tool_name = "*"

                        state_machine.add_bypass(
                            rule_id=rule_id,
                            tool_name=tool_name,
                            scope="session",
                            reason="Pre-populated from environment",
                            source="environment",
                        )

            constitution_context = """
=== GOVERNOR CONSTITUTION ===
Governor v1.5 is active. Current phase: EXECUTE

Phase Requirements:
- INIT: Read-only mode for context gathering
- RESEARCH: Information gathering and analysis
- PLAN: Strategy and task planning
- EXECUTE: Implementation and execution
- VALIDATE: Testing and verification
- COMMIT: Final review and commitment

Governance Rules:
- All tool usage is subject to phase-based gating
- Destructive operations require explicit approval
- Violations are logged and may block session completion
- Bypass commands available: /bypass <rule_id>:<tool>

Compliance Status: Active
=== END CONSTITUTION ===
"""

            return self._build_allow_response(
                reason="Session initialized. Governor is active.",
                additional_context=constitution_context,
            )

        except Exception as e:
            # Log the exception
            log_execution(
                "SessionStart",
                {
                    "event": "handler_error",
                    "error": str(e),
                    "fail_closed": FAIL_CLOSED,
                    "session_id": payload.get("session_id", ""),
                },
            )
            traceback.print_exc(file=sys.stderr)

            # Apply fail-closed logic
            if FAIL_CLOSED:
                # Fail-closed: warn on error (SessionStart can't block session)
                log_execution(
                    "SessionStart", {"event": "fail_closed_warning", "error": str(e)}
                )
                constitution_context = """
=== GOVERNOR CONSTITUTION ===
Governor v1.5 is active. Current phase: EXECUTE

! WARNING: Governor error during session initialization: {error}
Governor may not function correctly in fail-closed mode.

Phase Requirements:
- INIT: Read-only mode for context gathering
- RESEARCH: Information gathering and analysis
- PLAN: Strategy and task planning
- EXECUTE: Implementation and execution
- VALIDATE: Testing and verification
- COMMIT: Final review and commitment

Governance Rules:
- All tool usage is subject to phase-based gating
- Destructive operations require explicit approval
- Violations are logged and may block session completion
- Bypass commands available: /bypass <rule_id>:<tool>

Compliance Status: ERROR
=== END CONSTITUTION ===
""".format(error=str(e))
                return self._build_allow_response(
                    reason="Session initialized with error. Governor may not function correctly.",
                    additional_context=constitution_context,
                )
            else:
                # Fail-open: attempt to continue on error for availability
                log_execution(
                    "SessionStart", {"event": "fail_open_continue", "error": str(e)}
                )
                constitution_context = """
=== GOVERNOR CONSTITUTION ===
Governor v1.5 is active. Current phase: EXECUTE

! WARNING: Governor error during session initialization: {error}
Governor operating in fail-open mode.

Phase Requirements:
- INIT: Read-only mode for context gathering
- RESEARCH: Information gathering and analysis
- PLAN: Strategy and task planning
- EXECUTE: Implementation and execution
- VALIDATE: Testing and verification
- COMMIT: Final review and commitment

Governance Rules:
- All tool usage is subject to phase-based gating
- Destructive operations require explicit approval
- Violations are logged and may block session completion
- Bypass commands available: /bypass <rule_id>:<tool>

Compliance Status: ERROR (FAIL-OPEN)
=== END CONSTITUTION ===
""".format(error=str(e))
                return self._build_allow_response(
                    reason="Session initialized with error. Governor operating in fail-open mode.",
                    additional_context=constitution_context,
                )
