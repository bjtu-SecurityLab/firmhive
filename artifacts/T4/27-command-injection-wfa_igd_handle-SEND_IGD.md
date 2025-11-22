---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: command-injection-wfa_igd_handle-SEND_IGD
---

### command-injection-wfa_igd_handle-SEND_IGD

- **File/Directory Path:** `etc/scripts/wfa_igd_handle.php`
- **Location:** `wfa_igd_handle.php:187-202`
- **Risk Score:** 8.5
- **Confidence:** 8.0
- **Description:** A command injection vulnerability was identified in the `SEND_IGD` mode. `$wan_ip` is obtained via `query("REDACTED_PASSWORD_PLACEHOLDER")`, and `$DS_PORT` may originate from user input. These variables are concatenated into the `upnpc` command and executed through `exe_ouside_cmd`. The critical code location is at `wfa_igd_handle.php:187-202`.
- **Code Snippet:**
  ```
  function exe_ouside_cmd($cmd)
  {
      $ext_node="REDACTED_PASSWORD_PLACEHOLDER_node";
      setattr($ext_node, "get", $cmd);
      get("x", $ext_node);
      del($ext_node);
  }
  ```
- **Keywords:** exe_ouside_cmd, SEND_IGD, $wan_ip, $DS_PORT, upnpc, query, REDACTED_PASSWORD_PLACEHOLDER, REDACTED_PASSWORD_PLACEHOLDER_default_port
- **Notes:** Further analysis is required to determine the specific source of `$DS_PORT` to confirm whether it originates directly from HTTP request parameters. It is recommended to review all code paths that invoke `exe_ouside_cmd`.
