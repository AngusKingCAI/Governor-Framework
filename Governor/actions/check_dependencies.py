"""
Check Dependencies Action - Verify and install required packages
Layer 4: Action. Imports _base.py ONLY.
"""

import sys
import subprocess
from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class CheckDependenciesAction(RuleAction):
    """Action to check and install required dependencies."""
    
    @property
    def name(self) -> str:
        return "check_dependencies"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the dependency check action."""
        required_packages = ["pyyaml", "jsonschema", "ruff"]
        missing_packages = []
        installation_results = {}
        
        # Check if each required package is installed
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        # Install missing packages
        if missing_packages:
            from ._base import log_execution
            log_execution("check_dependencies_action", {
                "action": "installing_packages",
                "missing_packages": missing_packages
            })
            
            for package in missing_packages:
                try:
                    # Use pip to install the package
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        installation_results[package] = "success"
                        log_execution("check_dependencies_action", {
                            "action": "install_success",
                            "package": package
                        })
                    else:
                        installation_results[package] = f"failed: {result.stderr}"
                        log_execution("check_dependencies_action", {
                            "action": "install_failed",
                            "package": package,
                            "error": result.stderr
                        })
                except subprocess.TimeoutExpired:
                    installation_results[package] = "timeout"
                    log_execution("check_dependencies_action", {
                        "action": "install_timeout",
                        "package": package
                    })
                except Exception as e:
                    installation_results[package] = f"error: {str(e)}"
                    log_execution("check_dependencies_action", {
                        "action": "install_error",
                        "package": package,
                        "error": str(e)
                    })
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("check_dependencies_action", {
            "required_packages": required_packages,
            "missing_packages": missing_packages,
            "installation_results": installation_results,
            "status": "all_installed" if not missing_packages else "attempted_installation"
        })
        
        # Return allow regardless (non-blocking)
        # Installation failures are logged but don't block the session
        if not missing_packages:
            reason = "All required dependencies are installed."
        elif all(result == "success" for result in installation_results.values()):
            reason = f"Successfully installed missing dependencies: {', '.join(missing_packages)}."
        else:
            failed_packages = [pkg for pkg, result in installation_results.items() if result != "success"]
            reason = f"Failed to install some dependencies: {', '.join(failed_packages)}. Governor features may not work correctly."
        
        return ActionResult(
            decision="allow",
            reason=reason
        )
