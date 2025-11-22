---
firmware: R6400v2-V1.0.2.46_1.0.36
alert: env_get-X509_verify_cert-getenv
---

### env_get-X509_verify_cert-getenv

- **File/Directory Path:** `lib/libcrypto.so.1.0.0`
- **Location:** `libcrypto.so.1.0.0:0xfa388 (X509_verify_cert)`
- **Risk Score:** 8.0
- **Confidence:** 7.5
- **Description:** An `env_get` call was found in the `X509_verify_cert` function, likely used to retrieve the 'OPENSSL_ALLOW_PROXY_CERTS' environment variable. Security risk: This variable may influence certificate verification logic, potentially allowing attackers to bypass certificate validation.
- **Code Snippet:**
  ```
  Not provided in original data
  ```
- **Keywords:** X509_verify_cert, getenv, OPENSSL_ALLOW_PROXY_CERTS
- **Notes:** Critical configurations that directly affect certificate verification
