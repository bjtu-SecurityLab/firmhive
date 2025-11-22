import os
import sys
import json
import time
import argparse
import threading

from typing import Dict, List, Any, Optional, Type, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.baseagent import BaseAgent
from agent.core.assistants import BaseAssistant, ParallelBaseAssistant
from agent.core.builder import build_agent, AgentConfig, AssistantToolConfig

from firmware.utils.finder import find_firmware_root
from firmware.utils.convert2md import load_knowledge_base
from firmware.tools import FlexibleContext, ExecutableTool, GetContextInfoTool, ShellExecutorTool, Radare2Tool, Radare2FileTargetTool
    #  VulnerabilitySearchTool

from firmware.knowagent import KnowledgeBaseAgent, QueryFindingsTool, ListUniqueValuesTool, StoreFindingsTool
from firmware.delegator import ParallelFunctionDelegator,ParallelDeepFileAnalysisDelegator,ParallelDeepDirectoryAnalysisDelegator,\
                            DeepFileAnalysisAssistant,DeepDirectoryAnalysisAssistant

# Import the three agent classes from their new locations
from firmware.executor_agent import ExecutorAgent, DEFAULT_TOOL_CLASSES
from firmware.planner_agent import PlannerAgent, FUNCTION_ANALYSIS_TOOLS
from firmware.prompt.executor_prompt import DEFAULT_WORKER_EXECUTOR_SYSTEM_PROMPT
from firmware.prompt.planner_prompt import DEFAULT_FILE_SYSTEM_PROMPT
from firmware.prompt.function_prompt import DEFAULT_FUNCTION_SYSTEM_PROMPT
from firmware.prompt.kb_prompt import DEFAULT_KB_SYSTEM_PROMPT
from firmware.prompt.response_format import SHARED_RESPONSE_FORMAT_BLOCK
from firmware.prompt.verification_prompt import DEFAULT_VERIFICATION_TASK_TEMPLATE, DEFAULT_VERIFICATION_INSTRUCTION_TEMPLATE


def _create_nested_call_chain_config(max_iterations: int, max_depth: int = 4) -> AgentConfig:
    """Helper function to create a nested configuration for ParallelFunctionDelegator.
       Each layer delegates to the next using ParallelFunctionDelegator.
       All layers use the same system prompt focused on call chain analysis.
    """
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1 for call chain config.")

    current_config = AgentConfig(
        agent_class=ExecutorAgent, 
        tool_configs=FUNCTION_ANALYSIS_TOOLS, 
        system_prompt=DEFAULT_FUNCTION_SYSTEM_PROMPT, 
        max_iterations=max_iterations
    )

    for _ in range(max_depth - 1):
        delegator_tool = AssistantToolConfig(
            assistant_class=ParallelFunctionDelegator, 
            sub_agent_config=current_config, 
        )
        wrapper_tools = [*FUNCTION_ANALYSIS_TOOLS, delegator_tool]
        current_config = AgentConfig(
            agent_class=ExecutorAgent, 
            tool_configs=wrapper_tools, 
            system_prompt=DEFAULT_FUNCTION_SYSTEM_PROMPT, 
            max_iterations=max_iterations
        )

    return current_config

def create_kb_agent_config(
    max_iterations: int = 50,
) -> AgentConfig:

    kb_agent_cfg = AgentConfig(
        agent_class=KnowledgeBaseAgent,
        tool_configs=[QueryFindingsTool, ListUniqueValuesTool, StoreFindingsTool],
        system_prompt=DEFAULT_KB_SYSTEM_PROMPT,
        max_iterations=max_iterations
    )
    return kb_agent_cfg

