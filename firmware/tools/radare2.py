"""
Radare2Tool - Radare2 session tool for analyzing the current binary file.
"""
import r2pipe
from typing import Dict, Any, Optional
from agent.basetool import ExecutableTool
from agent.context import FlexibleContext


class Radare2Tool(ExecutableTool):
    name: str = "r2"
    description: str = """
    Interacts with a Radare2 interactive session to analyze the current binary file. Note that this tool automatically establishes and maintains an r2 session for the current analysis focus file.

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
            "command": {
                "type": "string",
                "description": "Command to interact directly with Radare2"
            }
        },
        "required": ["command"]
    }
    timeout = 600

    def __init__(self, context: FlexibleContext):
        super().__init__(context)
        self.r2: Optional[r2pipe.Pipe] = None
        self._initialize_r2()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def _initialize_r2(self):
        if self.r2:
            return True

        file_path = self.context.get("file_path")
        if not file_path:
            print("Error: Cannot initialize Radare2 without file_path in context.")
            return False

        print(f"Initializing Radare2 session for: {file_path}...")
        try:
            self.r2 = r2pipe.open(file_path, flags=['-e', 'scr.interactive=false'])
            print("Running initial analysis (aaa) for r2 main tool session...")
            self.r2.cmd('aaa')
            print("Radare2 session initialized.")
            return True
        except Exception as e:
            print(f"Error initializing Radare2 session: {e}")
            self.r2 = None
            return False

    def execute(self, command: str) -> str:
        if not self.r2:
            print("Radare2 session not ready, attempting initialization...")
            if not self._initialize_r2():
                return "[Error] Radare2 session failed to initialize. Check file path and r2 installation."

        if not command:
            return "[Error] No command provided to Radare2."

        print(f"Executing r2 command: {command}")
        try:
            result = self.r2.cmd(command)
            return result.strip() if result else f"[No output from {command} command]"
        except Exception as e:
            print(f"Error executing Radare2 command '{command}': {e}. Resetting pipe.")
            return f"[Error] Failed to execute command '{command}': {e}. Radare2 pipe might be unstable."

    def close(self):
        if self.r2:
            print(f"Closing Radare2 pipe for {self.context.get('file_path', 'unknown file')}...")
            try:
                self.r2.quit()
            except Exception as e:
                print(f"Error during r2.quit() for {self.context.get('file_path', 'unknown file')}: {e}")
            finally:
                self.r2 = None
                print("Radare2 pipe closed and r2 instance reset.")
        else:
            pass
