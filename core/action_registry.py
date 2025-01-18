from typing import Dict, List, Callable, Any, Optional
import inspect
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class ActionValidationError(Exception):
    pass

def validate_parameters(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        try:
            sig.bind(*args, **kwargs)
        except TypeError as e:
            raise ActionValidationError(f"Invalid parameters for action: {str(e)}")
        return func(*args, **kwargs)
    return wrapper

class ActionRegistry:
    def __init__(self):
        self.actions: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}
        self.required_params: Dict[str, Dict[str, type]] = {}

    def register(self, name: str, func: Callable, description: Optional[str] = None):
        """Register an action with the registry"""
        validated_func = validate_parameters(func)
        self.actions[name] = validated_func
        self.descriptions[name] = description or func.__doc__ or "No description provided"
        
        # Extract parameter information
        sig = inspect.signature(func)
        self.required_params[name] = {
            param.name: param.annotation
            for param in sig.parameters.values()
            if param.default == inspect.Parameter.empty
        }

    def execute(self, name: str, **kwargs) -> Any:
        """Execute a registered action"""
        if name not in self.actions:
            raise KeyError(f"Action '{name}' not found in registry")
        
        try:
            return self.actions[name](**kwargs)
        except ActionValidationError as e:
            logger.error(f"Action validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            raise

    def get_action_schema(self, name: str) -> Dict[str, Any]:
        """Get the schema for a registered action"""
        if name not in self.actions:
            raise KeyError(f"Action '{name}' not found in registry")
        
        return {
            "name": name,
            "description": self.descriptions[name],
            "required_parameters": self.required_params[name]
        }

    def list_actions(self) -> List[Dict[str, Any]]:
        """List all registered actions and their schemas"""
        return [self.get_action_schema(name) for name in self.actions]

    def has_action(self, name: str) -> bool:
        """Check if an action exists"""
        return name in self.actions