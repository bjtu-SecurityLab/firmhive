"""
Directory-related delegators for analyzing subdirectories within firmware.
"""
import os
from typing import Any, Dict, Optional, List, Union, Type

from agent.baseagent import BaseAgent
from agent.context import FlexibleContext
from agent.basetool import ExecutableTool
from agent.core.assistants import BaseAssistant, ParallelBaseAssistant


class DeepDirectoryAnalysisAssistant(BaseAssistant):
    name = "DeepDirectoryAnalysisAssistant"
    description = """
    Agent for deep analysis of a specified subdirectory within your current directory scope.
    Can only analyze subdirectories in the current directory (direct children or deeper nested directories).
    Use simple relative paths like 'hnap' or 'subdir/nested' for directories in your scope.
    Suitable for deep analysis tasks of a single subdirectory. You can decide the next analysis task after observing the result of a single step. For targeted analysis such as verification tasks, it is highly recommended to use this agent.
    """
    parameters = {
        "type": "object",
        "properties": {
            "dir_name": {
                "type": "string",
                "description": "The directory path relative to your current directory (e.g., 'hnap', 'init.d'). You can only access subdirectories within your current directory scope."
            },
            "run_in_background": {
                "type": "boolean",
                "description": "Whether to run this task in the background.",
                "default": False
            }
        },
        "required": ["dir_name"],
        "description": "Object containing the directory analysis target. Use paths relative to your current working directory."
    }
    timeout = 9600

    def __init__(
        self,
        context: FlexibleContext,
        agent_class_to_create: Type[BaseAgent] = BaseAgent,
        default_sub_agent_tool_classes: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        default_sub_agent_max_iterations: int = 10,
        sub_agent_system_prompt: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        final_name = name or DeepDirectoryAnalysisAssistant.name
        final_description = description or DeepDirectoryAnalysisAssistant.description

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
        
    def _get_sub_agent_task_details(self, **kwargs: Any) -> Dict[str, Any]:
        dir_name = kwargs.get("dir_name")
        if not dir_name or not isinstance(dir_name, str):
            return {"task": "Error: A valid directory name is required for analysis."}
        
        return {
            "task": f"Focus on analyzing the content of directory '{dir_name}' and look for exploitable information and clues.",
            "dir_name": dir_name
        }

    def _prepare_sub_agent_context(self, sub_agent_context: FlexibleContext, **task_details: Any) -> FlexibleContext:
        dir_name = task_details.get("dir_name")

        if not dir_name or not isinstance(dir_name, str):
            raise ValueError("Error: A valid directory path is required for analysis.")

        dir_name = dir_name.lstrip('/')

        firmware_root = self.context.get("base_path")
        if not firmware_root or not os.path.isdir(firmware_root):
            raise ValueError("Missing valid firmware root directory 'base_path' in context, cannot resolve path.")

        scope_dir = self.context.get("current_dir")
        if not scope_dir or not os.path.isdir(scope_dir):
            raise ValueError("Missing valid working directory 'current_dir' in context, cannot perform scope check.")

        resolved_path_from_current = os.path.normpath(os.path.join(scope_dir, dir_name))
        resolved_path_from_root = os.path.normpath(os.path.join(firmware_root, dir_name))
        
        if os.path.exists(resolved_path_from_current) and os.path.isdir(resolved_path_from_current):
            resolved_path = resolved_path_from_current
        elif os.path.exists(resolved_path_from_root) and os.path.isdir(resolved_path_from_root):
            resolved_path = resolved_path_from_root
        else:
            resolved_path = resolved_path_from_current

        real_firmware_root = os.path.realpath(firmware_root)
        real_scope_dir = os.path.realpath(scope_dir)
        try:
            real_resolved_path = os.path.realpath(resolved_path)
        except FileNotFoundError:
            raise ValueError(f"Directory '{dir_name}' not found in firmware.")

        if not os.path.commonpath([real_resolved_path, real_firmware_root]) == real_firmware_root:
            raise ValueError(f"The provided path '{dir_name}' is invalid, may contain '..' or point outside the firmware root directory.")

        if not os.path.commonpath([real_resolved_path, real_scope_dir]) == real_scope_dir:
            current_dir_name = os.path.relpath(scope_dir, firmware_root)
            basename_only = os.path.basename(dir_name)
            potential_correct_path = os.path.join(current_dir_name, basename_only)
            potential_full_path = os.path.join(firmware_root, potential_correct_path)
            
            if os.path.exists(potential_full_path) and os.path.isdir(potential_full_path):
                raise ValueError(
                    f"Path format error: You provided '{dir_name}', but you must use the COMPLETE path relative to firmware root. "
                    f"You are in directory '{current_dir_name}'. To analyze its subdirectory '{basename_only}', "
                    f"use the full path: '{potential_correct_path}' (not just '{basename_only}')."
                )
            else:
                raise ValueError(
                    f"Access denied: Directory '{dir_name}' is not within your current working directory '{current_dir_name}'. "
                    f"You are strictly restricted to analyzing subdirectories within '{current_dir_name}' only. "
                    f"Cross-directory and upward directory analysis is not allowed. If you need to analyze other directories, "
                    f"report this limitation and suggest that a different agent with appropriate scope should handle it."
                )

        if not os.path.isdir(resolved_path):
            raise ValueError(f"The specified path '{dir_name}' is not a valid directory.")

        sub_agent_context.set("current_dir", resolved_path)
        sub_agent_context.set("file_path", None)
        return sub_agent_context

    def _build_sub_agent_prompt(self, usr_init_msg: Optional[str], **task_details: Any) -> str:
        task = task_details.get("task", "No directory analysis task provided.")
        
        usr_init_msg_content = usr_init_msg if usr_init_msg else "No user initial request provided"
        
        return (
            f"User initial request:\n{usr_init_msg_content}\n\n"
            f"Current task:\n{task}"
        )



class ParallelDeepDirectoryAnalysisDelegator(ParallelBaseAssistant):
    name = "ParallelDeepDirectoryAnalysisDelegator"
    description = """
    Deep directory analysis delegator - distributes analysis tasks for multiple subdirectories within your current directory scope to sub-agents for parallel processing.
    Can only analyze subdirectories in the current directory (direct children or deeper nested directories).
    Use simple relative paths for directories in your scope.
    Suitable for deep analysis tasks of multiple subdirectories at the same time. For complex tasks or comprehensive analysis, it is highly recommended to use this delegator.
    """
    parameters = {
        "type": "object",
        "properties": {
            "dir_names": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "The directory path relative to your current directory (e.g., 'hnap', 'init.d'). You can only access subdirectories within your current directory scope."
                },
                "description": "List of directory paths to be analyzed in parallel. Use paths relative to your current working directory."
            },
            "run_in_background": {
                "type": "boolean",
                "description": "Whether to run this task in the background.",
                "default": False
            }
        },
        "required": ["dir_names"],
        "description": "Object containing the list of directory analysis targets within your current directory scope."
    }
    timeout = 9600

    def __init__(
        self,
        context: FlexibleContext,
        agent_class_to_create: Type[BaseAgent] = BaseAgent,
        default_sub_agent_tool_classes: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        default_sub_agent_max_iterations: int = 10,
        sub_agent_system_prompt: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        final_name = name or ParallelDeepDirectoryAnalysisDelegator.name
        final_description = description or ParallelDeepDirectoryAnalysisDelegator.description

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

    def _extract_task_list(self, **kwargs: Any) -> List[Dict[str, Any]]:
        dir_names = kwargs.get("dir_names", [])
        return [{"dir_name": dir_name} for dir_name in dir_names]

    def _get_sub_agent_task_details(self, **task_item: Any) -> Dict[str, Any]:
        dir_name = task_item.get("dir_name")
        if not dir_name or not isinstance(dir_name, str):
            return {"task": "Error: A valid directory name is required for parallel analysis."}
        
        return {
            "task": f"Focus on analyzing the content of directory '{dir_name}' and look for exploitable information and clues.",
            "dir_name": dir_name
        }

    def _prepare_sub_agent_context(self, sub_agent_context: FlexibleContext, **task_details: Any) -> FlexibleContext:
        dir_name = task_details.get("dir_name")

        if not dir_name or not isinstance(dir_name, str):
            raise ValueError("Error: A valid directory path is required for analysis.")
        
        dir_name = dir_name.lstrip('/')

        firmware_root = self.context.get("base_path")
        if not firmware_root or not os.path.isdir(firmware_root):
            raise ValueError("Missing valid firmware root directory 'base_path' in context, cannot resolve path.")

        scope_dir = self.context.get("current_dir")
        if not scope_dir or not os.path.isdir(scope_dir):
            raise ValueError("Missing valid working directory 'current_dir' in context, cannot perform scope check.")

        resolved_path_from_current = os.path.normpath(os.path.join(scope_dir, dir_name))
        resolved_path_from_root = os.path.normpath(os.path.join(firmware_root, dir_name))
        
        if os.path.exists(resolved_path_from_current) and os.path.isdir(resolved_path_from_current):
            resolved_path = resolved_path_from_current
        elif os.path.exists(resolved_path_from_root) and os.path.isdir(resolved_path_from_root):
            resolved_path = resolved_path_from_root
        else:
            resolved_path = resolved_path_from_current

        real_firmware_root = os.path.realpath(firmware_root)
        real_scope_dir = os.path.realpath(scope_dir)
        try:
            real_resolved_path = os.path.realpath(resolved_path)
        except FileNotFoundError:
            raise ValueError(f"Directory '{dir_name}' not found in firmware.")

        if not os.path.commonpath([real_resolved_path, real_firmware_root]) == real_firmware_root:
            raise ValueError(f"The provided path '{dir_name}' is invalid, may contain '..' or point outside the firmware root directory.")

        if not os.path.commonpath([real_resolved_path, real_scope_dir]) == real_scope_dir:
            current_dir_name = os.path.relpath(scope_dir, firmware_root)
            basename_only = os.path.basename(dir_name)
            potential_correct_path = os.path.join(current_dir_name, basename_only)
            potential_full_path = os.path.join(firmware_root, potential_correct_path)
            
            if os.path.exists(potential_full_path) and os.path.isdir(potential_full_path):
                raise ValueError(
                    f"Path format error: You provided '{dir_name}', but you must use the COMPLETE path relative to firmware root. "
                    f"You are in directory '{current_dir_name}'. To analyze its subdirectory '{basename_only}', "
                    f"use the full path: '{potential_correct_path}' (not just '{basename_only}')."
                )
            else:
                raise ValueError(
                    f"Access denied: Directory '{dir_name}' is not within your current working directory '{current_dir_name}'. "
                    f"You are strictly restricted to analyzing subdirectories within '{current_dir_name}' only. "
                    f"Cross-directory and upward directory analysis is not allowed. If you need to analyze other directories, "
                    f"report this limitation and suggest that a different agent with appropriate scope should handle it."
                )

        if not os.path.isdir(resolved_path):
            raise ValueError(f"The specified path '{dir_name}' is not a valid directory.")

        sub_agent_context.set("current_dir", resolved_path)
        return sub_agent_context

    def _build_sub_agent_prompt(self, usr_init_msg: Optional[str], **task_details: Any) -> str:
        task = task_details.get("task", f"No directory analysis task provided #{task_details.get('task_index',-1)+1}.")

        usr_init_msg_content = usr_init_msg if usr_init_msg else "No user initial request provided"
        
        return (
            f"User initial request:\n{usr_init_msg_content}\n\n"
            f"Current task:\n{task}"
        )



class DescriptiveDirectoryAnalysisAssistant(BaseAssistant):
    name = "DescriptiveDirectoryAnalysisAssistant"
    description = """
    Agent for deep analysis of a specified subdirectory within your current directory scope with a custom task description.
    Can only analyze subdirectories in the current directory (direct children or deeper nested directories).
    Use simple relative paths for directories in your scope.
    Suitable for deep analysis tasks of a single subdirectory with specific instructions. You can decide the next analysis task after observing the result of a single step. For targeted analysis such as verification tasks, it is highly recommended to use this agent.
    """
    parameters = {
        "type": "object",
        "properties": {
            "dir_name": {
                "type": "string",
                "description": "The directory path relative to your current directory (e.g., 'hnap', 'init.d'). You can only access subdirectories within your current directory scope."
            },
            "task": {
                "type": "string",
                "description": "Specific task description on how to analyze the directory."
            },
            "run_in_background": {
                "type": "boolean",
                "description": "Whether to run this task in the background.",
                "default": False
            }
        },
        "required": ["dir_name", "task"],
        "description": "Object containing the directory analysis target and detailed task description. Use paths relative to your current working directory."
    }

    def __init__(
        self,
        context: FlexibleContext,
        agent_class_to_create: Type[BaseAgent] = BaseAgent,
        default_sub_agent_tool_classes: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = None,
        default_sub_agent_max_iterations: int = 10,
        sub_agent_system_prompt: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        final_name = name or DescriptiveDirectoryAnalysisAssistant.name
        final_description = description or DescriptiveDirectoryAnalysisAssistant.description

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

    def _get_sub_agent_task_details(self, **kwargs: Any) -> Dict[str, Any]:
        dir_name = kwargs.get("dir_name")
        task = kwargs.get("task")

        if not dir_name or not isinstance(dir_name, str):
            return {"task": "Error: A valid directory name is required for analysis."}
        
        if not task:
            task = f"Focus on analyzing the content of directory '{dir_name}' and look for exploitable information and clues."
        
        return {
            "task": task,
            "dir_name": dir_name
        }

    def _prepare_sub_agent_context(self, sub_agent_context: FlexibleContext, **task_details: Any) -> FlexibleContext:
        dir_name = task_details.get("dir_name")

        if not dir_name or not isinstance(dir_name, str):
            raise ValueError("Error: A valid directory path is required for analysis.")

        dir_name = dir_name.lstrip('/')

        firmware_root = self.context.get("base_path")
        if not firmware_root or not os.path.isdir(firmware_root):
            raise ValueError("Missing valid firmware root directory 'base_path' in context, cannot resolve path.")

        scope_dir = self.context.get("current_dir")
        if not scope_dir or not os.path.isdir(scope_dir):
            raise ValueError("Missing valid working directory 'current_dir' in context, cannot perform scope check.")

        resolved_path_from_current = os.path.normpath(os.path.join(scope_dir, dir_name))
        resolved_path_from_root = os.path.normpath(os.path.join(firmware_root, dir_name))
        
        if os.path.exists(resolved_path_from_current) and os.path.isdir(resolved_path_from_current):
            resolved_path = resolved_path_from_current
        elif os.path.exists(resolved_path_from_root) and os.path.isdir(resolved_path_from_root):
            resolved_path = resolved_path_from_root
        else:
            resolved_path = resolved_path_from_current

        real_firmware_root = os.path.realpath(firmware_root)
        real_scope_dir = os.path.realpath(scope_dir)
        try:
            real_resolved_path = os.path.realpath(resolved_path)
        except FileNotFoundError:
            raise ValueError(f"Directory '{dir_name}' not found in firmware.")

        if not os.path.commonpath([real_resolved_path, real_firmware_root]) == real_firmware_root:
            raise ValueError(f"The provided path '{dir_name}' is invalid, may contain '..' or point outside the firmware root directory.")

        if not os.path.commonpath([real_resolved_path, real_scope_dir]) == real_scope_dir:
            current_dir_name = os.path.relpath(scope_dir, firmware_root)
            basename_only = os.path.basename(dir_name)
            potential_correct_path = os.path.join(current_dir_name, basename_only)
            potential_full_path = os.path.join(firmware_root, potential_correct_path)
            
            if os.path.exists(potential_full_path) and os.path.isdir(potential_full_path):
                raise ValueError(
                    f"Path format error: You provided '{dir_name}', but you must use the COMPLETE path relative to firmware root. "
                    f"You are in directory '{current_dir_name}'. To analyze its subdirectory '{basename_only}', "
                    f"use the full path: '{potential_correct_path}' (not just '{basename_only}')."
                )
            else:
                raise ValueError(
                    f"Access denied: Directory '{dir_name}' is not within your current working directory '{current_dir_name}'. "
                    f"You are strictly restricted to analyzing subdirectories within '{current_dir_name}' only. "
                    f"Cross-directory and upward directory analysis is not allowed. If you need to analyze other directories, "
                    f"report this limitation and suggest that a different agent with appropriate scope should handle it."
                )

        if not os.path.isdir(resolved_path):
            raise ValueError(f"The specified path '{dir_name}' is not a valid directory.")

        sub_agent_context.set("current_dir", resolved_path)
        sub_agent_context.set("file_path", None)
        return sub_agent_context

    def _build_sub_agent_prompt(self, usr_init_msg: Optional[str], **task_details: Any) -> str:
        task = task_details.get("task", "No directory analysis task provided.")
        
        usr_init_msg_content = usr_init_msg if usr_init_msg else "No user initial request provided"
        
        return (
            f"User initial request:\n{usr_init_msg_content}\n\n"
            f"Current task:\n{task}"
        )
