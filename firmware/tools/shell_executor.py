"""
ShellExecutorTool - Safe, read-only shell command executor with directory scope restrictions.
"""
import os
import shlex
import subprocess
from typing import Dict, Any, Optional
from agent.basetool import ExecutableTool
from agent.context import FlexibleContext


class ShellExecutorTool(ExecutableTool):
    name = "execute_shell"
    ALLOWED_COMMANDS = ['file', 'find', 'strings', 'grep', 'head', 'tail', 'readelf', 'cat', 'sort', 'ls']
    DANGEROUS_PATTERNS = ['>', '>>', 'cd', 'pushd', 'popd', ';', '&&', '||', '`', '$(']
    timeout = 180

    def __init__(self, context: Optional[FlexibleContext] = None):
        super().__init__(context)
        file_path = self.context.get("file_path", "Not specified")
        file_name = os.path.basename(file_path) if file_path else "Not specified"
        current_dir = self.context.get("current_dir", "Not specified")

        self.description = f"""Execute read-only shell commands in the current directory ({os.path.basename(current_dir)}). 
    **Warning:** This tool is strictly confined to the current working directory. All file operations must not reference parent or any other directories. It is recommended to use the `file` tool for exploration and identification within the current directory.
    **Note:** All commands are executed in the current directory. All path arguments should be relative to the current directory. Paths containing '/' or '..' are forbidden.
    Supported commands: {', '.join(self.ALLOWED_COMMANDS)}.
    Output redirection ('>', '>>'), command chaining, and directory changes are prohibited."""

        self.parameters = {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": f"The shell command to execute. The command will be executed in the '{os.path.basename(current_dir)}' directory. All paths in the command should be relative to this directory."
                }
            },
            "required": ["command"]
        }


    def execute(self, command: str) -> str:
        return self.execute_shell(command=command)
    
    def _resolve_path(self, path: str, working_dir: str) -> Optional[str]:
        if os.path.isabs(path):
            return None

        real_working_dir = os.path.realpath(working_dir)
        
        prospective_path = os.path.join(real_working_dir, path)
        real_prospective_path = os.path.realpath(prospective_path)

        if real_prospective_path.startswith(real_working_dir + os.sep) or real_prospective_path == real_working_dir:
            return real_prospective_path
        
        return None


    def _is_safe_command(self, command: str) -> tuple[bool, str]:
        if not command or not command.strip():
            return False, "Command cannot be empty."
        
        base_path = self.context.get("base_path")
        current_dir = self.context.get("current_dir")

        if not base_path or not os.path.isdir(os.path.normpath(base_path)):
            return False, "[Security Error] No valid firmware root directory (base_path) provided in the context."
        if not current_dir or not os.path.isdir(os.path.normpath(current_dir)):
            return False, "[Security Error] No valid working directory (current_dir) provided in the context."
        
        norm_current_dir = os.path.normpath(current_dir)
        norm_base_path = os.path.normpath(base_path)
        if not norm_current_dir.startswith(norm_base_path):
            return False, f"[Security Error] The current working directory '{current_dir}' is not within the firmware root directory '{base_path}'."

        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in command:
                return False, f"[Security Error] Command contains a forbidden pattern: '{pattern}'"

        try:
            tokens = shlex.split(command)
        except ValueError as e:
            return False, f"Failed to parse command: {e}."
        
        if not tokens:
            return False, "Invalid command."
        
        base_cmd = tokens[0]
        
        if base_cmd not in self.ALLOWED_COMMANDS:
            return False, f"[Security Error] Command '{base_cmd}' is not in the list of allowed commands ({', '.join(sorted(self.ALLOWED_COMMANDS))})."
        
        path_like_cmds = {'file', 'cat', 'head', 'tail', 'readelf', 'strings', 'ls'}

        if base_cmd in path_like_cmds:
            for token in tokens[1:]:
                if not token.startswith('-'):
                    if self._resolve_path(token, current_dir) is None:
                        return False, f"[Security Error] Argument '{token}' resolves to a path outside the current working directory or contains illegal characters."
        elif base_cmd == 'find':
            path_arg_found = False
            for token in tokens[1:]:
                if not token.startswith('-'):
                    if not path_arg_found:
                        if self._resolve_path(token, current_dir) is None:
                            return False, f"[Security Error] The search path '{token}' for the find command resolves to a path outside the current working directory."
                        path_arg_found = True
        elif base_cmd == 'grep':
            if len(tokens) > 2 and not tokens[-1].startswith('-'):
                path_token = tokens[-1]
                if self._resolve_path(path_token, current_dir) is None:
                    return False, f"[Security Error] The file path '{path_token}' for the grep command resolves to a path outside the current working directory."
        
        return True, ""

    def execute_shell(self, command: str) -> str:
        try:
            is_safe, error_msg = self._is_safe_command(command)
            if not is_safe:
                return f"[Security Error] {error_msg}"
            
            working_dir = os.path.normpath(str(self.context.get("current_dir"))) 
            
            cmd_args = shlex.split(command)

            result = subprocess.run(
                cmd_args,
                shell=False,
                cwd=working_dir, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                check=False, 
                encoding='utf-8', 
                errors='ignore'
            )
            
            output = f"Exit Code: {result.returncode}\n"
            if result.stdout:
                output += f"Stdout:\n{result.stdout}\n"
            if result.stderr:
                output += f"Stderr:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired: 
            return f"[Error] Command '{command[:100]}...' timed out after {self.timeout}s."
        except Exception as e: 
            return f"[Error] Command '{command[:100]}...' failed to execute: {e}"
