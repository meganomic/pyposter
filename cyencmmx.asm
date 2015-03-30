GLOBAL encode
   EXPORT encode

section .code bits 64

encode:
	push r12 ; save r12 and r13, I need those registers for stuff
	push r13
	push r14
	push rbx
	push rdi
	xor rbx, rbx
	xor r9, r9
	xor r11, r11
	xor r13, r13
	mov r14, rcx ; need rcx for scasb so move the pointer
	
	movq mm6, [special4]
	movq mm5, [special3]
	movq mm4, [special2]
	movq mm3, [special1]

.encodeset:
	cmp r8, 8
	jle .specialchar ; The last 8 or less characters need special treatment
	movq mm0, [r14] ; Move character from memory to register
	paddb mm0, [const1] ; + 42

	pxor mm1, mm1
	movq mm7, mm0 ; temporary copy
	pcmpeqb mm7, mm3
	por mm1, mm7
	movq mm7, mm0
	pcmpeqb mm7, mm4
	por mm1, mm7
	movq mm7, mm0
	pcmpeqb mm7, mm5
	por mm1, mm7
	movq mm7, mm0
	pcmpeqb mm7, mm6
	por mm1, mm7
	movq r10, mm1
	cmp r10, 0
	jne .scmultientry
	cmp r11, 119
	jge .scmultientry ; Need special handling if we go over line length limit
	jmp .writesettobuffer

.scmultientry:
	movq rax, mm0
	
.scmulti:
	add r13, 1
	mov rdi, scmulticmp
	mov rcx, 4
	repnz scasb
	jz .scmulti2
	;jmp .scnextcharmulti

.scnextcharmulti:
	mov byte [rdx], al ; Move encoded byte to output array
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	ror rax, 8
	sub r8, 1
	jz .exitprogram
	cmp r11, 127
	jge .scnewlinemulti
	cmp r13, 8
	je .nextset
	jmp .scmulti

.scmulti2:
	add al, 64 ; This time we add 64
	mov byte [rdx], 61 ; Add escape character
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	jmp .scnextcharmulti

.nextset:
	xor r13, r13
	add r14, 8
	jmp .encodeset

.scnewlinemulti:
	mov byte [rdx], 13 ; \r
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	mov byte [rdx], 10 ; \n
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	xor r11, r11
	cmp r13, 8
	je .nextset
	jmp .scmulti

.specialchar:
	add r13, 1
	mov r10b, byte [r14] ; Move character from memory to register
	add r10b, 42 ; Add 42 before modulus
	cmp r10b, 0 ; Check for illegal characters
	je .sc
	cmp r10b, 10
	je .sc
	cmp r10b, 13
	je .sc
	cmp r10b, 61
	je .sc
	jmp .scoutputencoded

.sc:
	add r10b, 64 ; This time we add 64
	mov byte [rdx], 61 ; Add escape character
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	jmp .scoutputencoded

.scnextchar:
	add r14, 1
	sub r8, 1
	jnz .specialchar
	jmp .exitprogram

.scoutputencoded:
	mov byte [rdx], r10b ; Move encoded byte to output array
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	cmp r11, 127
	jge .scnewline
	cmp r13, 8
	je .exitprogram
	jmp .scnextchar

.scnewline:
	mov byte [rdx], 13 ; \r
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	mov byte [rdx], 10 ; \n
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	xor r11, r11
	cmp r13, 8
	je .exitprogram
	jmp .scnextchar

.writesettobuffer:
	movq [rdx], mm0 ; Move encoded byte to output array
	add rdx, 8 ; increase output array pointer
	add r14, 8 ; increase input pointer
	add r9, 8 ; Increase size of output
	add r11, 8 ; Increase line length
	sub r8, 8 ; Done encoding 8 bytes
	cmp r8, 0 ; Any chars left to encode?
	jle .exitprogram ; If not, exit
	cmp r11, 127
	jge .newline
	jmp .encodeset ; Encode another 8 bytes

.newline:
	mov byte [rdx], 13 ; \r
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	mov byte [rdx], 10 ; \n
	add rdx, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	xor r11, r11
	jmp .encodeset

.exitprogram:
	mov rax, r9 ; Return output size
	emms
	pop rdi
	pop rbx
	pop r14
	pop r13 ; restore some registers to their original state
	pop r12
	ret

section .data
scmulticmp:	dd 0x3D0D0A00
special1:	dq 0x3D0D0A003D0D0A00
special2:	dq 0x0D0A003D0D0A003D
special3:	dq 0x0A003D0D0A003D0D
special4:	dq 0x003D0D0A003D0D0A
const1:		dq 0x2A2A2A2A2A2A2A2A