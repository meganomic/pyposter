import configparser, argparse, glob, nntplib, zlib, os, sys
import parts, nzb, preprocess

class usenet:
	def __init__(self, serveraddress, port, username, password, head_from, head_newsgroups):
		self.port = port
		self.serveraddress = serveraddress
		self.username = username
		self.password = password
		self.head_from = head_from
		self.head_newsgroups = head_newsgroups

	def connect(self): # Connect to the server, strangely enough
		self.server = nntplib.NNTP(self.serveraddress, self.port, self.username, self.password)

	def quit(self):
		self.server.quit() # Gotta close down that connection

	def post(self, article):
		self.server.post(article) # Post the article to usenet

	def message_header(self, subject, messageid): # Format the article header
		return bytes('From: ' +  self.head_from + '\r\nNewsgroups: ' + self.head_newsgroups + '\r\nSubject: ' + subject + '\r\nMessage-ID: <' + messageid + '>\r\n\r\n', 'utf-8')

def upload_file(filenm, subject, usenet_con, nzbs, blocksize):
	crc32 = zlib.crc32(open(filenm,'rb').read()) & 0xffffffff # Get crc32 of entire file for yenc specification

	with open(filenm, 'rb') as f:
		filename = os.path.split(filenm)[1]
		print('Uploading ' + filename + '... ', end='\r')
		f.seek(0, 2) # Seek to EOF
		filesize = f.tell() # Size of file
		if filesize <= blocksize: # Calculate number of segments
			segments = 1 # If size is below 640000 then there is only 1 segment.
			nzfile = nzbs.add_file(usenet_con.head_from, subject + ' - \"' + filename + '\" ' + str(filesize) + ' yEnc bytes')
		else:
			segments = int(filesize / blocksize)
			nzfile = nzbs.add_file(usenet_con.head_from, subject + ' - \"' + filename + '\" ' + 'yEnc ' + '(1' + '/' + str(segments) + ')')

		f.seek(0,0) # Reset file pointer
		data = bytearray(blocksize) # Need a buffer for reading the file into
		
		for seg in range(0,segments): # Let's go through the segments!
			print('Uploading ' + filename + '... Part %d of %d' % (seg+1, segments), end='\r')
			bytesread = f.readinto(data) # Read data
			part = parts.part(data, seg+1, segments, filename, bytesread, crc32) # Add relevant data to message part
			if segments == 1:
				subject_ed = subject + ' - \"' + filename + '\" ' + str(filesize) + ' yEnc bytes'
			else:
				subject_ed = subject + ' - \"' + filename + '\" ' + 'yEnc ' + '(' + str(seg+1) + '/' + str(segments) + ')'
			messageid = nzfile.add_segment(bytesread, seg+1)
			article = usenet_con.message_header(subject_ed, messageid) + part.header() + part.encode() + part.trailer() # Construct message
			usenet_con.post(article) # Post article to usenet

		print('Uploading ' + filename + '... ' + 'Done!               ')

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
	parser = argparse.ArgumentParser(usage='%(prog)s [options] subject newsgroup file(s)', description='Post files to usenet.')
	parser.add_argument('newsgroup', help = 'Newsgroup to post to')
	parser.add_argument('files', metavar = 'file(s)', nargs = '+',
						help = 'list of files to upload')
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
	
	# Setup usenet connection
	usenet_con = usenet(config['pyposter']['server'], config['pyposter']['port'], username, password, config['pyposter']['from'], args.newsgroup)
	usenet_con.connect() # Connect to server

	nzbs = nzb.nzb(config['pyposter']['from'], args.subject)
	nzbs.add_group(args.newsgroup)
	
	allfiles = []
	for filearg in args.files: # I need a list of all files for processing
		for file in glob.glob(escapefilename(filearg)): # Expand possible wildcards and iterate over results
			allfiles.append(file) # Add file to list

	if args.subject == None: # If no subject set, use the filename of the first file
		args.subject = os.path.splitext(os.path.split(allfiles[0])[1])[0]

	if args.split == True: # Should split preprocessing be run?
		for file in preprocess.process(allfiles, True, False, int(config['process']['blocksize']), int(config['process']['desiredsize'])):
			upload_file(file, args.subject, usenet_con, nzbs, int(config['process']['blocksize'])) # Go upload the files!
	elif args.rar == True: # Should rar preprocessing be run?
		for file in preprocess.process(allfiles, False, False, int(config['process']['blocksize']), int(config['process']['desiredsize'])):
			upload_file(file, args.subject, usenet_con, nzbs, int(config['process']['blocksize'])) # Go upload the files!
	else: # Preprocessing is for losers. Just upload the file pls.
		for file in allfiles:
			upload_file(file, args.subject, usenet_con, nzbs, int(config['process']['blocksize'])) # Go upload the files!

	usenet_con.quit() # Remember to disconnect =)

	if args.nonzb == False:
		nzbs.save(args.subject + '.nzb') # Save the nzb file using subject as name

if __name__ == '__main__':
	main()
