"""
Overseer Framework - Central Governance Hub

This module implements the central governance hub for the Overseer Framework,
providing hook orchestration, policy evaluation coordination, and audit logging
while maintaining true agnosticism, fail-closed security, and zero external dependencies.

Architecture Principles Compliance:
- Principle 1: True Agnosticism - Zero hardcoded CLI assumptions
- Principle 2: Modular Architecture - Layer-independent components
- Principle 3: Small Reusable Kernel - Minimal core with zero dependencies
- Principle 4: Rule-Based Governance - Declarative policies with versioning
- Principle 5: In-Path Fail-Closed Enforcement - Block on failure
- Principle 6: Deterministic Discrete Verdicts - Allow/deny/modify
- Principle 7: Stateless and Idempotent - Independent hook decisions
- Principle 8: Standardized Hook Payloads - Canonical payload model
- Principle 9: Audit Trail and Observability - Comprehensive JSONL logging
- Principle 10: Digital Sovereignty - Local installation, vendor independence
- Principle 11: Hook Composability - Chaining, isolation, configurable order
- Principle 13: Timeout Enforcement - Configurable timeouts
- Principle 15: Emergency Controls - Kill switch and halt capability
- Principle 20: Configuration Integrity - Hash-based verification
- Principle 21: Secrets Protection - Detection and redaction
- Principle 23: Input Validation - Prompt injection defense
- Principle 24: Defense in Depth - Layered security
- Principle 25: Least Privilege - Minimum necessary permissions
- Principle 26: Reversibility-Weighted - Risk-based oversight
- Principle 27: Subagent Isolation - No automatic inheritance
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from hmac import compare_digest
from json import JSONDecodeError, dumps, loads
from logging import FileHandler, Formatter, getLogger, Logger
from os import chmod, fsync
from pathlib import Path
from platform import system as platform_system
from re import compile as regex_compile, IGNORECASE
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ============================================================================
# Foundation Classes (Step 1)
# ============================================================================

@dataclass
class GovernanceDecision:
    """Governance decision with full context."""
    decision: str  # "allow", "deny", "modify"
    policy_id: str
    rationale: str
    context: Dict[str, Any]
    evaluated_rules: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CanonicalPayload:
    """Canonical payload model for all hooks (Principle 8)."""
    action_type: str
    agent_identity: str
    resource: str
    access_level: str
    audit_context: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class HookResult:
    """Hook execution result."""
    decision: str  # "allow", "deny", "modify"
    reason: str
    modified_context: Optional[Dict[str, Any]] = None


class HookPhase(Enum):
    """Hook phase enumeration."""
    PRE_TOOL_USE = "pre_tool_use"
    POST_TOOL_USE = "post_tool_use"
    ON_ERROR = "on_error"


# ============================================================================
# Protocol Layer (Step 2)
# ============================================================================

class ProtocolLayer:
    """Protocol layer for canonical payload management (Principle 8)."""
    
    REQUIRED_FIELDS = ["action_type", "agent_identity", "resource", "access_level", "audit_context"]
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def validate_payload(self, payload: CanonicalPayload) -> bool:
        """Validate canonical payload structure."""
        for field in self.REQUIRED_FIELDS:
            if not hasattr(payload, field) or getattr(payload, field) is None or getattr(payload, field) == "":
                self.logger.error({
                    "File": "overseer.py",
                    "component": "ProtocolLayer",
                    "Time": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "event": "payload_validation_failed",
                        "missing_field": field
                    }
                })
                return False
        return True
    
    def log_payload(self, payload: CanonicalPayload, phase: str):
        """Log canonical payload transformation."""
        self.logger.info({
            "File": "overseer.py",
            "component": "ProtocolLayer",
            "Time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "event": "payload_transformed",
                "phase": phase,
                "action_type": payload.action_type,
                "agent_identity": payload.agent_identity,
                "resource": payload.resource,
                "access_level": payload.access_level
            }
        })


# ============================================================================
# Audit Logger (Step 3)
# ============================================================================

class AuditLogger:
    """Structured JSONL logger with tamper-evident audit trail (Principle 9)."""
    
    SECRET_PATTERNS = {
        'api_key': regex_compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?', IGNORECASE),
        'password': regex_compile(r'password["\']?\s*[:=]\s*["\']?([^"\']{6,})["\']?', IGNORECASE),
        'sk_': regex_compile(r'sk[_-]?[a-zA-Z0-9_\-]{16,}', IGNORECASE),
    }
    
    def __init__(self, log_dir: str, component: str):
        self.log_dir = Path(log_dir)
        self.component = component
        self.log_dir.mkdir(parents=True, exist_ok=True)
        # Set restrictive directory permissions (owner only) on Unix-like systems
        if platform_system() != 'Windows':
            chmod(self.log_dir, 0o700)

        # Create date-specific log file
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{component}-Log-{date_str}.jsonl"

        self.logger = getLogger(f"Overseer.{component}")
        self.logger.setLevel(getLogger().level)

        # File handler with JSON formatter
        handler = FileHandler(log_file)
        handler.setFormatter(self._json_formatter())
        self.logger.addHandler(handler)

        # Set restrictive file permissions (owner read/write only) on Unix-like systems
        if platform_system() != 'Windows':
            chmod(log_file, 0o600)

        # Tamper-evident audit trail
        self.previous_hash = self._get_last_hash(log_file)
        self.hash_lock = Lock()
        # NOTE: hash_lock provides thread safety within a single process.
        # Multi-process concurrent writes should be handled at deployment/infrastructure
        # level (e.g., single-writer architecture, external log aggregation service).
    
    def _json_formatter(self) -> Formatter:
        """Custom JSON formatter using stdlib only."""
        class JSONFormatter(Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "File": getattr(record, "File", "unknown"),
                    "component": getattr(record, "component", "unknown"),
                    "data": getattr(record, "data", {})
                }
                return dumps(log_entry)
        return JSONFormatter()
    
    def _get_last_hash(self, log_file: Path) -> str:
        """Get hash of last log entry for chain integrity."""
        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = loads(lines[-1])
                        return last_entry.get("hash", "")
        except Exception:
            pass
        return ""
    
    def _compute_hash(self, entry: Dict[str, Any], previous_hash: str) -> str:
        """Compute hash of entry with previous hash for chain integrity."""
        data = dumps(entry, sort_keys=True) + previous_hash
        return sha256(data.encode()).hexdigest()
    
    def log_decision(self, decision: GovernanceDecision):
        """Log governance decision with tamper-evident protection."""
        # Redact secrets from decision context
        redacted_context = self._redact_secrets(decision.context)
        # Also redact secrets from evaluated_rules
        redacted_rules = self._redact_secrets(decision.evaluated_rules)
        
        log_entry = {
            "timestamp": decision.timestamp,
            "decision": decision.decision,
            "policy_id": decision.policy_id,
            "rationale": decision.rationale,
            "context": redacted_context,
            "evaluated_rules": redacted_rules
        }
        
        # Compute hash with previous hash (hash of redacted data)
        with self.hash_lock:
            entry_hash = self._compute_hash(log_entry, self.previous_hash)
            log_entry["hash"] = entry_hash
            
            # Append to log (append-only)
            log_file = self.log_dir / f"{self.component}-Log-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
            with open(log_file, 'a') as f:
                f.write(dumps(log_entry) + '\n')
                f.flush()
                fsync(f.fileno())
            # Ensure file permissions are set (important for new files on day rollover)
            if platform_system() != 'Windows':
                chmod(log_file, 0o600)

            self.previous_hash = entry_hash
    
    def _redact_secrets(self, data: Any) -> Any:
        """Detect and redact secrets from data."""
        if isinstance(data, str):
            for secret_type, pattern in self.SECRET_PATTERNS.items():
                data = pattern.sub(f'{secret_type}: [REDACTED]', data)
            return data
        elif isinstance(data, dict):
            # Also check dict keys for secret indicators
            redacted_dict = {}
            for k, v in data.items():
                if any(indicator in k.lower() for indicator in ['api_key', 'password', 'token', 'secret', 'private_key']):
                    # Redact values for secret keys
                    redacted_dict[k] = '[REDACTED]'
                else:
                    redacted_dict[k] = self._redact_secrets(v)
            return redacted_dict
        elif isinstance(data, list):
            return [self._redact_secrets(item) for item in data]
        return data
    
    def verify_integrity(self) -> bool:
        """Verify audit log integrity using hash chain."""
        log_file = self.log_dir / f"{self.component}-Log-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
        if not log_file.exists():
            return True
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        previous_hash = ""
        for i, line in enumerate(lines):
            try:
                entry = loads(line)
                entry_hash = entry.get('hash', '')
                
                # Verify hash chain
                computed_hash = self._compute_hash(
                    {k: v for k, v in entry.items() if k != 'hash'},
                    previous_hash
                )
                
                if not compare_digest(computed_hash, entry_hash):
                    self.logger.error({
                        "File": "overseer.py",
                        "component": "AuditLogger",
                        "Time": datetime.now(timezone.utc).isoformat(),
                        "data": {
                            "event": "log_tampering_detected",
                            "line": i
                        }
                    })
                    return False
                
                previous_hash = entry_hash
            except Exception as e:
                self.logger.error({
                    "File": "overseer.py",
                    "component": "AuditLogger",
                    "Time": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "event": "integrity_verification_error",
                        "error": str(e)
                    }
                })
                return False
        
        return True


# ============================================================================
# Config Manager (Step 6)
# ============================================================================

class ConfigManager:
    """Configuration manager with integrity verification (Principle 20)."""
    
    def __init__(self, config_path: str, audit_logger: AuditLogger):
        self.config_path = Path(config_path)
        self.audit_logger = audit_logger
        self.config_hash = self._compute_config_hash()
        self._verify_config_integrity()
        self._store_config_hash()  # Store trusted hash for future verification
        self.config = self._load_config()
        self.config_lock = Lock()
    
    def _compute_config_hash(self) -> str:
        """Compute configuration hash for integrity verification."""
        if self.config_path.exists():
            with open(self.config_path, 'rb') as f:
                return sha256(f.read()).hexdigest()
        return ""
    
    def _verify_config_integrity(self):
        """Verify configuration integrity on load against stored trusted hash."""
        current_hash = self._compute_config_hash()
        hash_file = self.config_path.with_suffix('.sha256')
        
        # If sidecar hash file exists, verify against it
        if hash_file.exists():
            stored_hash = hash_file.read_text().strip()
            if current_hash and stored_hash and not compare_digest(current_hash, stored_hash):
                raise ValueError("Configuration integrity check failed - possible tampering")
        # If no sidecar exists, this is first run - we'll store it after verification
    
    def _store_config_hash(self):
        """Store trusted configuration hash to sidecar file for future verification."""
        if self.config_hash:
            hash_file = self.config_path.with_suffix('.sha256')
            hash_file.write_text(self.config_hash)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return {}
        
        with open(self.config_path, 'r') as f:
            config = loads(f.read())
        
        # Redact secrets from in-memory representation
        return self._redact_secrets(config)
    
    def _redact_secrets(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Redact secrets from configuration."""
        redacted_dict = {}
        for k, v in config.items():
            if any(indicator in k.lower() for indicator in ['api_key', 'password', 'token', 'secret', 'private_key']):
                # Redact values for secret keys
                redacted_dict[k] = '[REDACTED]'
            else:
                redacted_dict[k] = v
        return redacted_dict
    
    def get_adapter_config(self, adapter_name: str) -> Dict[str, Any]:
        """Get configuration for specific adapter."""
        return self.config.get("adapters", {}).get(adapter_name, {})
    
    def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration."""
        return self.config.get("governance", {})
    
    def reload_config(self, authorized_by: str, reason: str):
        """Reload configuration with authorization tracking and integrity verification."""
        with self.config_lock:
            old_hash = self.config_hash
            new_hash = self._compute_config_hash()
            
            # Verify integrity against stored hash
            hash_file = self.config_path.with_suffix('.sha256')
            if hash_file.exists():
                stored_hash = hash_file.read_text().strip()
                if new_hash and stored_hash and not compare_digest(new_hash, stored_hash):
                    self.audit_logger.logger.error({
                        "File": "overseer.py",
                        "component": "ConfigManager",
                        "Time": datetime.now(timezone.utc).isoformat(),
                        "data": {
                            "event": "config_reload_integrity_failed",
                            "authorized_by": authorized_by,
                            "reason": reason,
                            "stored_hash": stored_hash,
                            "current_hash": new_hash
                        }
                    })
                    raise ValueError("Configuration integrity check failed on reload - possible tampering")
            
            self.config_hash = new_hash
            self.config = self._load_config()
            self._store_config_hash()  # Update trusted hash after successful reload
            
            # Log configuration change
            self.audit_logger.logger.info({
                "File": "overseer.py",
                "component": "ConfigManager",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "config_reloaded",
                    "authorized_by": authorized_by,
                    "reason": reason,
                    "old_hash": old_hash,
                    "new_hash": self.config_hash
                }
            })


# ============================================================================
# Hook Registry (Step 4)
# ============================================================================

class HookRegistry:
    """Hook registration and orchestration (Principle 11)."""
    
    def __init__(self, config: Dict[str, Any], audit_logger: AuditLogger):
        self.config = config
        self.audit_logger = audit_logger
        self.hooks: Dict[str, List[Tuple[int, Callable]]] = {}
        self.allowed_hooks = self._load_hook_allowlist()
        self.logger = audit_logger.logger
        self.hook_lock = Lock()
    
    def _load_hook_allowlist(self) -> Set[str]:
        """Load allowed hook types from configuration."""
        governance_config = self.config.get("governance", {})
        return set(governance_config.get("allowed_hooks", [
            "pre_tool_use",
            "post_tool_use",
            "on_error"
        ]))
    
    def register_hook(self, hook_type: str, hook_func: Callable, priority: int = 100):
        """Register hook with priority-based ordering."""
        with self.hook_lock:
            # Verify hook is allowlisted
            if hook_type not in self.allowed_hooks:
                self.logger.error({
                    "File": "overseer.py",
                    "component": "HookRegistry",
                    "Time": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "event": "hook_type_not_allowed",
                        "hook_type": hook_type
                    }
                })
                raise ValueError(f"Hook type {hook_type} not in allowlist")
            
            if hook_type not in self.hooks:
                self.hooks[hook_type] = []
            
            self.hooks[hook_type].append((priority, hook_func))
            # Sort by priority (lower priority = executed first)
            self.hooks[hook_type].sort(key=lambda x: x[0])
            
            self.logger.info({
                "File": "overseer.py",
                "component": "HookRegistry",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "hook_registered",
                    "hook_type": hook_type,
                    "priority": priority,
                    "hook": hook_func.__name__
                }
            })
    
    def execute_hook(self, hook_type: str, event: Dict[str, Any], timeout: float = 10.0) -> HookResult:
        """Execute hook with fail-closed semantics.

        Args:
            hook_type: Type of hook to execute
            event: Event data to pass to hook
            timeout: Configured timeout value (in seconds) for adapter/infrastructure enforcement.
                    Note: Core does not enforce timeout cross-platform; timeout parameter is
                    provided for configuration purposes. Actual timeout enforcement should be
                    implemented at the adapter/infrastructure layer using platform-appropriate
                    mechanisms (signal.alarm on Unix, threading.Timer, or async timeout).

        Returns:
            HookResult with decision, reason, and optional modified context
        """
        if hook_type not in self.hooks:
            self.logger.warning({
                "File": "overseer.py",
                "component": "HookRegistry",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "hook_type_not_found",
                    "hook_type": hook_type
                }
            })
            return HookResult(decision="allow", reason="No hooks registered")

        for priority, hook in self.hooks[hook_type]:
            try:
                # Execute hook (timeout enforcement is adapter/infrastructure responsibility)
                result = hook(event)
                
                if result.decision == "deny":
                    return result
                elif result.decision == "modify":
                    event = result.modified_context or event
                    
            except Exception as e:
                self.logger.error({
                    "File": "overseer.py",
                    "component": "HookRegistry",
                    "Time": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "event": "hook_execution_error",
                        "hook_type": hook_type,
                        "hook": hook.__name__,
                        "error": str(e)
                    }
                })
                # Fail-closed: hook errors produce deny
                return HookResult(decision="deny", reason=f"Hook execution failed - fail-closed: {str(e)}")
        
        return HookResult(decision="allow", reason="All hooks passed")


# ============================================================================
# Policy Coordinator (Step 5)
# ============================================================================

class PolicyCoordinator:
    """
    Stateless policy evaluation coordinator (Principle 4, 6, 7).

    NOTE: This is a placeholder coordinator designed to integrate with external
    policy engines (OPA, Cedar, etc.) or adapter-specific policy implementations.
    The framework does not include a built-in policy evaluation engine to maintain
    true agnosticism (Principle 1) and allow adapters to integrate with their
    preferred policy systems.

    Integration options:
    - External policy engines via hooks
    - Adapter-specific policy loading
    - Custom policy evaluators registered as hooks
    """
    
    def __init__(self, config: Dict[str, Any], audit_logger: AuditLogger):
        self.config = config
        self.audit_logger = audit_logger
        self.policy_cache = {}
        self.cache_lock = Lock()
        self.logger = audit_logger.logger
        self.resolution_strategy = config.get("governance", {}).get("conflict_resolution", "deny_wins")
    
    def evaluate(self, context: Dict[str, Any]) -> GovernanceDecision:
        """
        Evaluate policies deterministically with first-match semantics.
        
        Contract:
        - Stateless: No mutable state between calls (Principle 7)
        - Deterministic: Same inputs → same outputs (Principle 6)
        - Fail-closed: Errors produce deny (Principle 5)
        """
        try:
            # Load policies (cached if possible)
            policies = self._load_policies()
            
            evaluations = []
            first_allow = None
            
            for policy in policies:
                try:
                    result = self._evaluate_policy(policy, context)
                    evaluations.append({
                        "policy_id": policy.get("id", "unknown"),
                        "decision": result.decision,
                        "rationale": result.rationale
                    })
                    
                    if result.decision == "deny":
                        # Deny-wins: short-circuit immediately
                        return GovernanceDecision(
                            decision="deny",
                            policy_id=policy.get("id", "unknown"),
                            rationale=result.rationale,
                            evaluated_rules=evaluations,
                            context=context
                        )
                    elif result.decision == "allow" and first_allow is None:
                        first_allow = (policy.get("id", "unknown"), result.rationale)
                        
                except Exception as e:
                    self.logger.error({
                        "File": "overseer.py",
                        "component": "PolicyCoordinator",
                        "Time": datetime.now(timezone.utc).isoformat(),
                        "data": {
                            "event": "policy_evaluation_error",
                            "policy_id": policy.get("id", "unknown"),
                            "error": str(e)
                        }
                    })
                    # Fail-closed: policy errors result in deny
                    return GovernanceDecision(
                        decision="deny",
                        policy_id="error",
                        rationale=f"Policy evaluation error: {str(e)}",
                        evaluated_rules=evaluations,
                        context=context
                    )
            
            # Default: allow if no deny and at least one allow
            if first_allow:
                return GovernanceDecision(
                    decision="allow",
                    policy_id=first_allow[0],
                    rationale=first_allow[1],
                    evaluated_rules=evaluations,
                    context=context
                )
            
            # Default deny if no policies matched
            return GovernanceDecision(
                decision="deny",
                policy_id="default",
                rationale="No policies matched, default deny",
                evaluated_rules=evaluations,
                context=context
            )
            
        except Exception as e:
            self.logger.error({
                "File": "overseer.py",
                "component": "PolicyCoordinator",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "policy_coordinator_error",
                    "error": str(e)
                }
            })
            # Fail-closed
            return GovernanceDecision(
                decision="deny",
                policy_id="error",
                rationale=f"Policy coordinator error: {str(e)}",
                evaluated_rules=[],
                context=context
            )
    
    def _load_policies(self) -> List[Dict[str, Any]]:
        """
        Load policies from configuration (cached).

        PLACEHOLDER: This method is intended to be overridden or replaced by
        adapter-specific implementations that load policies from external sources
        (OPA, Cedar, YAML files, etc.). The current implementation returns an
        empty list, resulting in default deny behavior (fail-closed).
        """
        # Placeholder: In production, load from Overseer/Rules/ or external policy engine
        # For now, return empty list - policies to be implemented by adapters
        return []

    def _evaluate_policy(self, policy: Dict[str, Any], context: Dict[str, Any]) -> HookResult:
        """
        Evaluate single policy against context.

        PLACEHOLDER: This method is intended to be overridden or replaced by
        adapter-specific implementations that integrate with external policy engines.
        The coordinator pattern delegates actual policy evaluation to separate
        components (OPA, Cedar, custom evaluators, etc.).
        """
        # Placeholder: Policy evaluation logic to be implemented by adapters
        # This follows the coordinator pattern - actual policy execution in separate components
        return HookResult(decision="allow", reason="Policy evaluation not yet implemented")


# ============================================================================
# Emergency Controls (Step 7)
# ============================================================================

class EmergencyControls:
    """Emergency controls for kill switch and halt capability (Principle 15)."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.emergency_halted = False
        self.halt_reason = ""
        self.halt_lock = Lock()
        self.logger = audit_logger.logger
    
    def emergency_halt(self, scope: str = "global", reason: str = ""):
        """Emergency halt of agent sessions."""
        with self.halt_lock:
            self.emergency_halted = True
            self.halt_reason = reason
            
            self.logger.critical({
                "File": "overseer.py",
                "component": "EmergencyControls",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "emergency_halt",
                    "scope": scope,
                    "reason": reason
                }
            })
    
    def is_halted(self) -> bool:
        """Check if emergency halt is active."""
        return self.emergency_halted
    
    def resume(self, authorized_by: str, reason: str):
        """Resume operations after emergency halt."""
        with self.halt_lock:
            self.emergency_halted = False
            self.halt_reason = ""
            
            self.logger.info({
                "File": "overseer.py",
                "component": "EmergencyControls",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "emergency_resume",
                    "authorized_by": authorized_by,
                    "reason": reason
                }
            })


