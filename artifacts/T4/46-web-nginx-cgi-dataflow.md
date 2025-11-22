---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: web-nginx-cgi-dataflow
---

### web-nginx-cgi-dataflow

- **File/Directory Path:** `etc_REDACTED_PASSWORD_PLACEHOLDER.conf`
- **Location:** `etc_ro/nginx/conf/nginx.conf -> fastcgi.conf -> 127.0.0.1:8188`
- **Risk Score:** 7.5
- **Confidence:** 8.25
- **Description:** Found complete data flow path from HTTP request to CGI handler: 1) Nginx receives HTTP requests at '/cgi-bin/luci/', 2) FastCGI configuration maps HTTP parameters (QUERY_STRING, REQUEST_URI, etc.) to CGI variables, 3) Requests are forwarded to CGI handler at 127.0.0.1:8188. The security risk depends on how the CGI handler processes these mapped parameters.
- **Code Snippet:**
  ```
  location /cgi-bin/luci/ {
      fastcgi_pass 127.0.0.1:8188;
      fastcgi_index index.php;
      include fastcgi.conf;
  }
  ```
- **Keywords:** /cgi-bin/luci/, fastcgi_pass, 127.0.0.1:8188, fastcgi_param, QUERY_STRING, REQUEST_URI
- **Notes:** Critical next step: Analyze the binary/script listening on 127.0.0.1:8188 to identify how it processes mapped HTTP parameters and whether these parameters are passed to dangerous functions.
