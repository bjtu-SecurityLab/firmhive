---
firmware: R7500
alert: Config-Injection-cmd_ftp
---

### Config-Injection-cmd_ftp

- **File/Directory Path:** `lib/dnicmd/cmd_ftp`
- **Location:** `cmd_ftp: functions 'scan_sharefoler_in_this_disk' and 'print_onesharefolder_config'`
- **Risk Score:** 7.5
- **Confidence:** 8.5
- **Description:** In the 'cmd_ftp' script, the share name is obtained from the NVRAM variable 'shared_usb_folder' and directly inserted into the proftpd configuration file, lacking input validation and escaping. Attackers can inject arbitrary configurations by setting a malicious share name (containing newline characters and proftpd configuration directives). For example, the share name can contain directives such as '</Directory><Limit ALL>AllowAll</Limit>', breaking the configuration file structure and adding unauthorized permission rules. Trigger condition: After the attacker modifies the NVRAM variable, the script regenerates the configuration file (such as through a service restart). Exploitation method: The attacker uses valid credentials to modify the share name via the web interface, causing proftpd to load malicious configurations, allowing unauthorized file access or privilege escalation.
- **Code Snippet:**
  ```
  In the 'scan_sharefoler_in_this_disk' function:
  sharename=\`echo "$sharefolder_item" | awk -F* '{print $1}' | sed 's/ //g'\`
  ...
  print_onesharefolder_config "$sharename" "$access" "$j"
  
  In the 'print_onesharefolder_config' function:
  cat <<EOF >>$proftpd_tmpfile
  	<Directory /tmp/ftpadmin/shares/$1>
  	AllowOverwrite    on
  		<Limit DIRS>
  			DenyAll
  EOF
  ...
  cat <<EOF >> $proftpd_tmpfile
  	</Directory>
  EOF
  ```
- **Keywords:** shared_usb_folder (NVRAM variable), /tmp/proftpd.conf (configuration file path), /bin/config (configuration tool)
- **Notes:** This vulnerability relies on the attacker being able to modify the NVRAM variable, possibly through the web interface. Further verification is needed to check if the web interface filters share name input. It is recommended to check how other components (such as the web server) handle share name input. The vulnerability may allow non-root users to gain unauthorized file access via FTP.
