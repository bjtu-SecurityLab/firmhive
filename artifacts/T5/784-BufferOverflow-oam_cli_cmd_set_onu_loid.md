---
firmware: TD_W9970_V1_150831
alert: a-command-injection-vulnerability-exists-when-the-dhcpv6-client-processes-reply-
---

### a-command-injection-vulnerability-exists-when-the-dhcpv6-client-processes-reply-

- **File/Directory Path:** `usr/sbin/dhcp6c`
- **Location:** `dhcp6c:0x00405394 fcn.00405394 (client6_recv); dhcp6c:0x00413818,0x00414aec sym.client6_script`
- **Risk Score:** 10.0
- **Confidence:** 8.5
- **Description:** A command injection vulnerability exists when the DHCPv6 client processes reply messages. An attacker can control option data (such as the DNS server list) by sending a malicious DHCPv6 reply message. This data is parsed and passed to the client6_script function, and external scripts are executed via environment variables in the execve call. Specific behavior: When the device receives a DHCPv6 REPLY message, the client6_recv function calls dhcp6_get_options to parse the options, passing the tainted option list to client6_script; in client6_script, the tainted data is converted to strings and stored in an environment variable array, ultimately executing the script via execve, lacking filtering and validation of the option content. Trigger condition: An attacker sends a crafted DHCPv6 reply message (e.g., via a man-in-the-middle attack or by controlling the DHCPv6 server), where the option data contains malicious strings. Constraints: The code has basic error checking (such as option existence), but does not perform security processing on the option content; the in6addr2str function may limit the input format, but if the data is misused or the conversion function has defects, it might be bypassed. Potential attack: An attacker can exploit this vulnerability to inject commands, execute arbitrary code with root privileges, escalate privileges, or control the device. Exploitation method: Forge a DHCPv6 reply message to inject malicious environment variable values.
- **Code Snippet:**
  ```
Decompiled from fcn.00405394 (client6_recv):
0x00405538: bal sym.dhcp6_get_options  // Parse DHCPv6 options, tainted data stored to aiStack_2128
0x004064c4: bal sym.client6_script    // Call client6_script, passing tainted options
Decompiled from sym.client6_script:
0x00413818: sw a3, (arg_8ch)          // Tainted data stored from parameter to stack
0x0041383c: lw v0, 0x58(a3)           // Access tainted data offset 0x58 (DNS server list)
0x00413d78: bal sym.in6addr2str       // Convert address to string
0x00413d24: sw v0, (v1)               // Store string to environment variable array
0x00414aec: jalr t9                   // Call execve, using environment variables to execute script
  ```
- **Keywords:** command
- **Notes:** Auto-curated from results directory; verify in target environment.
