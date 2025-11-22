---
firmware: TD-W8980_V1_150514
alert: REDACTED_PASSWORD_PLACEHOLDER-FTP-REDACTED_PASSWORD_PLACEHOLDER:1234
---

### REDACTED_PASSWORD_PLACEHOLDER-FTP-REDACTED_PASSWORD_PLACEHOLDER:1234

- **File/Directory Path:** `etc/vsftpd_REDACTED_PASSWORD_PLACEHOLDER`
- **Location:** `./etc/vsftpd_REDACTED_PASSWORD_PLACEHOLDER:First entry`
- **Risk Score:** 8.0
- **Confidence:** 9.0
- **Description:** Hardcoded FTP credentials found in plain text format 'REDACTED_PASSWORD_PLACEHOLDER:REDACTED_PASSWORD_PLACEHOLDER:flag1:flag2'. The credentials are stored without any encryption, which violates security best practices. The flags (1:1 or 0:0) might indicate account permissions or status, but their exact meaning would require further analysis of the vsftpd configuration.
- **Code Snippet:**
  ```
  REDACTED_PASSWORD_PLACEHOLDER:1234:1:1;guest:guest:0:0;test:test:1:1;$
  ```
- **Keywords:** vsftpd_REDACTED_PASSWORD_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER:1234, guest:guest, test:test
- **Notes:** The credentials are stored in plain text, which is a security best practice violation. The file should be properly secured with appropriate permissions, and the credentials should be stored in an encrypted format or managed through a secure authentication system.
