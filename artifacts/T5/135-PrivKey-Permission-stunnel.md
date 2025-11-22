---
firmware: _DIR890LA1_FW111b02_20170519_beta01.bin.extracted
alert: PrivKey-Permission-stunnel
---

### PrivKey-Permission-stunnel

- **File/Directory Path:** `etc/stunnel.conf`
- **Location:** `stunnel.conf (implicit via configuration) and file permissions at /etc/stunnel.key`
- **Risk Score:** 9.0
- **Confidence:** 9.5
- **Description:** The stunnel.key private key file permissions are set to 777 (rwxrwxrwx), allowing any user (including non-root users) to read the file. An attacker as a logged-in non-root user can directly perform read operations (for example, using 'cat /etc/stunnel.key') to obtain the private key. After the private key is leaked, the attacker can use it to decrypt SSL/TLS communications, perform man-in-the-middle attacks, or impersonate the service identity. The trigger condition is simple: the attacker only needs valid login credentials and file read permissions. No other vulnerabilities or complex steps are required to complete the exploitation. Constraint conditions: no boundary checks or access controls, the file is globally readable. Potential attack methods include passive eavesdropping or active hijacking of encrypted sessions.
- **Code Snippet:**
  ```
  key = /etc/stunnel.key
  # File permissions: -rwxrwxrwx 1 user user 1679 May  19  2017 stunnel.key
  ```
- **Keywords:** /etc/stunnel.key, /etc/stunnel_cert.pem
- **Notes:** This finding is based on direct evidence: the file permissions are 777 and the file exists. It is recommended to immediately fix the file permissions (for example, set to 600) and review other related files (such as stunnel_cert.pem). Although stunnel runs with root privileges (setuid=0) and debug mode enabled (debug=7) may increase the risk, there is currently a lack of complete attack chain evidence. Subsequent analysis should check if the stunnel binary has vulnerabilities and whether the log file (/var/log/stunnel.log) permissions are inappropriate.
