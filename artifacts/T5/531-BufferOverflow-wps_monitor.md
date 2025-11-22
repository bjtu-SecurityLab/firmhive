---
firmware: R7000
alert: BufferOverflow-wps_monitor
---

### BufferOverflow-wps_monitor

- **File/Directory Path:** `bin/wps_monitor`
- **Location:** `bin/wps_monitor:0xcc60 (fcn.0000c9d8 strcpy call), bin/wps_monitor:0xc658 (fcn.0000c5b0 sprintf call), bin/wps_monitor:0xdb10 (fcn.0000d4b0 strcpy call)`
- **Risk Score:** 7.5
- **Confidence:** 8.0
- **Description:** In the wps_monitor binary, multiple buffer overflow vulnerabilities were discovered, primarily due to the use of strcpy and sprintf functions lacking input validation and boundary checks. An attacker, as an authenticated non-root user, can inject overly long strings by controlling NVRAM variables (such as wps_config_command, wps_ifname, lan_hwaddr) or passing malicious parameters to the wps_monitor program. When the program processes these inputs, data is obtained via nvram_get and directly copied to fixed-size stack buffers (e.g., 100 bytes), causing stack buffer overflow. This can overwrite the return address or critical stack data, allowing the attacker to execute arbitrary code. Trigger conditions include: the attacker setting malicious NVRAM values (using nvram_set) or invoking wps_monitor with long parameters; the exploitation method involves crafting carefully designed input strings to control program flow and execute shellcode. The vulnerabilities exist in multiple functions, including fcn.0000c9d8, fcn.0000c5b0, and fcn.0000d4b0, forming a complete attack chain from input points to dangerous operations.
- **Code Snippet:**
  ```
  Decompiled code example from fcn.0000c9d8:
    sym.imp.strcpy(iVar13, puVar12);  // iVar13 points to stack buffer, puVar12 from param_2 or nvram_get
  Decompiled code example from fcn.0000c5b0:
    sym.imp.sprintf(iVar7, *0xc6ac, puVar6, param_3);  // iVar7 is stack buffer, puVar6 and param_3 contain tainted data
  Decompiled code example from fcn.0000d4b0:
    sym.imp.strcpy(fp, src);  // src from lan_ifnames or similar NVRAM variable
  ```
- **Keywords:** NVRAM variables: wps_config_command, wps_ifname, lan_hwaddr, wps_uuid, lan_ifnames, wan_ifnames, Function symbols: nvram_get, nvram_set, strcpy, sprintf, IPC/Network interface: Indirect control via NVRAM settings
- **Notes:** Vulnerabilities are based on decompiled code analysis; evidence shows external inputs flow into dangerous functions via NVRAM or parameters. Complete attack chain: input point (NVRAM variables) -> data flow (nvram_get) -> dangerous operation (strcpy/sprintf without boundary checks) -> potential exploitation (stack overflow). Further validation is needed for exact stack buffer sizes and exploit feasibility, but code patterns indicate high risk. Recommend subsequent testing for actual exploitation and checking other related files such as NVRAM configuration files or startup scripts. No command injection or format string vulnerabilities were found.
