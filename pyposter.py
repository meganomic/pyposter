import configparser, argparse, glob, nntplib, zlib, os
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

def upload_file(filenm, subject, usenet_con, nzbs):
	crc32 = zlib.crc32(open(filenm,'rb').read()) & 0xffffffff # Get crc32 of entire file for yenc specification

	with open(filenm, 'rb') as f:
		filename = os.path.split(filenm)[1]
		print('Uploading ' + filename + '... ', end='\r')
		f.seek(0, 2) # Seek to EOF
		filesize = f.tell() # Size of file
		if filesize <= 640000: # Calculate number of segments
			segments = 1 # If size is below 640000 then there is only 1 segment.
			nzfile = nzbs.add_file(usenet_con.head_from, subject + ' - \"' + filename + '\" ' + str(filesize) + ' yEnc bytes')
		else:
			segments = int(filesize / 640000)
			nzfile = nzbs.add_file(usenet_con.head_from, subject + ' - \"' + filename + '\" ' + 'yEnc ' + '(1' + '/' + str(segments) + ')')

		f.seek(0,0) # Reset file pointer
		data = bytearray(640000) # Need a buffer for reading the file into
		
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

def main():
	# Need some commandline options
	parser = argparse.ArgumentParser(usage='%(prog)s [options] subject newsgroup file(s)', description='Post files to usenet.')
	parser.add_argument('subject', help = 'Subject line')
	parser.add_argument('newsgroup', help = 'Newsgroup to post to')
	parser.add_argument('files', metavar = 'file(s)', nargs = '+',
						help = 'list of files to upload')
	parser.add_argument('--user', dest = 'username', help = 'Username for usenet server')
	parser.add_argument('--password', dest = 'password', help = 'Password for usenet server')

	args = parser.parse_args() # Contains the arguments

	config = configparser.ConfigParser()
	config.read('pyposter.ini') # Read the ini file

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
		for file in glob.glob(filearg): # Expand possible wildcards and iterate over results
			allfiles.append(file)
	
	for file in preprocess.process(allfiles, True, False):
		upload_file(file, args.subject, usenet_con, nzbs) # Go upload the files!

	usenet_con.quit() # Remember to disconnect =)

	nzbs.save(args.subject + '.nzb') # Save the nzb file using subject as name

if __name__ == '__main__':
	main()
