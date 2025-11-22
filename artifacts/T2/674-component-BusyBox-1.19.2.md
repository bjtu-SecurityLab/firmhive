---
firmware: TL-WA701ND_V2_140324
alert: sbom-uclibc-pktlogconf
---

### sbom-uclibc-pktlogconf

- **File/Directory Path:** `sbin/pktlogconf`
- **Location:** `sbin/pktlogconf: HIDDEN: /lib/ld-uClibc.so.0`
- **Risk Score:** 9.8
- **Confidence:** 8.5
- **Description:** The uClibc component has been detected in the file 'sbin/pktlogconf'. Associated CVEs include:
1. CVE-2017-9728: An out-of-bounds read vulnerability exists in the get_subexp function in misc/regex/regexec.c of uClibc 0.9.33.2 when processing specially crafted regular expressions (CVSS 9.8)
2. CVE-2022-29503: A memory corruption vulnerability exists in the libpthread linuxthreads functionality of uClibC 0.9.33.2 and uClibC-ng 1.0.40 (CVSS 9.8)
3. CVE-2021-43523: Improper handling of special characters in domain names returned by DNS servers in uClibc and uClibc-ng prior to version 1.0.39 (CVSS 9.6)
The specific version number of uClibc needs to be confirmed for more accurate vulnerability matching
- **Code Snippet:**
  ```
HIDDEN: /lib/ld-uClibc.so.0
  ```
- **Keywords:** N/A
- **Notes:** Auto-curated from results directory; verify in target environment.
