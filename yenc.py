def encode(data):
	encdata = bytearray()
	clinelen = 0
	for b in data:
		o = (b+42) % 256 # Do magic yenc encoding
		if o == 0x00 or o == 0x0A or o == 0x0D or o == 0x3D: # Check for forbidden characters
			encdata.append(0x3D) # Add escape character
			clinelen += 1
			o = (o+64) % 256 # Do magic yenc encoding for escaped character

		encdata.append(o) # Save encoded data

		clinelen += 1
		if clinelen >= 127: # New line before it gets too long
			encdata.append(0x0D)
			encdata.append(0x0A)
			clinelen = 0

	return encdata