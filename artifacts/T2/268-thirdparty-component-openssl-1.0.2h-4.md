---
firmware: DIR-868L_fw_revA_1-12_eu_multi_20170316
alert: thirdparty-component-openssl-1.0.2h
---

### thirdparty-component-openssl-1.0.2h

- **File/Directory Path:** `etc/openssl.cnf`
- **Location:** `libssl.so.1.0.0 (HIDDEN)`
- **Risk Score:** 9.0
- **Confidence:** 8.75
- **Description:** The file 'lib/libssl.so.1.0.0' contains explicit information indicating OpenSSL version 1.0.2h. This version has multiple known critical vulnerabilities, including heap buffer boundary check errors (CVE-2016-2177), information disclosure (CVE-2016-2176), memory corruption (CVE-2016-2105, CVE-2016-2106), etc. These vulnerabilities may lead to security risks such as denial of service, information disclosure, or remote code execution.
- **Code Snippet:**
  ```
  SSLv3 part of OpenSSL 1.0.2h  3 May 2016
  ```
- **Keywords:** OpenSSL 1.0.2h, libssl.so.1.0.0, SSLv3 part of OpenSSL 1.0.2h, TLSv1 part of OpenSSL 1.0.2h, DTLSv1 part of OpenSSL 1.0.2h
- **Notes:** It is recommended to upgrade OpenSSL to a higher version to fix these vulnerabilities. In particular, CVE-2016-2177 has the highest CVSSv3 score of 9.8 and should be addressed immediately.
