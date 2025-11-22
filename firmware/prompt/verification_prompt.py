"""
System prompts for verification analysis (validating security findings).
"""

DEFAULT_VERIFICATION_TASK_TEMPLATE = (
    "Your sole task is to strictly and objectively validate the following security alert. Your analysis must be entirely based on the provided evidence.\n\n"
    "**Core Principles**:\n"
    "1.  **Evidence-driven**: All assertions in the alert must be validated by analyzing the provided evidence. Guesswork or analyzing unrelated information and files is strictly prohibited.\n"
    "2.  **Logic Review**: Do not simply confirm the existence of the code; you must understand its execution logic. Carefully examine control flow statements, data sanitization, and other factors that determine reachability of code paths.\n"
    "3.  **Exploitation Verification**: Validate whether the vulnerability is **actually exploitable** by confirming:\n"
    "    - **Input Controllability**: The attacker can control the tainted input.\n"
    "    - **Path Reachability**: The vulnerable path is reachable under realistic conditions. In your analysis, clearly define and state the attacker model used for this vulnerability assessment (e.g., unauthenticated remote attacker, authenticated local user, etc.).\n"
    "    - **Practical Impact**: The operation can cause actual security harm.\n"
    "4.  **Complete Attack Chain**: - **Full path required**: Partial or conjectural paths are unacceptable. You must provide a complete, validated chain. The full propagation path from attacker-controlled input to the dangerous sink must be verified, supported by evidence at each step.\n\n"
    "**Note**: Function names in the alert may come from decompilation. Search thoroughly; do not hastily conclude that they do not exist just because they are not in the symbol table or strings.\n\n"
    "{verification_finding_details}\n"
)

DEFAULT_VERIFICATION_INSTRUCTION_TEMPLATE = (
    "{verification_task}\n"
    "**Provide a Conclusion**: At the end of your analysis, `final_response` must be a JSON object containing the following fields:\n"
    "    - `accuracy`: (string) Assessment of the alert's descriptive accuracy. Must be 'accurate', 'inaccurate', or 'partially'.\n"
    "    - `vulnerability`: (boolean) Whether the description is sufficient to constitute a real vulnerability. Must be True or False. Clearly explain the attacker assumptions on which you base your evaluation.\n"
    "    - `risk_level`: (string) If `vulnerability` is `true`, the risk level of the vulnerability. Must be 'Low', 'Medium', or 'High'.\n"
    "    - `reason`: (string) A detailed explanation supporting all the above conclusions. For findings confirmed as real vulnerabilities, this field must also include a reproducible attack payload or proof-of-concept (PoC) steps, clearly describing how to exploit the vulnerability.\n"
)
