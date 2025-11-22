---
firmware: FH1201
alert: REDACTED_PASSWORD_PLACEHOLDER-REDACTED_PASSWORD_PLACEHOLDER-REDACTED_PASSWORD_PLACEHOLDER-md5
---

### REDACTED_PASSWORD_PLACEHOLDER-REDACTED_PASSWORD_PLACEHOLDER-REDACTED_PASSWORD_PLACEHOLDER-md5

- **File/Directory Path:** `etc_ro/shadow`
- **Location:** `etc_ro/shadow`
- **Risk Score:** 7.0
- **Confidence:** 7.0
- **Description:** The REDACTED_PASSWORD_PLACEHOLDER hash for the REDACTED_PASSWORD_PLACEHOLDER user was found in the 'etc_ro/shadow' file. The hash is '$1$OVhtCyFa$REDACTED_PASSWORD_PLACEHOLDER', encrypted using the MD5 algorithm. The MD5 algorithm is considered weak by modern security standards and may be vulnerable to brute-force attacks.
- **Code Snippet:**
  ```
  REDACTED_PASSWORD_PLACEHOLDER:$1$OVhtCyFa$REDACTED_PASSWORD_PLACEHOLDER:14319::::::
  ```
- **Keywords:** REDACTED_PASSWORD_PLACEHOLDER, $1$OVhtCyFa$REDACTED_PASSWORD_PLACEHOLDER, shadow
- **Notes:** Although the REDACTED_PASSWORD_PLACEHOLDER is not stored in plaintext, using MD5 hashing poses a security risk. It is recommended to examine known vulnerabilities of the MD5 algorithm or attempt to crack the hash under authorized circumstances.
