import os
import re
import json
import uuid
import time
import queue
import inspect
import asyncio
import functools
import threading
import concurrent.futures
from typing import List, Dict, Any, Optional, Type, Union

from agent.jsonoutputllm import JSONOutputLLM
from agent.llmclient import LLMClient
from agent.common import Message
from agent.historystrategy import HistoryStrategy
from agent.basetool import ExecutableTool
from agent.context import FlexibleContext


class BaseAgent(JSONOutputLLM):
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        tools: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        system_prompt: str = "You are a helpful AI assistant.",
        output_schema: Optional[Dict[str, Any]] = None,
        max_iterations: int = 25,
        history_strategy: Optional[HistoryStrategy] = None,
        messages_filters: Optional[List[Dict[str, str]]] = None,
        context: Optional[FlexibleContext] = None,
        agent_instance_name: Optional[str] = None
    ):
        self.context = context if context is not None else FlexibleContext()
        self.llm_client = llm_client or LLMClient()
        self.tool_configs = tools if tools is not None else []
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.history_strategy = history_strategy
        if messages_filters is not None:
            self.messages_filters = messages_filters
        self.background_tasks: Dict[str, asyncio.Task] = {} 
        self.background_jobs: Dict[str, Dict] = {}

        self._setup_output_paths(agent_instance_name)
        self.name = agent_instance_name or self.__class__.__name__

        if self.tool_configs:
            initialized_tools_list = self._initialize_tools_from_list(self.tool_configs, self.context)
            self.tools = {tool.name: tool for tool in initialized_tools_list}
        else:
            self.tools = {}

        default_output_schema = {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Think step-by-step here. Analyze the current situation, goals, available tools, and conversation history. Decide whether to call a tool or use the 'finish' action to provide the final answer."
                },
                "action": {
                    "type": "string",
                    "description": "Select the next action. Must be one of the available tool names, 'wait', or 'finish'."
                },
                "action_input": {
                    "oneOf": [
                        {"type": "object"},
                        {"type": "string"} 
                    ],
                    "description": "Parameters for the tool call or the final response. If action is a tool name, provide the required parameters for that tool (usually an object); if it's 'finish', provide the final response using 'final_response' as the key for action_input (usually an object containing a string)."
                },
                "status": {
                    "type": "string",
                    "enum": ["continue", "complete"],
                    "description": "Must be 'continue' (if a tool is selected) or 'complete' (if 'finish' is selected)."
                }
            },
            "required": ["thought", "action", "action_input", "status"]
        }
        self.output_schema = output_schema or default_output_schema
        self.final_output_schema = None
        
        super().__init__(self.llm_client, self.system_prompt, output_schema=self.output_schema)
        
        self.add_message('system', self._build_initial_system_message_content())

    def _setup_output_paths(self, agent_instance_name: Optional[str]):
        log_identifier = agent_instance_name or self.__class__.__name__

        sanitized_agent_id = re.sub(r'[<>:"/\\|?*\s.]', '_', log_identifier)
        if not sanitized_agent_id:
            sanitized_agent_id = "agent"

        parent_log_dir = self.context.get("agent_log_dir")

        current_agent_log_dir: str
        if parent_log_dir and isinstance(parent_log_dir, str):
            subagents_dir = os.path.join(parent_log_dir, "subagents")
            current_agent_log_dir = os.path.join(subagents_dir, f"{sanitized_agent_id}_logs")
        else:
            output_base_dir = self.context.get("output", ".")
            if not isinstance(output_base_dir, str) or not output_base_dir.strip():
                output_base_dir = "."
            current_agent_log_dir = os.path.join(output_base_dir, f"{sanitized_agent_id}_logs")

        self.context.set("agent_log_dir", current_agent_log_dir)

        try:
            os.makedirs(current_agent_log_dir, exist_ok=True)
            self.messages_log_path = os.path.join(current_agent_log_dir, 'message.jsonl')
            print(f"BaseAgent '{log_identifier}' initialized. Messages will be saved to: {self.messages_log_path}")
        except OSError as e:
            print(f"[BaseAgent Setup] Warning: Could not create/access agent log directory '{current_agent_log_dir}'. Error: {e}. Message logging will be disabled.")
            self.messages_log_path = None

    def _initialize_tools_from_list(self, tool_inputs: List[Union[Type[ExecutableTool], ExecutableTool]], context: Optional[FlexibleContext]) -> List[ExecutableTool]:
        final_tools_list: List[ExecutableTool] = []
        processed_names = set()

        if not tool_inputs:
            return []

        for tool_input in tool_inputs:
            tool_instance: Optional[ExecutableTool] = None
            tool_name = "Unknown"

            try:
                if inspect.isclass(tool_input) and issubclass(tool_input, ExecutableTool):
                    tool_class = tool_input
                    tool_name = getattr(tool_class, 'name', tool_class.__name__)
                    if tool_name in processed_names:
                        continue
                    if context is None:
                         print(f"Warning: Cannot instantiate tool class {tool_name} without context. Skipping.")
                         continue
                    tool_instance = tool_class(context=context)
                    processed_names.add(tool_name)

                elif isinstance(tool_input, ExecutableTool):
                    tool_instance = tool_input
                    tool_name = getattr(tool_instance, 'name', tool_instance.__class__.__name__)
                    if tool_name in processed_names:
                        continue

                    if hasattr(tool_instance, 'context') and context is not None:
                        if tool_instance.context is None or id(tool_instance.context) != id(context):
                            tool_instance.context = context
                        else:
                            pass
                    processed_names.add(tool_name)

                else:
                    print(f"Warning: Skipping invalid item in tools list: {tool_input} (Type: {type(tool_input)})")
                    continue

                if tool_instance:
                    required_attrs = ['name', 'description', 'execute', 'parameters']
                    if not all(hasattr(tool_instance, attr) for attr in required_attrs):
                         print(f"Warning: Tool instance {tool_name} is missing required attributes ({required_attrs}) for Tool registration. Skipping.")
                         continue
                    
                    execute_method = getattr(tool_instance, 'execute', None)
                    if not callable(execute_method):
                        print(f"Warning: Tool instance {tool_name} has a non-callable 'execute' attribute. Skipping.")
                        continue

                    final_tools_list.append(tool_instance)

            except Exception as e:
                print(f"Error: Processing tool '{tool_name}' failed: {e}")

        print(f"{self.__class__.__name__} tools: {[t.name for t in final_tools_list]}")
        return final_tools_list

    def _get_response_format_prompt(self) -> str:
        base_prompt = super()._get_response_format_prompt()
        
        if self.final_output_schema:
            final_schema_str = json.dumps(self.final_output_schema, ensure_ascii=False, indent=2)
            final_prompt_part = f"""

--- Final Output Schema ---
When you use the 'finish' action, the value of the 'final_response' key in 'action_input' must be a JSON object that conforms to the following schema:

{final_schema_str}
"""
            return base_prompt + final_prompt_part
            
        return base_prompt

    def _build_initial_system_message_content(self) -> str:
        tool_section = self._format_tools_for_prompt()
        format_section = self._get_response_format_prompt()
        
        full_content = f"{self.system_prompt}\n\n"
        if self.tools:
            full_content += f"Current available tools:\n{tool_section}\n\n"

            background_capable_tools = []
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'parameters') and isinstance(tool.parameters, dict):
                    properties = tool.parameters.get('properties', {})
                    if 'run_in_background' in properties:
                        background_capable_tools.append(tool_name)
            
            if background_capable_tools:
                full_content += "**Background Execution & Task Scheduling**:\n"
                full_content += "- Set `run_in_background: true` in action_input to run tasks asynchronously.\n"
                full_content += "- Results from background tasks are automatically injected when they complete.\n"
                full_content += "- Use 'wait' action when you need background results before proceeding.\n\n"
                full_content += "Scheduling Strategy (avoid omissions & duplicates, maximize efficiency):\n"
                full_content += "1. Identify independent tasks and launch them in background if you don't immediately need results.\n"
                full_content += "2. Continue with other work while background tasks run in parallel.\n"
                full_content += "3. Use 'wait' when dependent tasks require background results.\n"
                full_content += "4. Track all launched background tasks mentally to avoid duplicates.\n"
                full_content += "5. Before 'finish', ensure all background tasks are complete and results incorporated.\n\n"
        else:
            full_content += "Current no available tools.\n\n"
        
        full_content += f"Response format requirements:\n{format_section}"
        return full_content

    def _format_tools_for_prompt(self) -> str:
        if not self.tools:
            return "Current no available tools."
        
        tool_descriptions = "\n\n".join(
            [tool.format_for_prompt() for tool in self.tools.values()]
        )
        return tool_descriptions

    def _prepare_llm_request_messages(self) -> List[Message]:
        if not self.messages or self.messages[0].role != 'system':
            print("Error: Message history is empty or the first message is not a system message!")
            return self.messages[:]

        system_message = self.messages[0]
        history_to_manage = self.messages[1:]  
        
        if self.history_strategy is not None:
            try:
                managed_history = self.history_strategy.apply(history_to_manage)
            except Exception as e:
                print(f"Error: Applying history strategy ({type(self.history_strategy).__name__}) failed: {e}. Falling back to keeping all.")
                managed_history = history_to_manage[:]  
        else:
            managed_history = history_to_manage[:]  

        messages_to_send = [system_message] + managed_history
        return messages_to_send

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        if tool_name not in self.tools:
            error_msg = f"Error: Tool '{tool_name}' does not exist. Available tools: {list(self.tools.keys())}"
            print(error_msg)
            return error_msg

        tool = self.tools[tool_name]
        print(f"Executing tool: {tool_name} with input: {json.dumps(tool_input, ensure_ascii=False, default=str)}")
        result_queue = queue.Queue()

        def execute_in_thread():
            try:
                safe_input_for_exec = {str(k): v for k, v in tool_input.items()}
                result = tool.execute(**safe_input_for_exec)
                result_queue.put(("success", result))
            except Exception as e:
                print(f"Exception in tool '{tool_name}' execution thread: {e}")
                result_queue.put(("error", e))

        thread = threading.Thread(target=execute_in_thread, daemon=True, name=f"ToolThread-{tool_name}")
        thread.start()
        
        default_timeout = 300
        timeout_seconds = tool.timeout if hasattr(tool, 'timeout') and tool.timeout is not None else default_timeout

        try:
            status, result = result_queue.get(timeout=timeout_seconds)
            
            tool_input_str_for_log = json.dumps(tool_input, ensure_ascii=False, default=str)
            
            if status == "success":
                try:
                    if result is None:
                        raw_output = f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n <No return value>"
                        return raw_output
                    
                    result_str = str(result)
                    
                    if not result_str.strip() and result_str != "":
                         raw_output = f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n <Empty string>"
                         return raw_output
                    
                    formatted_result = f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n {result_str}"
                    return formatted_result
                except Exception as e:
                     print(f"Warning: Tool '{tool_name}' result cannot be safely converted to string or formatted: {e}")
                     raw_output = f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n <Undisplayable complex object, conversion/formatting error: {str(e)}>"
                     return raw_output
            else:
                error_obj = result 
                print(f"Tool '{tool_name}' execution failed. Input: {tool_input_str_for_log}. Error: {type(error_obj).__name__}: {str(error_obj)}")
                error_raw_output = f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n <Execution failed, error: {type(error_obj).__name__}: {str(error_obj)}>"
                return error_raw_output
        except queue.Empty:
            print(f"Tool '{tool_name}' execution timed out (exceeded {timeout_seconds} seconds). Input: {json.dumps(tool_input, ensure_ascii=False, default=str)}")
            timeout_raw_output = f"Tool: {tool_name}\nParameters: {json.dumps(tool_input, ensure_ascii=False, default=str)}\nResult:\n <Execution timed out, exceeded {timeout_seconds} seconds>"
            return timeout_raw_output
        except Exception as e:
             print(f"Unexpected queue or processing error during tool '{tool_name}' execution: {e}. Input: {json.dumps(tool_input, ensure_ascii=False, default=str)}")
             error_queue_raw_output = f"Tool: {tool_name}\nParameters: {json.dumps(tool_input, ensure_ascii=False, default=str)}\nResult:\n <Unexpected error during execution: {str(e)}>"
             return error_queue_raw_output

    async def _execute_tool_async(self, tool_name: str, tool_input: dict) -> str:
        """
        Asynchronously executes a tool in a separate thread to avoid blocking the event loop.
        """
        if tool_name not in self.tools:
            error_msg = f"Error: Tool '{tool_name}' does not exist. Available tools: {list(self.tools.keys())}"
            print(error_msg)
            return error_msg

        tool = self.tools[tool_name]
        loop = asyncio.get_running_loop()
        
        default_timeout = 600
        timeout_seconds = tool.timeout if hasattr(tool, 'timeout') and tool.timeout is not None else default_timeout

        try:
            safe_input_for_exec = {str(k): v for k, v in tool_input.items()}
            
            if hasattr(tool, 'aexecute') and callable(getattr(tool, 'aexecute')):
                result = await asyncio.wait_for(
                    tool.aexecute(**safe_input_for_exec), 
                    timeout=timeout_seconds
                )
            else:
                future = loop.run_in_executor(
                    None,
                    functools.partial(tool.execute, **safe_input_for_exec)
                )
                result = await asyncio.wait_for(future, timeout=timeout_seconds)

            tool_input_str_for_log = json.dumps(tool_input, ensure_ascii=False, default=str)
            
            if result is None:
                return f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n <No return value>"
            
            result_str = str(result)
            
            if not result_str.strip() and result_str != "":
                return f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n <Empty string>"
            
            return f"Tool: {tool_name}\nParameters: {tool_input_str_for_log}\nResult:\n {result_str}"

        except asyncio.TimeoutError:
            error_msg = f"Tool: {tool_name}\nParameters: {json.dumps(tool_input, ensure_ascii=False, default=str)}\nResult:\n <Execution failed, error: TimeoutError: Tool execution exceeded {timeout_seconds} seconds.>"
            print(f"Tool '{tool_name}' execution timed out.")
            return error_msg
        except Exception as e:
            error_msg = f"Tool: {tool_name}\nParameters: {json.dumps(tool_input, ensure_ascii=False, default=str)}\nResult:\n <Execution failed, error: {type(e).__name__}: {str(e)}>"
            print(f"Exception in async tool '{tool_name}' execution: {e}")
            return error_msg

    def _auto_execute_tools(self, tool_calls: List[Dict[str, Any]]):
        """Helper method to execute a list of tools concurrently using threads."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_tool_call = {}
            for tool_call in tool_calls:
                tool_name = tool_call.get("name") or tool_call.get("tool_name")
                tool_input = tool_call.get("input") or tool_call.get("tool_input", {})
                if not tool_name:
                    print("Warning: tool_name not provided in tool_call, skipping.")
                    continue
                
                future = executor.submit(self._execute_tool, tool_name, tool_input)
                future_to_tool_call[future] = tool_call

            for future in concurrent.futures.as_completed(future_to_tool_call):
                tool_call = future_to_tool_call[future]
                tool_name = tool_call.get("name") or tool_call.get("tool_name")
                try:
                    tool_result = future.result()
                    print(f"Tool execution result for '{tool_name}':\n{tool_result}")
                    self.add_message('user', tool_result, type='tool_result')
                except Exception as exc:
                    print(f"Tool '{tool_name}' generated an exception: {exc}")
                    error_message = f"Tool execution for '{tool_name}' failed with error: {exc}"
                    self.add_message('user', error_message, type='tool_result_error')

    async def _aauto_execute_tools(self, tool_calls: List[Dict[str, Any]]):
        """Helper method to execute a list of tools concurrently."""
        tasks = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name") or tool_call.get("tool_name")
            tool_input = tool_call.get("input") or tool_call.get("tool_input", {})
            if not tool_name:
                print("Warning: tool_name not provided in tool_call, skipping.")
                continue
            tasks.append(self._execute_tool_async(tool_name, tool_input))
        
        if not tasks:
            return

        tool_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in tool_results:
            if isinstance(result, Exception):
                print(f"An exception occurred during concurrent tool execution: {result}")
                self.add_message('user', f"Tool execution failed with error: {result}", type='tool_result_error')
            else:
                print(f"Tool execution result:\n{result}")
                self.add_message('user', result, type='tool_result')

    def run(self, user_input: str = None, auto_tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        if user_input:
            self.add_message('user', user_input)
            print(f"User input:\n {user_input}")
            print(f"Current context:\n {self.context}")
        
        if auto_tools:
            self._auto_execute_tools(auto_tools)

        final_answer = None
        is_waiting_for_jobs = False
        iteration_count = 0
        while iteration_count < self.max_iterations:
            if not is_waiting_for_jobs:
                iteration_count += 1
            
            print(f"\n----- [Iteration {iteration_count}/{self.max_iterations}] -----")

            injected_a_result = self._check_and_inject_background_jobs()

            if is_waiting_for_jobs and injected_a_result:
                print("A background job completed. Resuming...")
                is_waiting_for_jobs = False
            
            if is_waiting_for_jobs:
                if self.background_jobs:
                    print(f"Waiting for {len(self.background_jobs)} background job(s) to complete...")
                    time.sleep(1)
                    continue
                else:
                    print("All background jobs are complete. Resuming LLM interaction for final summary.")
                    is_waiting_for_jobs = False

            prompt_messages = self._prepare_llm_request_messages()

            max_parse_retries = 3
            parsed_response = None
            raw_response = ""
            
            for retry_count in range(max_parse_retries):
                try:
                    output_dir = self.context.get("output")
                    response_obj = self.get_llm_response(prompt_messages, output_dir=output_dir)
                    raw_response = response_obj['content']
                    print(f"LLM Raw Response (Iteration {iteration_count}, Attempt {retry_count+1}):\n{raw_response}")
                    
                    if retry_count == 0:  
                        self.add_message('assistant', raw_response)    
                    parsed_response = self._parse_llm_response(raw_response)
                    print(f"Parsed LLM Response: {json.dumps(parsed_response, indent=2, ensure_ascii=False, default=str)}")
                    
                    if "error" in parsed_response:
                        raise ValueError(f"Parsing error: {parsed_response['error']}: {parsed_response.get('message', 'Unknown error')}")
                    
                    break
                    
                except Exception as e:
                    print(f"Response parsing failed (Attempt {retry_count+1}/{max_parse_retries}): {e}")
                    if retry_count < max_parse_retries - 1:  
                        format_reminder_prompt = self._get_response_format_prompt()
                        error_feedback_to_llm = f"""