def create_file_analysis_config(
    include_kb: bool,
    max_iterations: int = 50,
    main_system_prompt: Optional[str] = None, 
    sub_level_system_prompt: Optional[str] = None,
) -> AgentConfig:
    """
    Blueprint for file analysis tasks (2 layers only: one delegation level).
    L0: Planner (top level, can delegate to L1)
    L1: Executor (terminal level, cannot delegate further - only has tools and function call chain analysis)
    
    This ensures file analysis delegation is strictly one level deep.
    """
    effective_main_prompt = main_system_prompt or DEFAULT_FILE_SYSTEM_PROMPT
    final_sub_level_prompt = sub_level_system_prompt or DEFAULT_FILE_SYSTEM_PROMPT
    
    # Create nested call chain config for function analysis
    nested_call_chain_sub_agent_config = _create_nested_call_chain_config(max_iterations, max_depth=4)
    call_chain_assistant_tool_cfg = AssistantToolConfig(
        assistant_class=ParallelFunctionDelegator, 
        sub_agent_config=nested_call_chain_sub_agent_config,
    )

    # L1: Terminal executor - only has tools and function analysis, NO further delegation
    l1_tool_configs: List[Union[Type[ExecutableTool], AssistantToolConfig]] = [
        *DEFAULT_TOOL_CLASSES.copy(),
        call_chain_assistant_tool_cfg,
        # VulnerabilitySearchTool(),  # for CVE search if needed
    ]

    if include_kb:
        kb_config = create_kb_agent_config(max_iterations=max_iterations)
        hierarchical_kb_manager_tool_cfg = AssistantToolConfig(
            assistant_class=BaseAssistant, 
            sub_agent_config=kb_config,
            description="Used to query all known information about this firmware's file system. Can query known findings for files and known findings for other files. You can prioritize querying known findings for files, then link to known findings for other files via the results. Note that no findings means there are currently no findings."
        )
        l1_tool_configs.append(hierarchical_kb_manager_tool_cfg)

    l1_agent_cfg = AgentConfig(
        agent_class=ExecutorAgent,
        tool_configs=l1_tool_configs,
        system_prompt=final_sub_level_prompt,
        max_iterations=max_iterations
    )
    
    # L0: Top-level planner - can delegate to L1 via BaseAssistant/ParallelBaseAssistant
    l0_tool_configs: List[Union[Type[ExecutableTool], AssistantToolConfig]] = [
        GetContextInfoTool,
        ShellExecutorTool,
        Radare2Tool,
        AssistantToolConfig(
            assistant_class=BaseAssistant,
            sub_agent_config=l1_agent_cfg,
            description="The assistant can interact with files to perform specific file analysis tasks. Use case: When you need analysis results for a single-step task before deciding the next analysis task."
        ),
        AssistantToolConfig(
            assistant_class=ParallelBaseAssistant,
            sub_agent_config=l1_agent_cfg,
            description="Each assistant can interact with files, executing multiple file analysis sub-tasks in parallel. Use cases: 1. When a complex task needs to be broken down into multiple independent sub-tasks. 2. Sub-tasks have no strict execution order dependencies. 3. Recommended for large-scale and complex tasks to execute multiple sub-tasks in parallel, improving analysis efficiency."
        )
    ]

    file_analyzer_config = AgentConfig(
        agent_class=PlannerAgent,
        tool_configs=l0_tool_configs,
        system_prompt=effective_main_prompt, 
        max_iterations=max_iterations
    )
    return file_analyzer_config


def create_firmware_analysis_blueprint(
    include_kb: bool = True,
    max_levels: int = 4,
    max_iterations_per_agent: int = 50,
) -> AgentConfig:
    """
    Creates a multi-layered, planner-executor nested firmware analysis agent configuration.
    Each planning level (Lx_Planner) guides an Lx_Executor.
    The Lx_Executor explores its assigned directory and uses assistants to:
    - Delegate file analysis (Deep File Analysis Assistant -> Generic File Analyzer Config)
    - Delegate subdirectory analysis (Recursive Directory Analysis Assistant -> Deeper Level Planner Config)
    The deepest level planner's executor will delegate subdirectories to a terminal executor.
    """
    if max_levels < 1:
        raise ValueError("max_levels must be at least 1.")

    file_analyzer_config = create_file_analysis_config(
        include_kb=include_kb,
        max_iterations=max_iterations_per_agent,
    )
    kb_query_tool_cfg = create_kb_agent_config(
        max_iterations=max_iterations_per_agent, 
    )
    
    terminal_worker_config = AgentConfig(
        agent_class=ExecutorAgent,
        tool_configs=[
            GetContextInfoTool,
            ShellExecutorTool,
            AssistantToolConfig(
                assistant_class=DeepFileAnalysisAssistant,
                sub_agent_config=file_analyzer_config,
            ),
            AssistantToolConfig(
                assistant_class=ParallelDeepFileAnalysisDelegator,
                sub_agent_config=file_analyzer_config,
            )
        ],
        system_prompt=DEFAULT_WORKER_EXECUTOR_SYSTEM_PROMPT,
        max_iterations=max_iterations_per_agent
    )

    for _ in range(max_levels - 1, -1, -1):
        worker_tools = [
            GetContextInfoTool,
            ShellExecutorTool,
            Radare2FileTargetTool,
            AssistantToolConfig(
                assistant_class=DeepFileAnalysisAssistant,
                sub_agent_config=file_analyzer_config,
            ),
            AssistantToolConfig(
                assistant_class=DeepDirectoryAnalysisAssistant,
                sub_agent_config=terminal_worker_config,
            ),
            AssistantToolConfig(
                assistant_class=ParallelDeepFileAnalysisDelegator,
                sub_agent_config=file_analyzer_config,
            ),
            AssistantToolConfig(
                assistant_class=ParallelDeepDirectoryAnalysisDelegator,
                sub_agent_config=terminal_worker_config, 
            )
        ]
        if include_kb:
            worker_tools.append(AssistantToolConfig(
                assistant_class=BaseAssistant,
                sub_agent_config=kb_query_tool_cfg,
            ))
        
        current_worker_system_prompt = DEFAULT_WORKER_EXECUTOR_SYSTEM_PROMPT

        current_worker_config = AgentConfig(
            agent_class=ExecutorAgent,
            tool_configs=worker_tools,
            system_prompt=current_worker_system_prompt,
            max_iterations=max_iterations_per_agent
        )

        terminal_worker_config = current_worker_config

    return terminal_worker_config
