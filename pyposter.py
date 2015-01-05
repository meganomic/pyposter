import fnmatch, os, sys
import yenc, parts
from optparse import OptionParser

def loadfile(filename):
	with open(filename, 'rb') as f:
		f.seek(0, 2) # Seek to EOF
		size = f.tell() # Size of file
		if size <= 640000: # Calculate numnber of segments
			segments = 1
		else:
			segments = int(size / 640000)

		f.seek(0,0) # Reset file pointer
		data = bytearray(640000)

		for num in range(0,segments):
			bytesread = f.readinto(data)
			part = parts.part(data, num+1, segments, filename, bytesread)
			with open('asdfaf' + str(num) + '.txt', 'wb') as f2:
				complete = part.header() + part.encode() + part.trailer()
				f2.write(complete)

def encode():
	with open('readme.md', 'rb') as f:
		data = f.read()
		encdata = yenc.encode(data)

	with open('asdfaf.txt', 'wb') as f:
		f.write(encdata)

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
	loadfile('ragnarok.001')