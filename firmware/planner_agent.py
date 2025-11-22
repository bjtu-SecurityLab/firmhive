"""
PlannerAgent - File Analysis Agent that stores results after analysis.
"""
import os
from typing import Dict, List, Any, Optional, Type, Union

from agent.baseagent import BaseAgent
from firmware.tools import FlexibleContext, ExecutableTool, GetContextInfoTool, ShellExecutorTool, Radare2Tool
from firmware.knowagent import KnowledgeBaseAgent
from firmware.prompt.response_format import SHARED_RESPONSE_FORMAT_BLOCK
from firmware.prompt.planner_prompt import DEFAULT_FILE_SYSTEM_PROMPT
from firmware.prompt.function_prompt import DEFAULT_FUNCTION_SYSTEM_PROMPT


DEFAULT_TOOL_CLASSES: List[Union[Type[ExecutableTool], ExecutableTool]] = [
    GetContextInfoTool, ShellExecutorTool, Radare2Tool
]


class PlannerAgent(BaseAgent):
    """File Analysis Agent (receives external Context, dependencies injected externally, includes tool execution environment and objects), and stores results after analysis."""

    def __init__(
        self,
        tools: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        system_prompt: str = None,
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

        kb_context = self.context.copy()
        self.kb_storage_agent = KnowledgeBaseAgent(context=kb_context)
   
    def run(self, user_input: str = None) -> Any:

        findings = str(super().run(user_input=user_input))
        
        store_prompt = (
            f"New analysis results are as follows:\n"
            f"{findings}\n\n"
            f"Based on the above analysis results, your current task is to determine whether they are critical. "
            f"If they do, you need to store and organize the analysis results."
            f"User's core requirement is: {self.context.get('user_input', 'Not provided')}\n"
        )
        self.kb_storage_agent.run(user_input=store_prompt)

        return findings


FUNCTION_ANALYSIS_TOOLS = [Radare2Tool]
