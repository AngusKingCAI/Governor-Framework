"""
PostCompaction Handler - Re-inject state after compaction
Layer 2: Handler. Imports _base.py ONLY.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to post_compaction.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "post_compaction.py",
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


class PostCompactionHandler(HookHandler):
    """Handler for PostCompaction hook events."""

    @property
    def hook_name(self) -> str:
        return "PostCompaction"

    @property
    def can_block(self) -> bool:
        return False

    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the PostCompaction handler logic."""
        log_execution("PostCompaction", {"event": "post_compaction"})

        current_phase = state_machine.get_phase()
        exec_count = state_machine.get_counter("exec")

        state_context = f"""
=== GOVERNOR STATE RE-INJECTION ===
Current Phase: {current_phase}
Executions: {exec_count}
=== END STATE RE-INJECTION ===
"""

        return self._build_allow_response(
            reason=f"Post-compaction state re-injection complete. Phase: {current_phase}",
            additional_context=state_context,
        )