Your previous response could not be parsed or validated correctly due to: {str(e)}
The raw response started with: {raw_response[:200]}...

Please strictly follow the required JSON schema and formatting instructions.
Ensure all required fields are present and the JSON is well-formed.

Required schema:
{format_reminder_prompt}

Retry generating the response.
"""
                        self.add_message('user', error_feedback_to_llm, type='parse_error')
                        prompt_messages = self._prepare_llm_request_messages()  
                    else:
                        print(f"Maximum retry attempts reached, failed to parse LLM response")
                        parsed_response = {
                            "error": "parse_error_max_retries",
                            "thought": f"After {max_parse_retries} attempts, still unable to generate a valid formatted response",
                            "action": "finish",
                            "action_input": {"final_response": f"Sorry, I encountered a technical issue and couldn't process your request correctly."},
                            "status": "complete"
                        }
            
            if parsed_response is None or "error" in parsed_response:
                print("Failed to parse LLM response, using default error response")
                parsed_response = {
                    "thought": "Failed to parse response",
                    "action": "finish",
                    "action_input": {"final_response": "Sorry, I encountered a technical issue and couldn't process your request correctly."},
                    "status": "complete"
                }

            action = parsed_response.get("action")
            action_input = parsed_response.get("action_input")
            status = parsed_response.get("status")  

            if action == "wait":
                if self.background_jobs:
                    print("Action is 'wait', and background jobs are running. Entering waiting mode.")
                    is_waiting_for_jobs = True
                    continue
                else:
                    print("Warning: Agent chose 'wait' action but no background jobs are running.")
                    self.add_message('user', "Warning: You used the 'wait' action, but there are no background jobs running. Please choose another action or use 'finish' to complete the task.", type='system_warning')
                    continue

            if status == "complete" or (action == "finish" and status != "continue"):
                if self.background_jobs:
                    print("Agent wants to finish, but background jobs are running. Entering waiting mode.")
                    is_waiting_for_jobs = True
                    self.add_message('user', "System Note: Your request to finish is acknowledged, but background jobs are still running. The system will wait for them to complete before generating the final summary. To explicitly wait without finishing, use the 'wait' action next time.", type='system_note')
                    continue

                if isinstance(action_input, dict) and "final_response" in action_input:
                    final_answer = action_input["final_response"]
                else:
                    final_answer = parsed_response
                break 

            elif action and action != "finish" and status == "continue": 
                if not isinstance(action_input, dict):
                     tool_result = f"Error: 'action_input' for tool '{action}' is invalid or missing (requires a dictionary), received {type(action_input)}."
                     print(tool_result)
                     self.add_message('user', tool_result, type='tool_result_error')
                else:
                    tool_to_run = self.tools.get(action)
                    if tool_to_run and getattr(tool_to_run, 'is_background_task', False):
                        task_id = f"{action}_{uuid.uuid4().hex[:6]}"
                        print(f"Detected background task tool: '{action}'. Starting with Task ID: {task_id}...")
                        
                        result_queue = queue.Queue()
                        
                        def execute_in_thread_bg():
                            try:
                                safe_input_for_exec = {str(k): v for k, v in action_input.items()}
                                result = tool_to_run.execute(**safe_input_for_exec)
                                result_queue.put(("success", result))
                            except Exception as e:
                                print(f"Exception in background tool '{action}' thread: {e}")
                                result_queue.put(("error", e))
                        
                        thread = threading.Thread(target=execute_in_thread_bg, daemon=True, name=f"BGToolThread-{task_id}")
                        thread.start()
                        
                        self.background_jobs[task_id] = {
                            "thread": thread,
                            "queue": result_queue,
                            "tool_name": action,
                            "tool_input": action_input
                        }
                        
                        tool_started_message = f"Background task started. Task Name: '{action}', Task ID: '{task_id}'. You can continue with other operations; the result will be provided automatically later."
                        print(tool_started_message)
                        self.add_message('user', tool_started_message, type='tool_result')
                        continue

                    else:
                        tool_result = self._execute_tool(action, action_input)
                        print(f"Tool execution result:\n{tool_result}")
                        self.add_message('user', tool_result, type='tool_result')

            else: 
                 print("Warning: LLM response format inconsistency or status mismatch with action")
                 status_mismatch = f"Error: Your response is inconsistent. If action is '{action}', status should be 'complete' if action is 'finish' else 'continue', but received '{status}'."
                 self.add_message('user', status_mismatch, type='error')
                 continue 

        else: 
            print(f"Max iterations reached ({self.max_iterations})")
            final_answer = "Max iterations reached but no answer found."
            if self.messages and self.messages[-1].role == 'assistant':
                final_answer = self.messages[-1].content

        print(f"{self.__class__.__name__} finished")
        return final_answer if final_answer is not None else "Sorry, I was unable to complete the request."

    async def arun(self, user_input: str = None, auto_tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        if user_input:
            self.add_message('user', user_input)
            print(f"User input:\n {user_input}")
            print(f"Current context:\n {self.context}")

        if auto_tools:
            await self._aauto_execute_tools(auto_tools)

        final_answer = None
        is_waiting_for_tasks = False
        
        iteration_count = 0
        while iteration_count < self.max_iterations:
            if not is_waiting_for_tasks:
                iteration_count += 1
            
            print(f"\n----- [Async Iteration {iteration_count}/{self.max_iterations}] -----")

            injected_a_result = await self._check_and_inject_background_tasks()

            if is_waiting_for_tasks and injected_a_result:
                print("A background task completed. Resuming LLM interaction.")
                is_waiting_for_tasks = False

            if is_waiting_for_tasks:
                if self.background_tasks:
                    print(f"Waiting for {len(self.background_tasks)} background task(s) to complete...")
                    await asyncio.sleep(0.5)
                    continue
                else:
                    print("All background tasks are complete. Resuming LLM interaction for final summary.")
                    is_waiting_for_tasks = False
            
            prompt_messages = self._prepare_llm_request_messages()

            max_parse_retries = 3
            parsed_response = None
            raw_response = ""
            
            for retry_count in range(max_parse_retries):
                try:
                    output_dir = self.context.get("output")
                    response_obj = await self.get_llm_response_async(prompt_messages, output_dir=output_dir)
                    raw_response = response_obj['content']
                    print(f"LLM Raw Response (Async Iteration {iteration_count+1}, Attempt {retry_count+1}):\n{raw_response}")
                    
                    if retry_count == 0:  
                        self.add_message('assistant', raw_response)    
                    parsed_response = self._parse_llm_response(raw_response)
                    print(f"Parsed LLM Response: {json.dumps(parsed_response, indent=2, ensure_ascii=False, default=str)}")
                    
                    if "error" in parsed_response:
                        raise ValueError(f"Parsing error: {parsed_response['error']}: {parsed_response.get('message', 'Unknown error')}")
                    
                    break
                    
                except Exception as e:
                    print(f"Response parsing failed (Async Attempt {retry_count+1}/{max_parse_retries}): {e}")
                    if retry_count < max_parse_retries - 1:  
                        format_reminder_prompt = self._get_response_format_prompt()
                        error_feedback_to_llm = f"""
