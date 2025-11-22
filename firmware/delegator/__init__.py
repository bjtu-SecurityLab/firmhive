"""
Firmware analysis delegators package.
"""
from firmware.delegator.function_delegator import ParallelFunctionDelegator
from firmware.delegator.file_delegator import (
    DeepFileAnalysisAssistant,
    ParallelDeepFileAnalysisDelegator,
    DescriptiveFileAnalysisAssistant
)
from firmware.delegator.directory_delegator import (
    DeepDirectoryAnalysisAssistant,
    ParallelDeepDirectoryAnalysisDelegator,
    DescriptiveDirectoryAnalysisAssistant
)

__all__ = [
    # Function delegator
    'ParallelFunctionDelegator',
    # File delegators
    'DeepFileAnalysisAssistant',
    'ParallelDeepFileAnalysisDelegator',
    'DescriptiveFileAnalysisAssistant',
    # Directory delegators
    'DeepDirectoryAnalysisAssistant',
    'ParallelDeepDirectoryAnalysisDelegator',
    'DescriptiveDirectoryAnalysisAssistant',
]
