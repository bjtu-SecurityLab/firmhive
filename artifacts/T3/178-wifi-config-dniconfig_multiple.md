---
firmware: R9000
alert: wifi-config-dniconfig_multiple
---

### wifi-config-dniconfig_multiple

- **File/Directory Path:** `etc/dni-wifi-config`
- **Location:** `etc/dni-wifi-config`
- **Risk Score:** 8.5
- **Confidence:** 8.5
- **Description:** Multiple "dniconfig get" values were read to obtain various WiFi configuration parameters (endis_wl_radio, wl_sectype, wps_status, etc.). These values directly controlled security settings and radio operations without proper validation, posing a high risk.
- **Keywords:** dniconfig get endis_wl_radio, dniconfig get wl_sectype, dniconfig get wps_status, dniconfig get endis_ssid_broadcast, dniconfig get wl_access_ctrl_on, dniconfig get wl_country
- **Notes:** configuration_load
