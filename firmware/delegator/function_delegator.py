"""
Function-related delegators for analyzing function call chains in binary files.
"""
import os
from typing import Any, Dict, Optional, List, Union, Type

from agent.baseagent import BaseAgent
from agent.context import FlexibleContext
from agent.basetool import ExecutableTool
from agent.core.assistants import BaseAssistant, ParallelBaseAssistant


class ParallelFunctionDelegator(ParallelBaseAssistant):
    name = "FunctionDelegator"
    description = """
    Function Analysis Delegator - An agent specialized in analyzing function call chains in binary files. Its responsibility is to forward-track the flow of tainted data between function calls. You can delegate potential external entry points to this agent for in-depth tracing.
    """

    parameters = {
        "type": "object",
        "properties": {
            "tasks": { 
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string", 
                            "description": (
                                "When creating an analysis task for a sub-function, your description must clearly include the following four points:\n"
                                "1. **Target Function**: The name and address of the sub-function to analyze.\n"
                                "2. **Taint Entry**: The specific register or stack address where the taint is located in the sub-function (e.g., 'The taint is in the first parameter register r0').\n"
                                "3. **Taint Source**: How this tainted data was produced in the parent function (e.g., 'This value was obtained by the parent function main via calling nvram_get(\"lan_ipaddr\")').\n"
                                "4. **Analysis Objective**: Clearly indicate that the new task should trace this new taint entry (e.g., 'Trace r0 within the sub-function')."
                            )
                        },
                        "task_context": {
                            "type": "string", 
                            "description": (
                                "(Optional) Provide supplementary context that may affect the analysis. This information is not part of the taint flow itself, but may influence the execution path of the sub-function. For example:\n"
                                "- 'The value of register r2 at this point is 0x100, representing the maximum buffer length.'\n"
                                "- 'The global variable `is_admin` was set to 1 before this call.'\n"
                                "- 'Assume the file has been successfully opened during analysis.'"
                            )
                        }
                    },
                    "required": ["task"]
                },
                "description": "A list of function analysis tasks to be performed."
            },
            "run_in_background": {
                "type": "boolean",
                "description": "Whether to run this task in the background.",
                "default": False
            }
        },
        "required": ["tasks"]
    }

    def __init__(self, 
                 context: FlexibleContext,
                 agent_class_to_create: Type[BaseAgent] = BaseAgent,
                 default_sub_agent_tool_classes: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
                 default_sub_agent_max_iterations: int = 10,
                 sub_agent_system_prompt: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 timeout: Optional[int] = None
                ):
        final_name = name or ParallelFunctionDelegator.name
        final_description = description or ParallelFunctionDelegator.description
        
        super().__init__(
            context=context,
            agent_class_to_create=agent_class_to_create,
            default_sub_agent_tool_classes=default_sub_agent_tool_classes,
            default_sub_agent_max_iterations=default_sub_agent_max_iterations,
            sub_agent_system_prompt=sub_agent_system_prompt,
            name=final_name,
            description=final_description,
            timeout=timeout
        )

    def _get_sub_agent_task_details(self, **task_item: Any) -> Dict[str, Any]:
        task = task_item.get("task", "")
        task_context = task_item.get("task_context", "")
        return {
            "task": task,
            "task_context": task_context
        }
    
    def _build_sub_agent_prompt(self, usr_init_msg: Optional[str], **task_details: Any) -> str:
        task = task_details.get("task")
        task_context = task_details.get("task_context")

        usr_init_msg_content = usr_init_msg if usr_init_msg else "No user initial request provided"
        task_content = task if task else "No task provided"

        prompt_parts = [
            f"User core request:\n{usr_init_msg_content}",
            f"Current specific task:\n{task_content}"
        ]

        if task_context:
            prompt_parts.append(f"Supplementary context:\n{task_context}")

        return "\n\n".join(prompt_parts)
    
    def _extract_task_list(self, **kwargs: Any) -> List[Dict[str, Any]]:
        tasks = kwargs.get("tasks", [])
        if not isinstance(tasks, list):
            return []
        return [task for task in tasks if isinstance(task, dict)]
