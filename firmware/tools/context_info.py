"""
GetContextInfoTool - Get current analysis context information.
"""
import os
from typing import Dict, Any
from agent.basetool import ExecutableTool


class GetContextInfoTool(ExecutableTool):
    name = "get_context_info"
    description = "Get context information for the current analysis task, such as the file or directory being analyzed."
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self) -> str:
        file_path = self.context.get("file_path")
        current_dir = self.context.get("current_dir")
        base_path = self.context.get("base_path")
        file_name_str = os.path.basename(file_path) if file_path else "Not specified"
        dir_name_str = os.path.basename(current_dir) if current_dir else "Not specified"
        rel_dir_path = os.path.relpath(current_dir, base_path) if current_dir and base_path else "Not specified"
        
        return (
            f"Current analysis focus:\n"
            f"- File: {file_name_str}\n"
            f"- Directory: {dir_name_str}\n"
            f"- Directory path relative to firmware root: {rel_dir_path}"
        )
