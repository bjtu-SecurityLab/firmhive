---
firmware: R9000
alert: envvar-wl_psk_phrase
---

### envvar-wl_psk_phrase

- **File/Directory Path:** `sbin/update-wifi`
- **Location:** `sbin/update-wifi:441,449-453`
- **Risk Score:** 9.0
- **Confidence:** 8.5
- **Description:** Accessing the WiFi REDACTED_PASSWORD_PLACEHOLDER environment variable 'wl_psk_phrase' in the '/sbin/update-wifi' script, directly processing and using it for configuration, poses a high risk.
- **Code Snippet:**
  ```
  HIDDEN
  ```
- **Keywords:** wl_psk_phrase
- **Notes:** WiFi passwords are directly processed and used for configuration, high risk
