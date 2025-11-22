---
firmware: R8000-V1.0.4.4_1.1.42
alert: buffer-overflow-taskset-mask-parsing
---

### buffer-overflow-taskset-mask-parsing

- **File/Directory Path:** `usr/bin/taskset`
- **Location:** `taskset:0x00008b78 (function fcn.00008b78, in the bit-setting loops for mask and CPU list parsing)`
- **Risk Score:** 7.5
- **Confidence:** 8.0
- **Description:** The taskset binary contains a buffer overflow vulnerability in the CPU affinity mask parsing logic. When processing user-provided CPU mask strings or CPU list values, the code fails to validate bounds before writing to a fixed-size stack buffer (128 bytes for the affinity mask). Specifically:
- In mask parsing (without -c option), a mask string with length >=257 characters causes the bit index (uVar5) to exceed the buffer size, leading to out-of-bounds writes starting at offset -92 from the stack frame base.
- In CPU list parsing (with -c option), a CPU index >=1024 directly results in out-of-bounds writes, as the bit index (uVar7) is used without checks.
The out-of-bounds write uses an OR operation with a controlled bit shift (1 << (index & 0x1f)), allowing partial control over the written value. This can overwrite saved registers or the return address on the stack, potentially leading to arbitrary code execution or denial of service. An attacker with valid login credentials can trigger this by running taskset with a maliciously long mask string or high CPU index, e.g., `taskset $(python -c 'print("0"*257)') /bin/sh` or `taskset -c 2000 /bin/sh`.
- **Code Snippet:**
  ```
  Relevant code from decompilation:
  // Mask parsing path (iVar11 == 0)
  puVar12 = param_2[iVar2]; // user input string
  iVar2 = sym.imp.strlen(puVar12);
  // ... loop processing each character
  uVar1 = *puVar9;
  uVar15 = uVar1 - 0x30;
  // ... process character
  if ((uVar15 & 1) != 0) {
      iVar2 = iVar19 + (uVar5 >> 5) * 4;
      *(iVar2 + -0xdc) = *(iVar2 + -0xdc) | iVar14 << (uVar5 & 0x1f); // out-of-bounds write if uVar5 >> 5 >= 32
  }
  // Similar for other bits
  
  // CPU list parsing path (iVar11 != 0)
  iVar16 = sym.imp.sscanf(iVar2, *0x923c, iVar19 + -4); // parse integer
  uVar13 = *(iVar19 + -4);
  // ... range processing
  iVar16 = iVar19 + (uVar7 >> 5) * 4;
  *(iVar16 + -0xdc) = *(iVar16 + -0xdc) | 1 << (uVar7 & 0x1f); // out-of-bounds write if uVar7 >= 1024
  ```
- **Keywords:** argv[1] (CPU mask string), argv[2] (CPU list string with -c option)
- **Notes:** The vulnerability is theoretically exploitable for code execution, but full exploitation depends on stack layout predictability and the ability to control the written value precisely (limited to setting bits). Further analysis is needed to determine the exact offset of the return address and develop a reliable exploit. The binary has no special privileges (e.g., SUID), so exploitation would yield user-level code execution. Recommended next steps: analyze stack frame layout using r2, test crash scenarios, and explore combined writes for better control.
