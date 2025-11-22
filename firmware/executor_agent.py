"""
ExecutorAgent - System Analysis Agent for firmware analysis.
"""
import os
from typing import Dict, List, Any, Optional, Type, Union

from agent.baseagent import BaseAgent
from firmware.tools import FlexibleContext, ExecutableTool, GetContextInfoTool, ShellExecutorTool, Radare2Tool
from firmware.prompt.executor_prompt import DEFAULT_WORKER_EXECUTOR_SYSTEM_PROMPT


DEFAULT_TOOL_CLASSES: List[Union[Type[ExecutableTool], ExecutableTool]] = [
    GetContextInfoTool, ShellExecutorTool, Radare2Tool
]


class ExecutorAgent(BaseAgent):
    """System Analysis Agent (receives external Context, dependencies injected externally, includes tool execution environment and objects)"""

    def __init__(
        self,
        tools: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        system_prompt: str = DEFAULT_WORKER_EXECUTOR_SYSTEM_PROMPT,
        output_schema: Optional[Dict[str, Any]] = None,
        max_iterations: int = 50,
        history_strategy = None,
        context: Optional[FlexibleContext] = None,
        messages_filters: List[Dict[str, str]] = None,
        **extra_params: Any
    ):
        self.file_path = context.get("file_path") if context else None
        self.file_name = os.path.basename(self.file_path) if self.file_path else None
        self.current_dir = context.get("current_dir")

        tools_to_pass = tools if tools is not None else DEFAULT_TOOL_CLASSES
        self.messages_filters = messages_filters if messages_filters else [{'from': context.get('base_path')+os.path.sep, 'to': ''}, {'from': 'user_name', 'to': 'user'}] if context and context.get('base_path') else []
        
        super().__init__(
            tools=tools_to_pass, 
            system_prompt=system_prompt, 
            output_schema=output_schema, 
            max_iterations=max_iterations, 
            history_strategy=history_strategy, 
            context=context,
            messages_filters=self.messages_filters,
            **extra_params
        )
