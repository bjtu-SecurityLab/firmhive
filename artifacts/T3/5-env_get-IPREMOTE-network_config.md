---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: env_get-IPREMOTE-network_config
---

### env_get-IPREMOTE-network_config

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `./sbin/acos_service:fcn.REDACTED_PASSWORD_PLACEHOLDER:0x1523c [getenv]`
- **Risk Score:** 8.5
- **Confidence:** 8.75
- **Description:** The remote IP address is used for route configuration. Using it unsanitized directly in the route_add command may lead to arbitrary route injection.
- **Code Snippet:**
  ```
  getenv('IPREMOTE') used in route_add command
  ```
- **Keywords:** IPREMOTE, route_add, acosNvramConfig_set
- **Notes:** Multiple locations found: 0x1523c, 0x155e8, 0x156d4
