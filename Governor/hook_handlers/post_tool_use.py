"""
PostToolUse Handler - Log execution and increment counters
Layer 2: Handler. Imports _base.py ONLY.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to post_tool_use.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "post_tool_use.py",
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


class PostToolUseHandler(HookHandler):
    """Handler for PostToolUse hook events."""

    @property
    def hook_name(self) -> str:
        return "PostToolUse"

    @property
    def can_block(self) -> bool:
        return False

    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the PostToolUse handler logic."""
        tool_name = payload.get("tool", "unknown")
        tool_status = payload.get("status", "success")

        log_execution(
            "PostToolUse",
            {"event": "post_tool_use", "tool": tool_name, "status": tool_status},
        )

        # Evaluate rules via engine (engine handles ActionContext creation)
        additional_context = ""
        if engine:
            rule_results = engine.evaluate_rules("PostToolUse", payload, state_machine)

            # Collect additional_context from rule results
            for result in rule_results:
                if result.additional_context:
                    additional_context += result.additional_context
                    log_execution(
                        "PostToolUse",
                        {"action": "context_injected", "source": result.reason},
                    )

        # Increment counter for successful execution
        if tool_status == "success":
            state_machine.increment_counter("exec")

        return self._build_allow_response(
            reason=f"Tool execution logged: {tool_name}",
            additional_context=additional_context,
        )
