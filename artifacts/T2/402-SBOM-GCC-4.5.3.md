---
firmware: R6400v2-V1.0.2.46_1.0.36
alert: SBOM-GCC-4.5.3
---

### SBOM-GCC-4.5.3

- **File/Directory Path:** `opt/rcagent/cgi_processor`
- **Location:** `cgi_processor: (version string) 'GCC: (Buildroot 2012.02) 4.5.3'`
- **Risk Score:** 7.0
- **Confidence:** 7.5
- **Description:** GCC component information extracted from the cgi_processor executable. Version 4.5.3 contains known critical vulnerabilities:
- CVE-2011-1078: The gcc-4.5.3 compiler in Buildroot 2012.02 has a vulnerability that allows attackers to cause a denial of service (crash) via a crafted source file.
- **Code Snippet:**
  ```
  Evidence string: 'GCC: (Buildroot 2012.02) 4.5.3'
  ```
- **Keywords:** GCC: (Buildroot 2012.02) 4.5.3
- **Notes:** Version information is clear, known high-risk vulnerabilities exist.
