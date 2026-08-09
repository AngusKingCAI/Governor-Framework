"""
Auto Format Python Action - Run Ruff format and check on Python files
Layer 4: Action. Imports _base.py ONLY.
"""

import subprocess
import sys
import os
from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class AutoFormatPythonAction(RuleAction):
    """Action to auto-format Python files using Ruff."""
    
    @property
    def name(self) -> str:
        return "auto_format_python"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the auto-format Python action."""
        # Get file path from payload
        tool_input = payload.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("auto_format_python_action", {
            "file_path": file_path,
            "is_python_file": file_path.endswith(".py")
        })
        
        # Only process Python files
        if not file_path.endswith(".py"):
            return ActionResult(
                decision="allow",
                reason="Not a Python file, skipping auto-format"
            )
        
        # Check if file exists
        if not os.path.isfile(file_path):
            log_execution("auto_format_python_action", {
                "error": "File not found",
                "file_path": file_path
            })
            return ActionResult(
                decision="allow",
                reason=f"File not found: {file_path}"
            )
        
        format_results = {}
        
        # Run ruff format
        try:
            format_result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            format_results["format_returncode"] = format_result.returncode
            format_results["format_stdout"] = format_result.stdout
            format_results["format_stderr"] = format_result.stderr
            
            log_execution("auto_format_python_action", {
                "action": "ruff_format",
                "file_path": file_path,
                "returncode": format_result.returncode,
                "changed": format_result.returncode != 0
            })
            
        except subprocess.TimeoutExpired:
            format_results["format_error"] = "timeout"
            log_execution("auto_format_python_action", {
                "action": "ruff_format",
                "file_path": file_path,
                "error": "timeout"
            })
        except Exception as e:
            format_results["format_error"] = str(e)
            log_execution("auto_format_python_action", {
                "action": "ruff_format",
                "file_path": file_path,
                "error": str(e)
            })
        
        # Run ruff check --fix
        try:
            check_result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "--fix", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            format_results["check_returncode"] = check_result.returncode
            format_results["check_stdout"] = check_result.stdout
            format_results["check_stderr"] = check_result.stderr
            
            log_execution("auto_format_python_action", {
                "action": "ruff_check_fix",
                "file_path": file_path,
                "returncode": check_result.returncode,
                "fixes_applied": check_result.returncode != 0
            })
            
        except subprocess.TimeoutExpired:
            format_results["check_error"] = "timeout"
            log_execution("auto_format_python_action", {
                "action": "ruff_check_fix",
                "file_path": file_path,
                "error": "timeout"
            })
        except Exception as e:
            format_results["check_error"] = str(e)
            log_execution("auto_format_python_action", {
                "action": "ruff_check_fix",
                "file_path": file_path,
                "error": str(e)
            })
        
        # Log final results
        log_execution("auto_format_python_action", {
            "action": "format_complete",
            "file_path": file_path,
            "results": format_results
        })
        
        return ActionResult(
            decision="allow",
            reason=f"Auto-formatted Python file: {file_path}",
            additional_context=f"\n=== PYTHON AUTO-FORMAT COMPLETE ===\nFile: {file_path}\nRuff format and check --fix executed successfully."
        )
