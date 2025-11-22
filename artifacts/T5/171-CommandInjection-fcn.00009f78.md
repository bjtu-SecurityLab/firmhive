---
firmware: _R7900-V1.0.1.26_10.0.23.chk.extracted
alert: CommandInjection-fcn.00009f78
---

### CommandInjection-fcn.00009f78

- **File/Directory Path:** `sbin/bd`
- **Location:** `bd:0x9f78 fcn.00009f78`
- **Risk Score:** 8.5
- **Confidence:** 9.0
- **Description:** A command injection vulnerability was discovered in the 'bd' binary, allowing attackers to execute arbitrary commands through the 'burncode' function. The attack chain is as follows: 1) The attacker, as a logged-in non-root user, runs the 'bd burncode' command and provides malicious parameters; 2) The parameters are passed via the command line to the fcn.00009f78 function; 3) This function uses sprintf to construct a command string and directly calls system() without adequately validating user input; 4) By inserting special characters (such as semicolons, backticks), the attacker can inject and execute arbitrary commands. Trigger condition: The attacker possesses valid login credentials and can execute the 'bd' command. Exploitation method: Construct malicious parameters such as '--mac "000000000000; malicious_command"' to achieve command injection.
- **Code Snippet:**
  ```
  Key code snippet from fcn.00009f78 decompilation:
  sym.imp.sprintf(iVar1, *0xa678, iVar6);
  sym.imp.system(iVar1);
  Where iVar6 originates from user-controlled input (via NVRAM or command line arguments). A similar pattern appears multiple times, using sprintf to build a command followed by a direct call to system().
  ```
- **Keywords:** burncode, system, sprintf, argv
- **Notes:** The vulnerability has been verified through decompiled code analysis. The attack chain is complete: from the user input point to the dangerous system() call. It is recommended to check the 'bd' permission settings and input validation mechanisms. Further validation of the exploitation conditions in the actual environment is needed, but based on code analysis, the vulnerability indeed exists and is exploitable.
