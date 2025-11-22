---
firmware: FH1206
alert: Command-Injection-igd_osl_nat_config
---

### Command-Injection-igd_osl_nat_config

- **File/Directory Path:** `usr/sbin/igd`
- **Location:** `igd:0x00402084 sym.igd_osl_nat_config`
- **Risk Score:** 9.0
- **Confidence:** 8.5
- **Description:** A command injection exists in the UPnP IGD port-mapping path. The user-controlled parameter `NewInternalClient` is embedded into a shell command using `sprintf` without sanitization and executed via `_eval`. An attacker on the local network can craft a malicious AddPortMapping request to execute arbitrary commands with the privileges of the `igd` process (typically root).
- **Code Snippet:**
  ```
  // Build command with unsanitized input
  ( *(iVar + -0x7f78) )(pcVar6, *(iVar + -0x7fe0) + 0x591c, param_1, *(param_2 + 0x10), *(param_2 + 0x1a), *(param_2 + 0x2c));
  // Append user-controlled data (NewInternalClient)
  (*pcVar12)(pcVar6, param_2);
  // Execute via _eval
  ( *(iVar + -0x7f20) )(apcStack_19c, *(iVar + -0x7fe0) + 0x5968, 0, 0);
  ```
- **Keywords:** UPnP, AddPortMapping, NewInternalClient, sprintf, _eval
- **Notes:** Verified as High risk in automated analysis. Attack surface is often enabled by default. Confirm UPnP exposure and authentication in deployment; consider disabling UPnP or enforcing strict input validation and command construction.