Your previous response could not be parsed or validated correctly due to: {str(e)}
The raw response started with: {raw_response[:200]}...

Please strictly follow the required JSON schema and formatting instructions.
Ensure all required fields are present and the JSON is well-formed.

Required schema:
{format_reminder_prompt}

Retry generating the response.
"""
                        self.add_message('user', error_feedback_to_llm, type='parse_error')
                        prompt_messages = self._prepare_llm_request_messages()  
                    else:
                        print(f"Maximum retry attempts reached, failed to parse LLM response")
                        parsed_response = {
                            "error": "parse_error_max_retries",
                            "thought": f"After {max_parse_retries} attempts, still unable to generate a valid formatted response",
                            "action": "finish",
                            "action_input": {"final_response": f"Sorry, I encountered a technical issue and couldn't process your request correctly."},
                            "status": "complete"
                        }
            
            if parsed_response is None or "error" in parsed_response:
                print("Failed to parse LLM response, using default error response")
                parsed_response = {
                    "thought": "Failed to parse response",
                    "action": "finish",
                    "action_input": {"final_response": "Sorry, I encountered a technical issue and couldn't process your request correctly."},
                    "status": "complete"
                }

            action = parsed_response.get("action")
            action_input = parsed_response.get("action_input")
            status = parsed_response.get("status")  

            if action == "wait":
                if self.background_tasks:
                    print("Action is 'wait', and background tasks are running. Entering waiting mode.")
                    is_waiting_for_tasks = True
                    continue
                else:
                    print("Warning: Agent chose 'wait' action but no background tasks are running.")
                    self.add_message('user', "Warning: You used the 'wait' action, but there are no background tasks running. Please choose another action or use 'finish' to complete the task.", type='system_warning')
                    continue

            if status == "complete" or (action == "finish" and status != "continue"):
                if self.background_tasks:
                    print("Agent wants to finish, but background tasks are running. Entering waiting mode.")
                    is_waiting_for_tasks = True
                    self.add_message('user', "System Note: Your request to finish is acknowledged. The system will now wait for all background tasks to complete before generating the final summary. To explicitly wait without finishing, use the 'wait' action next time.", type='system_note')
                    continue
                
                if isinstance(action_input, dict) and "final_response" in action_input:
                    final_answer = action_input["final_response"]
                else:
                    final_answer = parsed_response
                break 

            elif action and action != "finish" and status == "continue": 
                if not isinstance(action_input, dict):
                     tool_result = f"Error: 'action_input' for tool '{action}' is invalid or missing (requires a dictionary), received {type(action_input)}."
                     print(tool_result)
                     self.add_message('user', tool_result, type='tool_result_error')
                else:
                    tool_to_run = self.tools.get(action)
                    if tool_to_run and getattr(tool_to_run, 'is_background_task', False):
                        task_id = f"{action}_{uuid.uuid4().hex[:6]}"
                        # Detected a background task tool; start it and inform the user in English
                        print(f"Detected background task tool: '{action}'. Starting, task ID: {task_id}...")
                        
                        new_task = asyncio.create_task(self._execute_tool_async(action, action_input))
                        self.background_tasks[task_id] = new_task
                        
                        tool_started_message = (
                            f"Background task started. Task name: '{action}', task ID: '{task_id}'. "
                            "You can continue with other operations; the result will arrive automatically later."
                        )
                        print(tool_started_message)
                        self.add_message('user', tool_started_message, type='tool_result')
                        continue

                    else:
                        tool_result = await self._execute_tool_async(action, action_input)
                        print(f"Tool execution result:\n{tool_result}")
                        self.add_message('user', tool_result, type='tool_result')

            else: 
                 print("Warning: LLM response format inconsistency or status mismatch with action")
                 status_mismatch = f"Error: Your response is inconsistent. If action is '{action}', status should be 'complete' if action is 'finish' else 'continue', but received '{status}'."
                 self.add_message('user', status_mismatch, type='error')
                 continue 

        else:
            print(f"Max iterations reached ({self.max_iterations})")
            final_answer = "Max iterations reached but no answer found."
            if self.messages and self.messages[-1].role == 'assistant':
                final_answer = self.messages[-1].content
        
        print(f"{self.__class__.__name__} finished")
        return final_answer if final_answer is not None else "Sorry, I was unable to complete the request."

    def _check_and_inject_background_jobs(self) -> bool:
        """
        Checks the status of background jobs, injects results of completed jobs into the message history.
        Returns: True if at least one job result was injected, otherwise False.
        """
        completed_jobs = {}
        injected_a_result = False
        for task_id, job_info in self.background_jobs.items():
            if not job_info['thread'].is_alive():
                try:
                    status, result = job_info['queue'].get_nowait()
                    tool_name = job_info['tool_name']
                    tool_input = job_info['tool_input']
                    tool_input_str = json.dumps(tool_input, ensure_ascii=False, default=str)
                    
                    if status == "success":
                        result_str = str(result)
                        job_result_message = f"Background job '{task_id}' ({tool_name}) has completed.\nParameters: {tool_input_str}\nResult:\n{result_str}"
                    else:
                        error_obj = result
                        job_result_message = f"Background job '{task_id}' ({tool_name}) failed.\nParameters: {tool_input_str}\nError: {type(error_obj).__name__}: {str(error_obj)}"

                    print(f"--- Injected Background Job Result ---\n{job_result_message}\n---------------------------------------")
                    self.add_message('user', job_result_message, type='background_tool_result')

                except queue.Empty:
                    error_message = f"Background job '{task_id}' finished but no result was found in its queue."
                    print(f"--- Injected Background Job Error ---\n{error_message}\n--------------------------------------")
                    self.add_message('user', error_message, type='background_tool_error')
                except Exception as e:
                    error_message = f"An unexpected error occurred while processing result for background job '{task_id}': {e}"
                    print(f"--- Injected Background Job Error ---\n{error_message}\n--------------------------------------")
                    self.add_message('user', error_message, type='background_tool_error')
                
                completed_jobs[task_id] = job_info
                injected_a_result = True

        for task_id in completed_jobs:
            del self.background_jobs[task_id]
        
        return injected_a_result

    async def _check_and_inject_background_tasks(self) -> bool:
        """
        Check the status of background tasks and inject any completed task results into
        the message history.
        Returns: True if at least one task result was injected; otherwise False.
        """
        completed_tasks = {}
        injected_a_result = False
        for task_id, task in self.background_tasks.items():
            if task.done():
                try:
                    result = await task
                    tool_result_message = (
                        f"Background task '{task_id}' has completed.\nResult:\n{result}"
                    )
                    print(f"--- Injected Background Task Result ---\n{tool_result_message}\n---------------------------------------")
                    self.add_message('user', tool_result_message, type='background_tool_result')
                except Exception as e:
                    error_message = (
                        f"Background task '{task_id}' failed.\nError: {type(e).__name__}: {e}"
                    )
                    print(f"--- Injected Background Task Error ---\n{error_message}\n--------------------------------------")
                    self.add_message('user', error_message, type='background_tool_error')
                
                completed_tasks[task_id] = task
                injected_a_result = True

        for task_id in completed_tasks:
            del self.background_tasks[task_id]
        
        return injected_a_result

    def stream(self, user_input: str = None) -> List[Dict[str, Any]]:
        print(f"System prompt:\n {self.messages[0].content}")
        conversation: List[Dict[str, Any]] = []
        
        if self.messages and self.messages[0].role == "system":
            conversation.append({
                "role": "system",
                "content": self.messages[0].content
            })

        if user_input:
            self.add_message('user', user_input)
            print(f"Stream input:\n {user_input}")
            conversation.append({
                "role": "user",
                "content": user_input
            })
        
        for i in range(self.max_iterations):
            print(f"\n----- [Iteration {i + 1}/{self.max_iterations}] (Stream Mode) -----")
            
            prompt_messages = self._prepare_llm_request_messages()
            
            max_parse_retries = 3
            parsed_response = None
            raw_response = ""

            for retry_count in range(max_parse_retries):
                print(f"----- Calling LLM (Stream Mode, Attempt {retry_count+1}/{max_parse_retries}) -----")
                try:
                    output_dir = self.context.get("output")
                    response_obj = self.get_llm_response(prompt_messages, output_dir=output_dir)
                    raw_response = response_obj['content']
                    print(f"----- LLM Raw Response (first 500) -----\n{raw_response[:500]}{'...' if len(raw_response)>500 else ''}\n" + "-"*20)
                    
                    if retry_count == 0:
                        self.add_message('assistant', raw_response)
                        conversation.append({
                            "role": "assistant",
                            "content": raw_response
                        })
                    
                    print(f"----- Parsing LLM Response (Stream Mode, Attempt {retry_count+1}/{max_parse_retries}) -----")
                    parsed_response = self._parse_llm_response(raw_response)
                    print(f"----- Parsed Result -----\n{json.dumps(parsed_response, indent=2, ensure_ascii=False)}\n" + "-"*20)
                    
                    if "error" in parsed_response:
                        raise ValueError(f"Parsing error: {parsed_response['error']}: {parsed_response.get('message', 'Unknown error')}")
                    
                    break
                    
                except Exception as e:
                    print(f"Response parsing failed (Stream Mode, Attempt {retry_count+1}/{max_parse_retries}): {e}")
                    if retry_count < max_parse_retries - 1:  
                        format_reminder = self._get_response_format_prompt()
                        error_message_to_llm = f"""
