"""
Hook Handler Base Class - Simplified ABC for all hook handlers
Layer 2: Base class. Imports protocol.py ONLY.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file - isolated to hook_handlers/_base.py."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)

        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Hook-Handler-Log-{today}.jsonl")

        entry = {
            "File": "_base.py",
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


# Import protocol module for response building
try:
    from ..protocol import build_hook_response
except ImportError:
    from protocol import build_hook_response


class HookHandler(ABC):
    """Abstract base class for all hook handlers."""

    @property
    @abstractmethod
    def hook_name(self) -> str:
        """Get the hook name this handler processes."""
        pass

    @property
    @abstractmethod
    def can_block(self) -> bool:
        """Indicate if this handler can block operations."""
        pass

    @abstractmethod
    def execute(
        self, payload: Dict[str, Any], state_machine: Any, engine: Any
    ) -> Dict[str, Any]:
        """Execute the hook handler logic."""
        pass

    def _build_response(
        self,
        internal_decision: str,
        reason: str,
        additional_context: str = "",
        updated_input: Optional[Dict] = None,
        bypass_menu: Optional[Dict] = None,
        permission_decision: Optional[str] = None,
        permission_decision_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a protocol-compliant hook response."""
        return build_hook_response(
            internal_decision=internal_decision,
            reason=reason,
            hook_event_name=self.hook_name,
            additional_context=additional_context,
            updated_input=updated_input,
            bypass_menu=bypass_menu,
            permission_decision=permission_decision,
            permission_decision_reason=permission_decision_reason,
        )

    def _build_allow_response(
        self, reason: str, additional_context: str = ""
    ) -> Dict[str, Any]:
        """Build an allow response."""
        return self._build_response("allow", reason, additional_context)

    def _build_deny_response(
        self, reason: str, additional_context: str = ""
    ) -> Dict[str, Any]:
        """Build a deny response."""
        return self._build_response("deny", reason, additional_context)

    def _build_warn_response(
        self, reason: str, additional_context: str = ""
    ) -> Dict[str, Any]:
        """Build a warn response."""
        return self._build_response("warn", reason, additional_context)
