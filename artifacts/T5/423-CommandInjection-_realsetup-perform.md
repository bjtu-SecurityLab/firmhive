---
firmware: DIR-895L_fw_revA_1-13_eu_multi_20170113
alert: CommandInjection-_realsetup-perform
---

### CommandInjection-_realsetup-perform

- **File/Directory Path:** `usr/lib/ipsec/_realsetup`
- **Location:** `File: _realsetup Function: perform (around lines 106-116) and startup section (around lines 200-210)`
- **Risk Score:** 7.5
- **Confidence:** 7.0
- **Description:** A command injection vulnerability via the 'IPSECinterfaces' environment variable was discovered in the '_realsetup' script. The issue originates from the 'perform' function using 'eval' to execute command strings, and the '$IPSECinterfaces' variable is not quoted during concatenation. When the script is run with 'start' or '_autostart' arguments, if 'IPSECinterfaces' contains shell metacharacters (such as ';', '&'), malicious commands will be executed. An attacker, as a non-root user, can exploit this by setting the environment variable and waiting for the script to run with root privileges (e.g., via a system service), achieving command execution and privilege escalation. Triggering the vulnerability requires script execution and controllable environment variables; the exploit chain is complete but relies on external conditions.
- **Code Snippet:**
  ```
  perform() {
      if $display
      then
          echo "    " "$*"
      fi
  
      if $execute
      then
          eval "$*"   # Dangerous: directly eval arguments
      fi
  }
  
  # Used in the startup section, $IPSECinterfaces is unquoted:
  perform ipsec _startklips \
          --info $info \
          --debug "\"$IPSECklipsdebug\"" \
          --omtu "\"$IPSECoverridemtu\"" \
          --fragicmp "\"$IPSECfragicmp\"" \
          --hidetos "\"$IPSEChidetos\"" \
          --log "\"$IPSECsyslog\"" \
          $IPSECinterfaces "||" \
      "{" rm -f $lock ";" exit 1 ";" "}"
  ```
- **Keywords:** IPSECinterfaces, IPSEC_setupflags, perform function
- **Notes:** The exploit chain is complete but relies on external conditions: the script must run with root privileges, and the attacker must be able to set environment variables (e.g., via login shell, service configuration, or file injection). It is recommended to further analyze how the script is invoked (e.g., via init script or service) and the source of environment variables (e.g., /etc/default/ipsec). Other variables like 'IPSEC_setupflags' may also affect behavior but do not directly cause command injection.
