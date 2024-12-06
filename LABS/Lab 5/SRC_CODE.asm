        .global _main

_main:
        MOV x0, #10
        MOV x1, #20
        ADD x2, x0, #5
        ADD x2, x2, x1
        BL foo
        MOV x0, x2
        HALT

foo:
        ADD x2, x2, #5
        MOV PC, x6    ; return to caller
