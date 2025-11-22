---
firmware: TL-MR3020_V1_150921
alert: env-MODULE_PATH-rc.wlan
---

### env-MODULE_PATH-rc.wlan

- **File/Directory Path:** `etc/rc.d/rc.wlan`
- **Location:** `./etc/rc.d/rc.wlan:80-91`
- **Risk Score:** 9.0
- **Confidence:** 8.5
- **Description:** env_get

Control module loading path. Malicious values may lead to arbitrary code execution. The variable is used to construct kernel module loading parameters (insmod command). Although the script checks for null values, there is no explicit input sanitization before using the values for module parameters.
- **Code Snippet:**
  ```
  MODULE_PATHHIDDENinsmodHIDDEN
  ```
- **Keywords:** insmod, MODULE_PATH
- **Notes:** Further verification is required to determine whether these environment variables are set through NVRAM or other configuration systems.
