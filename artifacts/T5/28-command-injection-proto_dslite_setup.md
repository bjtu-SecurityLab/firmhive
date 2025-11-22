---
firmware: _C2600-US-up-ver1-1-8-P1_20170306-rel33259_.bin.extracted
alert: command-injection-proto_dslite_setup
---

### command-injection-proto_dslite_setup

- **File/Directory Path:** `lib/netifd/proto/dslite.sh`
- **Location:** `dslite.sh:18-22 proto_dslite_setup`
- **Risk Score:** 8.5
- **Confidence:** 8.0
- **Description:** A command injection vulnerability exists in the 'resolveip' command call. When the 'AFTR_name' variable contains malicious content (such as semicolon-separated commands), it will be interpreted and executed by the shell in the command substitution '$(resolveip -6 -t 5 "$server")'. Trigger condition: An attacker sets a malicious 'AFTR_name' value through an accessible interface (such as a network configuration API), which is triggered when the script executes tunnel setup. Potential exploitation method: Injecting commands such as '; malicious_command' can lead to arbitrary code execution with root privileges, achieving privilege escalation. Constraints: The script relies on the external 'resolveip' command and does not validate or escape the input.
- **Code Snippet:**
  ```
      local server
      json_get_var server AFTR_name
      [ -n "$server" ] && [ -z "$peeraddr" ] && {
          for ip6 in $(resolveip -6 -t 5 "$server"); do
              # ( proto_add_host_dependency "$cfg" "$ip6" )
              peeraddr="$ip6"
          done
      }
  ```
- **Keywords:** AFTR_name, resolveip
- **Notes:** Assumes the script runs with root privileges (common for network configuration scripts). The attack chain is complete: input point ('AFTR_name') → data flow (unfiltered direct use in command) → dangerous operation (arbitrary command execution). It is recommended to validate the behavior of the 'resolveip' command and the script's calling context. Associated files may include network configuration files and IPC mechanisms. Subsequent analysis should check the input source of 'AFTR_name' (such as UCI configuration or web interface) to confirm exploitability.
