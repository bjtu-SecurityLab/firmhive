import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from agent.context import FlexibleContext


class ExecutableTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]
    timeout: int = 30

    def __init__(self, context: Optional[FlexibleContext] = None):
        self.context = context

    @abstractmethod
    def execute(self, **kwargs: Any) -> str:
        pass

    def format_for_prompt(self) -> str:
        param_str = "No parameters"
        if hasattr(self, 'parameters') and self.parameters:
            try:
                param_str = json.dumps(self.parameters, indent=2, ensure_ascii=False)
            except TypeError:
                param_str = str(self.parameters)
        
        name = getattr(self, 'name', self.__class__.__name__)
        description = getattr(self, 'description', 'No description available.')
        
        return f"- Name: {name}\n  Description: {description}\n  Parameters (JSON Schema format):\n{param_str}"
