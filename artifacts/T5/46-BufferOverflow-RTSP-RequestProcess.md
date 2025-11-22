---
firmware: _DCS-935L_A1_FW_1.10.01_20161128_r4156.bin.extracted
alert: BufferOverflow-RTSP-RequestProcess
---

### BufferOverflow-RTSP-RequestProcess

- **File/Directory Path:** `usr/sbin/rtsp/rtspd`
- **Location:** `rtspd:0x40443c RequestProcess`
- **Risk Score:** 7.5
- **Confidence:** 8.0
- **Description:** In the RequestProcess function, when handling RTSP PLAY requests, the code uses sprintf to format a URI string from user-controlled inputs without proper bounds checking. Specifically, at address 0x40443c, sprintf is called with a destination buffer that may be fixed-size, and the inputs include scheme, host, port, and path from the RTSP request. An attacker can craft a long URI in a PLAY request to overflow the buffer, potentially leading to arbitrary code execution. The trigger condition is sending a malicious PLAY request with an overly long URI. Constraints include the buffer size not being verified, and the attack can be performed by an authenticated non-root user via the RTSP interface.
- **Code Snippet:**
  ```
  // From RequestProcess decompilation
  if (*(param_1 + 0x4c) < 1) {
      sprintf(iVar11, "%s://%s/%s", *(param_1 + 0x3c), *(param_1 + 0x48), *(param_1 + 0x50));
  } else {
      sprintf(iVar11, "%s://%s:%d/%s", *(param_1 + 0x3c), *(param_1 + 0x48), *(param_1 + 0x4c), *(param_1 + 0x50));
  }
  ```
- **Keywords:** RTSP PLAY method, URI parameters
- **Notes:** This vulnerability is highly exploitable due to the use of sprintf without bounds checking. The destination buffer iVar11 is likely on the stack, making it susceptible to stack-based buffer overflow. Further analysis is needed to determine the exact buffer size and exploitability, but the presence of this pattern in a network-facing function makes it a prime target. Recommend testing with long URIs to confirm overflow.
