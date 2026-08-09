"""
Action Base Classes - Simplified ABC for all actions
Layer 4: Base class. NO imports from Governor.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import os
import sys
import json
import inspect
from datetime import datetime

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Actions-Log-{today}.jsonl")
        
        # Get actual caller's file information using inspect
        caller_file = "actions/_base.py"
        try:
            frame = inspect.currentframe().f_back
            if frame:
                caller_file = frame.f_code.co_filename
                # Get just the filename for cleaner logs
                caller_file = os.path.basename(caller_file)
        except Exception:
            pass  # Fall back to default if inspect fails
        
        entry = {
            "File": caller_file,
            "action": component,
            "Time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            
    except Exception as e:
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()


@dataclass
class ActionResult:
    """Result of action execution."""
    decision: str  # "allow" | "deny" | "modify" | "warn"
    reason: str
    modified_payload: Optional[Dict[str, Any]] = None
    additional_context: str = ""
    bypass_key: str = ""
    bypass_menu: Optional[Dict[str, Any]] = None
    permission_decision: Optional[str] = None  # "ask" for bypass menu
    permission_decision_reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate decision value."""
        valid_decisions = ["allow", "deny", "modify", "warn"]
        if self.decision not in valid_decisions:
            raise ValueError(f"Invalid decision: {self.decision}")


@dataclass
class ActionContext:
    """Context provided to actions during execution."""
    state_machine: Any
    hook_name: str
    payload: Dict[str, Any]
    trace_id: str = "unknown"


class RuleAction(ABC):
    """Abstract base class for all Governor actions."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the action name."""
        pass
    
    @abstractmethod
    def get_required_params(self) -> List[str]:
        """Get list of required parameter names."""
        pass
    
    @abstractmethod
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any], 
                 context: ActionContext) -> ActionResult:
        """Evaluate the action with given payload and parameters."""
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        """Validate that all required parameters are provided."""
        required = self.get_required_params()
        missing = [p for p in required if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters for {self.name}: {missing}")
