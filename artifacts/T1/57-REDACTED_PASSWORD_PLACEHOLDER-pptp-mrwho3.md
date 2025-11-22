---
firmware: _US_AC9V1.0BR_V15.03.05.14_multi_TD01.bin.extracted
alert: REDACTED_PASSWORD_PLACEHOLDER-pptp-mrwho3
---

### REDACTED_PASSWORD_PLACEHOLDER-pptp-mrwho3

- **File/Directory Path:** `webroot_REDACTED_PASSWORD_PLACEHOLDER.txt`
- **Location:** `webroot_REDACTED_PASSWORD_PLACEHOLDER.txt`
- **Risk Score:** 8.0
- **Confidence:** 9.0
- **Description:** Hardcoded PPTP VPN REDACTED_PASSWORD_PLACEHOLDER and REDACTED_PASSWORD_PLACEHOLDER combination found. The REDACTED_PASSWORD_PLACEHOLDER 'mrwho3' and REDACTED_PASSWORD_PLACEHOLDER 'REDACTED_PASSWORD_PLACEHOLDER' are stored in plaintext within the configuration file. These credentials are used for PPTP VPN connections, with the connection status shown as enabled (connsta=1).
- **Code Snippet:**
  ```
  {"connsta": "1", "REDACTED_PASSWORD_PLACEHOLDER": "mrwho3", "REDACTED_PASSWORD_PLACEHOLDER": "REDACTED_PASSWORD_PLACEHOLDER", "netEn": "1", "serverIp": "192.168.0.12", "serverMask": "255.255.255.0", "remark": "pptprule", "enable": "1"}
  ```
- **Keywords:** REDACTED_PASSWORD_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER, connsta
- **Notes:** The REDACTED_PASSWORD_PLACEHOLDER is enabled and could be directly exploited by attackers.
