import os
import time
import openai
import json
import asyncio
import pathlib
from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Any, Optional

class LLMClient:
    _instance = None
    
    def __new__(cls, config_path: str = 'config.ini'):
        if cls._instance is None:
            cls._instance = super(LLMClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = 'config.ini'):
        if not hasattr(self, 'initialized'):
            import configparser
            self.config = configparser.ConfigParser()
            
            config_path_to_read = None
            if pathlib.Path(config_path).is_file():
                config_path_to_read = config_path
            else:
                try:
                    current_path = pathlib.Path(__file__).resolve().parent
                    for _ in range(4): 
                        potential_path = current_path / 'config.ini'
                        if potential_path.is_file():
                            config_path_to_read = potential_path
                            break
                        current_path = current_path.parent
                except Exception:
                    pass

            if config_path_to_read:
                print(f"[LLMClient] Reading configuration from: {config_path_to_read}")
                self.config.read(str(config_path_to_read), encoding='utf-8')
            else:
                print(f"[LLMClient] Warning: Could not find '{config_path}'. Trying to read from default locations.")
                self.config.read(config_path, encoding='utf-8')

            self.active_text_provider = self.config.get('common', 'active_model', fallback='openai')
            self.active_vision_provider = self.config.get('common', 'active_vision_model', fallback=self.active_text_provider)

            self._provider_cache: Dict[str, Dict[str, Any]] = {}

            self.callbacks = []
            self.initialized = True
    
    def add_callback(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _load_provider(self, provider_name: str) -> Dict[str, Any]:
        if provider_name in self._provider_cache:
            return self._provider_cache[provider_name]
        section = provider_name
        env_var_name = f"{provider_name.upper()}_API_KEY"
        if provider_name.lower() == 'openai':
            env_var_name = 'OPENAI_API_KEY'
        
        api_key = os.environ.get(env_var_name)
        if not api_key:
            api_key = self.config.get(section, 'api_key', fallback=None)
            
        model = self.config.get(section, 'model', fallback='gpt-4o')
        base_url = self.config.get(section, 'base_url', fallback=None)
        org_id = self.config.get(section, 'org_id', fallback=None)
        temperature = float(self.config.get(section, 'temperature', fallback='0'))
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None,
            organization=org_id if org_id else None
        )
        
        async_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None,
            organization=org_id if org_id else None
        )

        cfg = {
            'client': client,
            'async_client': async_client,
            'api_key': api_key,
            'model': model,
            'base_url': base_url,
            'org_id': org_id,
            'temperature': temperature,
            'provider_name': provider_name,
        }
        self._provider_cache[provider_name] = cfg
        return cfg

    def _infer_mode_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        # Default to text; if any message content includes image(s), return 'vl'
        try:
            for msg in messages:
                content = msg.get('content')
                # OpenAI "multi-part" message style: content is a list of parts
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            ptype = part.get('type')
                            if ptype in ('image_url', 'image'):
                                return 'vl'
                            # Some providers might embed data URLs as text; heuristic
                            if ptype == 'text' and isinstance(part.get('text'), str) and 'data:image' in part.get('text'):
                                return 'vl'
                # Fallback heuristic on string content
                if isinstance(content, str) and 'data:image' in content:
                    return 'vl'
        except Exception:
            pass
        return 'text'

    def invoke(self, messages: List[Dict[str, Any]], stream: bool = False, 
                timeout: Optional[float] = None, max_retries: int = 3, output_dir: Optional[str] = None,
                mode: Optional[str] = None) -> Dict[str, Any]:
        # Resolve mode: explicit > inferred > default 'text'
        selected_mode = (mode or '').lower()
        if selected_mode not in ('image', 'text', ''):
            selected_mode = ''
        if not selected_mode:
            selected_mode = self._infer_mode_from_messages(messages)
        if selected_mode in ('image'):
            provider_name = self.active_vision_provider
        else:
            provider_name = self.active_text_provider

        cfg = self._load_provider(provider_name)
        client: OpenAI = cfg['client']
        model = cfg['model']
        temperature = cfg['temperature']

        for callback in self.callbacks:
            if hasattr(callback, 'on_llm_start'):
                try:
                    callback.on_llm_start({"name": provider_name}, [msg.get('content', '') for msg in messages])
                except Exception:
                    pass
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    stream=stream,
                    timeout=timeout,
                    seed=42
                )
                
                if stream:
                    collected_chunks = []
                    collected_content = ""
                    
                    for chunk in response:
                        collected_chunks.append(chunk)
                        try:
                            if chunk.choices and chunk.choices[0].delta.content:
                                content_chunk = chunk.choices[0].delta.content
                                collected_content += content_chunk
                                for callback in self.callbacks:
                                    if hasattr(callback, 'on_llm_new_token'):
                                        callback.on_llm_new_token(content_chunk)
                        except Exception:
                            continue
                    
                    result = {
                        "content": collected_content,
                        "usage": {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0
                        },
                        "prompt_messages": messages
                    }
                else:
                    # Some providers may not return usage
                    try:
                        usage = {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    except Exception:
                        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                    result = {
                        "content": response.choices[0].message.content,
                        "usage": usage,
                        "prompt_messages": messages
                    }
                
                if output_dir and not stream:
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                        log_file_path = os.path.join(output_dir, 'token_usage.jsonl')
                        log_entry = result['usage']
                        with open(log_file_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
                    except Exception as e:
                        print(f"[LLMClient] Warning: Failed to log token usage to {output_dir}. Error: {e}")
                
                for callback in self.callbacks:
                    if hasattr(callback, 'on_llm_end'):
                        try:
                            callback.on_llm_end({
                                "llm_output": {
                                    "token_usage": result["usage"],
                                    "model_name": model
                                },
                                "generations": [[{"text": result["content"]}]]
                            })
                        except Exception:
                            pass
                
                return result
                
            except (openai.APIError, openai.APIConnectionError, openai.RateLimitError) as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                time.sleep(wait_time)
                
            except Exception as e:
                raise
        
        raise Exception(f"Failed to get response from LLM after {max_retries} retries.")

    async def ainvoke(self, messages: List[Dict[str, Any]], stream: bool = False, 
                timeout: Optional[float] = None, max_retries: int = 3, output_dir: Optional[str] = None,
                mode: Optional[str] = None) -> Dict[str, Any]:
        selected_mode = (mode or '').lower()
        if selected_mode not in ('image', 'text', ''):
            selected_mode = ''
        if not selected_mode:
            selected_mode = self._infer_mode_from_messages(messages)
        if selected_mode in ('image'):
            provider_name = self.active_vision_provider
        else:
            provider_name = self.active_text_provider

        cfg = self._load_provider(provider_name)
        client: AsyncOpenAI = cfg['async_client']
        model = cfg['model']
        temperature = cfg['temperature']

        for callback in self.callbacks:
            if hasattr(callback, 'on_llm_start'):
                try:
                    callback.on_llm_start({"name": provider_name}, [msg.get('content', '') for msg in messages])
                except Exception:
                    pass
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    stream=stream,
                    timeout=timeout,
                    seed=42
                )
                
                if stream:
                    collected_chunks = []
                    collected_content = ""
                    
                    async for chunk in response:
                        collected_chunks.append(chunk)
                        try:
                            if chunk.choices and chunk.choices[0].delta.content:
                                content_chunk = chunk.choices[0].delta.content
                                collected_content += content_chunk
                                for callback in self.callbacks:
                                    if hasattr(callback, 'on_llm_new_token'):
                                        callback.on_llm_new_token(content_chunk)
                        except Exception:
                            continue
                    
                    result = {
                        "content": collected_content,
                        "usage": {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0
                        },
                        "prompt_messages": messages
                    }
                else:
                    # Some providers may not return usage
                    try:
                        usage = {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    except Exception:
                        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                    result = {
                        "content": response.choices[0].message.content,
                        "usage": usage,
                        "prompt_messages": messages
                    }
                
                if output_dir and not stream:
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                        log_file_path = os.path.join(output_dir, 'token_usage.jsonl')
                        log_entry = result['usage']
                        with open(log_file_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
                    except Exception as e:
                        print(f"[LLMClient] Warning: Failed to log token usage to {output_dir}. Error: {e}")
                
                for callback in self.callbacks:
                    if hasattr(callback, 'on_llm_end'):
                        try:
                            callback.on_llm_end({
                                "llm_output": {
                                    "token_usage": result["usage"],
                                    "model_name": model
                                },
                                "generations": [[{"text": result["content"]}]]
                            })
                        except Exception:
                            pass
                
                return result
                
            except (openai.APIError, openai.APIConnectionError, openai.RateLimitError) as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                raise
        
        raise Exception(f"Failed to get response from LLM after {max_retries} retries.")

class DefaultCallback:
    """Default callback implementation for LLMClient that tracks LLM interactions without logging"""
    
    def __init__(self):
        self.start_time = None
        self.total_tokens = 0
        
    def on_llm_start(self, serialized, messages):
        self.start_time = time.time()
        
    def on_llm_new_token(self, token):
        pass
        
    def on_llm_end(self, response):
        if self.start_time:
            token_usage = response.get("llm_output", {}).get("token_usage", {})
            total_tokens = token_usage.get("total_tokens", 0)
            self.total_tokens += total_tokens
        
    def on_llm_error(self, error):
        pass
        
    def reset_stats(self):
        self.total_tokens = 0

if __name__ == "__main__":
    llm_client = LLMClient()
    
    test_message = [{"role": "user", "content": "Hello, please briefly introduce yourself."}]
    
    response = llm_client(test_message,mode='text')
    print(f"\nLLM response:\n{response['content']}\n")
    print(f"\nPrompt messages:\n{response['prompt_messages']}\n")
    print(f"Token usage:\n{response['usage']}\n")
