#!/usr/bin/env python3
"""
Main entry point for FirmwareHive analysis tool.
"""
import os
import sys
import argparse

from firmware.utils.finder import find_firmware_root
from firmware.master_agent import FirmwareMasterAgent


def main():
    """Main entry point for firmware analysis."""
    default_user_input = (
        "You must conduct a comprehensive analysis of the firmware file system, including binaries, configuration files, scripts, etc. The core objective is to identify and report complete, feasible, and actually exploitable attack chains from untrusted input points to dangerous operations. "
        "The analysis must focus on vulnerabilities with clear exploitable evidence, not merely theoretical flaws. Clearly and independently define and state the attacker model being evaluated.\n"
        "1. **Input Point Identification**: Identify all untrusted input sources in relevant files (binaries, configuration files, scripts, etc.), including but not limited to network interfaces (HTTP, API, sockets), IPC, NVRAM/environment variables, etc.\n"
        "2. **Data Flow Tracking**: Trace the propagation paths of untrusted data within the system and analyze whether there is a lack of proper validation, filtering, or boundary checking.\n"
        "3. **Component Interaction Analysis**: Focus on interactions between components (e.g., `nvram` get/set, IPC communication, front-end/back-end interaction), observing how externally controllable data flows within the system and affects other components.\n"
        "4. **Final Output**: The report should clearly describe the attack paths and security vulnerabilities most likely to be successfully exploited by attackers, assess their prerequisites, reproduction steps, and likelihood of success. For each finding, clearly indicate the attacker model and assumptions used (including authentication level, required privileges, exposed surface/reachability, etc.), and provide the rationale."
    )

    parser = argparse.ArgumentParser(description="Firmware Analysis Master Agent")
    parser.add_argument("--search_dir", type=str, required=True, help="Path to the directory to search for firmware root.")
    parser.add_argument("--output", type=str, default="output", help="Base directory for analysis output.")
    parser.add_argument("--mode", type=str, choices=['analyze', 'verify', 'all'], default='all', 
                        help="Execution mode: 'analyze' only, 'verify' only, or 'all' (analyze then verify).")
    parser.add_argument("--user_input", type=str, default=default_user_input, help="User input/prompt for the analysis. Uses a default prompt if not provided in 'analyze' or 'all' mode.")
    parser.add_argument("--finding", type=str, help="A string describing a specific finding to verify. If not provided in 'verify' mode, findings are loaded from the knowledge base.")
    parser.add_argument("--concurrent", action="store_true", help="Run verification concurrently.")
    parser.add_argument("--max_workers", type=int, default=5, help="Max workers for concurrent verification.")
    
    args = parser.parse_args()

    firmware_root = find_firmware_root(args.search_dir)
    if not firmware_root:
        print(f"Error: Could not find a valid firmware root in '{args.search_dir}'.")
        sys.exit(1)
    
    print(f"Found firmware root at: {firmware_root}")

    output_dir = args.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Output will be saved to: {output_dir}")

    master_agent = FirmwareMasterAgent(
        max_levels_for_blueprint=4,
        firmware_root_path=firmware_root,
        output_dir=output_dir,
        user_input=args.user_input,
    )
    
    if args.mode == 'analyze':
        print("\n--- Running in Analysis-Only Mode ---")
        master_agent.run()
        print("\n--- Analysis complete ---")

    elif args.mode == 'verify':
        print("\n--- Running in Verification-Only Mode ---")
        if args.concurrent:
            master_agent.verify_concurrently(
                max_workers=args.max_workers,
                finding_to_verify=args.finding
            )
        else:
            master_agent.verify(
                finding_to_verify=args.finding
            )
        print("\n--- Verification complete ---")

    elif args.mode == 'all':
        print("\n--- Running in Analysis and Verification Mode ---")
        summary = master_agent.run()
        
        if args.concurrent:
            master_agent.verify_concurrently(max_workers=args.max_workers, finding_to_verify=args.finding)
        else:
            master_agent.verify(finding_to_verify=args.finding)
        print("\n--- Analysis and Verification complete ---")


if __name__ == "__main__":
    main()
