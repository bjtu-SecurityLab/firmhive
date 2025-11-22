---
firmware: DIR-885L_fw_revA_1-13_eu_multi_20170119
alert: env_get-dynamic_var_1
---

### env_get-dynamic_var_1

- **File/Directory Path:** `sbin/udevd`
- **Location:** `./sbin/udevd:fcn.0000e4c0 (0xea84)`
- **Risk Score:** 9.0
- **Confidence:** 8.5
- **Description:** Dynamically compute environment variable names and perform string concatenation in './sbin/udevd'. Potential command injection risk, high security vulnerability.
- **Code Snippet:**
  ```
getenv(dynamic_var) -> strlcat
  ```
- **Keywords:** command
- **Notes:** Auto-curated from results directory; verify in target environment.
