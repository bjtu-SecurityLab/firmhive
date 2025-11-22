---
firmware: R7500
alert: in-the-function-fcn.00009c88-there-exists-a-stack-buffer-overflow-vulnerability.
---

### in-the-function-fcn.00009c88-there-exists-a-stack-buffer-overflow-vulnerability.

- **File/Directory Path:** `bin/ookla`
- **Location:** `ookla:0x9c88 fcn.00009c88`
- **Risk Score:** 10.0
- **Confidence:** 8.5
- **Description:** In the function fcn.00009c88, there exists a stack buffer overflow vulnerability. The vulnerability is triggered during a memcpy operation, where the copy length is calculated as strlen(source buffer) - 0x11. If the string length of the source buffer (from param_1 + 0x820) is less than 0x11 (17 bytes), the length calculation underflows, becoming a very large unsigned value (for example, when strlen=0, the length becomes 0xFFFFFFFF), causing memcpy to copy excessive data to the target stack buffer. The target buffer is located low in the stack frame; an overflow can overwrite the saved return address (LR), allowing an attacker to control program flow. Trigger condition: An attacker provides param_1 input such that param_1 + 0x820 points to a short string (length < 17). param_1 originates from command-line argument processing (via getopt_long in fcn.00014680); a user can control the data by running the ookla binary and passing specially crafted arguments. Constraint: The source buffer length must be less than 17 bytes to trigger the underflow; the target buffer size is fixed, and an overflow can overwrite critical stack data. Potential attack method: An attacker constructs a short string input, triggers the overflow to overwrite the return address, achieving arbitrary code execution. Since the attacker possesses valid login credentials (non-root user), they can run the binary locally and escalate privileges. Related code logic: The vulnerability stems from a lack of bounds checking during input processing, directly using the strlen calculation result as the memcpy length.
- **Code Snippet:**
  ```
iVar1 = sym.imp.strlen(piVar7 + 0 + -0x400);
sym.imp.memcpy(piVar7 + 0 + -0x500, piVar7 + 0 + -0x400, iVar1 + -0x11);
  ```
- **Keywords:** command
- **Notes:** Auto-curated from results directory; verify in target environment.
