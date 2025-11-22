---
firmware: Archer_D2_V1_150921
alert: web-http_libjs-script_injection
---

### web-http_libjs-script_injection

- **File/Directory Path:** `REDACTED_PASSWORD_PLACEHOLDER.htm`
- **Location:** `lib.js`
- **Risk Score:** 8.0
- **Confidence:** 7.75
- **Description:** The file 'lib.js' contains multiple functions (tpAjax, io, cgi, exe) that handle HTTP requests and process user input without proper sanitization. These functions can execute scripts from the response text when 'bScript' is true, equivalent to 'eval' in risk. This behavior allows arbitrary script execution if the response text is malicious. The vulnerability is triggered when: 1) The response text contains malicious scripts, and 2) 'bScript' is set to true. This could lead to remote code execution or session hijacking if an attacker controls the response text (e.g., via server compromise or MITM attacks).
- **Code Snippet:**
  ```
  var REDACTED_SECRET_KEY_PLACEHOLDER = function() {
      if (xhr.readyState == 4) {
          if (s.bScript)
              $.script(xhr.responseText);
          if (s.success)
              s.success(s.bScript ? 0 : xhr.responseText);
      }
  };
  ```
- **Keywords:** tpAjax, io, cgi, exe, XMLHttpRequest, eval, exec, script, responseText, bScript
- **Notes:** The functions should be modified to sanitize the response text before execution. Additionally, the use of 'bScript' should be reviewed to ensure it is only enabled when absolutely necessary and with trusted sources. Further analysis of the server-side components generating the responses is recommended to ensure they are not vulnerable to injection attacks.
