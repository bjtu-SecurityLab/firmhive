---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: cmd_injection-web-process_datamanage_usbeject
---

### cmd_injection-web-process_datamanage_usbeject

- **File/Directory Path:** `usr/bin/app_data_center`
- **Location:** `app_data_center:0xa730-0xa7c0 (process_datamanage_usbeject)`
- **Risk Score:** 9.5
- **Confidence:** 8.5
- **Description:** A high-risk command injection vulnerability was discovered in the process_datamanage_usbeject function of the app_data_center program. Attackers can execute arbitrary system commands by controlling the 'dev_name' parameter in HTTP requests. The vulnerability trigger path is: 1) Obtaining the unvalidated 'dev_name' parameter through get_querry_var; 2) Using snprintf to insert the parameter into the command string 'cfm post netctrl 51?op=3,string_info=%s'; 3) Directly invoking system to execute the constructed command.
- **Code Snippet:**
  ```
0x0000a730      fefcffeb       bl sym.get_querry_var
...
0x0000a7b0      74fbffeb       bl sym.imp.snprintf
0x0000a7c0      37fbffeb       bl sym.imp.system
  ```
- **Keywords:** command, system
- **Notes:** Auto-curated from results directory; verify in target environment.
