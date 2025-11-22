---
firmware: R8000-V1.0.4.4_1.1.42
alert: thirdparty-avahi-libavahi-core
---

### thirdparty-avahi-libavahi-core

- **File/Directory Path:** `usr/lib/libavahi-core.so.6.0.1`
- **Location:** `usr/lib/libavahi-core.so.6.0.1`
- **Risk Score:** 8.5
- **Confidence:** 4.0
- **Description:** The file 'usr/lib/libavahi-core.so.6.0.1' is version 6.0.1 of the Avahi core library. This version contains multiple known critical vulnerabilities, including CVE-2017-6519 (CVSS 9.1), CVE-2021-26720 (CVSS 7.8), and CVE-2021-3502 (CVSS 5.5). These vulnerabilities may lead to denial of service, information leakage, and local symlink attacks.
- **Code Snippet:**
  ```
  N/A
  ```
- **Keywords:** libavahi-core.so.6.0.1, Avahi, CVE-2017-6519, CVE-2021-26720, CVE-2021-3502
- **Notes:** It is recommended to update to the latest version of the Avahi core library to fix these vulnerabilities. Further verification can be done by checking the package metadata to confirm the exact version information.
