"""
Engine - Load rules, match triggers, execute actions
Layer 3: Self-contained. Imports actions/_base.py ONLY.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to engine.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Engine-Log-{today}.jsonl")

        entry = {
            "File": "engine.py",
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


# Import action base classes
try:
    from .actions._base import ActionContext, ActionResult, RuleAction
except ImportError:
    from actions._base import ActionContext, ActionResult

# Import actions registry
try:
    from .actions import _ACTIONS
except ImportError:
    from actions import _ACTIONS


# Rule directory
RULES_DIR = os.path.join(GOVERNOR_ROOT, "rules")


class Engine:
    """Rule engine for Governor."""

    def __init__(self, current_agent: str = None):
        """Initialize engine."""
        self.rules: List[Dict[str, Any]] = []
        self.current_agent = current_agent
        self._load_rules()

    def _load_rules(self):
        """Load rule YAML files from universal and agent-specific directories."""
        # Load universal rules from Governor/rules/
        self._load_rules_from_dir(RULES_DIR, "universal")

        # Load agent-specific rules from Governor/rules/{agent}/ if agent is set
        if self.current_agent:
            agent_rules_dir = os.path.join(RULES_DIR, self.current_agent)
            self._load_rules_from_dir(agent_rules_dir, f"agent_{self.current_agent}")

        log_execution(
            "Engine", {"action": "load_rules_complete", "total_rules": len(self.rules)}
        )

    def _load_rules_from_dir(self, rules_dir: str, source: str):
        """Load rules from a specific directory."""
        if not os.path.exists(rules_dir):
            log_execution(
                "Engine",
                {
                    "action": "load_rules",
                    "status": "no_dir",
                    "source": source,
                    "path": rules_dir,
                },
            )
            return

        try:
            import yaml
        except ImportError:
            print("Warning: yaml not installed, rules not loaded", file=sys.stderr)
            log_execution(
                "Engine",
                {"action": "load_rules", "status": "yaml_missing", "source": source},
            )
            return

        for filename in os.listdir(rules_dir):
            if not filename.endswith(".yaml") and not filename.endswith(".yml"):
                continue

            filepath = os.path.join(rules_dir, filename)
            try:
                with open(filepath, "r") as f:
                    rule_data = yaml.safe_load(f)
                    if rule_data:
                        # Check if rule has agent field and if it matches current agent
                        rule_agent = rule_data.get("agent")
                        if rule_agent and rule_agent != self.current_agent:
                            log_execution(
                                "Engine",
                                {
                                    "action": "rule_skipped",
                                    "file": filename,
                                    "rule_id": rule_data.get("id", "unknown"),
                                    "reason": "agent_mismatch",
                                    "rule_agent": rule_agent,
                                    "current_agent": self.current_agent,
                                },
                            )
                            continue

                        self.rules.append(rule_data)
                        log_execution(
                            "Engine",
                            {
                                "action": "rule_loaded",
                                "file": filename,
                                "rule_id": rule_data.get("id", "unknown"),
                                "source": source,
                            },
                        )
            except Exception as e:
                print(f"Warning: Failed to load rule {filename}: {e}", file=sys.stderr)
                log_execution(
                    "Engine",
                    {
                        "action": "rule_load_failed",
                        "file": filename,
                        "error": str(e),
                        "source": source,
                    },
                )

    def evaluate_rules(
        self, hook_name: str, payload: Dict[str, Any], state_machine: Any = None
    ) -> List[ActionResult]:
        """Evaluate rules for hook event."""
        # Import ActionContext here (Layer 3 can import from Layer 4)
        try:
            from .actions._base import ActionContext
        except ImportError:
            from actions._base import ActionContext

        # Create context if state_machine provided
        if state_machine:
            context = ActionContext(
                state_machine=state_machine,
                hook_name=hook_name,
                payload=payload,
                trace_id=payload.get("trace_id", "unknown"),
            )
        else:
            context = None

        results = []

        for rule in self.rules:
            if self._matches_trigger(rule, hook_name, payload):
                result = self._execute_rule(rule, payload, context)
                if result:
                    results.append(result)

        return results

    def _matches_trigger(
        self, rule: Dict[str, Any], hook_name: str, payload: Dict[str, Any]
    ) -> bool:
        """Check if rule trigger matches."""
        trigger = rule.get("trigger", {})

        log_execution(
            "Engine",
            {
                "action": "match_trigger_start",
                "rule_id": rule.get("id", "unknown"),
                "hook_name": hook_name,
                "trigger_hook": trigger.get("hook"),
                "trigger_tool": trigger.get("tool"),
                "payload_tool": payload.get("tool_name"),
            },
        )

        # Check hook name
        if trigger.get("hook") != hook_name:
            return False

        # Check tool name(s) if specified
        tool_name = payload.get("tool_name", "")

        # Support both single tool and multiple tools
        if "tool" in trigger:
            if trigger["tool"] != tool_name:
                return False
        elif "tools" in trigger:
            tools = trigger["tools"]
            if isinstance(tools, list):
                if tool_name not in tools:
                    return False
            else:
                # Single tool specified in tools field
                if tools != tool_name:
                    return False

        # Check file path condition if specified in rule
        tool_input = payload.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Log for debugging
        log_execution(
            "Engine",
            {
                "action": "check_condition",
                "file_path": file_path,
                "rule_id": rule.get("id", "unknown"),
            },
        )

        # Check if rule has condition for file path
        check = rule.get("check", {})
        if check:
            condition = check.get("condition", {})
            field = condition.get("field", "")
            operator = condition.get("operator", "")
            pattern = condition.get("pattern", "")

            if field == "tool_input" and pattern:
                # Generic pattern matching for file paths
                import os

                matched = False
                if operator == "equals":
                    filename = os.path.basename(file_path)
                    matched = filename == pattern
                elif operator == "path_contains":
                    matched = pattern in file_path
                elif operator == "path_starts_with":
                    matched = file_path.startswith(pattern)
                elif operator == "path_ends_with":
                    matched = file_path.endswith(pattern)

                log_execution(
                    "Engine",
                    {
                        "action": "condition_result",
                        "rule_id": rule.get("id", "unknown"),
                        "operator": operator,
                        "pattern": pattern,
                        "file_path": file_path,
                        "matched": matched,
                    },
                )

                if not matched:
                    return False

        return True

    def _execute_rule(
        self, rule: Dict[str, Any], payload: Dict[str, Any], context: ActionContext
    ) -> ActionResult:
        """Execute rule action."""
        action_name = rule.get("action", "block_command")
        action_params = rule.get("params", {})
        allow_bypass = action_params.get("allow_bypass", False)

        log_execution(
            "Engine",
            {
                "action": "execute_rule",
                "rule": rule.get("id", "unknown"),
                "action_name": action_name,
                "allow_bypass": allow_bypass,
            },
        )

        # Get action instance
        action = _ACTIONS.get(action_name)
        if not action:
            return ActionResult(
                decision="allow", reason=f"Action not found: {action_name}"
            )

        # Execute action
        try:
            result = action.evaluate(payload, action_params, context)

            # Framework-level bypass handling: transform deny to ask if rule allows bypass
            if result.decision == "deny" and allow_bypass:
                result.permission_decision = "ask"
                result.permission_decision_reason = result.reason
                log_execution(
                    "Engine",
                    {
                        "action": "bypass_allowed",
                        "rule": rule.get("id", "unknown"),
                        "original_decision": "deny",
                        "transformed_to": "ask",
                    },
                )

            return result
        except Exception as e:
            return ActionResult(decision="allow", reason=f"Action execution error: {e}")
