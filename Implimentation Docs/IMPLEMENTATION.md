# Overseer Framework Implementation Guide

**Version**: 1.0.0  
**Date**: 2026-08-11  
**Purpose**: Define coding conventions, implementation patterns, and development guidelines for the Overseer Framework

## Overview

This document provides implementation-specific guidance for building the Overseer Framework. While ARCHITECTURE.md defines the high-level architectural principles, this document focuses on concrete implementation details, coding standards, and development practices.

---

## Code Organization Conventions

### File Structure

```
Overseer/
├── Core/
│   ├── overseer.py              # Central entry point and orchestrator
│   ├── protocol/                # Protocol module - canonical data models
│   │   ├── __init__.py
│   │   ├── models.py            # Canonical payload definitions
│   │   ├── validators.py        # Schema validation
│   │   └── transformers.py      # Data transformation utilities
│   ├── engine/                  # Engine module - policy evaluation
│   │   ├── __init__.py
│   │   ├── evaluator.py         # Policy evaluation logic
│   │   ├── conflict_resolver.py # Conflict resolution strategies
│   │   └── policy_loader.py     # Policy loading and hot-reload
│   ├── state_machine/           # State Machine module - governance state
│   │   ├── __init__.py
│   │   ├── base.py              # Base state machine classes
│   │   ├── emergency.py         # Emergency control states
│   │   └── workflow.py          # Workflow orchestration states
│   └── hook_handler/            # Hook Handler - single dynamic dispatcher
│       ├── __init__.py
│       └── dispatcher.py        # Dynamic hook dispatcher
├── Adapter/
│   ├── __init__.py
│   ├── base.py                  # BaseAdapter class
│   └── [AppName]-Adapter.py     # Framework-specific adapters (devin, claude, cursor, vscode)
├── Config/
│   └── config.json              # Configuration and adapter selection
├── Actions/
│   ├── __init__.py
│   ├── base.py                  # BaseAction class
│   ├── [PolicyName].py         # User policy execution logic
│   └── Meta-Actions/
│       └── [MetaRuleName].py    # Meta rule enforcement
├── Rules/
│   ├── [PolicyName].json        # User policy definitions
│   └── Meta-Rules/
│       └── [MetaRuleName].json  # Meta rule definitions
├── Logs/                        # Layer-specific JSONL log files
└── Tests/                       # Test suites
```

### Naming Conventions

- **Adapters**: `[AppName]-Adapter.py` (e.g., `Devin-Adapter.py`, `Cursor-Adapter.py`)
- **Policy Files**: `[PolicyName].json` (e.g., `file-deletion-protection.json`)
- **Execution Logic**: `[PolicyName].py` (matches policy file name)
- **Meta Rules**: `[MetaRuleName].py` (e.g., `policy-format-validator.py`)
- **Protocol**: `models.py`, `validators.py`, `transformers.py` (within protocol module)
- **Engine**: `evaluator.py`, `conflict_resolver.py`, `policy_loader.py` (within engine module)
- **State Machine**: `base.py`, `emergency.py`, `workflow.py` (within state_machine module)
- **Hook Handler**: `dispatcher.py` (single dynamic dispatcher)

---

## Coding Conventions

### Python Style

Follow PEP 8 with the following Overseer-specific conventions:

```python
# Use descriptive function names that indicate governance intent
def evaluate_tool_use_permission(action_type, agent_identity, resource, access_level):
    """Evaluate whether tool use is permitted based on governance policy."""
    pass

# Use type hints for clarity
from typing import Dict, Any, Optional

def transform_adapter_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Transform adapter-specific event to canonical payload."""
    pass

# Use dataclasses for structured data
from dataclasses import dataclass

@dataclass
class GovernanceDecision:
    decision: str  # "allow", "deny", "modify"
    policy_id: str
    rationale: str
    context: Dict[str, Any]
```

### Error Handling

