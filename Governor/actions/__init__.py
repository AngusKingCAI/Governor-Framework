"""
Actions auto-discovery registry
"""

import importlib
import pkgutil
from ._base import RuleAction

# Auto-discover and register all actions
_ACTIONS = {}

for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name.startswith("_"):
        continue
    
    try:
        module = importlib.import_module(f".{module_name}", package=__name__)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, RuleAction) and 
                attr is not RuleAction):
                instance = attr()
                _ACTIONS[instance.name] = instance
    except Exception:
        pass

__all__ = ["_ACTIONS"]
