---
firmware: R7000
alert: network-MAC-download
---

### network-MAC-download

- **File/Directory Path:** `bin/startcircle`
- **Location:** `startcircle:6-11`
- **Risk Score:** 8.0
- **Confidence:** 9.0
- **Description:** MAC address is downloaded from remote server (meetcircle.co) with fallback to hardcoded value, creating potential MITM risk. The MAC address is obtained via wget without transport security and used for network configuration.
- **Keywords:** MAC, ROUTERMAC, wget, meetcircle.co
- **Notes:** network_input
