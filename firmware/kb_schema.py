"""
Knowledge base data structures and schemas for firmware analysis.
"""
import json
import os
import fcntl
from typing import Dict, List, Any

from agent.context import FlexibleContext

DEFAULT_KB_FILE = "knowledge_base.jsonl"

FINDING_SCHEMA: Dict[str, Dict[str, Any]] = {
    "name": {
        "type": "string", 
        "description": "A unique identifier for the finding. Suggested format: '<type>-<function/module>'."
    },
    "location": {
        "type": "string",
        "description": "Precise location (file:line_number function_name address)."
    },
    "description": {
        "type": "string",
        "description": "Detailed description of the finding or observation."
    },
    "link_identifiers": {
        "type": "array",
        "items": {"type": "string"},
        "description": "A list of specific identifiers related to this finding (e.g., NVRAM variable, function name, file path). Avoid generic terms; ensure accurate tracking across files and inter-process data flows/interactions."
    },
    "code_snippet": {
        "type": "string",
        "description": "A code snippet directly related to the finding. Should include enough context to understand the issue, typically 3-10 lines."
    },
    "risk_score": {
        "type": "number",
        "description": "Risk score (0.0-10.0)."
    },
    "confidence": {
        "type": "number",
        "description": "Confidence in the correctness and exploitability of the finding (0.0-10.0)."
    },
    "notes": {
        "type": "string",
        "description": "Other notes for human analysts, including assumptions made, files or variable sources needing further verification, remaining issues, or suggestions for next analysis steps."
    }
}


FINDING_SCHEMA_REQUIRED_FIELDS: List[str] = ["location", "description"]


class KnowledgeBaseMixin:
    """
    Mixin class providing knowledge base initialization and data loading functionality.
    Used by knowledge base tools to manage finding storage and retrieval.
    """
    def _initialize_kb(self, context: FlexibleContext):
        output_from_context = context.get("output")

        if output_from_context and isinstance(output_from_context, str):
            self.output = output_from_context
        else:
            raise ValueError("'output' not found in context or invalid.")

        if not os.path.exists(self.output):
            try:
                os.makedirs(self.output, exist_ok=True)
                print(f"Created output directory: {os.path.abspath(self.output)}")
            except OSError as e:
                print(f"Warning: Could not create output directory '{self.output}': {e}. Attempting to create the knowledge base file in the current directory.")
                self.output = "."

        self.kb_file_path = os.path.join(self.output, DEFAULT_KB_FILE)

        kb_specific_dir = os.path.dirname(self.kb_file_path)
        if kb_specific_dir and not os.path.exists(kb_specific_dir):
            try:
                os.makedirs(kb_specific_dir, exist_ok=True)
            except OSError as e:
                 print(f"Warning: Could not create specific directory for KB file '{kb_specific_dir}': {e}")

        print(f"Knowledge base file path set to: {os.path.abspath(self.kb_file_path)}")

    def _load_kb_data(self, lock_file) -> List[Dict[str, Any]]:
        findings = []
        try:
            fcntl.flock(lock_file, fcntl.LOCK_SH)
            lock_file.seek(0)
            for line_bytes in lock_file:
                if not line_bytes.strip():
                    continue
                try:
                    findings.append(json.loads(line_bytes.decode('utf-8-sig')))
                except json.JSONDecodeError as e:
                    print(f"Warning: Error parsing a line in the knowledge base, skipped. Error: {e}. Line: {line_bytes[:100]}...")
            return findings
        except Exception as e:
            print(f"Error loading KB '{self.kb_file_path}': {e}. Returning an empty list.")
            return []
        finally:
            try:
                fcntl.flock(lock_file, fcntl.LOCK_UN)
            except (ValueError, OSError):
                pass
