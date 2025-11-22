---
firmware: TD-W8980_V1_150514
alert: hardcoded-credentials-REDACTED_SECRET_KEY_PLACEHOLDER-PPPoE
---

### hardcoded-credentials-REDACTED_SECRET_KEY_PLACEHOLDER-PPPoE

- **File/Directory Path:** `etc/default_config.xml`
- **Location:** `default_config.xml (WANDevice instance=3 > REDACTED_SECRET_KEY_PLACEHOLDER instance=1 > REDACTED_SECRET_KEY_PLACEHOLDER instance=1)`
- **Risk Score:** 8.0
- **Confidence:** 8.0
- **Description:** Hardcoded PPPoE REDACTED_PASSWORD_PLACEHOLDER and REDACTED_PASSWORD_PLACEHOLDER were found in REDACTED_SECRET_KEY_PLACEHOLDER configuration. These credentials are used for 3G USB connections and could potentially be exploited for unauthorized network access. The REDACTED_PASSWORD_PLACEHOLDER type is PPPoE authentication credentials.
- **Code Snippet:**
  ```
  <REDACTED_PASSWORD_PLACEHOLDER val=WAP@CINGULAR.COM />
  <REDACTED_PASSWORD_PLACEHOLDER val=CINGULAR1 />
  ```
- **Keywords:** REDACTED_SECRET_KEY_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER, WAP@CINGULAR.COM, CINGULAR1
- **Notes:** These credentials appear to be default values for cellular network connections and may need to be modified in a production environment.
