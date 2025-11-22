---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: SBOM-uClibc-usr_bin_vmstat
---

### SBOM-uClibc-usr_bin_vmstat

- **File/Directory Path:** `usr/bin/vmstat`
- **Location:** `usr/bin/vmstat (strings output)`
- **Risk Score:** 9.8
- **Confidence:** 7.5
- **Description:** uClibc library found in usr/bin/vmstat with potential vulnerabilities. Exact version not specified but referenced via '/lib/ld-uClibc.so.0'. Known CVEs: CVE-2017-9728 (9.8), CVE-2022-29503 (9.8), CVE-2021-43523 (9.6).
- **Code Snippet:**
  ```
  /lib/ld-uClibc.so.0 and libc.so.0
  ```
- **Keywords:** /lib/ld-uClibc.so.0, libc.so.0
- **Notes:** configuration_load
