#import yenc
import ctypes

cyenc = ctypes.CDLL("cyenc.dll")

class part:
	def __init__(self, data, partnr, totalparts, name, size):
		self.startpos = 0
		self.endpos = 0
		self.partnr = partnr
		self.totalparts = totalparts
		self.size = size
		self.name = name
		self.data = data
		
		if size == 640000:
			self.startpos = partnr * size - size
			self.endpos = self.startpos + size
		else:
			self.startpos = (partnr - 1) * 640000
			self.endpos = self.startpos + size

	def header(self):
		if self.totalparts > 1:
			return bytes('=ybegin part=' + str(self.partnr) + ' total=' + str(self.totalparts) + ' line=128 size=' + str(self.size) + ' name=' + self.name + '\r\n' +	'=ypart begin=' + str(self.startpos) + ' end=' + str(self.endpos) + '\r\n', 'utf-8')
		else:
			return bytes('=ybegin line=128 size=' + str(self.size) + ' name=' + self.name + '\r\n', 'utf-8')
	def trailer(self):
		if self.totalparts > 1:
			return bytes('\r\n=yend size=' + str(self.size) + ' part=' + str(self.partnr), 'utf-8')
		else:
			return bytes('\r\n=yend size=' + str(self.size), 'utf-8')

	def encode(self):
		cyenc.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.c_int] # Convert to these types when calling dll function pls
		output = ctypes.create_string_buffer(self.size*2) # Create a big buffer so we don't run out of space
		encoded_size = cyenc.encode(ctypes.create_string_buffer(bytes(self.data)), output, self.size) # Encode to yenc using external dll
		return output[0:encoded_size]
