"""
Adapter layer for CLI-specific event conversion.

Each adapter handles:
- CLI-specific event name mapping
- Event format conversion (CLI format → StandardEvent)
- Response format conversion (StandardEvent → CLI format)
- CLI-specific peculiarities and compatibility
"""

from .devin_adapter import DevinAdapter

__all__ = ["DevinAdapter"]