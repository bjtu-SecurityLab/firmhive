---
firmware: R6400v2-V1.0.2.46_1.0.36
alert: command_execution-fcn.0001a084-0x1a210
---

### command_execution-fcn.0001a084-0x1a210

- **File/Directory Path:** `sbin/rc`
- **Location:** `sbin/rc:0x1a210 (fcn.0001a084)`
- **Risk Score:** 9.5
- **Confidence:** 8.5
- **Description:** In the fcn.0001a084 function, the environment variable value at address 0x1a210 is directly used in the `system()` call, posing a high risk of command injection. The environment variable value is passed to system command execution without adequate validation.
- **Code Snippet:**
  ```
Not available
  ```
- **Keywords:** command, system
- **Notes:** Auto-curated from results directory; verify in target environment.
