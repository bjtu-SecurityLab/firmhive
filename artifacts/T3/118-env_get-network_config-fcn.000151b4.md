---
firmware: R6200v2-V1.0.3.12_10.1.11
alert: env_get-network_config-fcn.000151b4
---

### env_get-network_config-fcn.000151b4

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `./sbin/acos_service: (fcn.000151b4, fcn.REDACTED_PASSWORD_PLACEHOLDER)`
- **Risk Score:** 8.0
- **Confidence:** 8.25
- **Description:** The functions fcn.000151b4 and fcn.REDACTED_PASSWORD_PLACEHOLDER were found to access environment variables for network configuration and routing management. The environment variable values are directly used in system commands (such as ifconfig and route) without apparent sanitization, posing a command injection risk.
- **Code Snippet:**
  ```
  Strings found: getenv, ifconfig, route_add, route_del
  ```
- **Keywords:** getenv, system, ifconfig, route_add, route_del
- **Notes:** It is recommended to audit all environment variables accessed through these functions and implement input validation
