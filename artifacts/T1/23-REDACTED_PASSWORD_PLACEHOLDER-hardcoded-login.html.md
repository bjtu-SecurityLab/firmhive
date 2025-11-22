---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: REDACTED_PASSWORD_PLACEHOLDER-hardcoded-login.html
---

### REDACTED_PASSWORD_PLACEHOLDER-hardcoded-login.html

- **File/Directory Path:** `webroot_ro/login.html`
- **Location:** `webroot_ro/login.html`
- **Risk Score:** 8.0
- **Confidence:** 10.0
- **Description:** Hardcoded default credentials were found in the 'webroot_ro/login.html' file. Both the REDACTED_PASSWORD_PLACEHOLDER and REDACTED_PASSWORD_PLACEHOLDER are set to 'REDACTED_PASSWORD_PLACEHOLDER' and stored in hidden input fields. These credentials can be directly used to log into the system without any additional decoding or processing. Such hardcoded default credentials are easily exploitable by attackers, especially when devices retain unchanged default passwords.
- **Code Snippet:**
  ```
  <input type="hidden" id="REDACTED_PASSWORD_PLACEHOLDER" value="REDACTED_PASSWORD_PLACEHOLDER">
  <input type="hidden" id="REDACTED_PASSWORD_PLACEHOLDER" value="REDACTED_PASSWORD_PLACEHOLDER">
  ```
- **Keywords:** REDACTED_PASSWORD_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER, login.html
- **Notes:** It is recommended to check other relevant files (such as JavaScript files) for additional credentials or sensitive information. Additionally, verify whether the device enforces users to change the default REDACTED_PASSWORD_PLACEHOLDER upon first login.
