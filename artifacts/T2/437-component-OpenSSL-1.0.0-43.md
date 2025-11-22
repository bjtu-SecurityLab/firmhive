---
firmware: R7000
alert: component-OpenSSL-1.0.0
---

### component-OpenSSL-1.0.0

- **File/Directory Path:** `bin/circled`
- **Location:** `bin/circled`
- **Risk Score:** 7.4
- **Confidence:** 7.5
- **Description:** The OpenSSL component version extracted from file 'bin/circled' is 1.0.0, evidenced by the string 'libcrypto.so.1.0.0'. Relevant CVEs include:
- CVE-2014-0224: CCS Injection vulnerability allowing man-in-the-middle attackers to hijack sessions or obtain sensitive information (CVSSv3: 7.4)
- CVE-2009-1379: Use-after-free vulnerability potentially causing denial of service (CVSSv3: N/A)
- CVE-2009-1387: NULL pointer dereference vulnerability potentially causing denial of service (CVSSv3: N/A)
- **Code Snippet:**
  ```
  libcrypto.so.1.0.0
  ```
- **Keywords:** libcrypto.so.1.0.0
- **Notes:** It is recommended to further verify the specific patch level of OpenSSL 1.0.0, as certain vulnerabilities may have been fixed in subsequent patches.
