---
firmware: DIR-885L_fw_revA_1-13_eu_multi_20170119
alert: buffer-overflow-tsa-strncpy
---

### buffer-overflow-tsa-strncpy

- **File/Directory Path:** `mydlink/tsa`
- **Location:** `mydlink/tsa:0x94b4 (strncpyHIDDEN)`
- **Risk Score:** 8.0
- **Confidence:** 7.5
- **Description:** Multiple buffer overflow risks were detected in file 'mydlink/tsa'. Critical call points: strncpy(puVar15 + -0x4d,*0x9cfc,0x11) and strncpy(puVar15 + -0xaf,*0x9d30,0x20). Trigger condition: when HTTP parameter length exceeds target buffer size. Security impact: may lead to stack overflow and arbitrary code execution.
- **Code Snippet:**
  ```
  sym.imp.strncpy(puVar15 + -0x4d,*0x9cfc,0x11);
  ```
- **Keywords:** strncpy, puVar15, *0x9cfc, *0x9d30, buffer overflow
- **Notes:** All strncpy call sites should verify that the buffer size is sufficient.
