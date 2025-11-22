---
firmware: Archer_C50
alert: BufferOverflow-http_cgi_main
---

### BufferOverflow-http_cgi_main

- **File/Directory Path:** `usr/bin/httpd`
- **Location:** `httpd:0x408c70 sym.http_cgi_main`
- **Risk Score:** 7.5
- **Confidence:** 8.0
- **Description:** A stack-based buffer overflow exists in `sym.http_cgi_main` due to unsafe use of `strcpy` at address 0x408c70. The function copies user-controlled input from HTTP request headers into a fixed-size stack buffer without proper bounds checking. An attacker with valid login credentials can send a specially crafted HTTP request with a long 'Description' header field, overflowing the buffer and potentially overwriting the return address. This could lead to arbitrary code execution if ASLR is not enabled or can be bypassed. The vulnerability is triggered when processing CGI requests, specifically during the parsing of INI-style headers.
- **Code Snippet:**
  ```
  0x00408c64      f882998f       lw t9, -sym.imp.strcpy(gp)
  0x00408c68      dc00a427       addiu a0, sp, 0xdc
  0x00408c6c      9d00a527       addiu a1, sp, 0x9d
  0x00408c70      09f82003       jalr t9
  ```
- **Keywords:** HTTP Request Headers, Description field, CGI parameters
- **Notes:** The buffer at sp+0xdc is on the stack, and the input from sp+0x9d is read from the HTTP stream via `http_stream_fgets`. Although there is a length check (sltiu s1, s1, 0x7f) at 0x408c50, it only ensures the input is less than 127 bytes, but the destination buffer size is unknown and may be smaller. Exploitation depends on the stack layout and mitigation bypasses. Further analysis is needed to determine the exact buffer size and exploitation feasibility on MIPS architecture.