Your previous response could not be parsed or validated: {str(e)}.
Raw response started with: {raw_response[:200]}...
Please strictly follow the required JSON schema:
{format_reminder}
Retry generating the response.
"""
                        self.add_message('user', error_message_to_llm, type='parse_error')
                        conversation.append({
                            "role": "system_feedback_to_llm",
                            "content": error_message_to_llm
                        })
                        prompt_messages = self._prepare_llm_request_messages()  
                    else:
                        print(f"Maximum retry attempts reached, failed to parse LLM response (Stream Mode)")
                        parsed_response = {
                            "error": "parse_error_max_retries",
                            "thought": f"After {max_parse_retries} attempts, still unable to generate a valid formatted response",
                            "action": "finish",
                            "action_input": {"final_response": "Sorry, I encountered a technical issue with response formatting."},
                            "status": "complete"
                        }
                        conversation.append({
                            "role": "error",
                            "content": f"After {max_parse_retries} attempts, still unable to parse LLM response"
                        })
            
            if parsed_response is None or "error" in parsed_response:
                print("Failed to parse LLM response, using default error response (Stream Mode)")
                parsed_response = {
                    "thought": "Failed to parse response",
                    "action": "finish",
                    "action_input": {"final_response": "Sorry, I encountered a technical issue and couldn't process your request correctly."},
                    "status": "complete"
                }
                if "error" not in conversation[-1]["role"]:  
                    conversation.append({
                        "role": "error",
                        "content": "Failed to parse response, cannot continue processing"
                    })
            
            action = parsed_response.get("action")
            action_input = parsed_response.get("action_input")
            status = parsed_response.get("status")
            
            if status == "complete" or (action == "finish" and status != "continue"):
                print("----- Completion status detected (Stream Mode) -----")
                final_response_content = "Task completed."
                if isinstance(action_input, dict) and "final_response" in action_input:
                    final_response_content = action_input["final_response"]
                elif isinstance(action_input, str):
                    final_response_content = action_input
                elif parsed_response.get("thought"):
                    final_response_content = f"Completed. Last thought: {parsed_response.get('thought')}"
                
                if conversation and conversation[-1].get("role") == "assistant_thought_process":
                    conversation[-1] = {"role": "assistant", "content": final_response_content}
                else:
                    conversation.append({"role": "assistant", "content": final_response_content})
                print(f"----- Final Response: {str(final_response_content)[:200]}...")
                break  
            
            elif action and action != "finish" and status == "continue":  
                print(f"----- Requesting tool execution: {action} (Stream Mode) -----")
                
                if not isinstance(action_input, dict):
                    tool_error_msg = f"Error: Tool '{action}' expects 'action_input' to be a dictionary, received {type(action_input)}: {str(action_input)[:100]}..."
                    print(f"----- {tool_error_msg}")
                    self.add_message('user', tool_error_msg, type='tool_result_error')
                    
                    conversation.append({
                        "role": "tool_error",
                        "tool_name": action,
                        "content": tool_error_msg
                    })
                else:
                    conversation.append({
                        "role": "tool_call",
                        "tool_name": action,
                        "tool_input": action_input
                    })
                    print(f"----- Executing tool '{action}' with input: {json.dumps(action_input, ensure_ascii=False, default=str)}")
                    tool_result_str = self._execute_tool(action, action_input)
                    print(f"----- Tool '{action}' result (first 500 chars): {tool_result_str[:500]}{'...' if len(tool_result_str)>500 else ''}")
                    self.add_message('user', tool_result_str, type='tool_result')
                    
                    conversation.append({
                        "role": "tool_result",
                        "tool_name": action,
                        "content": tool_result_str
                    })
            
            else:  
                print("----- Warning: LLM response format inconsistency or status mismatch with action (Stream Mode) -----")
                status_mismatch = f"Error: Response is inconsistent. If action is '{action}', status should be {'complete' if action == 'finish' else 'continue'}, but received '{status}'."
                self.add_message('user', status_mismatch, type='error')
                
                conversation.append({
                    "role": "error",
                    "content": status_mismatch
                })
                continue
        
        else:  
            print(f"----- Max iterations reached ({self.max_iterations}) (Stream Mode) -----")
            last_message_content = "Max iterations reached."
            if self.messages and self.messages[-1].role == 'assistant':
                last_assistant_response = self.messages[-1].content
                try:
                    parsed_last = self._parse_llm_response(last_assistant_response)
                    if isinstance(parsed_last.get("action_input"), dict) and "final_response" in parsed_last["action_input"]:
                        last_message_content = parsed_last["action_input"]["final_response"]
                    elif parsed_last.get("thought"):
                         last_message_content = f"Max iterations. Last thought: {parsed_last.get('thought')}"
                except Exception:
                    last_message_content = f"Max iterations. Last raw response: {last_assistant_response[:200]}..."
            
            conversation.append({
                "role": "assistant",
                "content": last_message_content
            })

        print(f"===== Agent run finished (Stream Mode) =====")
        return conversation

    async def astream(self, user_input: str = None) -> List[Dict[str, Any]]:
        print(f"System prompt:\n {self.messages[0].content}")
        conversation: List[Dict[str, Any]] = []
        
        if self.messages and self.messages[0].role == "system":
            conversation.append({
                "role": "system",
                "content": self.messages[0].content
            })

        if user_input:
            self.add_message('user', user_input)
            print(f"Stream input:\n {user_input}")
            conversation.append({
                "role": "user",
                "content": user_input
            })
        
        for i in range(self.max_iterations):
            print(f"\n----- [Iteration {i + 1}/{self.max_iterations}] (Async Stream Mode) -----")
            
            prompt_messages = self._prepare_llm_request_messages()
            
            max_parse_retries = 3
            parsed_response = None
            raw_response = ""

            for retry_count in range(max_parse_retries):
                print(f"----- Calling LLM (Async Stream Mode, Attempt {retry_count+1}/{max_parse_retries}) -----")
                try:
                    output_dir = self.context.get("output")
                    response_obj = await self.get_llm_response_async(prompt_messages, output_dir=output_dir)
                    raw_response = response_obj['content']
                    print(f"----- LLM Raw Response (first 500) -----\n{raw_response[:500]}{'...' if len(raw_response)>500 else ''}\n" + "-"*20)
                    
                    if retry_count == 0:
                        self.add_message('assistant', raw_response)
                        conversation.append({
                            "role": "assistant",
                            "content": raw_response
                        })
                    
                    print(f"----- Parsing LLM Response (Async Stream Mode, Attempt {retry_count+1}/{max_parse_retries}) -----")
                    parsed_response = self._parse_llm_response(raw_response)
                    print(f"----- Parsed Result -----\n{json.dumps(parsed_response, indent=2, ensure_ascii=False)}\n" + "-"*20)
                    
                    if "error" in parsed_response:
                        raise ValueError(f"Parsing error: {parsed_response['error']}: {parsed_response.get('message', 'Unknown error')}")
                    
                    break
                    
                except Exception as e:
                    print(f"Response parsing failed (Async Stream Mode, Attempt {retry_count+1}/{max_parse_retries}): {e}")
                    if retry_count < max_parse_retries - 1:  
                        format_reminder = self._get_response_format_prompt()
                        error_message_to_llm = f"""
