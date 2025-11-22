import copy
from typing import Dict, Any, Optional


class FlexibleContext:
    """
    A shared context class for tools, allowing arbitrary key-value pairs to be passed
    during initialization and stored as instance attributes.
    """
    def __init__(self, **kwargs: Any):
        self.file_path: Optional[str] = None
        self.file_name: Optional[str] = None
        self.current_dir: Optional[str] = None
        self.base_path: Optional[str] = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        items = (f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{type(self).__name__}({', '.join(items)})"

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        setattr(self, key, value)
        
    def copy(self) -> 'FlexibleContext':
        return copy.deepcopy(self)
    
    def __contains__(self, key: str) -> bool:
        return key in self.__dict__ or hasattr(self, key)

    def update(self, other_dict: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        if other_dict:
            for key, value in other_dict.items():
                setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
