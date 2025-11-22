---
firmware: R7000
alert: a-command-injection-vulnerability-was-identified-in-the-minidlna.exe-binary-when
---

### a-command-injection-vulnerability-was-identified-in-the-minidlna.exe-binary-when

- **File/Directory Path:** `usr/sbin/minidlna.exe`
- **Location:** `minidlna.exe:0xc6c4 (fcn.0000c028 case 6)`
- **Risk Score:** 10.0
- **Confidence:** 8.5
- **Description:** A command injection vulnerability was identified in the minidlna.exe binary when the `-R` (force rescan) option is used. The vulnerability occurs in the main function where user-controlled data from command-line arguments or configuration files is incorporated into a `system` call without proper sanitization. Specifically, the code constructs a command string using `snprintf` with the format `rm -rf %s/files.db %s/art_cache` and passes it to `system`. If an attacker can control the paths (e.g., through a malicious configuration file or command-line argument), they can inject arbitrary commands. This could lead to remote code execution if the minidlna process is running with elevated privileges or if the attacker has write access to configuration files.

- **Trigger Condition**: The vulnerability is triggered when the `-R` option is passed to minidlna, typically during a forced rescan of the media library.
- **Constraints and Boundary Checks**: The `snprintf` uses a buffer of 4096 bytes, but no validation is performed on the path inputs, allowing command injection if paths contain shell metacharacters.
- **Potential Exploitation**: An attacker with the ability to modify command-line arguments or configuration files (e.g., via a compromised script or weak file permissions) can inject commands to execute arbitrary code.
- **Code Logic**: The dangerous code is located in the main function's command-line parsing switch statement, case 6, where `system` is called with a user-influenced string.
- **Code Snippet:**
  ```
case 6:
    *(puVar28 + -0x21b4) = *(puVar28 + -0x2194);
    sym.imp.snprintf(puVar28 + -0x1184, 0x1000, *0xd06c);  // Format: "rm -rf %s/files.db %s/art_cache"
    sym.imp.system(puVar28 + -0x1184);  // Command injection here
    break;
  ```
- **Keywords:** command, system
- **Notes:** Auto-curated from results directory; verify in target environment.
