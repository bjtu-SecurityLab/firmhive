"""
Knowledge base unique values listing tool for firmware analysis.
"""
import json
from typing import Dict, List, Any

from agent.basetool import ExecutableTool
from agent.context import FlexibleContext
from firmware.kb_schema import KnowledgeBaseMixin


class ListUniqueValuesTool(ExecutableTool, KnowledgeBaseMixin):
    name: str = "ListUniqueValuesInKB"
    description: str = """Lists all unique values for a specified field in the knowledge base.

This is useful for exploring what data exists, which helps you formulate more precise queries.
For example:
  - If target_key='file_path', returns all unique file paths that have stored findings
  - If target_key='severity', returns all unique severity levels
  - If target_key='link_identifiers', returns all unique identifiers (e.g. function/symbol names) ever mentioned
This is commonly used before using QueryKnowledgeBase to know what query_value you can search for.
"""
    parameters: Dict = {
        "type": "object",
        "properties": {
            "target_key": {
                "type": "string",
                "description": "The field name whose unique values you want to see. For example, 'file_path', 'severity', 'link_identifiers', etc."
            }
        },
        "required": ["target_key"]
    }

    def __init__(self, context: FlexibleContext):
        ExecutableTool.__init__(self, context)
        KnowledgeBaseMixin._initialize_kb(self, context)

    def execute(self, target_key: str) -> Dict[str, Any]:
        all_data = self._load_kb_data()

        unique_values = set()
        for record in all_data:
            val = record.get(target_key)
            if val is None:
                continue
            if isinstance(val, list):
                for item in val:
                    unique_values.add(str(item))
            else:
                unique_values.add(str(val))

        unique_list = sorted(unique_values)
        count = len(unique_list)
        print(f"ListUniqueValuesInKB: Found {count} unique values for key '{target_key}'")
        return {
            "status": "success",
            "message": f"Found {count} unique values for '{target_key}'",
            "values": unique_list
        }
