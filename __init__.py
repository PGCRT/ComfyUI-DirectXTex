import sys
import os

_module_dir = os.path.dirname(__file__)
if _module_dir not in sys.path:
    sys.path.insert(0, _module_dir)

from .py.LoadDDSNode import (
    LoadDDSNode,
    NODE_CLASS_MAPPINGS as LoadDDSNode_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as LoadDDSNode_DISPLAY,
)
from .py.SaveDDSNode import (
    SaveDDSNode,
    NODE_CLASS_MAPPINGS as SaveDDSNode_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as SaveDDSNode_DISPLAY,
)

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(LoadDDSNode_MAPPINGS)
NODE_CLASS_MAPPINGS.update(SaveDDSNode_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(LoadDDSNode_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(SaveDDSNode_DISPLAY)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
