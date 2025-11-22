---
firmware: DIR-885L_fw_revA_1-13_eu_multi_20170119
alert: env_get-dynamic_var_1
---

### env_get-dynamic_var_1

- **File/Directory Path:** `sbin/udevd`
- **Location:** `./sbin/udevd:fcn.0000e4c0 (0xea84)`
- **Risk Score:** 8.5
- **Confidence:** 8.5
- **Description:** Dynamically compute environment variable names and perform string concatenation in './sbin/udevd'. Potential command injection risk, high security vulnerability.
- **Code Snippet:**
  ```
  getenv(dynamic_var) -> strlcat
  ```
- **Keywords:** getenv, strlcat, %{var}
- **Notes:** Risk Level 8.5 - Potential Command Injection
