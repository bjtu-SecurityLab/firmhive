---
firmware: _US_AC18V1.0BR_V15.03.05.05_multi_TD01.bin.extracted
alert: Command-Injection-spawn-fcgi-f-option
---

### Command-Injection-spawn-fcgi-f-option

- **File/Directory Path:** `usr/bin/spawn-fcgi`
- **Location:** `spawn-fcgi:0x95dc-0x9648 sym.fcgi_spawn_connection`
- **Risk Score:** 7.0
- **Confidence:** 9.0
- **Description:** A command injection vulnerability exists in the 'spawn-fcgi' binary when handling the -f option without providing positional arguments. The vulnerability arises in the fcgi_spawn_connection function, where user-controlled input from the -f option is concatenated into a shell command without proper sanitization. When no FastCGI application arguments are provided (i.e., no positional arguments after --), the program constructs a command string using strcat with the value from -f and executes it via /bin/sh -c. An attacker can exploit this by injecting shell metacharacters (e.g., ;, &, |) in the -f argument to execute arbitrary commands. The trigger condition is when spawn-fcgi is run with the -f option and no positional arguments. As a non-root user, the injected commands run with the same privileges, potentially allowing command execution in contexts where spawn-fcgi is used, though it does not escalate privileges directly.
- **Code Snippet:**
  ```
  0x000095dc      90001be5       ldr r0, [s2]                ; const char *s
  0x000095e0      cffdffeb       bl sym.imp.strlen           ; size_t strlen(const char *s)
  0x000095e4      0030a0e1       mov r3, r0
  0x000095e8      063083e2       add r3, r3, 6
  0x000095ec      0300a0e1       mov r0, r3                  ; size_t size
  0x000095f0      65fdffeb       bl sym.imp.malloc           ; void *malloc(size_t size)
  0x000095f4      0030a0e1       mov r3, r0
  0x000095f8      20300be5       str r3, [s1]                ; 0x20 ; 32
  0x000095fc      50390ae3       movw r3, str.exec           ; 0xa950 ; "exec "
  0x00009600      003040e3       movt r3, 0                  ; 0xa950 ; "exec "
  0x00009604      20001be5       ldr r0, [s1]                ; 0x20 ; 32 ; void *s1
  0x00009608      0310a0e1       mov r1, r3                  ; 0xa950 ; "exec " ; const void *s2
  0x0000960c      0620a0e3       mov r2, 6
  0x00009610      51fdffeb       bl sym.imp.memcpy           ; void *memcpy(void *s1, const void *s2, size_t n)
  0x00009614      90301be5       ldr r3, [s2]                ; 0x90 ; 144
  0x00009618      20001be5       ldr r0, [s1]                ; 0x20 ; 32 ; char *s1
  0x0000961c      0310a0e1       mov r1, r3                  ; const char *s2
  0x00009620      7afdffeb       bl sym.imp.strcat           ; char *strcat(char *s1, const char *s2)
  0x00009624      0030a0e3       mov r3, 0
  0x00009628      00308de5       str r3, [sp]
  0x0000962c      58090ae3       movw r0, str._bin_sh        ; 0xa958 ; "/bin/sh"
  0x00009630      000040e3       movt r0, 0                  ; 0xa958 ; "/bin/sh"
  0x00009634      60190ae3       movw r1, str.sh             ; 0xa960 ; "sh"
  0x00009638      001040e3       movt r1, 0                  ; 0xa960 ; "sh"
  0x0000963c      64290ae3       movw r2, str._c             ; 0xa964 ; "-c"
  0x00009640      002040e3       movt r2, 0                  ; 0xa964 ; "-c"
  0x00009644      20301be5       ldr r3, [s1]                ; 0x20 ; 32
  0x00009648      46fdffeb       bl sym.imp.execl            ; int execl(const char *path, const char *arg0, ...)
  ```
- **Keywords:** spawn-fcgi -f option, FastCGI application path
- **Notes:** This vulnerability requires the attacker to have the ability to execute spawn-fcgi with control over the -f option and without providing positional arguments. While it does not grant privilege escalation beyond the current user, it could be used in broader attack chains or in environments where spawn-fcgi is invoked by scripts or other processes. Further analysis could explore other input vectors or interactions with system components.
