import sys
import argparse

T1_HARDCODED_CREDENTIALS = (
    "Perform a comprehensive scan of the firmware file system to locate and report all hardcoded credentials and sensitive information."
)

T2_COMPONENT_CVE = (
    "Analyze the firmware to generate a software bill of materials (SBOM) for third-party components, and identify related high-risk vulnerabilities (CVEs)."
)

T3_NVRAM_INTERACTION = (
    "Analyze accesses to NVRAM and similar environment variable configuration systems (such as `getenv`) within the firmware. "
    "The core task is to identify and report the complete, unsanitized data flow paths from these variables to dangerous function calls."
)

T4_WEB_ATTACK_CHAIN = (
    "Analyze the firmware's web services to locate vulnerabilities where external HTTP input is passed to dangerous functions (such as `system`, `strcpy`). "
    "The core task is to identify and report the complete, unsanitized data flow paths from HTTP parameters to dangerous function calls."
)

T5_COMPREHENSIVE_ANALYSIS = (
    "You must conduct a comprehensive analysis of the firmware file system, including binaries, configuration files, scripts, etc. The core objective is to identify and report complete, feasible, and actually exploitable attack chains from untrusted input points to dangerous operations. "
    "The analysis must focus on vulnerabilities with clear exploitable evidence, not merely theoretical flaws. Clearly and independently define and state the attacker model being evaluated.\n"
    "1. **Input Point Identification**: Identify all untrusted input sources in relevant files (binaries, configuration files, scripts, etc.), including but not limited to network interfaces (HTTP, API, sockets), IPC, NVRAM/environment variables, etc.\n"
    "2. **Data Flow Tracking**: Trace the propagation paths of untrusted data within the system and analyze whether there is a lack of proper validation, filtering, or boundary checking.\n"
    "3. **Component Interaction Analysis**: Focus on interactions between components (e.g., `nvram` get/set, IPC communication, front-end/back-end interaction), observing how externally controllable data flows within the system and affects other components.\n"
    "4. **Final Output**: The report should clearly describe the attack paths and security vulnerabilities most likely to be successfully exploited by attackers, assess their prerequisites, reproduction steps, and likelihood of success. For each finding, clearly indicate the attacker model and assumptions used (including authentication level, required privileges, exposed surface/reachability, etc.), and provide the rationale."
)

def get_task_prompt(task_name: str) -> str:
    """
    Get the task instruction string by its variable name from the current module.
    """
    task_inputs = sys.modules[__name__]
    if not hasattr(task_inputs, task_name):
        print(f"Error: Task '{task_name}' not found.", file=sys.stderr)
        sys.exit(1)
    return getattr(task_inputs, task_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get a specific task prompt by its variable name.")
    parser.add_argument("task_name", type=str, help="The variable name of the task (e.g., T1_HARDCODED_CREDENTIALS).")
    args = parser.parse_args()
    
    prompt = get_task_prompt(args.task_name)
    print(prompt) 