"""
Adapter Layer - CLI-Specific Event Transformation

This layer provides adapters that transform CLI-specific events into
canonical payloads for Overseer governance.

Per ARCHITECTURE.md Principle 1 (True Agnosticism):
- Core framework has zero CLI-specific knowledge
- All CLI-specific logic lives in adapters
- Adapters selected via configuration
"""

from .base import BaseAdapter, AdapterCapabilities

__all__ = ["BaseAdapter", "AdapterCapabilities"]
