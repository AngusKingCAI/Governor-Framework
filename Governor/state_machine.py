"""
State Machine - Phase, bypass, counter state with inline locking
Layer 3: Self-contained. No imports from other Governor files.
"""

import hashlib
import json
import os
import sys
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to state_machine.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"StateMachine-Log-{today}.jsonl")

        entry = {
            "File": "state_machine.py",
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


# State file paths
STATE_DIR = os.path.join(GOVERNOR_ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
CHECKSUM_FILE = os.path.join(STATE_DIR, "state.json.checksum")

# Valid phases
VALID_PHASES = ["INIT", "EXECUTE", "RESEARCH", "PLAN", "VALIDATE", "COMMIT"]

# Compliance states
VALID_COMPLIANCE_STATES = [
    "testing_in_progress",
    "testing_complete",
    "blocked",
    "ready_to_proceed",
]

# Development mode
DEV_MODE = os.getenv("GOVERNOR_DEV_MODE", "0") == "1"


@contextmanager
def _file_lock(lock_path: str):
    """Simple file locking context manager."""
    lock_file = None
    try:
        # Create lock file
        lock_file = open(lock_path, "w")
        # Try to acquire exclusive lock (platform-specific)
        if os.name == "nt":  # Windows
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:  # Unix
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if lock_file:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            try:
                os.remove(lock_path)
            except:
                pass


def _compute_checksum(data: str) -> str:
    """Compute SHA-256 checksum of data."""
    return hashlib.sha256(data.encode()).hexdigest()


class StateMachine:
    """Runtime state machine for Governor."""

    def __init__(self, state_dir: str = STATE_DIR):
        """Initialize state machine."""
        self.state_dir = state_dir
        self.state_path = os.path.join(state_dir, "state.json")
        self.checksum_path = os.path.join(state_dir, "state.json.checksum")
        self.lock_path = os.path.join(state_dir, ".state.lock")

        self._state: Dict[str, Any] = {}
        self._lock = threading.Lock()

        os.makedirs(state_dir, exist_ok=True)
        self._load_state()

    def _load_state(self):
        """Load state from disk with checksum verification."""
        if not os.path.exists(self.state_path):
            self._initialize_state()
            return

        try:
            with open(self.state_path, "r") as f:
                data = f.read()

            # Verify checksum
            if os.path.exists(self.checksum_path):
                with open(self.checksum_path, "r") as f:
                    stored_checksum = f.read().strip()
                computed_checksum = _compute_checksum(data)
                if stored_checksum != computed_checksum:
                    print(
                        "Warning: State checksum mismatch, reinitializing",
                        file=sys.stderr,
                    )
                    self._initialize_state()
                    return

            self._state = json.loads(data)
        except (json.JSONDecodeError, IOError) as e:
            print(
                f"Warning: Failed to load state, reinitializing: {e}", file=sys.stderr
            )
            self._initialize_state()

    def _initialize_state(self):
        """Initialize default state."""
        self._state = {
            "phase": "EXECUTE",
            "current_agent": None,
            "counters": {"exec": 0, "validate": 0},
            "flags": {"research_required": False},
            "bypasses": {"runtime": [], "team": [], "once": [], "session": []},
            "permissions": {"runtime": [], "session": []},
            "violations": [],
            "pending_menus": [],
            "compliance": {
                "state": "testing_in_progress",
                "evidence": [],
                "last_verification": None,
                "blocked_reason": None,
            },
            "metadata": {
                "version": "1.5.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
            },
        }
        self._save_state()

    def _save_state(self):
        """Save state to disk with checksum."""
        self._state["metadata"]["last_updated"] = datetime.utcnow().isoformat()

        data = json.dumps(self._state, indent=2)
        checksum = _compute_checksum(data)

        # Write checksum first
        with open(self.checksum_path, "w") as f:
            f.write(checksum)
            f.flush()
            os.fsync(f.fileno())

        # Write state with atomic operation
        temp_path = self.state_path + ".tmp"
        with open(temp_path, "w") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, self.state_path)

    def get_phase(self) -> str:
        """Get current phase."""
        with self._lock:
            return self._state.get("phase", "EXECUTE")

    def set_phase(self, phase: str):
        """Set current phase."""
        if phase not in VALID_PHASES:
            raise ValueError(f"Invalid phase: {phase}")

        log_execution(
            "StateMachine",
            {"action": "set_phase", "old_phase": self.get_phase(), "new_phase": phase},
        )

        with self._lock:
            self._state["phase"] = phase
            self._save_state()

    def get_counter(self, counter_name: str) -> int:
        """Get counter value."""
        with self._lock:
            return self._state["counters"].get(counter_name, 0)

    def increment_counter(self, counter_name: str):
        """Increment counter."""
        with self._lock:
            old_value = self._state["counters"].get(counter_name, 0)
            self._state["counters"][counter_name] = old_value + 1
            self._save_state()

    def set_counter(self, counter_name: str, value: int):
        """Set counter value."""
        with self._lock:
            self._state["counters"][counter_name] = value
            self._save_state()

    def get_flag(self, flag_name: str) -> bool:
        """Get flag value."""
        with self._lock:
            return self._state["flags"].get(flag_name, False)

    def set_flag(self, flag_name: str, value: bool):
        """Set flag value."""
        with self._lock:
            self._state["flags"][flag_name] = value
            self._save_state()

    def add_bypass(
        self,
        rule_id: str,
        tool_name: str,
        scope: str = "session",
        reason: str = "",
        source: str = "",
    ):
        """Add bypass entry."""
        unique_id = str(uuid.uuid4())
        bypass_key = f"{rule_id}:{tool_name}:{unique_id}"

        log_execution(
            "StateMachine",
            {
                "action": "add_bypass",
                "rule_id": rule_id,
                "tool_name": tool_name,
                "scope": scope,
            },
        )

        with self._lock:
            bypass_entry = {
                "key": bypass_key,
                "rule_id": rule_id,
                "tool_name": tool_name,
                "scope": scope,
                "reason": reason,
                "source": source,
                "created_at": datetime.utcnow().isoformat(),
            }
            self._state["bypasses"][scope].append(bypass_entry)
            self._save_state()

    def is_bypassed(self, rule_id: str, tool_name: str) -> bool:
        """Check if tool is bypassed."""
        with self._lock:
            for scope in ["runtime", "team", "once", "session"]:
                for bypass in self._state["bypasses"][scope]:
                    if bypass["rule_id"] == rule_id or bypass["rule_id"] == "*":
                        if (
                            bypass["tool_name"] == tool_name
                            or bypass["tool_name"] == "*"
                        ):
                            return True
            return False

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get violations list."""
        with self._lock:
            return self._state.get("violations", [])

    def add_violation(self, violation: Dict[str, Any]):
        """Add violation entry."""
        with self._lock:
            self._state["violations"].append(violation)
            self._save_state()

    def clear_permissions(self, scope: str = "session"):
        """Clear permissions for scope."""
        with self._lock:
            self._state["permissions"][scope] = []
            self._save_state()

    def discover_agents(self) -> List[str]:
        """Discover available agents from .devin/agents.json."""
        agents_file = os.path.join(
            os.path.dirname(GOVERNOR_ROOT), ".devin", "agents.json"
        )

        if not os.path.exists(agents_file):
            log_execution(
                "StateMachine",
                {
                    "action": "discover_agents",
                    "status": "file_not_found",
                    "path": agents_file,
                },
            )
            return []

        try:
            with open(agents_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                agents = data.get("agents", [])

                log_execution(
                    "StateMachine",
                    {
                        "action": "discover_agents",
                        "status": "success",
                        "agents": agents,
                    },
                )

                return agents
        except (json.JSONDecodeError, KeyError) as e:
            log_execution(
                "StateMachine",
                {"action": "discover_agents", "status": "error", "error": str(e)},
            )
            return []

    def set_current_agent(self, agent: str) -> bool:
        """Set current agent with validation against discovered agents."""
        available_agents = self.discover_agents()

        if available_agents and agent not in available_agents:
            log_execution(
                "StateMachine",
                {
                    "action": "set_current_agent",
                    "status": "invalid_agent",
                    "agent": agent,
                    "available_agents": available_agents,
                },
            )
            return False

        log_execution(
            "StateMachine",
            {"action": "set_current_agent", "status": "success", "agent": agent},
        )

        with self._lock:
            self._state["current_agent"] = agent
            self._save_state()

        return True

    def get_current_agent(self) -> Optional[str]:
        """Get current agent."""
        with self._lock:
            return self._state.get("current_agent")

    def clear_current_agent(self):
        """Clear current agent."""
        log_execution(
            "StateMachine", {"action": "clear_current_agent", "status": "success"}
        )

        with self._lock:
            self._state["current_agent"] = None
            self._save_state()

    def set_mode(self, mode: str):
        """Set execution mode."""
        with self._lock:
            self._state["mode"] = mode
            self._save_state()

    @property
    def state(self) -> Dict[str, Any]:
        """Get state property for compatibility."""
        return self._state

    @state.setter
    def state(self, value: Dict[str, Any]):
        """Set state property for compatibility."""
        self._state = value

    def get_compliance_state(self) -> str:
        """Get current compliance state."""
        with self._lock:
            return self._state.get("compliance", {}).get("state", "testing_in_progress")

    def set_compliance_state(self, new_state: str, reason: str = None) -> bool:
        """Set compliance state with validation."""
        if new_state not in VALID_COMPLIANCE_STATES:
            log_execution(
                "StateMachine",
                {
                    "action": "set_compliance_state",
                    "error": f"Invalid compliance state: {new_state}",
                    "valid_states": VALID_COMPLIANCE_STATES,
                },
            )
            return False

        with self._lock:
            if "compliance" not in self._state:
                self._state["compliance"] = {
                    "state": "testing_in_progress",
                    "evidence": [],
                    "last_verification": None,
                    "blocked_reason": None,
                }

            current_state = self._state["compliance"]["state"]

            # Validate state transitions
            valid_transitions = {
                "testing_in_progress": ["testing_complete", "blocked"],
                "testing_complete": ["ready_to_proceed", "blocked"],
                "blocked": ["testing_in_progress", "ready_to_proceed"],
                "ready_to_proceed": ["testing_in_progress"],
            }

            if new_state not in valid_transitions.get(current_state, []):
                log_execution(
                    "StateMachine",
                    {
                        "action": "set_compliance_state",
                        "error": f"Invalid state transition: {current_state} -> {new_state}",
                        "valid_transitions": valid_transitions.get(current_state, []),
                    },
                )
                return False

            self._state["compliance"]["state"] = new_state
            if new_state == "blocked" and reason:
                self._state["compliance"]["blocked_reason"] = reason
            elif new_state != "blocked":
                self._state["compliance"]["blocked_reason"] = None

            self._state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            self._save_state()

            log_execution(
                "StateMachine",
                {
                    "action": "set_compliance_state",
                    "previous_state": current_state,
                    "new_state": new_state,
                    "reason": reason,
                },
            )

            return True

    def add_compliance_evidence(
        self, evidence_type: str, evidence_data: Dict[str, Any]
    ) -> bool:
        """Add evidence to compliance state."""
        with self._lock:
            if "compliance" not in self._state:
                self._state["compliance"] = {
                    "state": "testing_in_progress",
                    "evidence": [],
                    "last_verification": None,
                    "blocked_reason": None,
                }

            evidence_entry = {
                "type": evidence_type,
                "data": evidence_data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            self._state["compliance"]["evidence"].append(evidence_entry)
            self._state["compliance"]["last_verification"] = (
                datetime.utcnow().isoformat()
            )
            self._state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            self._save_state()

            log_execution(
                "StateMachine",
                {
                    "action": "add_compliance_evidence",
                    "evidence_type": evidence_type,
                    "evidence_count": len(self._state["compliance"]["evidence"]),
                },
            )

            return True

    def get_compliance_status(self) -> Dict[str, Any]:
        """Get full compliance status for rule checking."""
        with self._lock:
            compliance = self._state.get(
                "compliance",
                {
                    "state": "testing_in_progress",
                    "evidence": [],
                    "last_verification": None,
                    "blocked_reason": None,
                },
            )
            return {
                "state": compliance.get("state", "testing_in_progress"),
                "can_proceed": compliance.get("state") in ["ready_to_proceed"],
                "evidence_count": len(compliance.get("evidence", [])),
                "last_verification": compliance.get("last_verification"),
                "blocked_reason": compliance.get("blocked_reason"),
            }


if __name__ == "__main__":
    """CLI interface for state machine operations."""
    if len(sys.argv) > 1:
        sm = StateMachine()

        if sys.argv[1] == "set_agent" and len(sys.argv) > 2:
            agent = sys.argv[2]
            success = sm.set_current_agent(agent)
            if success:
                print(f"Agent set to: {agent}")
            else:
                print(f"Failed to set agent: {agent}")
                sys.exit(1)
        elif sys.argv[1] == "get_agent":
            agent = sm.get_current_agent()
            print(f"Current agent: {agent}")
        elif sys.argv[1] == "clear_agent":
            sm.clear_current_agent()
            print("Agent cleared")
        elif sys.argv[1] == "list_agents":
            agents = sm.discover_agents()
            print(f"Available agents: {agents}")
        elif sys.argv[1] == "get_compliance":
            status = sm.get_compliance_status()
            print("Compliance Status:")
            print(f"  State: {status['state']}")
            print(f"  Can Proceed: {status['can_proceed']}")
            print(f"  Evidence Count: {status['evidence_count']}")
            print(f"  Last Verification: {status['last_verification']}")
            if status["blocked_reason"]:
                print(f"  Blocked Reason: {status['blocked_reason']}")
        elif sys.argv[1] == "set_compliance" and len(sys.argv) > 2:
            new_state = sys.argv[2]
            reason = sys.argv[3] if len(sys.argv) > 3 else None
            success = sm.set_compliance_state(new_state, reason)
            if success:
                print(f"Compliance state set to: {new_state}")
            else:
                print(f"Failed to set compliance state to: {new_state}")
                sys.exit(1)
        elif sys.argv[1] == "add_evidence" and len(sys.argv) > 2:
            evidence_type = sys.argv[2]
            import json

            try:
                evidence_data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            except json.JSONDecodeError:
                print("Invalid JSON for evidence data")
                sys.exit(1)
            success = sm.add_compliance_evidence(evidence_type, evidence_data)
            if success:
                print(f"Evidence added: {evidence_type}")
            else:
                print("Failed to add evidence")
                sys.exit(1)
        else:
            print(
                "Usage: python state_machine.py [set_agent|get_agent|clear_agent|list_agents|get_compliance|set_compliance|add_evidence] [args]"
            )
            sys.exit(1)
    else:
        print(
            "Usage: python state_machine.py [set_agent|get_agent|clear_agent|list_agents|get_compliance|set_compliance|add_evidence] [args]"
        )
        sys.exit(1)
