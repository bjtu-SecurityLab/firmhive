---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: hardcoded-REDACTED_PASSWORD_PLACEHOLDER-RMT_invite_reg.htm-login
---

### hardcoded-REDACTED_PASSWORD_PLACEHOLDER-RMT_invite_reg.htm-login

- **File/Directory Path:** `www/cgi-bin/RMT_invite_reg.htm`
- **Location:** `RMT_invite_reg.htm`
- **Risk Score:** 8.0
- **Confidence:** 8.0
- **Description:** Hardcoded credentials were found in the RMT_invite_reg.htm file: The TXT_remote_login field value is '<%2041%>', which URL-decodes to ' A' (space followed by letter A). These credentials are located in hidden input fields and may be used for remote access control.
- **Code Snippet:**
  ```
  <input type="hidden" value="<%2041%>" name="TXT_remote_login" maxlength="25" size="28">
  <input type="hidden" value="<%2598%>" name="TXT_remote_password" maxlength="25" size="28">
  ```
- **Keywords:** TXT_remote_login, TXT_remote_password, <%2041%>, <%2598%>, hidden
- **Notes:** The REDACTED_PASSWORD_PLACEHOLDER field value '%98' may require further decoding. It is recommended to examine the RMT_invite.cgi file to understand how these credentials are utilized.
