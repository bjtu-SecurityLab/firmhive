"""
Knowledge base storage tool for firmware analysis findings.
"""
import json
import os
import fcntl
from typing import Dict, List, Any

from agent.basetool import ExecutableTool
from agent.context import FlexibleContext
from firmware.kb_schema import (
    FINDING_SCHEMA,
    FINDING_SCHEMA_REQUIRED_FIELDS,
    KnowledgeBaseMixin
)


class StoreFindingsTool(ExecutableTool, KnowledgeBaseMixin):
    name: str = "StoreStructuredFindings"
    description: str = "Stores structured firmware analysis findings into the knowledge base in append mode. Each finding must include detailed path and condition constraints to ensure traceability and verifiability."
    parameters: Dict = {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": FINDING_SCHEMA,
                    "required": FINDING_SCHEMA_REQUIRED_FIELDS
                },
                "description": "A list of findings to be stored. Each object in the list should follow the defined schema. Contextual information (like 'file_path') will be added automatically by the tool."
            }
        },
        "required": ["findings"]
    }

    def __init__(self, context: FlexibleContext):
        ExecutableTool.__init__(self, context)
        KnowledgeBaseMixin._initialize_kb(self, context)

    def execute(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        context_file_path = self.context.get("file_path")
        context_dir = self.context.get("current_dir")
        context_base_path = self.context.get("base_path")
        context_stage = self.context.get("stage")

        context_dir_path = None
        if context_dir and context_base_path:
            try:
                context_dir_path = os.path.relpath(context_dir, context_base_path)
            except ValueError:
                context_dir_path = context_dir

        if not findings:
            return {"status": "info", "message": "Info: No findings provided for storage."}

        enriched_findings = []
        for finding_dict in findings:
            if isinstance(finding_dict, dict):
                finding_copy = finding_dict.copy()

                if context_file_path:
                    finding_copy['file_path'] = os.path.relpath(context_file_path, context_base_path)
                elif context_dir_path:
                    finding_copy['dir_path'] = os.path.relpath(context_dir, context_base_path)
                if context_stage:
                    finding_copy['stage'] = context_stage

                enriched_findings.append(finding_copy)
            else:
                print(f"Warning: Non-dictionary item found in findings list and was ignored: {finding_dict}")

        if not enriched_findings:
            return {"status": "info", "message": "Info: No valid findings were processed for storage."}

        try:
            with open(self.kb_file_path, 'ab') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    for finding in enriched_findings:
                        try:
                            json_string = json.dumps(finding, ensure_ascii=False)
                            f.write(json_string.encode('utf-8'))
                            f.write(b'\n')
                        except TypeError as te:
                            print(f"CRITICAL: Could not serialize finding, skipped. Error: {te}. Content: {str(finding)[:200]}...")
                            continue
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)

            num_stored = len(enriched_findings)
            message = f"Successfully appended {num_stored} findings to the knowledge base."
            print(f"{message}")
            return {"status": "success", "message": message, "stored_count": num_stored}

        except Exception as e:
            error_message = f"Error storing findings: {str(e)}"
            print(f"{error_message} (Details: {e})")
            return {"status": "error", "message": error_message}
