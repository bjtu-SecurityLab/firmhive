---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: buffer_overflow-acos_service-strcpy
---

### buffer_overflow-acos_service-strcpy

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `sbin/acos_service:fcn.0000a5bc:0xa82c, main:0xb5b4, fcn.0000ca64:0xcb48, fcn.0000ca64:0xcbe8, fcn.0000ca64:0xccc8, fcn.0000ca64:0xcce0`
- **Risk Score:** 8.0
- **Confidence:** 7.75
- **Description:** Multiple buffer overflow vulnerabilities were discovered in '/sbin/acos_service', primarily due to unsafe strcpy() calls. These vulnerabilities occur in functions fcn.0000a5bc, main, and fcn.0000ca64 when copying data from configuration sources (obtained via acosNvramConfig_get()) to local buffers without proper size validation. If attackers can manipulate these configuration data, they could potentially exploit these vulnerabilities.
- **Code Snippet:**
  ```
  N/A
  ```
- **Keywords:** strcpy, acosNvramConfig_get, fcn.0000a5bc, main, fcn.0000ca64
- **Notes:** Further analysis is required on the input validation mechanisms of the acosNvramConfig_get() and acosNvramConfig_set() functions to determine whether these configuration sources can be controlled via the web interface or other external inputs. It is recommended to examine other components that interact with these functions, particularly the web service components.
