---
firmware: R7500
alert: sbom-uclibc-dynamic-linker-consolidated
---

### sbom-uclibc-dynamic-linker-consolidated

- **File/Directory Path:** `usr/sbin/athdiag`
- **Location:** `lib/ld-uClibc-0.9.33.2.so`
- **Risk Score:** 9.8
- **Confidence:** 8.5
- **Description:** Comprehensive analysis confirms that the uClibc dynamic linker (ld-uClibc.so.0) version 0.9.33.2 contains multiple critical vulnerabilities:
1. CVE-2017-9728: Out-of-bounds read vulnerability in regular expression processing (CVSS 9.8)
2. CVE-2022-29503: Memory corruption vulnerability in libpthread linuxthreads functionality (CVSS 9.8)
3. CVE-2017-9729: Stack exhaustion vulnerability in regular expression processing (CVSS 7.5)
4. CVE-2022-30295: DNS cache poisoning vulnerability due to predictable DNS transaction IDs (CVSS 6.5)

Version information was confirmed based on the /lib/ld-uClibc-0.9.33.2.so filename and internal version strings.
- **Code Snippet:**
  ```
uClibc 0.9.33.2 (from strings output)
  ```
- **Keywords:** N/A
- **Notes:** Auto-curated from results directory; verify in target environment.
