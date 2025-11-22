---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: env_get-libsmb_prog-sock_exec
---

### env_get-libsmb_prog-sock_exec

- **File/Directory Path:** `usr/sbin/smbd`
- **Location:** `usr/sbin/smbd:0x8f6dc (sym.cli_connect)`
- **Risk Score:** 8.5
- **Confidence:** 7.5
- **Description:** The value of the environment variable LIBSMB_PROG is directly passed to the sym.sock_exec function, posing a command injection risk. Trigger condition: When the program calls the sym.cli_connect function, the value of the LIBSMB_PROG environment variable will be directly passed to the sym.sock_exec function for execution.
- **Code Snippet:**
  ```
Not provided in the original analysis
  ```
- **Keywords:** command
- **Notes:** Auto-curated from results directory; verify in target environment.