# ============================================================================
# Overseer Main Class (Step 8)
# ============================================================================

class Overseer:
    """
    Central governance hub for the Overseer Framework.
    
    Responsibilities:
    - Hook registration and orchestration (Principle 11)
    - Policy evaluation coordination (Principle 4, 6, 7)
    - Canonical payload management (Principle 8)
    - Audit logging (Principle 9)
    - Emergency controls (Principle 15)
    - True agnosticism (Principle 1)
    - Fail-closed enforcement (Principle 5)
    """
    
    def __init__(self, config_path: str = "Overseer/Config/config.json"):
        """
        Initialize Overseer governance hub.
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize audit logger first (needed by all components)
        self.audit_logger = AuditLogger("Overseer/Logs", "Overseer")
        
        # Load configuration
        self.config_manager = ConfigManager(config_path, self.audit_logger)
        self.config = self.config_manager.config
        
        # Initialize components
        self.protocol_layer = ProtocolLayer(self.audit_logger.logger)
        self.hook_registry = HookRegistry(self.config, self.audit_logger)
        self.policy_coordinator = PolicyCoordinator(self.config, self.audit_logger)
        self.emergency_controls = EmergencyControls(self.audit_logger)
        
        self.logger = self.audit_logger.logger
        
        # Log initialization
        self.logger.info({
            "File": "overseer.py",
            "component": "Overseer",
            "Time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "event": "overseer_initialized",
                "config_path": config_path
            }
        })
    
    def evaluate_policies(self, payload: CanonicalPayload) -> GovernanceDecision:
        """
        Evaluate policies for canonical payload.
        
        Args:
            payload: Canonical payload from adapter
            
        Returns:
            Governance decision with full context
        """
        # Check emergency halt first
        if self.emergency_controls.is_halted():
            return GovernanceDecision(
                decision="deny",
                policy_id="emergency_halt",
                rationale=f"Emergency halt active: {self.emergency_controls.halt_reason}",
                context=payload.__dict__
            )
        
        # Validate payload
        if not self.protocol_layer.validate_payload(payload):
            return GovernanceDecision(
                decision="deny",
                policy_id="validation",
                rationale="Payload validation failed",
                evaluated_rules=[],
                context=payload.__dict__
            )
        
        # Evaluate policies
        decision = self.policy_coordinator.evaluate(payload.__dict__)
        
        # Log decision
        self.audit_logger.log_decision(decision)
        
        return decision
    
    def execute_hook(self, hook_type: str, event: Dict[str, Any]) -> str:
        """
        Execute hook with fail-closed semantics.
        
        Args:
            hook_type: Type of hook to execute
            event: Event data from adapter
            
        Returns:
            Governance decision ("allow", "deny", "modify")
        """
        # Check emergency halt first
        if self.emergency_controls.is_halted():
            self.logger.warning({
                "File": "overseer.py",
                "component": "Overseer",
                "Time": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "event": "hook_blocked_emergency_halt",
                    "hook_type": hook_type
                }
            })
            return "deny"
        
        # Get timeout from config
        governance_config = self.config_manager.get_governance_config()
        timeout = governance_config.get("timeouts", {}).get(hook_type, 10.0)
        
        # Execute hook with timeout
        result = self.hook_registry.execute_hook(hook_type, event, timeout)
        
        return result.decision
    
    def register_hook(self, hook_type: str, hook_func: Callable, priority: int = 100):
        """
        Register hook with Overseer.
        
        Args:
            hook_type: Type of hook (e.g., "pre_tool_use")
            hook_func: Hook function to execute
            priority: Execution priority (lower = executed first)
        """
        self.hook_registry.register_hook(hook_type, hook_func, priority)
    
    def emergency_halt(self, scope: str = "global", reason: str = ""):
        """
        Emergency halt of agent sessions.
        
        Args:
            scope: Scope of halt ("global" or specific agent)
            reason: Reason for emergency halt
        """
        self.emergency_controls.emergency_halt(scope, reason)
    
    def resume(self, authorized_by: str, reason: str):
        """
        Resume operations after emergency halt.
        
        Args:
            authorized_by: Who authorized the resume
            reason: Reason for resume
        """
        self.emergency_controls.resume(authorized_by, reason)


# ============================================================================
# Adapter Interface (for reference)
# ============================================================================

class BaseAdapter(ABC):
    """Base class for all framework adapters (Principle 1, 2)."""
    
    @abstractmethod
    def transform_event(self, event: Dict[str, Any]) -> CanonicalPayload:
        """Transform framework-specific event to canonical payload."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Declare adapter capabilities."""
        pass
    
    @abstractmethod
    def register_hooks(self, overseer: Overseer):
        """Register hooks with Overseer."""
        pass


