"""
Shared response format block for analysis findings.
"""

SHARED_RESPONSE_FORMAT_BLOCK = """
Each finding must include the following **core fields**:
- **`description`**: A detailed description of the finding, which must include:
* Specific manifestation and triggering conditions of the problem
* Detailed constraint and boundary check situations
* Potential attack and exploitation methods
* Relevant code logic or technical details

- **`link_identifiers`**: Specific NVRAM or ENV variable names, file paths, IPC socket paths, and custom shared function symbols to ensure accurate tracking of cross-file and cross-process data flow and interactions.
- **`location`**: Precise location (file:line_number function_name address)
- **`code_snippet`**: Return the complete relevant code segment, demonstrating vulnerability triggering conditions and exploitation methods.
- **`risk_score`**: Risk score (0.0-10.0). **Only findings with a complete, validated attack chain and clear security impact can score >= 7.0.**
- **`confidence`**: Confidence in the accuracy and exploitability analysis of the finding (0.0-10.0). **A score >= 8.0 requires a complete, verifiable attack chain from source to sink.**
- **`notes`**: Other important information for reference by human analysts, including: assumptions requiring further validation, associated files or functions of the finding, and recommended directions for further analysis.

#### Key Principles:
- **Exploitability is Mandatory**: If the user only requires reporting of actually exploitable attack chains, then theoretical weaknesses or bad practices (such as using `strcpy`) are not sufficient unless you can prove that they lead to a vulnerability.
- **Evidence Trumps Supposition**: All assertions must be supported by tool-generated evidence. If evidence is missing, state it explicitly. Do not speculate.
"""
