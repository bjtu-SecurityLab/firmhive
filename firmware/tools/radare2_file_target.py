"""
Radare2FileTargetTool - Radare2 session tool for analyzing a specified target binary file.
"""
import os
import r2pipe
from typing import Dict, Any, Optional
from agent.basetool import ExecutableTool
from agent.context import FlexibleContext


class Radare2FileTargetTool(ExecutableTool):
    name: str = "r2_file_target"
    description: str = """
    Interacts with a Radare2 interactive session to analyze a specified binary file. Note that this tool automatically establishes and maintains an r2 session for the target analysis object.

    Main features:
    - Send Radare2 commands and get the output
    - Session state is maintained between calls (for the same file)
    - Supports decompilation using the r2ghidra plugin:
    * Use the `pdg` command to decompile functions
    * Provides C-like pseudocode output

    """
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "The name of the file to be analyzed. Provide the path relative to the firmware root directory, do not start with ./."
            },
            "command": {
                "type": "string",
                "description": "Command to interact directly with Radare2"
            }
        },
        "required": ["file_name", "command"]
    }
    timeout = 600

    def __init__(self, context: FlexibleContext):
        super().__init__(context)
        self.r2: Optional[r2pipe.Pipe] = None
        self.current_analyzed_file: Optional[str] = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def _initialize_r2_for_file(self, file_path: str) -> bool:
        if self.r2 and self.current_analyzed_file == file_path:
            return True

        if self.r2:
            print(f"Closing Radare2 session for previous file: {self.current_analyzed_file}")
            self.close()

        if not file_path:
            print("Error: Cannot initialize Radare2 without a valid file_path.")
            return False
        
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}. Cannot initialize Radare2.")
            return False


        print(f"Initializing Radare2 session for: {file_path}...")
        try:
            self.r2 = r2pipe.open(file_path, flags=['-e', 'scr.interactive=false'])
            if not self.r2:
                print(f"Error: r2pipe.open failed for {file_path}. The file might not exist or r2 is not installed correctly.")
                self.current_analyzed_file = None
                return False
            print("Running initial analysis (aaa) for r2 file target tool...")
            self.r2.cmd('aaa')
            self.current_analyzed_file = file_path
            print(f"Radare2 session initialized successfully for: {file_path}")
            return True
        except Exception as e:
            print(f"Error initializing Radare2 session for {file_path}: {e}")
            self.r2 = None
            self.current_analyzed_file = None
            return False

    def execute(self, file_name: str, command: str) -> str:
        current_dir = self.context.get("current_dir")
        if not current_dir:
            return "[Error] current_dir not found in context. Cannot determine file path."

        if not file_name:
            return "[Error] No file_name provided."
        
        target_file_path = os.path.join(current_dir, file_name)

        if not self._initialize_r2_for_file(target_file_path):
            return f"[Error] Radare2 session failed to initialize for {target_file_path}. Ensure the file exists and Radare2 is correctly configured."

        if not self.r2:
            return f"[Error] Radare2 session is not available for {target_file_path} even after initialization attempt."

        if not command:
            return "[Error] No command provided to Radare2."

        print(f"Executing r2 command: '{command}' on file '{target_file_path}'")
        try:
            result = self.r2.cmd(command)
            return result.strip() if result is not None else f"[No output from '{command}' command]"
        except Exception as e:
            print(f"Error executing Radare2 command '{command}' on '{target_file_path}': {e}. Resetting pipe for this file.")
            self.close()
            return f"[Error] Failed to execute command '{command}' on '{target_file_path}': {e}. Pipe has been reset."

    def close(self):
        if self.r2:
            print(f"Closing Radare2 pipe for {self.current_analyzed_file}...")
            try:
                self.r2.quit()
            except Exception as e:
                print(f"Error during r2.quit() for {self.current_analyzed_file}: {e}")
            finally:
                self.r2 = None
                self.current_analyzed_file = None
                print("Radare2 pipe closed and state cleared.")
        else:
            pass
