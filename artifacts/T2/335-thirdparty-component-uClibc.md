---
firmware: FH1201
alert: thirdparty-component-uClibc
---

### thirdparty-component-uClibc

- **File/Directory Path:** `bin/ddostool`
- **Location:** `bin/ddostool`
- **Risk Score:** 9.0
- **Confidence:** 7.5
- **Description:** References to the third-party component uClibc were found in the file 'bin/ddostool', but the specific version could not be determined. Multiple high-risk CVEs may affect this component.
- **Code Snippet:**
  ```
  HIDDEN '/lib/ld-uClibc.so.0' HIDDEN '__uClibc_main' HIDDEN
  ```
- **Keywords:** /lib/ld-uClibc.so.0, __uClibc_main, libc.so.0
- **Notes:** Since the specific version of uClibc cannot be determined, all related CVEs should be considered potentially relevant. It is recommended to obtain the actual uClibc library file to identify its exact version. The related CVEs include: CVE-2017-9728 (9.8), CVE-2022-29503 (9.8), CVE-2021-43523 (9.6), CVE-2016-6264 (7.5), CVE-2021-27419 (7.3)
