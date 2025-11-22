---
firmware: R8000-V1.0.4.4_1.1.42
alert: hardcoded-credentials-startcircle-mac
---

### hardcoded-credentials-startcircle-mac

- **File/Directory Path:** `bin/startcircle`
- **Location:** `bin/startcircle`
- **Risk Score:** 7.0
- **Confidence:** 8.5
- **Description:** A hardcoded MAC address '8C:E2:DA:F0:FD:E7' was found in the file 'bin/startcircle', serving as a default value when unable to retrieve a MAC address from the server. This hardcoding may pose a risk of device identity spoofing.
- **Code Snippet:**
  ```
  HIDDEN，HIDDENMACHIDDEN
  ```
- **Keywords:** MAC, 8C:E2:DA:F0:FD:E7
- **Notes:** It is recommended to verify the usage scenarios and security implications of hardcoded MAC addresses.
