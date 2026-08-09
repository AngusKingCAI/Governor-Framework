"""
UserPromptSubmit Handler - Parse bypass commands
Layer 2: Handler. Imports _base.py ONLY.
"""

import json
import os
import re
import sys
import traceback
from datetime import datetime
from typing import Any, Dict

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration
FAIL_CLOSED = os.getenv("GOVERNOR_FAIL_CLOSED", "true").lower() == "true"


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to user_prompt_submit.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "user_prompt_submit.py",
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


class UserPromptSubmitHandler(HookHandler):
    """Handler for UserPromptSubmit hook events."""

    @property
    def hook_name(self) -> str:
        return "UserPromptSubmit"

    @property
    def can_block(self) -> bool:
        return False

    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the UserPromptSubmit handler logic."""
        # UserPromptSubmit payload uses 'prompt' field, not 'user_prompt'
        user_prompt = payload.get("prompt", payload.get("user_prompt", ""))

        log_execution(
            "UserPromptSubmit",
            {"event": "user_prompt_submit", "prompt_length": len(user_prompt)},
        )

        try:
            # Evaluate rules via engine (engine handles ActionContext creation)
            additional_context = ""
            if engine:
                rule_results = engine.evaluate_rules(
                    "UserPromptSubmit", payload, state_machine
                )

                # Collect additional_context from rule results
                for result in rule_results:
                    if result.additional_context:
                        additional_context += result.additional_context
                        log_execution(
                            "UserPromptSubmit",
                            {"action": "context_injected", "source": result.reason},
                        )

            # Parse bypass commands
            bypass_pattern = r"/bypass\s+(\S+)"
            matches = re.findall(bypass_pattern, user_prompt)

            for bypass_key in matches:
                if bypass_key == "all":
                    state_machine.add_bypass(
                        rule_id="*",
                        tool_name="*",
                        scope="once",
                        reason="User requested bypass all",
                        source="user_command",
                    )
                    additional_context += "\n✓ Bypass registered: next tool call only"
                else:
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
                        reason="User requested bypass",
                        source="user_command",
                    )
                    additional_context += f"\n✓ Bypass registered: {bypass_key}"

            return self._build_allow_response(
                reason="User prompt processed", additional_context=additional_context
            )

        except Exception as e:
            # Log the exception
            log_execution(
                "UserPromptSubmit",
                {
                    "event": "handler_error",
                    "error": str(e),
                    "fail_closed": FAIL_CLOSED,
                    "prompt_length": len(user_prompt),
                },
            )
            traceback.print_exc(file=sys.stderr)

            # Apply fail-closed logic
            if FAIL_CLOSED:
                # Fail-closed: deny on error to maintain security guarantees
                log_execution(
                    "UserPromptSubmit", {"event": "fail_closed_deny", "error": str(e)}
                )
                # UserPromptSubmit can't block, so we return an error message in additional_context
                return self._build_allow_response(
                    reason="User prompt processed with error",
                    additional_context=f"\n! Governor error: {e} (fail-closed mode active)",
                )
            else:
                # Fail-open: allow on error for availability (legacy behavior)
                log_execution(
                    "UserPromptSubmit", {"event": "fail_open_allow", "error": str(e)}
                )
                return self._build_allow_response(
                    reason="User prompt processed",
                    additional_context=f"\n! Governor error: {e} (fail-open mode - context may be incomplete)",
                )
