"""
Enforce Templates Action - Check if rule follows universal_rule.yaml.tpl format
Layer 4: Action. Imports _base.py ONLY.
"""

from typing import Any, Dict, List

from ._base import ActionContext, ActionResult, RuleAction


class EnforceTemplatesAction(RuleAction):
    """Action to validate rule files against template format."""

    @property
    def name(self) -> str:
        return "enforce_templates"

    def get_required_params(self) -> List[str]:
        return []

    def evaluate(
        self, payload: Dict[str, Any], params: Dict[str, Any], context: ActionContext
    ) -> ActionResult:
        """Evaluate the template validation action."""
        import yaml

        tool_input = payload.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Only validate YAML files in rules directory
        if not (file_path.endswith(".yaml") or file_path.endswith(".yml")):
            return ActionResult(
                decision="allow", reason="Not a YAML file, skipping template validation"
            )

        if "rules" not in file_path:
            return ActionResult(
                decision="allow",
                reason="Not in rules directory, skipping template validation",
            )

        # Log action evaluation
        from ._base import log_execution

        log_execution(
            "enforce_templates_action",
            {"file_path": file_path, "action": "template_validation"},
        )

        try:
            # Read the rule file
            with open(file_path, "r") as f:
                rule_content = yaml.safe_load(f)

            # Check required fields
            required_fields = [
                "id",
                "version",
                "tier",
                "name",
                "description",
                "trigger",
                "action",
            ]
            missing_fields = [
                field for field in required_fields if field not in rule_content
            ]

            if missing_fields:
                return ActionResult(
                    decision="allow",
                    reason=f"Template validation failed: missing required fields {missing_fields}",
                    additional_context=f"Rule missing required fields: {missing_fields}. Follow universal_rule.yaml.tpl template.",
                )

            # Check trigger structure
            trigger = rule_content.get("trigger", {})
            if not trigger:
                return ActionResult(
                    decision="allow",
                    reason="Template validation failed: missing trigger section",
                    additional_context="Rule must have trigger section with hook and optional tool specification.",
                )

            if "hook" not in trigger:
                return ActionResult(
                    decision="allow",
                    reason="Template validation failed: missing hook in trigger",
                    additional_context="Trigger must specify hook (e.g., SessionStart, PreToolUse, PostToolUse)",
                )

            # Check action
            action = rule_content.get("action", "")
            if not action:
                return ActionResult(
                    decision="allow",
                    reason="Template validation failed: missing action",
                    additional_context="Rule must specify action from Governor/actions/",
                )

            # Check params
            if "params" not in rule_content:
                return ActionResult(
                    decision="allow",
                    reason="Template validation failed: missing params section",
                    additional_context="Rule must have params section with at least reason field",
                )

            params = rule_content.get("params", {})
            if "reason" not in params:
                return ActionResult(
                    decision="allow",
                    reason="Template validation failed: missing reason in params",
                    additional_context="Params must include reason field",
                )

            # Template validation passed
            log_execution(
                "enforce_templates_action",
                {"file_path": file_path, "result": "validation_passed"},
            )

            return ActionResult(decision="allow", reason="Template validation passed")

        except Exception as e:
            # Log error but don't block on validation failures
            log_execution(
                "enforce_templates_action",
                {"file_path": file_path, "error": str(e), "result": "validation_error"},
            )

            return ActionResult(
                decision="allow",
                reason=f"Template validation error: {e}",
                additional_context="Template validation encountered an error. Manual review recommended.",
            )
