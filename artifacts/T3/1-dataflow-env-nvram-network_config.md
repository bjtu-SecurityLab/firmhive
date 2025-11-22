---
firmware: _AC1450-V1.0.0.36_10.0.17.chk.extracted
alert: dataflow-env-nvram-network_config
---

### dataflow-env-nvram-network_config

- **File/Directory Path:** `sbin/acos_service`
- **Location:** `HIDDEN: ./sbin/acos_service HIDDEN ./sbin/bd`
- **Risk Score:** 8.0
- **Confidence:** 7.5
- **Description:** The data flow correlation between environment variables (IFNAME/IPREMOTE) and NVRAM configuration (acosNvramConfig_set). Environment variable values may be written to NVRAM through the acosNvramConfig_set function, creating a potential attack vector. Attackers could influence NVRAM configuration by manipulating environment variables, thereby affecting system behavior.
- **Code Snippet:**
  ```
  HIDDEN -> acosNvramConfig_set -> NVRAM -> HIDDEN
  ```
- **Keywords:** IFNAME, IPREMOTE, acosNvramConfig_set, route_add, ifconfig
- **Notes:** Further verification is required to confirm whether the environment variables have indeed been written to NVRAM and the specific path where they are written.
