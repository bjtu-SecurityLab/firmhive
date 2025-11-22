---
firmware: TD-W8980_V1_150514
alert: env_get-LINES_COLUMNS-getenv
---

### env_get-LINES_COLUMNS-getenv

- **File/Directory Path:** `bin/gzip`
- **Location:** `bin/gzip:0x4067ec (fcn.004067c4)`
- **Risk Score:** 7.5
- **Confidence:** 7.5
- **Description:** The function fcn.004067c4 calls the `getenv` function to retrieve the values of the environment variables 'LINES' and 'COLUMNS', then passes these values to the `atoi` function for conversion without adequate input validation. If the values of these environment variables are not valid integers, it may lead to undefined behavior.
- **Code Snippet:**
  ```
  getenv("LINES");
  getenv("COLUMNS");
  atoi(value);
  ```
- **Keywords:** sym.imp.getenv, fcn.004067c4, LINES, COLUMNS, atoi
- **Notes:** The specific impact of these security risks depends on the environment in which 'bin/gzip' operates. In environments where environment variables are strictly controlled, the risks may be lower. However, in less secure environments, these issues could potentially be exploited. It is recommended to implement stricter validation and filtering for the use of these environment variables.
