---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: env_get-IPLOCAL-network_config
---

### env_get-IPLOCAL-network_config

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `./sbin/acos_service:fcn.REDACTED_PASSWORD_PLACEHOLDER:0x1523c [getenv]`
- **Risk Score:** 8.0
- **Confidence:** 8.25
- **Description:** The local IP address is used for network configuration. Using it directly in route_add without sanitization may lead to network redirection or man-in-the-middle attacks.
- **Code Snippet:**
  ```
  getenv('IPLOCAL') used in route_add command
  ```
- **Keywords:** IPLOCAL, route_add, strcmp, 10.64.64.64
- **Notes:** Multiple locations found: 0x1523c, 0x15480, 0x15598