# ============================================================================
# Main Entry Point
# ============================================================================

def create_overseer(config_path: str = "Overseer/Config/config.json") -> Overseer:
    """
    Factory function to create Overseer instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Initialized Overseer instance
    """
    return Overseer(config_path)


if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path
    
    # CLI entry point for Devin hooks
    # Usage: python overseer.py <hook_event_name>
    # Receives hook event data on stdin (JSON)
    # Returns decision on stdout (JSON)
    #
    # This entry point orchestrates:
    # 1. Load adapter from config
    # 2. Transform CLI event to CanonicalPayload
    # 3. Evaluate governance decision
    # 4. Return decision to CLI
    
    if len(sys.argv) < 2:
        print(json.dumps({"decision": "block", "reason": "Missing hook event name"}))
        sys.exit(2)
    
    hook_event_name = sys.argv[1]
    
    # Read event data from stdin
    try:
        event_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"decision": "block", "reason": f"Invalid JSON input: {str(e)}"}))
        sys.exit(2)
    
    # Load configuration
    config_path = "Overseer/Config/config.json"
    if not Path(config_path).exists():
        print(json.dumps({"decision": "block", "reason": "Config file not found"}))
        sys.exit(2)
    
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load adapter based on config
        adapter_name = config.get("adapter", "devin")
        sys.path.append(str(Path(__file__).parent.parent / "Adapter"))
        
        if adapter_name == "devin":
            from devin_adapter import DevinAdapter
            adapter = DevinAdapter(config, "Overseer/Logs")
        else:
            # For future adapters (claude, cursor, vscode)
            print(json.dumps({"decision": "block", "reason": f"Adapter {adapter_name} not yet implemented"}))
            sys.exit(2)
        
        # Transform event to canonical payload
        payload = adapter.transform_event({
            "hook_event_name": hook_event_name,
            **event_data
        })
        
        # Create Overseer instance
        overseer = Overseer(config_path)
        
        # Evaluate governance decision
        decision = overseer.evaluate_policies(payload)
        
        # Return decision to Devin CLI
        if decision.decision == "deny":
            print(json.dumps({
                "decision": "block",
                "reason": decision.rationale
            }))
            sys.exit(2)
        else:
            print(json.dumps({
                "decision": "approve",
                "reason": decision.rationale
            }))
            sys.exit(0)
            
    except Exception as e:
        print(json.dumps({
            "decision": "block",
            "reason": f"Governance error: {str(e)}"
        }))
        sys.exit(2)
