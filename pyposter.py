from optparse import OptionParser

def main():
	usage = "usage: %prog [options] file(s)"
	version = '%prog 0.1'
	parser = OptionParser(usage=usage, version=version)
	parser.add_option("-s", "--server", dest="server", type="string",
						help="usenet.com")
	parser.add_option("-P", "--port", dest="port", type="int",
						help="Usenet server port, default: 147", default=147)
	parser.add_option("-u", "--username", dest="username",
						help="Username", type="string")
	parser.add_option("-p", "--password", dest="password",
						help="Password", type="string")

	(options, args) = parser.parse_args()

	if len(args) <= 0:
		parser.error("Missing files argument")

	for path in args:
		paths = fnmatch.filter(os.listdir('.'), path.replace('[','?').replace(']','?'))

	if len(paths) <= 0:
		print("Can't find any files")
		sys.exit(1)

if __name__ == '__main__':
	main()