---
firmware: FH1201
alert: REDACTED_PASSWORD_PLACEHOLDER-hardcoded-REDACTED_PASSWORD_PLACEHOLDER-nobody
---

### REDACTED_PASSWORD_PLACEHOLDER-hardcoded-REDACTED_PASSWORD_PLACEHOLDER-nobody

- **File/Directory Path:** `etc_ro/REDACTED_PASSWORD_PLACEHOLDER`
- **Location:** `etc_ro/REDACTED_PASSWORD_PLACEHOLDER:4`
- **Risk Score:** 8.0
- **Confidence:** 8.0
- **Description:** The 'etc_ro/REDACTED_PASSWORD_PLACEHOLDER' file contains hardcoded user credentials for 'nobody' with hashed REDACTED_PASSWORD_PLACEHOLDER 'VBcCXSNG7zBAY'. The hash appears to be in a non-standard format, possibly using DES or another hashing algorithm. The presence of these hashed passwords in a world-readable file poses a security risk if the hashes can be cracked.
- **Code Snippet:**
  ```
  nobody:VBcCXSNG7zBAY:0:0:nobody for ftp:/:/bin/sh
  ```
- **Keywords:** nobody, VBcCXSNG7zBAY
- **Notes:** file_read
