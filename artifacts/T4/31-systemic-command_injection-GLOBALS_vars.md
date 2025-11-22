---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: systemic-command_injection-GLOBALS_vars
---

### systemic-command_injection-GLOBALS_vars

- **File/Directory Path:** `etc/scripts/IP-WAIT.php`
- **Location:** `multiple files`
- **Risk Score:** 9.0
- **Confidence:** 8.25
- **Description:** Systemic command injection risk patterns were identified in multiple PHP scripts. Several scripts (IP-WAIT.php, dhcp6s_helper.php, stopchild.php) retrieve parameters through the $_GLOBALS superglobal variable and directly pass them to command execution functions (such as cmd() or system()). These global variables include: INF, PHYINF, DEVNAM, DNS, ME, DST, GATEWAY, CHILDUID, etc. If these global variables originate from unvalidated HTTP input, they will lead to severe command injection vulnerabilities. Recommendations: 1) Conduct comprehensive audits of all scripts using $_GLOBALS variables; 2) Verify whether the sources of these variables are controllable; 3) Implement strict input validation and command parameter escaping.
- **Code Snippet:**
  ```
  Multiple instances found:
  1. IP-WAIT.php: main_entry($_GLOBALS["INF"], $_GLOBALS["PHYINF"], $_GLOBALS["DEVNAM"], $_GLOBALS["DNS"], $_GLOBALS["ME"]);
  2. dhcp6s_helper.php: cmd("ip -6 route add ".$_GLOBALS["DST"]." via ".$_GLOBALS["GATEWAY"]." dev ".$_GLOBALS["DEVNAM"]." table DHCP\n");
  3. stopchild.php: cmd("service INET.".$_GLOBALS["CHILDUID"]." stop");
  ```
- **Keywords:** $_GLOBALS, cmd, system, INF, PHYINF, DEVNAM, DNS, ME, DST, GATEWAY, CHILDUID
- **Notes:** This is a systemic risk pattern involving multiple scripts and global variables. Priority should be given to investigating the source of the $_GLOBALS variable, particularly confirming whether it originates from HTTP request parameters. It is recommended to create a complete variable contamination path diagram.
