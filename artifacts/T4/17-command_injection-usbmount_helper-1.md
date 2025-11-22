---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: command_injection-usbmount_helper-1
---

### command_injection-usbmount_helper-1

- **File/Directory Path:** `REDACTED_PASSWORD_PLACEHOLDER_helper.php`
- **Location:** `usbmount_helper.php:7-9`
- **Risk Score:** 9.0
- **Confidence:** 8.0
- **Description:** A high-risk command injection vulnerability was discovered in the 'REDACTED_PASSWORD_PLACEHOLDER_helper.php' file. Unvalidated external input variables $prefix and $pid are directly used to construct system commands (such as 'smartctl -H /dev/$dev' and 'sh REDACTED_PASSWORD_PLACEHOLDER_fsid.sh $prefix$pid'). Attackers can execute arbitrary commands by controlling these parameters. Further verification is required to determine whether these variables originate from HTTP requests.
- **Code Snippet:**
  ```
  $UID = toupper($prefix.$pid);
  if ($pid=="0") $dev = $prefix;
  else $dev = $prefix.$pid;
  setattr($base."/id", "get", "sh REDACTED_PASSWORD_PLACEHOLDER_fsid.sh ".$prefix.$pid);
  ```
- **Keywords:** $prefix, $pid, $dev, setattr, smartctl, usbmount_fsid.sh, toupper($prefix.$pid), XNODE_getpathbytarget
- **Notes:** Recommendations: 1) Validate all web interfaces calling this script 2) Check the sources of $prefix and $pid 3) Implement input validation and command escaping. Need to confirm whether these variables originate from HTTP requests to meet core user requirements.
