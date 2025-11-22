---
firmware: _US_WH450AV1BR_WH450A_V1.0.0.18_EN.bin.extracted
alert: StackBufferOverflow-fcn.00400fb4
---

### StackBufferOverflow-fcn.00400fb4

- **File/Directory Path:** `usr/sbin/igs`
- **Location:** `igs:0x00400ff8 fcn.00400fb4`
- **Risk Score:** 8.0
- **Confidence:** 8.5
- **Description:** In the fcn.00400fb4 function of the 'igs' file, there exists a stack buffer overflow vulnerability. This function uses strcpy to copy user-provided command line arguments (such as <bridge>) into a fixed-size stack buffer (size 0x420 bytes), without performing any boundary checks. An attacker can trigger the overflow by executing the 'igs' command and providing an overly long argument (exceeding 0x420 bytes), overwriting the return address on the stack (located at offset 0x428), which may lead to arbitrary code execution. Trigger condition: The attacker possesses valid login credentials (non-root user) and executes a command such as 'igs add bridge <long_string>'. Potential attack methods include control flow hijacking to escalate privileges or execute malicious code. The relevant code logic involves command line argument parsing, data being passed to fcn.00400fb4, and the dangerous strcpy operation.
- **Code Snippet:**
  ```
  From Radare2 decompilation and assembly code:
  - In fcn.00400fb4:
    0x00400fe0: addiu a2, zero, 0x420       ; Buffer size
    0x00400ff4: lw a1, 0xc(s1)             ; Load input from argument
    0x00400ff8: lw t9, -sym.imp.strcpy(gp) ; Load strcpy address
    0x00401000: jalr t9                    ; Call strcpy, copy input to stack buffer
  Stack buffer auStack_430 starts at sp+0x18, return address stored at sp+0x440.
  ```
- **Keywords:** Command line argument <bridge>, Function fcn.00400fb4, Function sym.igs_cfg_request_send, NVRAM/Environment variable: None, File path: /sbin/igs, IPC socket: netlink socket (in sym.igs_cfg_request_send)
- **Notes:** Vulnerability verified based on code evidence, but exploitation not tested in a real environment; Offset calculation (0x428) comes from assembly analysis, further verification is recommended to confirm the precise overflow point; Related files include the main function (handles command line) and sym.igs_cfg_request_send (network operations); Future analysis directions: Test specific argument length to trigger crash, check the impact of ASLR and other mitigation measures.
