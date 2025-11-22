---
firmware: TL-WR1043ND_V3_150514
alert: env_get-REDACTED_PASSWORD_PLACEHOLDER-sym.getpass_or_cancel
---

### env_get-REDACTED_PASSWORD_PLACEHOLDER-sym.getpass_or_cancel

- **File/Directory Path:** `REDACTED_PASSWORD_PLACEHOLDER`
- **Location:** `sym.getpass_or_cancel`
- **Risk Score:** 7.5
- **Confidence:** 8.0
- **Description:** The function `sym.getpass_or_cancel` retrieves the REDACTED_PASSWORD_PLACEHOLDER via `getenv('REDACTED_PASSWORD_PLACEHOLDER')`, posing a high risk of REDACTED_PASSWORD_PLACEHOLDER exposure. Sensitive REDACTED_PASSWORD_PLACEHOLDER information should not be transmitted through environment variables.
- **Code Snippet:**
  ```
  getenv("REDACTED_PASSWORD_PLACEHOLDER")
  ```
- **Keywords:** REDACTED_PASSWORD_PLACEHOLDER, sym.getpass_or_cancel, getenv
- **Notes:** High-risk environment variable access point, may lead to REDACTED_PASSWORD_PLACEHOLDER leakage
