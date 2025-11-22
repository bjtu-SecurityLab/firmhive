---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: systemic_command_injection-globals_vars
---

### systemic_command_injection-globals_vars

- **File/Directory Path:** `REDACTED_SENSITIVE_DATA`
- **Location:** `multiple files`
- **Risk Score:** 9.5
- **Confidence:** 8.5
- **Description:** Systemic command injection risk patterns identified in multiple PHP scripts:
1. Parameters obtained through $_GLOBALS variables (INF, PHYINF, DEVNAM, etc.)
2. Directly passed to command execution functions (cmd/system)
3. If these global variables originate from HTTP requests, it will lead to severe command injection vulnerabilities

Affected files:
IP-WAIT.php, dhcp6s_helper.php, stopchild.php, etc.
- **Code Snippet:**
  ```
N/A
  ```
- **Keywords:** command, system
- **Notes:** Auto-curated from results directory; verify in target environment.
