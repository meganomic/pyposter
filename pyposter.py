import fnmatch, os, sys, configparser, argparse
import yenc, parts, usenet

def loadfile(filename):
	with open(filename, 'rb') as f:
		f.seek(0, 2) # Seek to EOF
		size = f.tell() # Size of file
		if size <= 640000: # Calculate number of segments
			segments = 1
		else:
			segments = int(size / 640000)

		f.seek(0,0) # Reset file pointer
		data = bytearray(640000)

		for num in range(0,segments):
			bytesread = f.readinto(data) # Read data
			part = parts.part(data, num+1, segments, filename, bytesread) # Add relevant data to message part
			message = part.header() + part.encode() + part.trailer() # Construct message
			usenet.post(message) # Post message to usenet

def main():
	parser = argparse.ArgumentParser(usage='%(prog)s [options] subject newsgroup file(s)', description='Post articles to usenet.')
	parser.add_argument('subject', help = 'Subject line to use when posting')
	parser.add_argument('newsgroup', help = 'Newsgroup to post to')
	parser.add_argument('files', metavar = 'file(s)', nargs = '+',
						help = 'list of files to upload')
	parser.add_argument('--user', dest = 'username', help = 'Username for usenet server')
	parser.add_argument('--password', dest = 'password', help = 'Password for usenet server')

	args = parser.parse_args()

	config = configparser.ConfigParser()
	config.read('pyposter.ini')

	config['pyposter']['server']
	config['pyposter']['port']
	config['pyposter']['from']
	if not args.username: # Override ini file if commandline set
		username = config['pyposter']['username']
	if not args.password: # Override ini file if commandline set
		password = config['pyposter']['password']
	
	print(args.files)
	#serveraddress, port, username, password, head_from, head_newsgroups, head_subject):
	
	#usenet_con = usenet()

if __name__ == '__main__':
	main()
	#loadfile('ragnarok.001')