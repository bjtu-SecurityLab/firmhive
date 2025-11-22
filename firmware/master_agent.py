"""
FirmwareMasterAgent - Main orchestrator for firmware analysis and verification.
"""
import os
import json
import time
import threading
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.core.builder import build_agent, AgentConfig
from firmware.tools import FlexibleContext
from firmware.utils.convert2md import load_knowledge_base
from firmware.prompt.verification_prompt import DEFAULT_VERIFICATION_TASK_TEMPLATE, DEFAULT_VERIFICATION_INSTRUCTION_TEMPLATE
from firmware.toa import create_firmware_analysis_blueprint


class FirmwareMasterAgent: 
    def __init__(
        self,
        firmware_root_path: str,
        output_dir: str,
        user_input: str,
        max_levels_for_blueprint: int = 4,
        max_iterations_per_agent: int = 50,
        agent_instance_name: Optional[str] = "FirmwareMasterAgent",
    ):
        if not os.path.isdir(firmware_root_path):
            raise ValueError(f"Firmware root path '{firmware_root_path}' does not exist or is not a directory.")
        
        self.firmware_root_path = os.path.abspath(firmware_root_path)
        self.output_dir = os.path.abspath(output_dir)
        self.user_input = user_input
        self.max_levels = max_levels_for_blueprint
        self.max_iterations = max_iterations_per_agent
        self.agent_instance_name = agent_instance_name
        self.analysis_duration = 0.0
        self.verification_duration = 0.0
        self._verification_lock = threading.Lock()

        self.context = FlexibleContext(
            base_path=self.firmware_root_path,
            current_dir=self.firmware_root_path,
            output=self.output_dir,
            agent_log_dir=os.path.join(self.output_dir, f"{agent_instance_name}_logs"),
            user_input=self.user_input
        )

        master_agent_config = create_firmware_analysis_blueprint(
            max_levels=max_levels_for_blueprint,
            max_iterations_per_agent=max_iterations_per_agent,
        )
        
        self.master_agent = build_agent(master_agent_config, context=self.context)

    def run(self) -> str:
        initial_task = (
            f"Please analyze the firmware comprehensively, combining it with the user's core requirements. Currently located in firmware directory: {os.path.basename(self.firmware_root_path)}, user's core requirement is: {self.user_input} "
            f"Please start from this directory and analyze files and subdirectories layer by layer."
        )
        start_time = time.time()
        analysis_summary = self.master_agent.run(user_input=initial_task)
        end_time = time.time()
        self.analysis_duration = end_time - start_time
        print(f"Initial analysis completed, took {self.analysis_duration:.2f} seconds")
        
        self.summary()
        return analysis_summary

    def _get_findings_to_process(self, finding_to_verify: Optional[Union[Dict[str, Any], str]] = None) -> List[Dict[str, Any]]:
        """Loads all findings from the knowledge base, or processes a single specified finding."""
        if finding_to_verify:
            print("\n--- Starting verification of specified finding ---")
            if isinstance(finding_to_verify, str):
                return [{"description": finding_to_verify}] 
            elif isinstance(finding_to_verify, dict):
                return [finding_to_verify]
            return []
        
        print("\n--- Starting verification of all findings from knowledge base ---")
        kb_file_path = os.path.join(self.output_dir, "knowledge_base.jsonl")
        if not os.path.exists(kb_file_path):
            print(f"Knowledge base file '{kb_file_path}' does not exist, skipping verification.")
            return []
        
        all_findings = load_knowledge_base(kb_file_path)
        if not all_findings:
            print("Knowledge base is empty, no verification needed.")
            return []

        print(f"Loaded {len(all_findings)} findings from knowledge base for verification.")
        return all_findings

    def _verify_one_finding(self, finding: Dict[str, Any], verification_analyzer_config: AgentConfig):
        """
        Core logic for verifying a single finding.
        """
        finding_name_for_log = finding.get('name') or finding.get('description', 'untitled_finding')[:50].replace('/', '_')
        print(f"\n>> Starting verification: {finding_name_for_log}")
        
        finding_details = {k: v for k, v in finding.items() if k in ['location','description', 'file_path', 'code_snippet', 'risk_score']}
        verification_finding_details = (
            f"Verify the following finding:\n"
            f"```json\n"
            f"{json.dumps(finding_details, indent=2, ensure_ascii=False)}\n"
            f"```\n"
            f"**Requirements**:\n"
            f"1.  **Focused Verification**: All your operations must revolve around verifying this finding.\n"
            f"2.  **Evidence Support**: Your conclusions must be based on actual evidence returned by tools.\n"
            f"3.  **No Unrelated Analysis**: Do not explore any other potential issues outside of this finding.\n"
        )

        verification_task = DEFAULT_VERIFICATION_TASK_TEMPLATE.format(verification_finding_details=verification_finding_details)
        verification_prompt = DEFAULT_VERIFICATION_INSTRUCTION_TEMPLATE.format(verification_task=verification_task)
        
        task_context = self.context.copy()
        task_context.set("stage", f"verify_{finding_name_for_log}")
        task_context.set("user_input", verification_task)
        task_context.set("agent_log_dir", os.path.join(self.output_dir, "verify_tasks", f"verify_{finding_name_for_log}_logs"))
        
        task_start_time = time.time()
        tokens_before = self.calculate_token_usage()

        verification_analyzer_agent = build_agent(verification_analyzer_config, context=task_context)
        verification_result = verification_analyzer_agent.run(user_input=verification_prompt)
        
        task_end_time = time.time()
        tokens_after = self.calculate_token_usage()

        task_duration = task_end_time - task_start_time
        task_tokens = tokens_after - tokens_before

        print(f"<< Verification completed: {finding_name_for_log} (Time taken: {task_duration:.2f}s, Tokens: {task_tokens})")
        print(f"   Verification result: {verification_result}")

        verification_record = {
            'verification_task': finding_details,
            'verification_result': verification_result,
            'verification_duration_seconds': task_duration,
            'verification_token_usage': task_tokens
        }
        
        results_file_path = os.path.join(self.output_dir, "verification_results.jsonl")

        try:
            with self._verification_lock:
                with open(results_file_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(verification_record, ensure_ascii=False) + '\n')
            print(f"   Verification results written to: {results_file_path}")
        except IOError as e:
            print(f"   Failed to write verification results file: {e}")

    def verify(self, finding_to_verify: Optional[Union[Dict[str, Any], str]] = None):
        """
        [Sequential] Verifies one or more findings.
        If `finding_to_verify` is provided, only that finding is verified (can be dict or string).
        Otherwise, findings are loaded, filtered, and sampled from the knowledge base for verification.
        Verification results will be saved to a separate "verification_results.jsonl" file.
        """
        start_time = time.time()
        
        findings_to_process = self._get_findings_to_process(finding_to_verify)

        if not findings_to_process:
            print("No findings selected for verification.")
            return

        print(f"Total of {len(findings_to_process)} findings will be verified [sequentially].")

        verification_analyzer_config = create_firmware_analysis_blueprint(
            include_kb=False,
            max_levels=self.max_levels,
            max_iterations_per_agent=self.max_iterations,
        )

        for i, finding in enumerate(findings_to_process):
            print(f"--- (Sequential) Verifying {i+1}/{len(findings_to_process)} ---")
            self._verify_one_finding(finding, verification_analyzer_config)

        end_time = time.time()
        self.verification_duration += (end_time - start_time)
        print(f"\nThis sequential verification took {end_time - start_time:.2f} seconds. Total verification time accumulated: {self.verification_duration:.2f} seconds.")
        
        self.summary()
        print("This round of sequential verification tasks is complete.")

    def verify_concurrently(self, max_workers: int = 5, finding_to_verify: Optional[Union[Dict[str, Any], str]] = None):
        """
        [Concurrent] Verifies one or more findings.
        """
        start_time = time.time()
        
        findings_to_process = self._get_findings_to_process(finding_to_verify)

        if not findings_to_process:
            print("No findings selected for verification.")
            return

        print(f"Total of {len(findings_to_process)} findings will be verified [concurrently], using {max_workers} worker threads.")

        verification_analyzer_config = create_firmware_analysis_blueprint(
            include_kb=False,
            max_levels=self.max_levels,
            max_iterations_per_agent=self.max_iterations,
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._verify_one_finding, finding, verification_analyzer_config)
                for finding in findings_to_process
            ]
            for future in as_completed(futures):
                try:
                    future.result() 
                except Exception as exc:
                    print(f'A verification task generated an exception: {exc}')

        end_time = time.time()
        self.verification_duration += (end_time - start_time)
        print(f"\nThis concurrent verification took {end_time - start_time:.2f} seconds. Total verification time accumulated: {self.verification_duration:.2f} seconds.")
        
        self.summary()
        print("This round of concurrent verification tasks is complete.")

    def generate_report(self):
        """Generates a Markdown analysis report."""
        print("\nStarting analysis report generation")
        kb_path = os.path.join(self.output_dir, 'knowledge_base.jsonl')
        if not os.path.exists(kb_path):
            print(f"Knowledge base file '{kb_path}' does not exist, cannot generate report.")
            return None, "Knowledge base file does not exist"

        try:
            from firmware.utils.convert2md import convert_kb_to_markdown
            success, msg_or_path = convert_kb_to_markdown(kb_path)
            if success:
                print(f"Successfully generated Markdown report: {msg_or_path}")
                return msg_or_path, None
            else:
                print(f"Failed to generate report: {msg_or_path}")
                return None, msg_or_path
        except ImportError:
            error_msg = "Could not import report generation tools, skipping Markdown report generation."
            print(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"An unknown error occurred during report generation: {e}"
            print(error_msg)
            return None, error_msg

    def generate_verification_report(self):
        """Generates a Markdown verification report."""
        print("\nStarting verification report generation")
        
        try:
            from firmware.utils.convert2md import generate_verification_report_md
            
            success, msg_or_path = generate_verification_report_md(self.output_dir)
            
            if success:
                print(f"Successfully generated Markdown verification report: {msg_or_path}")
                return [msg_or_path], None 
            else:
                if "No verification results file found" in msg_or_path:
                    print(f"No 'verification_results.jsonl' file found in '{self.output_dir}', skipping verification report generation.")
                else:
                    print(f"Failed to generate verification report: {msg_or_path}")
                return None, msg_or_path
                    
        except ImportError:
            error_msg = "Could not import report generation tools, skipping Markdown verification report generation."
            print(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"An unknown error occurred during report generation: {e}"
            print(error_msg)
            return None, error_msg

    def calculate_token_usage(self):
        """Calculates and returns the total token usage."""
        token_usage_file = os.path.join(self.output_dir, "token_usage.jsonl")
        if not os.path.exists(token_usage_file):
            return 0

        total_tokens = 0
        try:
            with open(token_usage_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        total_tokens += data.get('total_tokens', 0)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error calculating token usage: {e}")
        return total_tokens

    def summary(self):
        """Creates and writes a summary.txt file. Regenerates and overwrites the summary on each call."""
        self.generate_report()
        self.generate_verification_report()
        
        total_tokens = self.calculate_token_usage()
        
        summary_path = os.path.join(self.output_dir, "summary.txt")
        summary_content = (
            f"Analysis and Verification Summary\n"
            f"Analysis Phase Duration: {self.analysis_duration:.2f} seconds\n"
            f"Verification Phase Duration: {self.verification_duration:.2f} seconds\n"
            f"Total Duration: {self.analysis_duration + self.verification_duration:.2f} seconds\n"
            f"Total Model Token Usage: {total_tokens}\n"
        )
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            print(f"\nSummary information updated: {summary_path}")
            print(summary_content)
        except IOError as e:
            print(f"Could not write summary file {summary_path}: {e}")
