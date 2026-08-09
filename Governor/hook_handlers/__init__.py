"""
Hook handlers auto-discovery registry
"""

import importlib
import pkgutil
from ._base import HookHandler

# Auto-discover and register all hook handlers
_HOOK_HANDLERS = {}

for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith("_"):
        continue
    
    try:
        module = importlib.import_module(f".{module_name}", package=__name__)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, HookHandler) and 
                attr is not HookHandler):
                instance = attr()
                _HOOK_HANDLERS[instance.hook_name] = instance
    except Exception:
        pass

# Manual registration for PermissionRequest (auto-discovery happens at import time)
try:
    from .permission_request import PermissionRequestHandler
    _HOOK_HANDLERS["PermissionRequest"] = PermissionRequestHandler()
except Exception:
    pass

__all__ = ["_HOOK_HANDLERS"]
