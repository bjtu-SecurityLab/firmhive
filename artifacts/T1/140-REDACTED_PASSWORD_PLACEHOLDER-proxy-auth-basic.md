---
firmware: R7000
alert: REDACTED_PASSWORD_PLACEHOLDER-proxy-auth-basic
---

### REDACTED_PASSWORD_PLACEHOLDER-proxy-auth-basic

- **File/Directory Path:** `opt/xagent/xagent`
- **Location:** `opt/xagent/xagent:http_helper.c (HIDDEN)`
- **Risk Score:** 8.0
- **Confidence:** 6.75
- **Description:** Hardcoded proxy authentication information was detected, in the format 'Proxy-Authorization: Basic %s', where %s may represent a Base64-encoded combination of REDACTED_PASSWORD_PLACEHOLDER and REDACTED_PASSWORD_PLACEHOLDER. This type of information is typically used for HTTP proxy authentication, and if leaked, could lead to unauthorized access to the proxy server. Further verification is required to determine whether this is actual hardcoded credentials or a format string. If it is a format string, real credentials might be populated during runtime.
- **Code Snippet:**
  ```
  Proxy-Authorization: Basic %s
  ```
- **Keywords:** Proxy-Authorization, Basic, http_helper.c
- **Notes:** Further verification is needed to determine whether this is an actual hardcoded REDACTED_PASSWORD_PLACEHOLDER or a format string. If it is a format string, real credentials might be populated during runtime.
