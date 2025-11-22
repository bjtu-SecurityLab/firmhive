---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: command_injection-dhcp6s_helper-cmd_execution
---

### command_injection-dhcp6s_helper-cmd_execution

- **File/Directory Path:** `etc/scripts/dhcp6s_helper.php`
- **Location:** `dhcp6s_helper.php`
- **Risk Score:** 8.0
- **Confidence:** 8.0
- **Description:** Command injection vulnerabilities were found in the dhcp6s_helper.php file:  
1. The `cmd()` function directly concatenates external inputs (such as `$_GLOBALS["DST"]`, `$_GLOBALS["GATEWAY"]`, `$_GLOBALS["DEVNAM"]`) and executes system commands (e.g., `ip -6 route add`), posing a command injection risk.  
2. The `add_route()` and `remove_route()` functions execute `ip -6 route` commands via `cmd()`, incorporating unvalidated external inputs.  
3. The `main_entry()` function calls different functions based on the value of `$_GLOBALS["ACTION"]` without strict input validation.  

Potential impact: Attackers can inject malicious commands by manipulating these global variables, potentially leading to arbitrary command execution.
- **Code Snippet:**
  ```
  cmd("ip -6 route add ".$_GLOBALS["DST"]." via ".$_GLOBALS["GATEWAY"]." dev ".$_GLOBALS["DEVNAM"]." table DHCP\n");
  ```
- **Keywords:** cmd, msg, $_GLOBALS, DST, GATEWAY, DEVNAM, ACTION, add_route, remove_route, main_entry
- **Notes:** It is recommended to implement strict validation and filtering of inputs from `$_GLOBALS` to avoid direct command concatenation. Functions such as `escapeshellarg()` or similar should be used to escape inputs. Although this file is not a direct CGI script, it processes potentially web-interface-originated inputs and executes system commands, necessitating further tracing of input sources.
