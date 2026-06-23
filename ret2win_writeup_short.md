# ROP ret2win - Writeup

## Challenge Overview

Buffer overflow in `pwnme()` function. Overflow the buffer and call `ret2win()` to get the flag.

---

## Step 1: Binary Analysis

![Binary Checksec](IMAGE_1_CHECKSEC.png)

- No stack canary
- NX enabled  
- PIE disabled
- 68 symbols available

Key findings:
- `ret2win` function exists at `0x400756`
- We can read symbols with ELF

---

## Step 2: Symbol Extraction

![Symbols](IMAGE_2_SYMBOLS.png)

Using `objdump -t`, we find all function addresses:
- `pwnme` at `0x4006e8` (vulnerable function)
- `ret2win` at `0x400756` (target function)
- `_start` at `0x4005b0`

---

## Step 3: Vulnerable Function Analysis

![Disassembly pwnme](IMAGE_5_PWNME.png)

The `pwnme()` function:
- Allocates 32 bytes local buffer (`sub rsp,0x20`)
- Reads 0x38 (56) bytes via `read()` 
- **Overflow: 56 bytes into 32-byte buffer = 24 byte overflow**
- Plus 8 bytes saved RBP = **40 byte offset to RIP**

---

## Step 4: Find Offset

![RSP Memory](IMAGE_3_MEMORY.png)

Using cyclic pattern to crash and find exact offset:
```
Offset = 40 bytes
```

Once we control RIP at offset 40, we can hijack execution.

---

## Step 5: Target Function

![ret2win disassembly](IMAGE_4_RET2WIN.png)

The `ret2win()` function:
- Calls `puts()` 
- Calls `system()` to print flag
- Returns

Address: `0x400756`

---

## Step 6: First Attempt - FAILS ❌

Direct jump to `ret2win` without RET gadget:

```
Payload: [40 bytes padding] + [ret2win address]
```

**Result:** SIGSEGV (Segmentation Fault)

**Why?** Stack alignment issue:
- After `pwnme()` returns, RSP is misaligned
- `system()` in PLT uses `movaps xmm0, [rsp]`
- `movaps` requires `RSP % 16 == 0`
- Misaligned RSP = crash ❌

---

## Step 7: Find RET Gadget

![ROP Gadgets](IMAGE_6_GADGETS.png)

Found simple gadgets:
```
0x40053e: ret
```

This RET gadget will fix alignment by popping one extra value from stack.

---

## Step 8: Working Payload with RET Gadget

![Exploit Sent](IMAGE_8_EXPLOIT.png)

Corrected payload structure:
```
[40 bytes padding] + [RET gadget] + [ret2win address]
```

When RET gadget executes:
- Pops `ret2win` address into RIP
- RSP += 8 (alignment fixed!)
- Jumps to `ret2win` with proper alignment ✓

---

## Step 9: Success! Flag Captured ✅

![Flag Output](IMAGE_8_SUCCESS.png)

```
Thank you!
Well done! Here's your flag:
ROPE{a_placeholder_32byte_flag!}
```

Process exits cleanly with code 0.

---

## Why RET Gadget Was Needed

**Without it:** 
- RSP misaligned after overflow
- `movaps` in `system()` PLT crashes

**With it:**
- RET gadget pops one extra time
- RSP becomes aligned
- `system()` loads successfully
- Flag printed!

**One RET instruction = pwned!** ✓
