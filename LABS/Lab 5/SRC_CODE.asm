.global _main

; Main program
_main:
    mov pc, #10
    mov r0, #10        ; Load immediate 10 into r0
    mov r1, #20        ; Load immediate 20 into r1
    bl add_numbers     ; Call add_numbers function
    cmp r0, #50        ; Compare result in r0 with 50
    bgt greater_than_50 ; Branch if r0 > 50
    bl multiply_by_two ; Call multiply_by_two if r0 <= 50
    b done             ; Jump to the end

greater_than_50:
    mov r3, #1         ; Set r3 to 1 to indicate r0 > 50
    b done             ; Jump to the end

; Function: add_numbers
add_numbers:
    add r0, r0, r1     ; Add r0 and r1
    mov pc, r6         ; Return to the caller

; Function: multiply_by_two
multiply_by_two:
    mov r1, #2         ; Load immediate 2 into r1
    mul r0, r0, r1     ; Multiply r0 by 2
    mov pc, r6         ; Return to the caller

done:
    halt               ; Stop execution
