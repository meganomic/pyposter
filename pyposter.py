import configparser, argparse, glob, nntplib, os, sys, math
import ctypes, random, time, platform, zlib, tempfile
import nzb, preprocess

class usenetfile():
	# Some variables that are the same for all files
	poster = None # Poster, obviously
	newsgroups = [] # Newsgroups to post to
	nzb = None # Nzb handler
	blocksize = None
	if platform.system() == 'Windows': # Check if it's windows
		cyenc = ctypes.CDLL(os.path.join(sys.path[0], 'cyenc.dll'))
	else:
		cyenc = ctypes.CDLL(os.path.join(sys.path[0], 'cyenc.so')) # Assume linux if not

	def __init__(self, filename, subject):
		self.filename = filename
		self.subject = subject
		self.currentsegment = 0
		self.crc32 = None # crc32 of the original file
		self.totalsegments = None
		self.filesize = None
		self.fd = open(filename, 'rb') # I like to live on the edge

		self.crc32 = zlib.crc32(self.fd.read()) & 0xffffffff # Get crc32 of entire file for yenc specification
		self.fd.seek(0, 2) # Seek to EOF
		self.filesize = self.fd.tell() # Size of file
		if self.filesize <= self.blocksize: # Calculate number of segments
			self.totalsegments = 1 # If size is below or equal to blocksize then there is only 1 segment.
			self.nzbfile = self.nzb.addfile(self.poster, self.subject + ' - \"' + self.filename + '\" ' + str(self.filesize) + ' yEnc bytes')
		else:
			self.totalsegments = math.ceil(self.filesize / self.blocksize)
			self.nzbfile = self.nzb.addfile(self.poster, self.subject + ' - \"' + self.filename + '\" ' + 'yEnc ' + '(1' + '/' + str(self.totalsegments) + ')')

		self.fd.seek(0,0) # Reset file pointer

	def __del__(self):
		self.fd.close() # Close the file

	def __iter__(self):
		return self

	def __next__(self):
		data = bytearray(self.blocksize)
		segmentsize = self.fd.readinto(data)
		if segmentsize	== 0: # If no data is read that means it's done!
			raise StopIteration

		pcrc32 = zlib.crc32(data) & 0xffffffff # crc32 of this part
		startpos = self.currentsegment * self.blocksize # Save the positions in the original file for this part so we can put it back together
		endpos = startpos + segmentsize

		# Yes this is correct
		self.currentsegment = self.currentsegment + 1 # Advance the segment counter

		# Make sure id is fucking unique, using 4x random numbers + current time. converting it to base36 for the lulz
		messageid = self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + self.__base36(int(time.time()*1000000)) + self.__base36(int(random.SystemRandom().randint(10000000, 99999999))) + '@' + self.poster.split(' ')[0].split('@')[1] # Create a message id using poster email and current posix time and some random numbers
		self.nzbfile.addsegment(segmentsize, self.currentsegment, messageid)

		if self.totalsegments > 1: # The yenc specification differs for multipart files vs singlepart files
			subject = self.subject + ' - \"' + self.filename + '\" ' + 'yEnc ' + '(' + str(self.currentsegment) + '/' + str(self.totalsegments) + ')'
			yencheader = bytes('=ybegin part=' + str(self.currentsegment) + ' total=' + str(self.totalsegments) + ' line=128 size=' + str(segmentsize) + ' name=' + self.filename + '\r\n' +	'=ypart begin=' + str(startpos) + ' end=' + str(endpos) + '\r\n', 'utf-8')
			yenctrailer = bytes('\r\n=yend size=' + str(segmentsize) + ' part=' + str(self.currentsegment) + ' pcrc32=' + str(hex(pcrc32))[2:10] + ' crc32=' + str(hex(self.crc32))[2:10], 'utf-8')
		else:
			subject = self.subject + ' - \"' + self.filename + '\" ' + str(self.filesize) + ' yEnc bytes'
			yencheader = bytes('=ybegin line=128 size=' + str(self.filesize) + ' name=' + self.filename + '\r\n', 'utf-8')
			yenctrailer = bytes('\r\n=yend size=' + str(self.filesize) + ' crc32=' + str(hex(self.crc32))[2:10], 'utf-8')

		# Usenet article header
		usenetheader = bytes('poster: ' +  self.poster + '\r\nNewsgroups: ' + ','.join(self.newsgroups).rstrip(',') + '\r\nSubject: ' + self.subject + '\r\nMessage-ID: <' + messageid + '>\r\n\r\n', 'utf-8')

		# Encode the data using yenc specification
		self.cyenc.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.c_int] # Convert to these types when calling dll function pls
		encodedoutput = ctypes.create_string_buffer(self.blocksize*2) # Create a big buffer so we don't run out of space
		encoded_size = self.cyenc.encode(ctypes.create_string_buffer(bytes(data)), encodedoutput, segmentsize) # Encode to yenc using external dll

		article = usenetheader + yencheader + encodedoutput[0:encoded_size] + yenctrailer # Construct message

		return article, self.currentsegment, self.totalsegments # Return fully formed usenet article

	def __base36(self, number): # Stole this function poster https://github.com/tonyseek/python-base36/blob/master/base36.py
		alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
		value = ''
		while number != 0:
			number, index = divmod(number, len(alphabet))
			value = alphabet[index] + value

		return value

