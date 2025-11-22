---
firmware: FH1201
alert: SBOM-GCC-3.3.2
---

### SBOM-GCC-3.3.2

- **File/Directory Path:** `bin/et`
- **Location:** `bin/et (strings output)`
- **Risk Score:** 7.0
- **Confidence:** 7.0
- **Description:** The use of GCC version 3.3.2 was detected in the file bin/et. This version has a known vulnerability, CVE-2000-1219, which affects the -ftrapv compiler option.
- **Code Snippet:**
  ```
  GCC: (GNU) 3.3.2
  ```
- **Keywords:** bcm57, GCC: (GNU) 3.3.2
- **Notes:** It is recommended to check whether the -ftrapv compiler option is used in the firmware.
