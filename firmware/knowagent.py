from typing import Dict, List, Any, Optional, Type, Union

from agent.baseagent import BaseAgent
from agent.historystrategy import HistoryStrategy
from agent.basetool import ExecutableTool
from agent.context import FlexibleContext

# Import knowledge base tools
from firmware.tools.kb_store import StoreFindingsTool
from firmware.tools.kb_query import QueryFindingsTool
from firmware.tools.kb_list import ListUniqueValuesTool

# Import knowledge base prompt
from firmware.prompt.kb_prompt import DEFAULT_KB_SYSTEM_PROMPT

DEFAULT_KB_TOOLS = [StoreFindingsTool, QueryFindingsTool, ListUniqueValuesTool]

class KnowledgeBaseAgent(BaseAgent):
    def __init__(
        self,
        context: FlexibleContext,
        max_iterations: int = 25,
        history_strategy: Optional[HistoryStrategy] = None,
        tools: Optional[List[Union[Type[ExecutableTool], ExecutableTool]]] = DEFAULT_KB_TOOLS,
        system_prompt: Optional[str] = DEFAULT_KB_SYSTEM_PROMPT,
        output_schema: Optional[Dict[str, Any]] = None,
        **extra_params: Any
    ):
        tools_to_pass = tools

        final_system_prompt = system_prompt

        self.messages_filters = [{'from': context.get('base_path'), 'to': ''}, {'from': 'user_name', 'to': 'user'}]

        super().__init__(
            tools=tools_to_pass,
            context=context,
            system_prompt=final_system_prompt,
            output_schema=output_schema,
            max_iterations=max_iterations,
            history_strategy=history_strategy,
            **extra_params
        )
