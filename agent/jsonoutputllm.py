import re
import json
from typing import List, Dict, Any, Callable, Optional

from agent.basellm import BaseLLM
from agent.llmclient import LLMClient
from agent.common import Message


class JSONOutputLLM(BaseLLM):
    def __init__(
        self, 
        llm_client: Callable[[List[Message]], str],
        system_prompt: str = "You are a helpful AI assistant.",
        output_schema: Optional[Dict[str, Any]] = None
    ):
        self.output_schema = output_schema or {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Thought process"
                },
                "response": {
                    "type": "string",
                    "description": "The final response to the user"
                }
            },
            "required": ["thought", "response"]
        }
        super().__init__(llm_client, system_prompt)
    
    def _get_response_format_prompt(self) -> str:
        output_schema_str = json.dumps(self.output_schema, ensure_ascii=False, indent=2)
        
        return f"""
You must respond in strict JSON format. Do not add any other text outside the JSON object.
Do not use markdown format (like ```json). Output a single JSON object directly.

The response must be a valid JSON object that conforms to the following schema:

{output_schema_str}

"""
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        try:
            match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
            else:
                match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if match:
                    json_str = match.group(0).strip()
                    if json_str.startswith("```") and json_str.endswith("```"):
                        json_str = json_str[3:-3].strip()
                else:
                    start_index = response_text.find('{')
                    end_index = response_text.rfind('}')

                    if start_index != -1 and end_index != -1 and end_index > start_index:
                        json_str = response_text[start_index:end_index + 1].strip()
                        if json_str.startswith("```") and json_str.endswith("```"):
                             json_str = json_str[3:-3].strip()
                    else:
                        raise json.JSONDecodeError("No valid JSON object found", response_text, 0)

            parsed = json.loads(json_str)
            
            if not isinstance(parsed, dict):
                raise ValueError("Parsed result is not a JSON object")
                
            required_fields = self.output_schema.get("required", [])
            missing_fields = [field for field in required_fields if field not in parsed]
            if missing_fields:
                raise ValueError(f"Response is missing required fields: {', '.join(missing_fields)}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}. Response text (first 200 chars): '{response_text[:200]}'")
            raise
        except ValueError as e:
            print(f"JSON content validation error: {e}. Response text (first 200 chars): '{response_text[:200]}'")
            raise
        except Exception as e:
            print(f"Unknown error during response parsing: {e}. Response text (first 200 chars): '{response_text[:200]}'")
            raise

    def run(self, user_input: str = None) -> Any:
        if user_input:
            self.add_message("user", user_input)
        messages = self.get_messages()
        llm_response = self.get_llm_response(messages, stream=False)
        return self._parse_llm_response(llm_response.get("content"))

    async def arun(self, user_input: str = None) -> Any:
        if user_input:
            self.add_message("user", user_input)
        messages = self.get_messages()
        llm_response = await self.get_llm_response_async(messages, stream=False)
        return self._parse_llm_response(llm_response.get("content"))
