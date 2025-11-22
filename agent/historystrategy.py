from agent.common import Message
from typing import List, Optional, Callable

class HistoryStrategy:
    def apply(self, messages: List[Message]) -> List[Message]:
        return messages.copy()

class KeepLastN(HistoryStrategy):
    def __init__(self, n: int):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer for KeepLastN")
        self.n = n

    def apply(self, messages: List[Message]) -> List[Message]:
        return messages[-self.n:]


class CompactToolHistory(HistoryStrategy):
    DEFAULT_KEEP_CHARS_COUNT = 1000
    DEFAULT_TOOL_TYPE = ["tool_result"]
    DEFAULT_SUMMARY_PREFIX = "Tool Result: "
    DEFAULT_SUMMARY_SUFFIX = "...result omitted, re-execute to view the full result for accurate analysis"

    def __init__(self,
                 keep_chars_count: int = DEFAULT_KEEP_CHARS_COUNT,
                 tool_message_types: List[str] = None,
                 keep_last_n: Optional[int] = None):
        if not isinstance(keep_chars_count, int) or keep_chars_count < 0:
            raise ValueError("keep_chars_count must be a non-negative integer")
        self.keep_chars_count = keep_chars_count
        self.tool_message_types = tool_message_types or self.DEFAULT_TOOL_TYPE
        self.keep_last_n = keep_last_n

    def apply(self, messages: List[Message]) -> List[Message]:
        if self.keep_last_n is not None and self.keep_last_n > 0 and self.keep_last_n < len(messages):
            messages = messages[-self.keep_last_n:]
            
        result = []
        for msg in messages:
            msg_type = msg.get('type')
            if isinstance(msg_type, str) and msg_type in self.tool_message_types:
                content_str = msg.content
                is_truncated = len(content_str) > self.keep_chars_count
                kept_content = content_str[:self.keep_chars_count]
                summary = (
                    f"{self.DEFAULT_SUMMARY_PREFIX}"
                    f"{kept_content}"
                    f"{self.DEFAULT_SUMMARY_SUFFIX if is_truncated else ']'}"
                )
                result.append(Message(role=msg.role, content=summary, type=msg.type))
            else:
                result.append(msg)
        return result


class KeepLatestTool(HistoryStrategy):
    DEFAULT_KEEP_CHARS_COUNT = 1000
    DEFAULT_TOOL_TYPE = ["tool_result"]
    DEFAULT_SUMMARY_PREFIX = "Previous Tool Result: "
    DEFAULT_SUMMARY_SUFFIX = "..."

    def __init__(self,
                 keep_chars_count: int = DEFAULT_KEEP_CHARS_COUNT,
                 tool_message_type: str = DEFAULT_TOOL_TYPE,
                 keep_last_n: Optional[int] = None):
        if not isinstance(keep_chars_count, int) or keep_chars_count < 0:
            raise ValueError("keep_chars_count must be a non-negative integer")
        self.keep_chars_count = keep_chars_count
        self.tool_message_type = tool_message_type
        self.keep_last_n = keep_last_n

    def apply(self, messages: List[Message]) -> List[Message]:
        if self.keep_last_n is not None and self.keep_last_n > 0 and self.keep_last_n < len(messages):
            messages = messages[-self.keep_last_n:]
            
        result = []
        last_tool_msg_index = -1
        for i in range(len(messages) - 1, -1, -1):
            msg_type = messages[i].get('type')
            if isinstance(msg_type, str) and msg_type in self.tool_message_type:
                last_tool_msg_index = i
                break

        for i, msg in enumerate(messages):
            msg_type = msg.get('type')
            if isinstance(msg_type, str) and msg_type == self.tool_message_type and i != last_tool_msg_index:
                content_str = msg.content
                is_truncated = len(content_str) > self.keep_chars_count
                kept_content = content_str[:self.keep_chars_count]
                summary = (
                    f"{self.DEFAULT_SUMMARY_PREFIX}"
                    f"{kept_content}"
                    f"{self.DEFAULT_SUMMARY_SUFFIX if is_truncated else ']'}"
                )
                result.append(Message(role=msg.role, content=summary, type=msg.type))
            else:
                result.append(msg)
        return result


class TokenLimit(HistoryStrategy):
    def __init__(self, max_tokens: int, tokenizer: Callable[[str], List[int]], keep_last_n: Optional[int] = None):
        if not isinstance(max_tokens, int) or max_tokens <= 0:
             raise ValueError("max_tokens must be a positive integer")
        self.max_tokens = max_tokens
        self.tokenizer = tokenizer
        self.keep_last_n = keep_last_n
        self._TOKENS_PER_MESSAGE = 3
        self._TOKENS_PER_NAME = 1

    def _count_message_tokens(self, message: Message) -> int:
        num_tokens = self._TOKENS_PER_MESSAGE
        for key, value in message.items():
             value_str = value if isinstance(value, str) else str(value)
             try: num_tokens += len(self.tokenizer(value_str))
             except Exception as e: print(f"Warning: Tokenizer failed: {e}"); num_tokens += len(value_str) // 3
             if key == "name": num_tokens += self._TOKENS_PER_NAME
        return num_tokens

    def apply(self, messages: List[Message]) -> List[Message]:
        if self.keep_last_n is not None and self.keep_last_n > 0 and self.keep_last_n < len(messages):
            messages = messages[-self.keep_last_n:]
            
        current_tokens = 0
        result: List[Message] = []
        for msg in reversed(messages):
            msg_tokens = self._count_message_tokens(msg)
            if current_tokens + msg_tokens <= self.max_tokens:
                result.append(msg)
                current_tokens += msg_tokens
            else: break
        return result[::-1]
    


class RepeatSystemMessage(HistoryStrategy):
    def __init__(self,
                 repeat_every_n: int = 10,
                 keep_last_n: Optional[int] = None):
        if not isinstance(repeat_every_n, int) or repeat_every_n <= 0:
            raise ValueError("repeat_every_n must be a positive integer")
        self.repeat_every_n = repeat_every_n
        self.keep_last_n = keep_last_n
        
    def apply(self, messages: List[Message]) -> List[Message]:
        if len(messages) < 2:
            return messages.copy()
            
        system_message = messages[0]
        user_message = messages[1]
        if system_message.get('role') != 'system' or user_message.get('role') != 'user':
            print("Warning: First message was not 'system' or second message was not 'user'. Repeating strategy skipped.")
            return messages.copy()
            
        if self.keep_last_n is not None and self.keep_last_n > 0 and len(messages) > self.keep_last_n:
             if self.keep_last_n == 1:
                 messages = [system_message]
             elif self.keep_last_n == 2:
                 messages = [system_message, user_message]
             else: 
                 num_from_end = self.keep_last_n - 2
                 if num_from_end >= len(messages) - 2:
                     messages = [system_message, user_message] + messages[2:]
                 else:
                     messages = [system_message, user_message] + messages[-num_from_end:]
        
        result = messages.copy()
        initial_len = len(messages) 
        
        insertions = 0
        for original_index in range(1 + self.repeat_every_n, initial_len, self.repeat_every_n):
            position = original_index + insertions
            if position <= len(result):
                result.insert(position, user_message)
                result.insert(position, system_message)
                insertions += 2 
                
        return result
