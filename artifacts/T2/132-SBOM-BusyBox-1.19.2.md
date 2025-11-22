---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: SBOM-BusyBox-1.19.2
---

### SBOM-BusyBox-1.19.2

- **File/Directory Path:** `webroot_REDACTED_PASSWORD_PLACEHOLDER.txt`
- **Location:** `bin/busybox`
- **Risk Score:** 9.8
- **Confidence:** 9.0
- **Description:** BusyBox component version 1.19.2, located at bin/busybox. This version contains multiple high-risk vulnerabilities, including CVE-2016-2148 (DHCP client heap overflow vulnerability, risk level 9.8), CVE-2016-2147 (DHCP client integer overflow vulnerability, risk level 7.5), and CVE-2011-5325 (tar command directory traversal vulnerability, risk level 7.5).
- **Code Snippet:**
  ```
  Direct string: 'BusyBox v1.19.2 (2015-04-22 19:07:41 HKT)'
  ```
- **Keywords:** BusyBox, 1.19.2, CVE-2016-2148, CVE-2016-2147, CVE-2011-5325
- **Notes:** Configuration load.  

Version information is confirmed through direct string comparison, which contains multiple high-risk vulnerabilities. It is recommended to prioritize fixing them.