```python
# Explicit error handling with logging
def evaluate_policy(event: Dict[str, Any]) -> GovernanceDecision:
    try:
        result = policy_engine.evaluate(event)
        return result
    except PolicyValidationError as e:
        logger.error(f"Policy validation failed: {e}", exc_info=True)
        return GovernanceDecision(decision="deny", policy_id="error", rationale=str(e), context=event)
    except Exception as e:
        logger.critical(f"Unexpected error in policy evaluation: {e}", exc_info=True)
        return GovernanceDecision(decision="deny", policy_id="error", rationale=str(e), context=event)
```

### Logging Convention

```python
import logging
import json

# Use structured logging for machine readability
logger = logging.getLogger(__name__)

def log_decision(decision: GovernanceDecision):
    """Log governance decision in structured format."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "decision": decision.decision,
        "policy_id": decision.policy_id,
        "rationale": decision.rationale,
        "context": decision.context
    }
    logger.info(json.dumps(log_entry))
```

---

## Adapter Implementation Pattern

### BaseAdapter Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAdapter(ABC):
    """Base class for all framework adapters."""
    
    @abstractmethod
    def transform_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
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
```

### Example Adapter Implementation

```python
from Overseer.Adapter.base import BaseAdapter

class DevinAdapter(BaseAdapter):
    """Adapter for Devin CLI."""
    
    def transform_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Devin CLI event to canonical payload."""
        return {
            "action_type": event.get("tool_name"),
            "agent_identity": event.get("agent_id"),
            "resource": event.get("parameters", {}).get("path"),
            "access_level": "write" if event.get("tool_name") == "edit" else "read",
            "audit_context": {
                "original_event": event,
                "adapter": "devin"
            }
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Declare Devin adapter capabilities."""
        return {
            "tool_use": True,
            "file_edit": True,
            "file_read": True
        }
    
    def register_hooks(self, overseer: Overseer):
        """Register Devin-specific hooks."""
        overseer.register_hook("PreToolUse", self.pre_tool_use_hook)
        overseer.register_hook("PostToolUse", self.post_tool_use_hook)
```

---

## Policy Definition Pattern

### JSON Policy Definition

```json
{
  "version": "1.0.0",
  "name": "File Deletion Protection",
  "description": "Prevents deletion of important files",
  "rules": [
    {
      "id": "1",
      "condition": "action_type == 'delete' and resource in protected_paths",
      "action": "deny",
      "rationale": "File is in protected paths list",
      "severity": "high"
    }
  ],
  "protected_paths": ["/etc", "/usr", "/bin", "/sbin"]
}
```

### Python Execution Logic with Policy Caching

```python
# file-deletion-protection.py
from Overseer.Actions.base import BaseAction
from typing import Dict, Any
import json
from functools import lru_cache

class FileDeletionProtection(BaseAction):
    """Enforce file deletion protection policy."""
    
    @lru_cache(maxsize=1)
    def _load_policy(self):
        """Load and cache policy configuration (called once at startup)."""
        with open("Overseer/Rules/file-deletion-protection.json") as f:
            return json.load(f)
    
    def execute(self, event: Dict[str, Any]) -> str:
        """Evaluate file deletion protection."""
        
        # Load policy configuration (cached after first call)
        policy = self._load_policy()
        
        # Check if resource is in protected paths
        resource = event.get("resource", "")
        protected_paths = policy.get("protected_paths", [])
        
        if resource in protected_paths:
            return "deny"
        
        return "allow"
```

---

## Meta Rule Implementation

### Meta Rule for Policy Format Validation

```python
# policy-format-validator.py
from Overseer.Actions.base import BaseAction
from typing import Dict, Any
import json

class PolicyFormatValidator(BaseAction):
    """Validate user policy format."""
    
    def execute(self, event: Dict[str, Any]) -> str:
        """Validate policy format before activation."""
        policy_file = event.get("policy_file")
        
        try:
            with open(policy_file) as f:
                policy = json.load(f)
            
            # Required fields
            required_fields = ["version", "name", "description", "rules"]
            for field in required_fields:
                if field not in policy:
                    raise ValueError(f"Missing required field: {field}")
            
            # Rule validation
            for rule in policy.get("rules", []):
                if "id" not in rule or "condition" not in rule or "action" not in rule:
                    raise ValueError("Rule missing required fields: id, condition, action")
            
            return "allow"
        
        except Exception as e:
            logger.error(f"Policy format validation failed: {e}")
            return "deny"
