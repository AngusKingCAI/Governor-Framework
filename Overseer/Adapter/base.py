"""
BaseAdapter - SDK Interface for CLI Adapters

This module defines the abstract base class that all CLI adapters must implement.
It provides the SDK interface for framework-agnostic adapter development.

Per ARCHITECTURE.md Principle 1 (True Agnosticism):
- Core framework has zero CLI-specific knowledge
- All CLI-specific logic lives in adapters
- Adapters implement well-defined SDK interface
- Capabilities discovered dynamically

Per ARCHITECTURE.md Principle 2 (Modular Architecture):
- Adapter layer operates independently with minimal coupling
- Single responsibility: CLI mapping and event transformation
- Well-defined interfaces with Overseer core
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from json import dumps
from logging import FileHandler, Formatter, getLogger, Logger
from os import chmod, fsync
from pathlib import Path
from platform import system as platform_system
from typing import Any, Dict, List, Optional, Set

# Import canonical payload from Overseer core
import sys
sys.path.append(str(Path(__file__).parent.parent / "Core"))
from overseer import CanonicalPayload


@dataclass
class AdapterCapabilities:
    """Capabilities exposed by an adapter (ARCHITECTURE.md Principle 1.4)."""
    supported_hooks: Set[str]  # e.g., {"PreToolUse", "PostToolUse"}
    supported_events: Set[str]  # e.g., {"tool_execution", "permission_request"}
    input_schema: Dict[str, Any]  # Expected input structure
    output_schema: Dict[str, Any]  # Output structure (CanonicalPayload)


class BaseAdapter(ABC):
    """
    Abstract base class for all CLI adapters.
    
    Adapters implement this SDK interface to transform CLI-specific events
    into canonical payloads for Overseer governance.
    
    Per ARCHITECTURE.md Principle 1.3 (Plugin SDK Pattern):
    - BaseAdapter requires transform_event(), get_capabilities(), register_hooks()
    - Consistent adapter development pattern
    - Well-defined interface for extensibility
    """
    
    def __init__(self, config: Dict[str, Any], log_dir: str):
        """
        Initialize adapter with configuration.
        
        Args:
            config: Adapter-specific configuration
            log_dir: Directory for adapter-specific JSONL logs
        """
        self.config = config
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive directory permissions (owner only) on Unix-like systems
        if platform_system() != 'Windows':
            chmod(self.log_dir, 0o700)
        
        # Create date-specific log file
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self.log_dir / f"Adapter-Log-{date_str}.jsonl"
        
        self.logger = getLogger(f"Overseer.Adapter.{self.__class__.__name__}")
        self.logger.setLevel(getLogger().level)
        
        # File handler with JSON formatter
        handler = FileHandler(log_file)
        handler.setFormatter(self._json_formatter())
        self.logger.addHandler(handler)
        
        # Set restrictive file permissions (owner read/write only) on Unix-like systems
        if platform_system() != 'Windows':
            chmod(log_file, 0o600)
        
        # Log initialization
        self.logger.info({
            "File": "base.py",
            "component": "BaseAdapter",
            "Time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "event": "adapter_initialized",
                "adapter_type": self.__class__.__name__,
                "config_keys": list(config.keys())
            }
        })
    
    def _json_formatter(self) -> Formatter:
        """Custom JSON formatter using stdlib only."""
        class JSONFormatter(Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage()
                }
                return dumps(log_entry)
        return JSONFormatter()
    
    @abstractmethod
    def transform_event(self, event: Dict[str, Any]) -> CanonicalPayload:
        """
        Transform CLI-specific event to canonical payload.
        
        This is the core adapter responsibility: mapping CLI-specific event
        structures to the framework-agnostic CanonicalPayload.
        
        Args:
            event: CLI-specific event data (e.g., Devin hook stdin)
            
        Returns:
            CanonicalPayload with standardized structure
            
        Raises:
            ValueError: If event is invalid or cannot be transformed
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> AdapterCapabilities:
        """
        Return adapter capabilities for dynamic discovery.
        
        Per ARCHITECTURE.md Principle 1.4 (Capability-Based Ports):
        - Adapters declare supported hooks, event types, and data schemas
        - Framework adapts to adapter capabilities automatically
        
        Returns:
            AdapterCapabilities with supported hooks, events, and schemas
        """
        pass
    
    @abstractmethod
    def register_hooks(self, hook_registry: Any) -> None:
        """
        Register adapter-specific hooks with the hook registry.
        
        Args:
            hook_registry: HookRegistry instance from Overseer core
        """
        pass
    
    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Validate event structure before transformation.
        
        Args:
            event: CLI-specific event data
            
        Returns:
            True if event is valid, False otherwise
        """
        required_fields = self.get_capabilities().input_schema.get("required", [])
        return all(field in event for field in required_fields)
