---
firmware: _DIR-880
alert: command-injection-_updown.mast-functions
---

### command-injection-_updown.mast-functions

- **File/Directory Path:** `usr/lib/ipsec/_updown.mast`
- **Location:** `_updown.mast:addsource function (approx. line 400 in content), _updown.mast:changesource function (approx. line 430), _updown.mast:doipsecrule function (approx. line 500)`
- **Risk Score:** 8.0
- **Confidence:** 7.0
- **Description:** In multiple functions of the '_updown.mast' script, environment variables are directly inserted into shell command strings and executed via eval, lacking input validation and escaping, leading to command injection vulnerabilities. Specific manifestations: When IPsec events (such as connection establishment or disconnection) trigger script execution, functions like 'addsource', 'changesource', and 'doipsecrule' use environment variables (such as PLUTO_MY_SOURCEIP, PLUTO_INTERFACE, PLUTO_CONNECTION) to construct command strings, which are then executed via eval. If an attacker can control these environment variables and inject shell metacharacters (such as semicolons, backticks), arbitrary commands can be executed. Trigger conditions include: the IPsec daemon (Pluto) calls the script with root privileges, and environment variables are maliciously set (e.g., through spoofing or malicious connection configuration). Potential attack methods: inject commands such as '; rm -rf /' or '; /bin/sh' to obtain a root shell. Constraints: The attacker needs to be able to influence IPsec configuration or environment variables, but as a logged-in user, this might be achieved through application vulnerabilities or configuration errors.
- **Code Snippet:**
  ```
  addsource() {
      st=0
      if ! ip -o route get ${PLUTO_MY_SOURCEIP%/*} | grep -q ^local; then
          it="ip addr add ${PLUTO_MY_SOURCEIP%/*}/32 dev ${PLUTO_INTERFACE%:*}"
          oops="\`eval $it 2>&1\`"
          st=$?
          # ... error handling
      fi
      return $st
  }
  
  changesource() {
      st=0
      parms="$PLUTO_PEER_CLIENT"
      parms2="dev $PLUTO_INTERFACE"
      parms3="src ${PLUTO_MY_SOURCEIP%/*}"
      it="ip route $cmd $parms $parms2 $parms3"
      oops="\`eval $it 2>&1\`"
      # ... error handling
  }
  
  doipsecrule() {
      srcnet=$PLUTO_MY_CLIENT_NET/$PLUTO_MY_CLIENT_MASK
      dstnet=$PLUTO_PEER_CLIENT_NET/$PLUTO_PEER_CLIENT_MASK
      rulespec="--src $srcnet --dst $dstnet -m mark --mark 0/0x80000000 -j MARK --set-mark $nf_saref"
      if $use_comment ; then
          rulespec="$rulespec -m comment --comment '$PLUTO_CONNECTION'"
      fi
      it="iptables -t mangle -I NEW_IPSEC_CONN 1 $rulespec"
      oops="\`set +x; eval $it 2>&1\`"
      # ... error handling
  }
  ```
- **Keywords:** PLUTO_MY_SOURCEIP, PLUTO_INTERFACE, PLUTO_PEER_CLIENT, PLUTO_MY_CLIENT_NET, PLUTO_MY_CLIENT_MASK, PLUTO_PEER_CLIENT_NET, PLUTO_PEER_CLIENT_MASK, PLUTO_CONNECTION, /etc/sysconfig/pluto_updown, /etc/default/pluto_updown
- **Notes:** Evidence comes from the script content, showing direct use of environment variables in eval commands. Further verification is needed: 1) Whether the script runs with root privileges in a real environment (typically called by the Pluto daemon); 2) Whether environment variables can be controlled by an attacker (e.g., through IPsec configuration or network spoofing). Subsequent analysis of the Pluto daemon's permission mechanisms and configuration file access controls is recommended. Other related functions like 'updateresolvconf' might also have similar issues, but command injection is more directly exploitable.
