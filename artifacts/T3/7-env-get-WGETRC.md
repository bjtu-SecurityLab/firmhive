---
firmware: _US_AC9V1.0BR_V15.03.05.14_multi_TD01.bin.extracted
alert: env_get-login_pre_suid_script-command_injection
---

### env_get-login_pre_suid_script-command_injection

- **File/Directory Path:** `bin/busybox`
- **Location:** `bin/busybox:0xf248`
- **Risk Score:** 9.0
- **Confidence:** 8.5
- **Description:** In bin/busybox, the LOGIN_PRE_SUID_SCRIPT environment variable is obtained via getenv, potentially used for command construction and execution logic. High risk, possibly exploitable for command injection.
- **Code Snippet:**
  ```
Not available
  ```
- **Keywords:** command
- **Notes:** Auto-curated from results directory; verify in target environment.
