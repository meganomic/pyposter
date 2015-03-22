GLOBAL encode
   EXPORT encode

section .code bits 64

encode:
	xor r9, r9 ; Make sure counter register i zero
	xor r11, r11
	xor r13, r13

.encodeset:
	cmp r8, 8
	jle .lasteight	
	movq mm0, [rcx] ; Move character from memory to register
	mov r10, const1
	movq mm1, [r10]
	paddb mm0, mm1
	mov r12, const2
	movq mm1, [r12]
	pand mm0, mm1
	jmp .checkforspecial

.checkforspecial:
	movq mm7, mm0 ; temporary copy
	mov r10, special1
	pcmpeqb mm7, [r10]
	movq r10, mm7
	cmp r10, 0
	jne .specialchar
	movq mm7, mm0
	mov r10, special2
	pcmpeqb mm7, [r10]
	movq r10, mm7
	cmp r10, 0
	jne .specialchar
	movq mm7, mm0
	mov r10, special3
	pcmpeqb mm7, [r10]
	movq r10, mm7
	cmp r10, 0
	jne .specialchar
	movq mm7, mm0
	mov r10, special4
	pcmpeqb mm7, [r10]
	movq r10, mm7
	cmp r10, 0
	jne .specialchar
	jmp .writesettobuffer

.specialchar:
	inc r13
	mov r10b, byte [rcx] ; Move character from memory to register
	add r10b, 42 ; Add 42 before modulus
	and r10b, 255 ; ultra fast modulus!!
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
	and r10b, 255 ; ultra fast modulus!! again
	mov byte [rdx], 61 ; Add escape character
	add rdx, 1 ; increase output array pointer
	inc r9 ; Increase size of output
	inc r11 ; Increase line length
	jmp .scoutputencoded

.scnextchar:
	add rcx, 1
	dec r8
	jnz .specialchar
	jmp .exitprogram

.scoutputencoded:
	mov byte [rdx], r10b ; Move encoded byte to output array
	add rdx, 1 ; increase output array pointer
	inc r9 ; Increase size of output
	inc r11 ; Increase line length
	cmp r11, 127
	jge .scnewline
	cmp r13, 7
	je .nextset
	jmp .scnextchar

.scnewline:
	mov byte [rdx], 13 ; \r
	add rdx, 1 ; increase output array pointer
	inc r9 ; Increase size of output
	mov byte [rdx], 10 ; \n
	add rdx, 1 ; increase output array pointer
	inc r9 ; Increase size of output
	xor r11, r11
	cmp r13, 8
	je .nextset
	jmp .scnextchar

.writesettobuffer:
	movq [rdx], mm0 ; Move encoded byte to output array
	add rdx, 8 ; increase output array pointer
	add rcx, 8 ; increase input pointer
	add r9, 8 ; Increase size of output
	add r11, 8 ; Increase line length
	sub r8, 8 ; Done encoding 8 bytes
	cmp r8, 0 ; Any chars left to encode?
	jle .exitprogram ; If not, exit
	cmp r11, 127
	jge .newline
	jmp .encodeset ; Encode another 8 bytes

.nextset:
	add rcx, 1
	dec r8
	jnz .encodeset
	jmp .exitprogram

.newline:
	mov byte [rdx], 13 ; \r
	add rdx, 1 ; increase output array pointer
	inc r9 ; Increase size of output
	mov byte [rdx], 10 ; \n
	add rdx, 1 ; increase output array pointer
	inc r9 ; Increase size of output
	xor r11, r11
	jmp .encodeset

.lasteight:
	jmp .specialchar

.exitprogram:
	mov rax, r9 ; Return output size
	emms
	ret

section .data
special1:	dq 0x3D0D0A003D0D0A00
special2:	dq 0x003D0D0A003D0D0A
special3:	dq 0x0A003D0D0A003D0D
special4:	dq 0x0D0A003D0D0A003D
const1:		dq 0x2A2A2A2A2A2A2A2A
const2:		dq 0xFFFFFFFFFFFFFFFF