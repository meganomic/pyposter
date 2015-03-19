import zlib, ctypes, random, time, platform, os, sys

if platform.system() == 'Windows': # Check if it's windows
    cyenc = ctypes.CDLL(os.path.join(sys.path[0], 'cyenc.dll'))
else:
    cyenc = ctypes.CDLL(os.path.join(sys.path[0], 'cyenc.so')) # Assume linux if not

class usenetfile():
	poster = None # Poster
	newsgroups = [] # Newsgroups to post to
	nzb = None
	blocksize = None

	def __init__(self, filename, subject):
		self.filename = filename
		self.subject = subject
		self.currentsegment = -1
		self.crc32 = None
		self.totalsegments = None
		self.index = None
		self.filesize = None
		self.fd = open(filename, 'rb') # I like to live on the edge

		self.crc32 = zlib.crc32(self.fd.read()) & 0xffffffff # Get crc32 of entire file for yenc specification
		self.fd.seek(0, 2) # Seek to EOF
		self.filesize = self.fd.tell() # Size of file
		if self.filesize <= self.blocksize: # Calculate number of segments
			self.totalsegments = 1 # If size is below or equal to blocksize then there is only 1 segment.
			self.nzbfile = self.nzb.addfile(self.poster, self.subject + ' - \"' + self.filename + '\" ' + str(self.filesize) + ' yEnc bytes')
		else:
			self.totalsegments = int(self.filesize / self.blocksize) + 1
			self.nzbfile = self.nzb.addfile(self.poster, self.subject + ' - \"' + self.filename + '\" ' + 'yEnc ' + '(1' + '/' + str(self.totalsegments) + ')')

		self.fd.seek(0,0) # Reset file pointer

	def __del__(self):
		self.fd.close() # Close the file

	def __iter__(self):
		return self

	def __gennextsegment(self):
		data = bytearray(self.blocksize)
		segmentsize = self.fd.readinto(data)
		pcrc32 = zlib.crc32(data) & 0xffffffff # Calculate part crc32 as part of yenc specification
		startpos = self.currentsegment * self.blocksize # Save the positions in the original file for this part so we can put it back together
		endpos = startpos + segmentsize
		
		# Make sure id is fucking unique, using 4x random numbers + current time. converting it to base36 for the lulz
		messageid = self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + self.__base36(int(time.time()*1000000)) + self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + '@' + self.poster.split(' ')[0].split('@')[1] # Create a message id using poster email and current posix time and some random numbers
		self.nzbfile.addsegment(segmentsize, self.currentsegment + 1, messageid)
		
		if self.totalsegments > 1: # The yenc specification differs for multipart files vs singlepart files
			subject = self.subject + ' - \"' + self.filename + '\" ' + 'yEnc ' + '(' + str(self.currentsegment + 1) + '/' + str(self.totalsegments) + ')'
			yencheader = bytes('=ybegin part=' + str(self.currentsegment + 1) + ' total=' + str(self.totalsegments) + ' line=128 size=' + str(segmentsize) + ' name=' + self.filename + '\r\n' +	'=ypart begin=' + str(startpos) + ' end=' + str(endpos) + '\r\n', 'utf-8')
			yenctrailer = bytes('\r\n=yend size=' + str(segmentsize) + ' part=' + str(self.currentsegment) + ' pcrc32=' + str(hex(pcrc32))[2:10] + ' crc32=' + str(hex(self.crc32))[2:10], 'utf-8')
		else:
			subject = self.subject + ' - \"' + self.filename + '\" ' + str(self.filesize) + ' yEnc bytes'
			yencheader = bytes('=ybegin line=128 size=' + str(self.filesize) + ' name=' + self.filename + '\r\n', 'utf-8')
			yenctrailer = bytes('\r\n=yend size=' + str(self.filesize) + ' crc32=' + str(hex(self.crc32))[2:10], 'utf-8')

		# Usenet article header
		usenetheader = bytes('poster: ' +  self.poster + '\r\nNewsgroups: ' + ','.join(self.newsgroups).rstrip(',') + '\r\nSubject: ' + self.subject + '\r\nMessage-ID: <' + messageid + '>\r\n\r\n', 'utf-8')

		cyenc.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.c_int] # Convert to these types when calling dll function pls
		encodedoutput = ctypes.create_string_buffer(self.blocksize*2) # Create a big buffer so we don't run out of space
		encoded_size = cyenc.encode(ctypes.create_string_buffer(bytes(data)), encodedoutput, segmentsize) # Encode to yenc using external dll

		article = usenetheader + yencheader + encodedoutput[0:encoded_size] + yenctrailer # Construct message
		return article

	def __next__(self):
		if self.currentsegment == self.totalsegments: # Check if we are on the last segment
			raise StopIteration
		self.currentsegment = self.currentsegment + 1
		return self.__gennextsegment()

	def __base36(self, number): # Stole this function poster https://github.com/tonyseek/python-base36/blob/master/base36.py
		alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
		value = ''
		while number != 0:
			number, index = divmod(number, len(alphabet))
			value = alphabet[index] + value

		return value