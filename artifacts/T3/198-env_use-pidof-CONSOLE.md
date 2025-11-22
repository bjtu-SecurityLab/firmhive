---
firmware: TD-W8980_V1_150514
alert: env_use-pidof-CONSOLE
---

### env_use-pidof-CONSOLE

- **File/Directory Path:** `bin/pidof`
- **Location:** `bin/pidof:0x4307b8`
- **Risk Score:** 7.0
- **Confidence:** 7.0
- **Description:** In the bin/pidof file, the CONSOLE environment variable is used as a file path in the open64() call at address 0x4307b8. There is a potential path injection risk, as an attacker who can control these environment variables may gain arbitrary file access.
- **Code Snippet:**
  ```
  open64(getenv("CONSOLE"), O_RDONLY)
  ```
- **Keywords:** CONSOLE, open64, 0x4307b8
- **Notes:** It is recommended to further verify the usage of environment variables in the open64() call to confirm whether there is a risk of path injection.
