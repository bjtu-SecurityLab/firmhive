---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: command_injection-wfa_igd_handle-get_public_ip
---

### command_injection-wfa_igd_handle-get_public_ip

- **File/Directory Path:** `etc/scripts/wfa_igd_handle.php`
- **Location:** `wfa_igd_handle.php`
- **Risk Score:** 8.0
- **Confidence:** 7.5
- **Description:** A command injection vulnerability was discovered in wfa_igd_handle.php. The get_public_ip() function directly executes URL commands obtained from external sources, which may lead to remote code execution. REDACTED_PASSWORD_PLACEHOLDER risks:
1. External URL content is directly executed as commands
2. Lack of validation for URL content
3. Execution of potentially malicious commands through system calls
- **Keywords:** get_public_ip, urlget, external_command
- **Notes:** Analyze the call path of the get_public_ip() function to confirm whether there are other similar patterns of remote command acquisition and execution.
