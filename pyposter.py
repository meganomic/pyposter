import fnmatch, os, sys, configparser, argparse, time
import parts
import nntplib

class usenet:
	def __init__(self, serveraddress, port, username, password, head_from, head_newsgroups):
		self.port = port
		self.serveraddress = serveraddress
		self.username = username
		self.password = password
		self.head_from = head_from
		self.head_newsgroups = head_newsgroups

	def connect(self):
		self.server = nntplib.NNTP(self.serveraddress, self.port, self.username, self.password)
		#self.server.set_debuglevel(1)

	def quit(self):
		self.server.quit()

	def post(self, article):
		self.server.post(article)

	def message_header(self, subject):
		return bytes('From: ' +  self.head_from + '\r\nNewsgroups: ' + self.head_newsgroups + '\r\nSubject: ' + subject + '\r\n\r\n', 'utf-8')

def upload_file(filename, usenet_con):
	with open(filename, 'rb') as f:
		f.seek(0, 2) # Seek to EOF
		filesize = f.tell() # Size of file
		if filesize <= 640000: # Calculate number of segments
			segments = 1
		else:
			segments = int(filesize / 640000)

		f.seek(0,0) # Reset file pointer
		data = bytearray(640000)

		for seg in range(0,segments):
			bytesread = f.readinto(data) # Read data
			part = parts.part(data, seg+1, segments, filename, bytesread) # Add relevant data to message part
			if segments == 1:
				subject = '\"' + filename + '\" ' + str(filesize) + ' yEnc bytes'
			else:
				subject = 'what about now nr 2' + ' - \"' + filename + '\" ' + 'yEnc ' + '(' + str(seg+1) + '/' + str(segments) + ')'
			article = usenet_con.message_header(subject) + part.header() + part.encode() + part.trailer() # Construct message
			usenet_con.post(article) # Post article to usenet
			time.sleep(0.01) # I get missing articles sometimes if there is no delay. I dunno, broken...

def main():
	parser = argparse.ArgumentParser(usage='%(prog)s [options] subject newsgroup file(s)', description='Post articles to usenet.')
	parser.add_argument('newsgroup', help = 'Newsgroup to post to')
	parser.add_argument('files', metavar = 'file(s)', nargs = '+',
						help = 'list of files to upload')
	parser.add_argument('--user', dest = 'username', help = 'Username for usenet server')
	parser.add_argument('--password', dest = 'password', help = 'Password for usenet server')

	args = parser.parse_args()

	config = configparser.ConfigParser()
	config.read('pyposter.ini')

	if args.username == None: # Override ini file if commandline set
		username = config['pyposter']['username']
	else:
		username = args.username

	if args.password == None: # Override ini file if commandline set
		password = config['pyposter']['password']
	else:
		password = args.password

	# Connect to usenet server
	usenet_con = usenet(config['pyposter']['server'], config['pyposter']['port'], username, password, config['pyposter']['from'], args.newsgroup)
	usenet_con.connect()

	for file in args.files:
		upload_file(file, usenet_con)
	
	usenet_con.quit()

if __name__ == '__main__':
	main()