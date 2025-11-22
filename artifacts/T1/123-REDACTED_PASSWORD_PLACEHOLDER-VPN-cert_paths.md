---
firmware: R6200v2-V1.0.3.12_10.1.11
alert: REDACTED_PASSWORD_PLACEHOLDER-VPN-cert_paths
---

### REDACTED_PASSWORD_PLACEHOLDER-VPN-cert_paths

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `acos_service (strings output)`
- **Risk Score:** 7.5
- **Confidence:** 7.5
- **Description:** VPN configuration files and certificates are being copied from hardcoded paths (REDACTED_PASSWORD_PLACEHOLDER_ca/). This could expose sensitive certificate material if the file system is compromised.
- **Code Snippet:**
  ```
  Not available from strings output
  ```
- **Keywords:** /tmp/openvpn/ca.crt, REDACTED_PASSWORD_PLACEHOLDER_ca/, client.crt, client.REDACTED_PASSWORD_PLACEHOLDER
- **Notes:** certificate_handling
