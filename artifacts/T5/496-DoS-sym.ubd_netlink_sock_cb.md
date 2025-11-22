---
firmware: FH1206
alert: Command-Injection-formexeCommand
---

### Command-Injection-formexeCommand

- **File/Directory Path:** `bin/httpd`
- **Location:** `httpd: sym.formexeCommand (0x0046eefc)`
- **Risk Score:** 9.0
- **Confidence:** 9.0
- **Description:** A command injection vulnerability exists in the HTTP form handler `formexeCommand`. User input from the `cmdinput` parameter is retrieved via `websGetVar` and directly passed into a command executed by `doSystemCmd` without sanitization. An authenticated attacker can inject OS commands (e.g., `; id`) to achieve code execution (often as root on embedded systems).
- **Code Snippet:**
  ```
  // Retrieve input
  uVar1 = (**(iVar4 + -0x78cc))(*&uStackX_0, *(iVar4 + -0x7fd8) - 0x3bc, *(iVar4 + -0x7fd8) - 0x3b0);
  (**(iVar4 + -0x71b0))(auStack_2308, uVar1);
  // Build/execute command without sanitization
  (**(iVar4 + -0x7860))(*(iVar4 + -0x7fd8) - 0x388, auStack_2308);
  (**(iVar4 + -0x7508))(auStack_2308);
  ```
- **Keywords:** cmdinput, websGetVar, doSystemCmd, httpd, form handler
- **Notes:** The handler is registered during HTTP server initialization (e.g., `formDefineTendDa`), making it reachable via normal web requests. Verify the runtime privileges of `httpd` to assess impact (often root). A simple PoC is to submit `cmdinput="; id"` to execute `id` on the device.
