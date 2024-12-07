    .global _main

_main:
    mov   r0, #10
    mov   r1, #0x14
    mov   r6, pc
    b     add_numbers
    mov   r1, #0b11
    mov   r6, pc
    b     multiply_numbers
    nop
    halt

add_numbers:
    add   r0, r0, r1
    mov   pc, r6

multiply_numbers:
    mul   r0, r0, r1
    mov   pc, r6
