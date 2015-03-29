default rel

section .text ;bits 64
global encode
encode:
	push r12 ; save r12 and r13, I need those registers for stuff
	push r13
	push rbx
	xor rbx, rbx
	xor r9, r9
	xor r11, r11
	xor r13, r13
	sub rdx, 1
	
	movq mm6, [special4]
	movq mm5, [special3]
	movq mm4, [special2]
	movq mm3, [special1]

.encodeset:
	cmp rdx, 8
	jle .lasteight ; The last 8 or less characters need special treatment
	movq mm0, [rdi] ; Move character from memory to register
	paddb mm0, [const1] ; + 42

	movq mm7, mm0 ; temporary copy
	pcmpeqb mm7, mm3
	movq r10, mm7
	cmp r10, 0
	jne .scmultientry
	movq mm7, mm0
	pcmpeqb mm7, mm4
	movq r10, mm7
	cmp r10, 0
	jne .scmultientry
	movq mm7, mm0
	pcmpeqb mm7, mm5
	movq r10, mm7
	cmp r10, 0
	jne .scmultientry
	movq mm7, mm0
	pcmpeqb mm7, mm6
	movq r10, mm7
	cmp r10, 0
	jne .scmultientry
	cmp r11, 119
	jge .scmultientry ; Need special handling if we go over line length limit
	jmp .writesettobuffer

.scmultientry:
	movq rax, mm0
	
.scmulti:
	add r13, 1
	mov bl, al
	cmp bl, 0 ; Check for illegal characters
	je .scmulti2
	cmp bl, 10
	je .scmulti2
	cmp bl, 13
	je .scmulti2
	cmp bl, 61
	je .scmulti2
	jmp .scnextcharmulti

.scmulti2:
	add bl, 64 ; This time we add 64
	mov byte [rsi], 61 ; Add escape character
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	jmp .scnextcharmulti

.scnextcharmulti:
	mov byte [rsi], bl ; Move encoded byte to output array
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	rol rax, 8
	sub rdx, 1
	jz .exitprogram
	cmp r11, 127
	jge .scnewlinemulti
	cmp r13, 8
	je .nextset
	jmp .scmulti

.nextset:
	xor r13, r13
	add rdi, 8
	jmp .encodeset

.scnewlinemulti:
	mov byte [rsi], 13 ; \r
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	mov byte [rsi], 10 ; \n
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	xor r11, r11
	cmp r13, 8
	je .nextset
	jmp .scmulti

.specialchar:
	add r13, 1
	mov r10b, byte [rdi] ; Move character from memory to register
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
	mov byte [rsi], 61 ; Add escape character
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	jmp .scoutputencoded

.scnextchar:
	add rdi, 1
	sub rdx, 1
	jnz .specialchar
	jmp .exitprogram

.scoutputencoded:
	mov byte [rsi], r10b ; Move encoded byte to output array
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	add r11, 1 ; Increase line length
	cmp r11, 127
	jge .scnewline
	cmp r13, 7
	je .nextset
	jmp .scnextchar

.scnewline:
	mov byte [rsi], 13 ; \r
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	mov byte [rsi], 10 ; \n
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	xor r11, r11
	cmp r13, 8
	je .nextset
	jmp .scnextchar

.writesettobuffer:
	movq [rsi], mm0 ; Move encoded byte to output array
	add rsi, 8 ; increase output array pointer
	add rdi, 8 ; increase input pointer
	add r9, 8 ; Increase size of output
	add r11, 8 ; Increase line length
	sub rdx, 8 ; Done encoding 8 bytes
	cmp rdx, 0 ; Any chars left to encode?
	jle .exitprogram ; If not, exit
	cmp r11, 127
	jge .newline
	jmp .encodeset ; Encode another 8 bytes

.lasteight:
	jmp .specialchar

.newline:
	mov byte [rsi], 13 ; \r
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	mov byte [rsi], 10 ; \n
	add rsi, 1 ; increase output array pointer
	add r9, 1 ; Increase size of output
	xor r11, r11
	jmp .encodeset

.exitprogram:
	mov rax, r9 ; Return output size
	emms
	pop rbx
	pop r13 ; restore some registers to their original state
	pop r12
	ret

section .data
special1:	dq 0x3D0D0A003D0D0A00
special2:	dq 0x0D0A003D0D0A003D
special3:	dq 0x0A003D0D0A003D0D
special4:	dq 0x003D0D0A003D0D0A
const1:		dq 0x2A2A2A2A2A2A2A2A
