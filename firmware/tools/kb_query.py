"""
Knowledge base query tool for firmware analysis findings.
"""
import json
from typing import Dict, List, Any

from agent.basetool import ExecutableTool
from agent.context import FlexibleContext
from firmware.kb_schema import KnowledgeBaseMixin


class QueryFindingsTool(ExecutableTool, KnowledgeBaseMixin):
    name: str = "QueryKnowledgeBase"
    description: str = "Queries the knowledge base to retrieve previously stored findings. Supports exact-match searching by file path, link identifiers, or notes."
    parameters: Dict = {
        "type": "object",
        "properties": {
            "query_key": {
                "type": "string",
                "enum": ["file_path", "link_identifiers", "notes"],
                "description": "The field to search on. 'link_identifiers' checks if any identifier in a finding's list matches; 'notes' does a substring check."
            },
            "query_value": {
                "description": "The value to match. For 'link_identifiers', it will check membership in the list. For 'notes', it checks substring."
            }
        },
        "required": ["query_key", "query_value"]
    }

    def __init__(self, context: FlexibleContext):
        ExecutableTool.__init__(self, context)
        KnowledgeBaseMixin._initialize_kb(self, context)

    @staticmethod
    def _check_match(record_value: Any, query_value: Any, query_key: str) -> bool:
        """
        Check if record_value matches query_value for the given query_key.
        """
        if query_key == "link_identifiers":
            if isinstance(record_value, list):
                return query_value in record_value
            return False
        elif query_key == "notes":
            if isinstance(record_value, str):
                return str(query_value).lower() in record_value.lower()
            return False
        else:
            return record_value == query_value

    def execute(self, query_key: str, query_value: Any) -> List[Dict[str, Any]]:
        all_data = self._load_kb_data()

        results = []
        for record in all_data:
            record_value = record.get(query_key)
            if record_value is not None:
                if self._check_match(record_value, query_value, query_key):
                    results.append(record)

        if results:
            print(f"QueryKnowledgeBase found {len(results)} records matching {query_key}={query_value}")
        else:
            print(f"QueryKnowledgeBase: No records found for {query_key}={query_value}")

        return results
