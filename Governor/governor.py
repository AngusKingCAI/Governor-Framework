"""
Governor.py - Entry point for Devin CLI hook system
Layer 1: Entry point. Own logging. Imports protocol.py ONLY.
"""

import json
import os
import sys
import traceback
import uuid
from datetime import datetime

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))

# Configuration
FAIL_CLOSED = os.getenv("GOVERNOR_FAIL_CLOSED", "true").lower() == "true"


def log_execution(component: str, data: dict):
    """Write to daily JSONL log file - isolated to governor.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Governor-Log-{today}.jsonl")

        entry = {
            "File": "governor.py",
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


def generate_trace_id():
    """Generate a new UUID4 trace ID."""
    return str(uuid.uuid4())


# Import protocol mapping
try:
    from .protocol import build_hook_response
except ImportError:
    from protocol import build_hook_response

# Import handler registry
try:
    from .hook_handlers import _HOOK_HANDLERS
except ImportError:
    from hook_handlers import _HOOK_HANDLERS

# Import state machine and engine
try:
    from .engine import Engine
    from .state_machine import StateMachine
except ImportError:
    from engine import Engine
    from state_machine import StateMachine


def main():
    """Main entry point for Governor hook handling."""
    try:
        hook_name = sys.argv[1]
        payload = json.loads(sys.stdin.read() or "{}")
        trace_id = generate_trace_id()

        log_execution(hook_name, {"event": "hook_fired", "trace_id": trace_id})

        handler = _HOOK_HANDLERS.get(hook_name)
        if not handler:
            raise ValueError(f"No handler for: {hook_name}")

        state_machine = StateMachine()
        current_agent = state_machine.get_current_agent()
        engine = Engine(current_agent=current_agent)
        response = handler.execute(payload, state_machine, engine)

        # If response is None, handler wants to exit with code 0 (let normal permissions handle it)
        if response is None:
            log_execution(hook_name, {"event": "hook_complete", "decision": "exit_0"})
            sys.exit(0)

        log_execution(
            hook_name, {"event": "hook_complete", "decision": response.get("decision")}
        )
        print(json.dumps(response, indent=2))

    except SystemExit:
        # Re-raise SystemExit to respect exit codes
        raise
    except Exception as e:
        log_execution(
            "error",
            {"event": "hook_error", "error": str(e), "fail_closed": FAIL_CLOSED},
        )
        traceback.print_exc(file=sys.stderr)

        # Build error response based on fail-closed configuration
        if FAIL_CLOSED:
            # Fail-closed: deny on error to maintain security guarantees
            response = build_hook_response(
                internal_decision="deny",
                reason=f"governor_error: {e} (fail-closed mode active)",
                hook_event_name=hook_name if "hook_name" in dir() else "Unknown",
            )
        else:
            # Fail-open: allow on error for availability (legacy behavior)
            response = build_hook_response(
                internal_decision="allow",
                reason=f"governor_error: {e} (fail-open mode active)",
                hook_event_name=hook_name if "hook_name" in dir() else "Unknown",
            )
        print(json.dumps(response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
