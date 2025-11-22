---
firmware: R7500
alert: sbom-uclibc-libc.so.0
---

### sbom-uclibc-libc.so.0

- **File/Directory Path:** `usr/sbin/remote_fsize`
- **Location:** `usr/sbin/remote_fsize`
- **Risk Score:** 9.8
- **Confidence:** 8.5
- **Description:** Analysis results of the uClibc component. Confirmed version: 0.9.33.2, evidence sources: filename of lib/ld-uClibc-0.9.33.2.so and internal version string confirmation, as well as usr/sbin/aclctl referencing the specific version file through shared library link /lib/ld-uClibc.so.0. Associated vulnerabilities: CVE-2017-9728 (out-of-bounds read vulnerability in regex processing, CVSS 9.8), CVE-2022-29503 (memory corruption vulnerability in libpthread linuxthreads functionality, CVSS 9.8), CVE-2017-9729 (stack exhaustion vulnerability in regex processing, CVSS 7.5), CVE-2022-30295 (DNS cache poisoning vulnerability due to predictable DNS transaction IDs, CVSS 8.1). Prioritize patching these critical vulnerabilities.
- **Code Snippet:**
  ```
N/A
  ```
- **Keywords:** N/A
- **Notes:** Auto-curated from results directory; verify in target environment.