```

---

## Configuration Management

### config.json Structure

```json
{
  "version": "1.0.0",
  "adapters": {
    "devin": {
      "enabled": true,
      "class": "Adapter.devin_adapter.DevAdapter",
      "config": {
        "timeout": 10
      }
    },
    "cursor": {
      "enabled": false,
      "class": "Adapter.cursor_adapter.CursorAdapter"
    }
  },
  "governance": {
    "default_mode": "blocking",
    "logging": {
      "level": "INFO",
      "format": "jsonl",
      "retention_days": 90
    },
    "timeouts": {
      "PreToolUse": 10,
      "PostToolUse": 5
    }
  }
}
```

### Configuration Loading

```python
import json
from typing import Dict, Any

class ConfigManager:
    """Manage Overseer configuration."""
    
    def __init__(self, config_path: str = "Overseer/Config/config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(self.config_path) as f:
            return json.load(f)
    
    def get_adapter_config(self, adapter_name: str) -> Dict[str, Any]:
        """Get configuration for specific adapter."""
        return self.config.get("adapters", {}).get(adapter_name, {})
    
    def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration."""
        return self.config.get("governance", {})
```

---

## Hook Implementation Pattern

### Hook Registration

```python
class Overseer:
    """Central governance hub."""
    
    def __init__(self):
        self.hooks = {
            "PreToolUse": [],
            "PostToolUse": [],
            "OnError": []
        }
    
    def register_hook(self, hook_type: str, hook_func: callable):
        """Register a hook function."""
        if hook_type not in self.hooks:
            raise ValueError(f"Unknown hook type: {hook_type}")
        self.hooks[hook_type].append(hook_func)
    
    def execute_hooks(self, hook_type: str, event: Dict[str, Any]) -> str:
        """Execute all hooks of a given type."""
        if hook_type not in self.hooks:
            return "allow"
        
        for hook in self.hooks[hook_type]:
            decision = hook(event)
            if decision == "deny":
                return "deny"
        
        return "allow"
```

### Example Hook Implementation

```python
def pre_tool_use_hook(event: Dict[str, Any]) -> str:
    """Pre-tool use governance hook."""
    # Transform event to canonical payload
    canonical = adapter.transform_event(event)
    
    # Evaluate policies
    decision = overseer.evaluate_policies(canonical)
    
    # Log decision
    log_decision(decision)
    
    return decision.decision
```

### Hook Handler Pattern

Overseer uses a single dynamic dispatcher per event type rather than multiple specific hook handlers. This provides better performance (parse once, shared work) and centralized conflict resolution.

```python
# Overseer/Core/hook_handler/dispatcher.py
from typing import Dict, Any, List, Callable
from Overseer.Core.protocol.models import CanonicalPayload
import logging
from datetime import datetime

class HookDispatcher:
    """Single dynamic dispatcher for hook coordination."""
    
    def __init__(self, engine, state_machine):
        """Initialize dispatcher with engine and state machine."""
        self.engine = engine
        self.state_machine = state_machine
        self.logger = logging.getLogger("Overseer.HookHandler.Dispatcher")
        self.handlers: Dict[str, List[Callable]] = {}
    
    def register_handler(self, hook_type: str, handler: Callable, priority: int = 50):
        """Register a handler for a specific hook type with priority."""
        if hook_type not in self.handlers:
            self.handlers[hook_type] = []
        self.handlers[hook_type].append((priority, handler))
        # Sort by priority (higher numbers first)
        self.handlers[hook_type].sort(key=lambda x: x[0], reverse=True)
    
    def dispatch(self, hook_type: str, event: Dict[str, Any]) -> str:
        """
        Dispatch hook event through registered handlers.
        
        Args:
            hook_type: Type of hook event (e.g., "PreToolUse")
            event: Raw event data from adapter
            
        Returns:
            Governance decision ("allow", "deny", "modify")
        """
        try:
            # Parse input once
            parsed_event = self._parse_event(event)
            
            # Check emergency state first
            emergency_state = self.state_machine.check_emergency_state()
            if emergency_state != "NORMAL":
                self.logger.warning({
                    "File": "dispatcher.py",
                    "component": "HookHandler",
                    "Time": datetime.utcnow().isoformat(),
                    "data": {
                        "event": "emergency_halt",
                        "hook_type": hook_type,
                        "emergency_state": emergency_state
                    }
                })
                return "deny"
            
            # Execute handlers in priority order
            if hook_type not in self.handlers:
                return "allow"  # Default allow if no handlers
            
            for priority, handler in self.handlers[hook_type]:
                decision = handler(parsed_event)
                if decision == "deny":
                    # DENY short-circuits immediately
                    self._log_decision(hook_type, decision, priority)
                    return "deny"
            
            # If no deny, return allow
            self._log_decision(hook_type, "allow", None)
            return "allow"
            
        except Exception as e:
            self.logger.error(f"Hook dispatcher error: {e}")
            return "deny"  # Fail-closed
    
    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and normalize event data once."""
        # Implementation for event parsing
        return event
    
    def _log_decision(self, hook_type: str, decision: str, priority: int):
        """Log hook decision."""
        self.logger.info({
            "File": "dispatcher.py",
            "component": "HookHandler",
            "Time": datetime.utcnow().isoformat(),
            "data": {
                "event": "hook_dispatch",
                "hook_type": hook_type,
                "decision": decision,
                "priority": priority
            }
        })
```

---

## Dependency Management

### Zero Runtime Dependencies

Overseer core should use only Python standard library. External dependencies for adapters should be clearly documented and optional.

```python
# Overseer core - stdlib only
import json
import logging
from typing import Dict, Any
from dataclasses import dataclass

# Adapter dependencies - optional and clearly documented
# DevinAdapter may require: requests
# CursorAdapter may require: different dependencies
```

### Dependency Declaration

```toml
# pyproject.toml
[project]
name = "overseer"
version = "1.0.0"
dependencies = [
    # Overseer core has NO runtime dependencies beyond standard library
]

[project.optional-dependencies]
devin = [
    "requests>=2.28.0"
]
cursor = [
    "cursor-client>=1.0.0"
]
```

---

## Testing Guidelines

### Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestAdapter(unittest.TestCase):
    """Test adapter functionality."""
    
    def test_transform_event(self):
        """Test event transformation to canonical payload."""
        adapter = DevinAdapter()
        event = {"tool_name": "edit", "agent_id": "agent-123", "parameters": {"path": "/tmp/file.txt"}}
        
        canonical = adapter.transform_event(event)
        
        self.assertEqual(canonical["action_type"], "edit")
        self.assertEqual(canonical["agent_identity"], "agent-123")
        self.assertEqual(canonical["resource"], "/tmp/file.txt")
    
    def test_get_capabilities(self):
        """Test capability declaration."""
        adapter = DevinAdapter()
        capabilities = adapter.get_capabilities()
        
        self.assertTrue(capabilities["tool_use"])
        self.assertTrue(capabilities["file_edit"])
```

### Integration Testing

```python
class TestGovernancePipeline(unittest.TestCase):
    """Test end-to-end governance pipeline."""
    
    def test_policy_enforcement(self):
        """Test policy enforcement through hook pipeline."""
        overseer = Overseer()
        adapter = DevinAdapter()
        
        # Register hooks
        adapter.register_hooks(overseer)
        
        # Test event
        event = {"tool_name": "delete", "agent_id": "agent-123", "parameters": {"path": "/etc/passwd"}}
        
        # Execute hooks
        decision = overseer.execute_hooks("PreToolUse", event)
        
        self.assertEqual(decision, "deny")
```

---

## Performance Guidelines

### Hook Performance Targets

- **PreToolUse hooks**: < 100ms (fast path for synchronous governance)
- **PostToolUse hooks**: < 500ms (allow more time for comprehensive logging)
- **Overall latency**: < 1 second for complete governance decision

### Performance Optimization

```python
# Use caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def get_policy_config(policy_id: str) -> Dict[str, Any]:
    """Cache policy configuration to avoid repeated file I/O."""
    with open(f"rules/{policy_id}.json") as f:
        return json.load(f)

# Use async I/O for logging to avoid blocking
import asyncio

async def log_decision_async(decision: GovernanceDecision):
    """Log decision asynchronously."""
    await asyncio.to_thread(log_decision, decision)
```

---

## Security Implementation Guidelines

### Secret Detection Pattern

```python
import re

SECRET_PATTERNS = {
    "api_key": r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
    "password": r'password["\']?\s*[:=]\s*["\']?([^"\']{8,})["\']?',
    "token": r'["\']?([a-zA-Z0-9_\-]{32,})["\']?'
}

def detect_secrets(text: str) -> list:
    """Detect secret patterns in text."""
    detected = []
    for secret_type, pattern in SECRET_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detected.append({"type": secret_type, "matches": matches})
    return detected

def mask_secrets(text: str) -> str:
    """Mask detected secrets in text."""
    for secret_type, pattern in SECRET_PATTERNS.items():
        text = re.sub(pattern, f"{secret_type}: *****", text, flags=re.IGNORECASE)
    return text
```

### Audit Trail Integrity

```python
import hashlib
import json

class AuditTrail:
    """Tamper-evident audit trail."""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.previous_hash = self._get_last_hash()
    
    def _get_last_hash(self) -> str:
        """Get hash of last log entry."""
        try:
            with open(self.log_file) as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get("hash", "")
        except FileNotFoundError:
            pass
        return ""
    
    def log(self, entry: Dict[str, Any]) -> None:
        """Log entry with hash chain."""
        entry["hash"] = self._compute_hash(entry, self.previous_hash)
        self.previous_hash = entry["hash"]
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _compute_hash(self, entry: Dict[str, Any], previous_hash: str) -> str:
        """Compute hash of entry with previous hash."""
        data = json.dumps(entry, sort_keys=True) + previous_hash
        return hashlib.sha256(data.encode()).hexdigest()
```

---

## Deployment Guidelines

### Installation

```bash
# Clone repository
git clone https://github.com/yourorg/overseer.git
cd overseer

# Install (no runtime dependencies for core)
pip install -e .

# Install adapter-specific dependencies
pip install -e ".[devin]"  # For Devin adapter
pip install -e ".[cursor]"  # For Cursor adapter
```

### Configuration

```bash
# Initialize configuration
python -m overseer init

# This creates:
# - Overseer/Config/config.json
# - Overseer/Rules/ (empty directory)
# - Overseer/Adapter/ (with base adapter)
# - Overseer/Logs/ (empty directory)
# - Overseer/Tests/ (empty directory)
```

### Running Overseer

```bash
# Start Overseer with specific adapter
python -m overseer --adapter devin

# Start with custom config
python -m overseer --config path/to/config.json
```

---

## Debugging Guidelines

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('overseer.log'),
        logging.StreamHandler()
    ]
)

# Enable debug logging for troubleshooting
logger.setLevel(logging.DEBUG)
```

### Debug Mode

```python
class Overseer:
    """Central governance hub with debug mode."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def execute_hooks(self, hook_type: str, event: Dict[str, Any]) -> str:
        """Execute hooks with debug logging."""
        if self.debug:
            logger.debug(f"Executing {hook_type} with event: {event}")
        
        decision = super().execute_hooks(hook_type, event)
        
        if self.debug:
            logger.debug(f"Decision: {decision}")
        
        return decision
```

---

## Version Control Guidelines

### Git Workflow

```bash
# Feature branch workflow
git checkout -b feature/new-adapter
# Make changes
git commit -m "Add new adapter for Framework X"
git push origin feature/new-adapter
# Create pull request

# Release workflow
git checkout main
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(adapter): add support for Cursor CLI

Implemented CursorAdapter with event transformation
and hook registration for tool use events.

Closes #123
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e ".[devin]"
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=overseer
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Contributing Guidelines

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes following coding conventions
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request with clear description

### Code Review Checklist

- [ ] Code follows PEP 8 and Overseer conventions
- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation updated
- [ ] No hardcoded dependencies added to core
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Error handling implemented
- [ ] Logging added where appropriate
