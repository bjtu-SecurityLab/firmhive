import inspect
from dataclasses import dataclass, field
from typing import Optional, List, Type, Union

from agent.baseagent import BaseAgent 
from agent.context import FlexibleContext
from agent.basetool import ExecutableTool

@dataclass
class AgentConfig:
    """Configuration for an Agent instance."""
    agent_class: Type[BaseAgent] = BaseAgent
    tool_configs: List[Union[Type[ExecutableTool], 'AssistantToolConfig']] = field(default_factory=list)
    system_prompt: Optional[str] = None
    max_iterations: int = 20
    agent_instance_name: Optional[str] = None

@dataclass
class AssistantToolConfig:
    """Configuration for an assistant tool instance and its sub-agent."""
    assistant_class: Type[ExecutableTool] 
    sub_agent_config: AgentConfig       
    name: Optional[str] = None
    description: Optional[str] = None
    timeout: Optional[int] = None

def build_assistant(assistant_config: AssistantToolConfig, context: FlexibleContext) -> ExecutableTool:
    """
    Only creates the Assistant itself, does not recursively instantiate its sub-tools.
    Passes sub-tool configuration as-is for deferred instantiation.
    """
    from agent.core.assistants import BaseAssistant, ParallelBaseAssistant

    sub_agent_tool_configs = assistant_config.sub_agent_config.tool_configs if assistant_config.sub_agent_config else []

    if issubclass(assistant_config.assistant_class, (BaseAssistant, ParallelBaseAssistant)):
        agent_to_create = assistant_config.sub_agent_config.agent_class if assistant_config.sub_agent_config and assistant_config.sub_agent_config.agent_class else BaseAgent
        return assistant_config.assistant_class(
            context=context,
            name=assistant_config.name,
            agent_class_to_create=agent_to_create,
            default_sub_agent_tool_classes=sub_agent_tool_configs,
            default_sub_agent_max_iterations=assistant_config.sub_agent_config.max_iterations if assistant_config.sub_agent_config else 10,
            sub_agent_system_prompt=assistant_config.sub_agent_config.system_prompt if assistant_config.sub_agent_config else None,
            description=assistant_config.description,
            timeout=assistant_config.timeout
        )
    else:
        print(f"Warning: Assistant class {assistant_config.assistant_class.__name__} is not a subclass of BaseAssistant or ParallelBaseAssistant. Attempting generic instantiation.")
        try:
            kwargs = {'context': context, 'name': assistant_config.name}
            if assistant_config.description is not None:
                kwargs['description'] = assistant_config.description
            return assistant_config.assistant_class(**kwargs)
        except TypeError as e:
             raise TypeError(f"Failed to instantiate {assistant_config.assistant_class.__name__} with generic parameters (context, name, description?). Specific handling needed or check class definition. Error: {e}")

def build_agent(agent_config: AgentConfig, context: FlexibleContext) -> BaseAgent:
    """
    Instantiates a new, independent set of tool instances for the Agent as needed.
    This function ensures isolation: each call performs a complete instantiation process.
    """
    agent_tools = []
    if agent_config.tool_configs:
        for tool_conf_or_class in agent_config.tool_configs:
            if isinstance(tool_conf_or_class, AssistantToolConfig):
                assistant_instance = build_assistant(tool_conf_or_class, context)
                agent_tools.append(assistant_instance)
            elif inspect.isclass(tool_conf_or_class) and issubclass(tool_conf_or_class, ExecutableTool):
                tool_instance = tool_conf_or_class(context=context)
                agent_tools.append(tool_instance)
            else:
                print(f"Warning: tool_conf_or_class in build_agent is neither AssistantToolConfig nor a valid Tool class: {tool_conf_or_class}")
                if isinstance(tool_conf_or_class, ExecutableTool):
                    agent_tools.append(tool_conf_or_class)

    return agent_config.agent_class(
        context=context,
        tools=agent_tools,
        system_prompt=agent_config.system_prompt,
        max_iterations=agent_config.max_iterations,
        agent_instance_name=agent_config.agent_instance_name
    ) 
