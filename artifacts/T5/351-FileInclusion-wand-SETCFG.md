---
firmware: DIR-868L_fw_revA_1-12_eu_multi_20170316
alert: FileInclusion-wand-SETCFG
---

### FileInclusion-wand-SETCFG

- **File/Directory Path:** `htdocs/webinc/wand.php`
- **Location:** `wand.php (in dophp call of SETCFG branch)`
- **Risk Score:** 6.0
- **Confidence:** 6.5
- **Description:** In the SETCFG branch, $svc is used to construct file paths and load PHP files via dophp. If $svc is user-controllable and contains path traversal sequences (such as '../'), it may lead to arbitrary file inclusion, thereby executing arbitrary code. For example, setting $svc to '../../../tmp/malicious' may include and execute /tmp/malicious.php. Trigger condition: user calls ACTION=SETCFG and provides malicious $PREFIX/postxml/module data. Potential exploitation method: achieve code execution by including malicious files.
- **Code Snippet:**
  ```
  $file = "/htdocs/phplib/setcfg/".$svc.".php";
  if (isfile($file)==1) dophp("load", $file);
  ```
- **Keywords:** $svc, $file, $PREFIX, /htdocs/phplib/setcfg/
- **Notes:** Need to confirm whether $svc is user-controllable and whether the dophp function executes the loaded file. It is recommended to check input validation and file path restrictions. Related functions such as query() and set() may involve data storage interactions.
