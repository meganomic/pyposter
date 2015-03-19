import configparser, argparse, glob, nntplib, zlib, os, sys
import nzb, preprocess, stuffs

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

def upload_file(filename, subject, usenetserver):
	ufile = stuffs.usenetfile(filename, subject)
	i = 1
	for article in ufile:
		with open('test' + str(i) + '.txt', 'wb') as f:
			f.write(article)
		i = i + 1
		#usenetserver.upload(article)


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

	allfiles = []
	for filearg in args.files: # I need a list of all files for processing
		for file in glob.glob(escapefilename(filearg)): # Expand possible wildcards and iterate over results
			allfiles.append(file) # Add file to list

	if args.subject == None: # If no subject set, use the filename of the first file
		args.subject = os.path.splitext(os.path.split(allfiles[0])[1])[0]

	nzbs = nzb.nzb(config['pyposter']['from'], args.subject)
	nzbs.addgroup(args.newsgroup)

	stuffs.usenetfile.poster = config['pyposter']['from']
	stuffs.usenetfile.newsgroups.append(args.newsgroup)
	stuffs.usenetfile.blocksize = int(config['process']['blocksize'])
	stuffs.usenetfile.nzb = nzbs

	# Setup usenet connection
	usenetserver = usenet(config['pyposter']['server'], config['pyposter']['port'], username, password)
	#usenetserver.connect() # Connect to server

	if args.split == True: # Should split preprocessing be run?
		for file in preprocess.process(allfiles, True, False, int(config['process']['blocksize']), int(config['process']['desiredsize'])):
			upload_file(file, args.subject, usenetserver) # Go upload the files!
	elif args.rar == True: # Should rar preprocessing be run?
		for file in preprocess.process(allfiles, False, False, int(config['process']['blocksize']), int(config['process']['desiredsize'])):
			upload_file(file, args.subject, usenetserver) # Go upload the files!
	else: # Preprocessing is for losers. Just upload the file pls.
		for file in allfiles:
			upload_file(file, args.subject, usenetserver) # Go upload the files!

	#usenetserver.quit() # Remember to disconnect =)

	if args.nonzb == False:
		nzbs.save(args.subject + '.nzb') # Save the nzb file using subject as name

if __name__ == '__main__':
	main()
