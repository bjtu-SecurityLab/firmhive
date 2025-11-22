---
firmware: R8000-V1.0.4.4_1.1.42
alert: a-heap-buffer-overflow-vulnerability-was-identified-in-the-function-sym.dnsredir
---

### a-heap-buffer-overflow-vulnerability-was-identified-in-the-function-sym.dnsredir

- **File/Directory Path:** `lib/modules/2.6.36.4brcmarm+/kernel/lib/br_dns_hijack.ko`
- **Location:** `br_dns_hijack.ko:0x08000090 (sym.dnsRedirect_getQueryName) and br_dns_hijack.ko:0x0800028c (sym.dnsRedirect_isNeedRedirect calling sym.dnsRedirect_getQueryName)`
- **Risk Score:** 10.0
- **Confidence:** 8.5
- **Description:** A heap buffer overflow vulnerability was identified in the function sym.dnsRedirect_getQueryName within the br_dns_hijack.ko kernel module. The function copies DNS query name labels to a heap-allocated buffer of fixed size 32 bytes (allocated via kmem_cache_alloc in sym.dnsRedirect_isNeedRedirect) using memcpy, without verifying the output buffer size. While there is a check on the cumulative input length against a maximum of 0x5dc (1500 bytes), no bounds check is performed on the output buffer. This allows an attacker to craft a DNS packet with a query name exceeding 32 bytes, leading to heap buffer overflow.

**Trigger Conditions:**
- The attacker must be able to send DNS packets to the device (e.g., via local network access).
- The DNS packet must contain a query name longer than 32 bytes.
- The packet must pass through the hook functions (sym.br_local_in_hook or sym.br_preroute_hook) to reach sym.dnsRedirect_isNeedRedirect, which calls the vulnerable function.

**Potential Exploitation:**
- The overflow can corrupt adjacent kernel heap structures, potentially leading to arbitrary code execution in kernel context or denial of service.
- As the module runs in kernel space, successful exploitation could allow privilege escalation from a non-root user to root.

**Data Flow:**
1. Input: DNS packet from network (untrusted input).
2. Flow: Packet processed by hook functions → sym.br_dns_hijack_hook.clone.4 → sym.dnsRedirect_dnsHookFn → sym.dnsRedirect_isNeedRedirect → sym.dnsRedirect_getQueryName (vulnerable memcpy).
3. Dangerous Operation: memcpy writes beyond the allocated heap buffer.
- **Code Snippet:**
  ```
// From sym.dnsRedirect_getQueryName disassembly:
0x0800006c      0060d0e5       ldrb r6, [r0]           ; Load length byte from input
0x08000084      0620a0e1       mov r2, r6              ; Set size for memcpy to length byte
0x08000088      0400a0e1       mov r0, r4              ; Output buffer
0x0800008c      0810a0e1       mov r1, r8              ; Input buffer
0x08000090      feffffeb       bl memcpy               ; Copy without output buffer check

// From sym.dnsRedirect_isNeedRedirect:
0x08000228      08019fe5       ldr r0, [reloc.kmalloc_caches] ; Allocate buffer
0x0800022c      2010a0e3       mov r1, 0x20            ; Size 32 bytes
0x08000230      feffffeb       bl reloc.kmem_cache_alloc
0x0800028c      feffffeb       bl reloc.dnsRedirect_getQueryName ; Call vulnerable function
  ```
- **Keywords:** N/A
- **Notes:** Auto-curated from results directory; verify in target environment.
