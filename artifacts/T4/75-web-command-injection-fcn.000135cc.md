---
firmware: DIR-885L_fw_revA_1-13_eu_multi_20170119
alert: web-command-injection-fcn.000135cc
---

### web-command-injection-fcn.000135cc

- **File/Directory Path:** `mydlink/tsa`
- **Location:** `fcn.000135cc`
- **Risk Score:** 8.5
- **Confidence:** 7.5
- **Description:** A command injection vulnerability was identified in function fcn.000135cc. This function executes external commands (mdb_get_admin_REDACTED_PASSWORD_PLACEHOLDER) via popen, with parameters derived from hardcoded strings and stack buffers. If upstream call chains permit user control over these parameters (e.g., through HTTP requests), it may lead to arbitrary command execution.
- **Keywords:** fcn.000135cc, popen, mdb_get_admin_REDACTED_PASSWORD_PLACEHOLDER, 0x19728, 0x13eac, 0x142f4, /goform/form_login
- **Notes:** It is necessary to audit all function paths that call fcn.000135cc to verify whether the source of the 0x19728 value can be controlled by users, especially checking if it originates from HTTP request parameters.
