---
firmware: R7500
alert: sbom-uclibc-internet
---

### sbom-uclibc-internet

- **File/Directory Path:** `usr/sbin/internet`
- **Location:** `usr/sbin/internet:0x000000f4 (HIDDEN)`
- **Risk Score:** 9.8
- **Confidence:** 8.5
- **Description:** The uClibc component was found referenced in the file 'usr/sbin/internet', with an unknown version (referenced as /lib/ld-uClibc.so.0). Three critical vulnerabilities were identified:  
1. CVE-2017-9728: Out-of-bounds read vulnerability when processing crafted regular expressions (risk score 9.8)  
2. CVE-2022-29503: Memory corruption vulnerability in the libpthread linuxthreads functionality (risk score 9.8)  
3. CVE-2021-43523: Incorrect handling of special characters returned by DNS servers, potentially leading to domain hijacking or remote code execution (risk score 9.6)  

Further analysis of library files in the firmware filesystem is required to obtain precise version information.
- **Code Snippet:**
  ```
HIDDEN: '/lib/ld-uClibc.so.0'
  ```
- **Keywords:** system
- **Notes:** Auto-curated from results directory; verify in target environment.
