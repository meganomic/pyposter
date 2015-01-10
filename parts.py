import yenc

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
			return bytes('=ybegin line=128 size=' + str(self.size) + ' name=' + name + '\r\n', 'utf-8')

	def trailer(self):
		if self.totalparts > 1:
			return bytes('\r\n=yend size=' + str(self.size) + ' part=' + str(self.partnr), 'utf-8')
		else:
			return bytes('\r\n=yend size=' + str(self.size), 'utf-8')

	def encode(self):
		return yenc.encode(self.data)