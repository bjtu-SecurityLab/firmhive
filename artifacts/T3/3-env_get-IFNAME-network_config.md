---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: env_get-IFNAME-network_config
---

### env_get-IFNAME-network_config

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `./sbin/acos_service:fcn.REDACTED_PASSWORD_PLACEHOLDER:0x1523c [getenv]`
- **Risk Score:** 7.5
- **Confidence:** 8.0
- **Description:** The network interface name is used for configuration and file operations. It is not properly sanitized before being used in file paths and system commands. An attacker-controlled IFNAME could lead to arbitrary file access or command execution.
- **Code Snippet:**
  ```
  getenv('IFNAME') used in file operations and command execution
  ```
- **Keywords:** IFNAME, strcat, fopen, ifconfig, acosNvramConfig_set
- **Notes:** Multiple locations found: 0x1523c, 0x152b4, 0x15310, 0x157ac, 0x158d8
