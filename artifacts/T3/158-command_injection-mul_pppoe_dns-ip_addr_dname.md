---
firmware: R9000
alert: command_injection-mul_pppoe_dns-ip_addr_dname
---

### command_injection-mul_pppoe_dns-ip_addr_dname

- **File/Directory Path:** `sbin/mul_pppoe_dns`
- **Location:** `sbin/mul_pppoe_dns`
- **Risk Score:** 7.0
- **Confidence:** 7.0
- **Description:** In the file 'sbin/mul_pppoe_dns', access to the command-line parameters '$ip_addr' and '$dname' was detected. These parameters are directly used in routing commands and file operations without adequate validation, posing risks of command injection and file path injection.
- **Code Snippet:**
  ```
  Not provided in the input
  ```
- **Keywords:** mulpppoe_ifname, RECORD_FILE, PPP1_DNS_FILE, ip_addr, dname
- **Notes:** It is recommended to further verify the source of command-line parameter inputs and the runtime environment of the script to ensure security.
