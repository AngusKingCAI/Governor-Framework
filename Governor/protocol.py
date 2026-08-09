"""
Protocol mapping layer for Governor.py v1.5

This module provides the interface between Governor's internal decision model
and the Devin CLI hook protocol. It implements the two-tier decision model
specified in v1.5 spec §4.4.

Key Functions:
- to_devin_decision(): Maps internal decisions to Devin protocol decisions
- build_hook_response(): Builds Devin-compatible hook responses with proper field placement

Protocol Isolation Benefits:
- Internal decision logic is decoupled from Devin CLI protocol format
- Changes to Devin protocol only require updates to this module
- Internal actions can use descriptive decision names (allow/deny/modify/warn)
- Protocol compliance is guaranteed through explicit mapping

Note: This is a pure protocol mapping layer with no internal state or logging.
"""

from typing import Optional


def to_devin_decision(internal: str, permission_decision: Optional[str] = None) -> str:
    """
    Map internal decisions to Devin protocol decisions.

    Governor uses a richer internal decision model with 4 states:
    - allow: Permitted execution
    - deny: Blocked execution
    - modify: Permitted with payload modification
    - warn: Permitted with warning context

    Devin CLI protocol uses 3 states:
    - approve: Permitted (maps to allow/modify/warn)
    - block: Blocked (maps to deny)
    - ask: Request user input (maps to deny with permissionDecision="ask")

    Args:
        internal: Internal decision string ("allow", "deny", "modify", "warn")
        permission_decision: Optional permission decision for PermissionRequest hook

    Returns:
        Devin protocol decision string ("approve", "block", "ask")

    Raises:
        ValueError: If internal decision is not recognized

    Example:
        >>> to_devin_decision("allow")
        'approve'
        >>> to_devin_decision("deny")
        'block'
        >>> to_devin_decision("deny", permission_decision="ask")
        'ask'
    """
    # If permission_decision is "ask", return "ask" for the bypass dialog
    if permission_decision == "ask":
        return "ask"

    mapping = {
        "allow": "approve",
        "modify": "approve",
        "warn": "approve",
        "deny": "block",
    }

    if internal not in mapping:
        raise ValueError(f"Unknown internal decision: {internal!r}")
    return mapping[internal]


def build_hook_response(
    internal_decision: str,
    reason: str,
    hook_event_name: str,
    *,
    additional_context: str = "",
    updated_input: Optional[dict] = None,
    bypass_menu: Optional[dict] = None,
    permission_decision: Optional[str] = None,
    permission_decision_reason: Optional[str] = None,
) -> dict:
    """
    Build Devin-compatible hook response with explicit keyword-only parameters.

    This function constructs the complete hook response JSON that Governor returns
    to Devin CLI. It ensures proper field placement per v1.5 spec §4.4:
    - governor_internal at top level (not nested in hookSpecificOutput)
    - Conditional field addition for updatedInput (only when internal_decision == "modify")
    - Conditional field addition for permissionDecision (only when not None)

    Args:
        internal_decision: Internal decision string ("allow", "deny", "modify", "warn")
        reason: Human-readable explanation for the decision
        hook_event_name: Name of the hook event (e.g., "PreToolUse", "SessionStart")
        additional_context: Optional context to inject into agent's prompt
        updated_input: Modified tool input (only used when internal_decision == "modify")
        bypass_menu: Optional bypass menu payload for interactive permission
        permission_decision: Optional permission decision for PermissionRequest hook

    Returns:
        Complete hook response dict compliant with Devin CLI protocol

    Example:
        >>> build_hook_response("allow", "Tool is allowed", "PreToolUse")
        {
            "decision": "approve",
            "governor_internal": {"decision": "allow"},
            "reason": "Tool is allowed",
            "hookSpecificOutput": {"hookEventName": "PreToolUse"}
        }
    """
    # When permission_decision is "ask", only return hookSpecificOutput (no decision field)
    # This matches the working implementation from git history commit 38d06bd
    if permission_decision == "ask":
        response = {
            "hookSpecificOutput": {
                "hookEventName": hook_event_name,
                "permissionDecision": "ask",
                "permissionDecisionReason": permission_decision_reason or reason,
            }
        }
        return response

    response = {
        "decision": to_devin_decision(internal_decision, permission_decision),
        "governor_internal": {"decision": internal_decision},
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
        },
    }

    # Conditional field addition per spec
    if additional_context:
        response["hookSpecificOutput"]["additionalContext"] = additional_context
    if updated_input is not None and internal_decision == "modify":
        response["hookSpecificOutput"]["updatedInput"] = updated_input
    if bypass_menu is not None:
        response["hookSpecificOutput"]["bypass_menu"] = bypass_menu

    return response
