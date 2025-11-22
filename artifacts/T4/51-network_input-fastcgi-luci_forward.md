---
firmware: _US_AC9V1.0BR_V15.03.05.14_multi_TD01.bin.extracted
alert: network_input-fastcgi-luci_forward
---

### network_input-fastcgi-luci_forward

- **File/Directory Path:** `etc_ro/nginx/conf/nginx.conf`
- **Location:** `nginx.conf:25-28, fastcgi.conf:1-20`
- **Risk Score:** 7.0
- **Confidence:** 8.0
- **Description:** In the nginx.conf file, the path /cgi-bin/luci/ is configured to forward via FastCGI to 127.0.0.1:8188, with multiple HTTP parameters (QUERY_STRING, REQUEST_METHOD, REQUEST_URI, etc.) being passed to the backend program through the fastcgi.conf file. These parameters may be passed to dangerous functions, posing potential security risks.
- **Code Snippet:**
  ```
  location /cgi-bin/luci/ {
      fastcgi_pass 127.0.0.1:8188;
      fastcgi_index index.php;
      include fastcgi.conf;
  }
  ```
- **Keywords:** fastcgi_pass, fastcgi_param, QUERY_STRING, REQUEST_METHOD, REQUEST_URI, 127.0.0.1:8188, /cgi-bin/luci/
- **Notes:** It is recommended to proceed with analyzing the FastCGI program listening on port 8188 to verify whether these HTTP parameters are being passed to dangerous functions such as system, exec, or strcpy.
