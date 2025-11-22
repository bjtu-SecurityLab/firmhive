from typing import Dict, Any, Optional

class Message(Dict[str, Any]):
    def __init__(self, role: str, content: str, type: Optional[str] = None, tool_call_id: Optional[str] = None, name: Optional[str] = None):
        try:
            content_str = str(content)
        except Exception:
            print(f"Warning: Could not convert message content to string. Using repr(). Original type: {type(content)}")
            content_str = repr(content)

        super().__init__(role=role, content=content_str)
        if type:
            self['type'] = type
        if tool_call_id:
            self['tool_call_id'] = tool_call_id
        if name:
            self['name'] = name

    @property
    def role(self) -> str: return str(self.get('role', 'unknown'))
    @property
    def content(self) -> str: return str(self.get('content', ''))
    @property
    def type(self) -> Optional[str]: return self.get('type')
    @property
    def tool_call_id(self) -> Optional[str]: return self.get('tool_call_id')
    @property
    def name(self) -> Optional[str]: return self.get('name')