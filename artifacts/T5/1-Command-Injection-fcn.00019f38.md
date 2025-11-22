---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: Command Injection-fcn.00019f38
---

### Command Injection-fcn.00019f38

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `acos_service:0x19f38 fcn.00019f38`
- **Risk Score:** 7.5
- **Confidence:** 7.0
- **Description:** A command injection vulnerability was discovered in function fcn.00019f38. When param_1 is not equal to 3 and is less than 3, the function retrieves data from the user input structure (offsets 4 and 8 of param_2), uses sprintf to embed it into a command string (address *0x1a1b8), and then executes it via system. The input is not filtered, allowing an attacker to inject arbitrary commands. Trigger condition: depends on the param_1 value and NVRAM check (acosNvramConfig_match), but as a logged-in user, an attacker can potentially control the trigger path via parameters. Exploitation method: manipulate input parameters to contain malicious commands (e.g., 'eth0; rm -rf /'), leading to privilege escalation or device destruction.
- **Code Snippet:**
  ```
  // fcn.00019f38 snippet
  else if (param_1 != 3 && param_1 + -3 < 0 == SBORROW4(param_1,3)) {
      iVar1 = puVar7 + -0x100;
      uVar5 = *(param_2 + 4);
      uVar2 = *(param_2 + 8);
      *(puVar7 + -0x108) = *(param_2 + 0xc);
      sym.imp.sprintf(iVar1, *0x1a1b8, uVar5, uVar2); // User input embedded into command
      sym.imp.printf(*0x1a1bc, iVar1);
      sym.imp.system(iVar1); // Execute command
      return 0;
  }
  ```
- **Keywords:** User input structure via param_2, NVRAM configuration via acosNvramConfig_match, Hardcoded string address: *0x1a1b8 (format string), Function symbols: fcn.00019f38, sym.imp.system, sym.imp.sprintf
- **Notes:** High exploitability, but requires more detailed verification of trigger conditions (e.g., specific impact of param_1 and NVRAM settings). The attack chain from input to command execution is complete, but confidence is slightly lower due to dependency conditions. Recommend analyzing the calling context to confirm attacker controllability.
