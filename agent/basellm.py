import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from agent.llmclient import LLMClient
from agent.common import Message


class BaseLLM(ABC):
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str = "You are a helpful AI assistant.",
    ):
        self.llm_client = llm_client or LLMClient()
        self.system_prompt = system_prompt
        self.messages: List[Message] = []
        
        if not hasattr(self, 'messages_filters'):
            self.messages_filters = []
            
    def _build_system_message(self) -> str:
        format_section = self._get_response_format_prompt()
        return f"{self.system_prompt}\n\n--- Response Format Requirements ---\n{format_section}"
    
    @abstractmethod
    def _get_response_format_prompt(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    def add_message(self, role: str, content: str, type: Optional[str] = None, tool_call_id: Optional[str] = None, name: Optional[str] = None):
        try:
            filtered_content = content
            for rule in getattr(self, 'messages_filters', []):
                try:
                    from_str = str(rule.get('from', ''))
                    to_str = str(rule.get('to', ''))
                    filtered_content = filtered_content.replace(from_str, to_str)
                except Exception:
                    continue
            msg = Message(role=role, content=filtered_content, type=type, tool_call_id=tool_call_id, name=name)
            self.messages.append(msg)
            
            if hasattr(self, 'messages_log_path') and self.messages_log_path:
                try:
                    with open(self.messages_log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                except Exception as e:
                    print(f"Warning: Failed to write message to log file {self.messages_log_path}. Error: {e}")

        except TypeError as e:
            print(f"Error: Failed to add message, content conversion failed - {e}")
        except Exception as e:
            print(f"Error: An unexpected error occurred while adding a message - {e}")
    
    def get_messages(self) -> List[Message]:
        return self.messages.copy()
    
    def clear_messages(self, keep_system_message: bool = False):
        if keep_system_message:
            self.messages = [self.messages[0]]
        else:
            self.messages = []
    
    def get_llm_response(self, messages: Optional[List[Message]] = None, **kwargs) -> Dict[str, Any]:
        msg_list = messages if messages is not None else self.messages
        return self.llm_client.invoke(msg_list, **kwargs)

    async def get_llm_response_async(self, messages: Optional[List[Message]] = None, **kwargs) -> Dict[str, Any]:
        msg_list = messages if messages is not None else self.messages
        return await self.llm_client.ainvoke(msg_list, **kwargs)