Your previous response could not be parsed or validated: {str(e)}.
Raw response started with: {raw_response[:200]}...
Please strictly follow the required JSON schema:
{format_reminder}
Retry generating the response.
"""
                        self.add_message('user', error_message_to_llm, type='parse_error')
                        conversation.append({
                            "role": "system_feedback_to_llm",
                            "content": error_message_to_llm
                        })
                        prompt_messages = self._prepare_llm_request_messages()  
                    else:
                        print(f"Maximum retry attempts reached, failed to parse LLM response (Async Stream Mode)")
                        parsed_response = {
                            "error": "parse_error_max_retries",
                            "thought": f"After {max_parse_retries} attempts, still unable to generate a valid formatted response",
                            "action": "finish",
                            "action_input": {"final_response": "Sorry, I encountered a technical issue with response formatting."},
                            "status": "complete"
                        }
                        conversation.append({
                            "role": "error",
                            "content": f"After {max_parse_retries} attempts, still unable to parse LLM response"
                        })
            
            if parsed_response is None or "error" in parsed_response:
                print("Failed to parse LLM response, using default error response (Async Stream Mode)")
                parsed_response = {
                    "thought": "Failed to parse response",
                    "action": "finish",
                    "action_input": {"final_response": "Sorry, I encountered a technical issue and couldn't process your request correctly."},
                    "status": "complete"
                }
                if "error" not in conversation[-1]["role"]:  
                    conversation.append({
                        "role": "error",
                        "content": "Failed to parse response, cannot continue processing"
                    })
            
            action = parsed_response.get("action")
            action_input = parsed_response.get("action_input")
            status = parsed_response.get("status")
            
            if status == "complete" or (action == "finish" and status != "continue"):
                print("----- Completion status detected (Async Stream Mode) -----")
                final_response_content = "Task completed."
                if isinstance(action_input, dict) and "final_response" in action_input:
                    final_response_content = action_input["final_response"]
                elif isinstance(action_input, str):
                    final_response_content = action_input
                elif parsed_response.get("thought"):
                    final_response_content = f"Completed. Last thought: {parsed_response.get('thought')}"
                
                if conversation and conversation[-1].get("role") == "assistant_thought_process":
                    conversation[-1] = {"role": "assistant", "content": final_response_content}
                else:
                    conversation.append({"role": "assistant", "content": final_response_content})
                print(f"----- Final Response: {str(final_response_content)[:200]}...")
                break  
            
            elif action and action != "finish" and status == "continue":  
                print(f"----- Requesting tool execution: {action} (Async Stream Mode) -----")
                
                if not isinstance(action_input, dict):
                    tool_error_msg = f"Error: Tool '{action}' expects 'action_input' to be a dictionary, received {type(action_input)}: {str(action_input)[:100]}..."
                    print(f"----- {tool_error_msg}")
                    self.add_message('user', tool_error_msg, type='tool_result_error')
                    
                    conversation.append({
                        "role": "tool_error",
                        "tool_name": action,
                        "content": tool_error_msg
                    })
                else:
                    conversation.append({
                        "role": "tool_call",
                        "tool_name": action,
                        "tool_input": action_input
                    })
                    print(f"----- Executing tool '{action}' with input: {json.dumps(action_input, ensure_ascii=False, default=str)}")
                    tool_result_str = await self._execute_tool_async(action, action_input)
                    print(f"----- Tool '{action}' result (first 500 chars): {tool_result_str[:500]}{'...' if len(tool_result_str)>500 else ''}")
                    self.add_message('user', tool_result_str, type='tool_result')
                    
                    conversation.append({
                        "role": "tool_result",
                        "tool_name": action,
                        "content": tool_result_str
                    })
            
            else:  
                print("----- Warning: LLM response format inconsistency or status mismatch with action (Async Stream Mode) -----")
                status_mismatch = f"Error: Response is inconsistent. If action is '{action}', status should be {'complete' if action == 'finish' else 'continue'}, but received '{status}'."
                self.add_message('user', status_mismatch, type='error')
                
                conversation.append({
                    "role": "error",
                    "content": status_mismatch
                })
                continue
        
        else:  
            print(f"----- Max iterations reached ({self.max_iterations}) (Async Stream Mode) -----")
            last_message_content = "Max iterations reached."
            if self.messages and self.messages[-1].role == 'assistant':
                last_assistant_response = self.messages[-1].content
                try:
                    parsed_last = self._parse_llm_response(last_assistant_response)
                    if isinstance(parsed_last.get("action_input"), dict) and "final_response" in parsed_last["action_input"]:
                        last_message_content = parsed_last["action_input"]["final_response"]
                    elif parsed_last.get("thought"):
                         last_message_content = f"Max iterations. Last thought: {parsed_last.get('thought')}"
                except Exception:
                    last_message_content = f"Max iterations. Last raw response: {last_assistant_response[:200]}..."
            
            conversation.append({
                "role": "assistant",
                "content": last_message_content
            })

        print(f"===== Agent run finished (Async Stream Mode) =====")
        return conversation