class usenet:
	def __init__(self, serveraddress, port, username, password):
		self.port = port
		self.serveraddress = serveraddress
		self.username = username
		self.password = password

	def connect(self): # Connect to the server, strangely enough
		self.server = nntplib.NNTP(self.serveraddress, self.port, self.username, self.password)

	def quit(self):
		self.server.quit() # Gotta close down that connection

	def post(self, article):
		self.server.post(article) # Post the article to usenet

def uploadfile(filename, subject, usenetserver):
	ufile = usenetfile(filename, subject)
	for article, segnr, tsegnr in ufile:
		print('Uploading ' + os.path.split(filename)[1] + '... ' + str(segnr) + ' of ' + str(tsegnr), end='\r')
		#usenetserver.upload(article)
	print('Uploading ' + os.path.split(filename)[1] + '... Done!                         ')

def escapefilename(filename): # Stupid glob. I don't want [ or ] to be special
	escapedfilename = []
	for char in filename:
		if char == '[':
			escapedfilename.append('[[]')
		elif char == ']':
			escapedfilename.append('[]]')
		else:
			escapedfilename.append(char)
	return ''.join(escapedfilename)

def main():
	# Need some commandline options
	parser = argparse.ArgumentParser(usage='%(prog)s [options] newsgroup file(s)', description='Post files to usenet.')
	parser.add_argument('newsgroup', help = 'Newsgroup to post to')
	parser.add_argument('files', metavar = 'file(s)', nargs = '+', help = 'list of files to upload')
	parser.add_argument('--subject', dest = 'subject', help = 'Subject line, uses filename if not set')
	parser.add_argument('--user', dest = 'username', help = 'Username for usenet server')
	parser.add_argument('--password', dest = 'password', help = 'Password for usenet server')
	parser.add_argument('--nonzb', action='store_true', help = "Don't create a nzb file")
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--rar', action='store_true', default = False, help = 'Rar files before upload')
	group.add_argument('--split', action='store_true', default = False, help = 'Split files before upload')

	args = parser.parse_args() # Contains the arguments

	config = configparser.ConfigParser()
	config.read(os.path.join(sys.path[0], 'pyposter.ini')) # Read the ini file

	if args.username == None: # Override ini file if commandline set
		username = config['pyposter']['username']
	else:
		username = args.username

	if args.password == None: # Override ini file if commandline set
		password = config['pyposter']['password']
	else:
		password = args.password

	allfiles = []
	for filearg in args.files: # I need a list of all files for processing
		for file in glob.glob(escapefilename(filearg)): # Expand possible wildcards and iterate over results
			allfiles.append(file) # Add file to list

	if args.subject == None: # If no subject set, use the filename of the first file
		args.subject = os.path.splitext(os.path.split(allfiles[0])[1])[0]

	nzbs = nzb.nzb(config['pyposter']['from'], args.subject)
	nzbs.addgroup(args.newsgroup)

	# Set some variables that are the same for all files
	usenetfile.poster = config['pyposter']['from']
	usenetfile.newsgroups.append(args.newsgroup)
	usenetfile.blocksize = int(config['process']['blocksize'])
	usenetfile.nzb = nzbs

	# Setup usenet connection
	usenetserver = usenet(config['pyposter']['server'], config['pyposter']['port'], username, password)
	#usenetserver.connect() # Connect to server

	if args.split == True: # Should split preprocessing be run?
		for filename in allfiles:
			tempdir = tempfile.TemporaryDirectory() # Setup a temporary directory
			for file in preprocess.process(filename, True, False, int(config['process']['blocksize']), int(config['process']['desiredsize']), tempdir.name):
				uploadfile(file, args.subject, usenetserver) # Go upload the files!
			tempdir.cleanup()
	elif args.rar == True: # Should rar preprocessing be run?
		tempdir = tempfile.TemporaryDirectory() # Setup a temporary directory
		for file in preprocess.process(allfiles, False, False, int(config['process']['blocksize']), int(config['process']['desiredsize']), tempdir.name):
			uploadfile(file, args.subject, usenetserver) # Go upload the files!
		tempdir.cleanup()
	else: # Preprocessing is for losers. Just upload the file pls.
		for file in allfiles:
			uploadfile(file, args.subject, usenetserver) # Go upload the files!

	#usenetserver.quit() # Remember to disconnect =)

	if args.nonzb == False:
		nzbs.save(args.subject + '.nzb') # Save the nzb file using subject as name

if __name__ == '__main__':
	main()