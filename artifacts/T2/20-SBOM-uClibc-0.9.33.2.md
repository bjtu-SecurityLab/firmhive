---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: SBOM-uClibc-0.9.33.2
---

### SBOM-uClibc-0.9.33.2

- **File/Directory Path:** `lib/libm.so.0`
- **Location:** `libm.so.0`
- **Risk Score:** 9.8
- **Confidence:** 8.5
- **Description:** The uClibc 0.9.33.2 component contains three critical vulnerabilities:
1. CVE-2017-9728 (CVSS 9.8): An out-of-bounds read vulnerability in the get_subexp function when processing specially crafted regular expressions
2. CVE-2022-29503 (CVSS 9.8): A memory corruption vulnerability in the libpthread linuxthreads functionality
3. CVE-2021-43523 (CVSS 9.6): Improper handling of special characters in domain names returned by DNS servers, potentially leading to domain hijacking or remote code execution

Version evidence source: 'libc.so.0' and 'libm.so.0' strings found in the file 'libm.so.0'
- **Keywords:** libc.so.0, libm.so.0
- **Notes:** Further confirmation of the specific version number of uClibc is required to more accurately match the vulnerability.
