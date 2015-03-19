'''
	Ultra simple mega ez nzb creator
'''

import time, random, html

class nzb_file:
	def __init__(self, poster, subject):
		self.poster = html.escape(poster, True) # Escape poster just incase, who knows
		self.subject = html.escape(subject, True) # Escape subject line since it contains quotes
		self.time = str(int(time.time())) # The current time
		self.segments = []
	
	def addsegment(self, segmentsize, segmentnr, messageid): # The segments of the file that was posted
		self.segments.append((str(segmentsize), str(segmentnr), messageid)) # Add segment to list
		return messageid # Return the Message-ID for use when posting
	
class nzb:
	def __init__(self, poster, subject):
		self.groups = []
		self.files = []

	def addfile(self, poster, subject):
		self.files.append(nzb_file(poster, subject)) # Add a nzb_file object to the files list
		return self.files[-1]

	def addgroup(self, group):
		self.groups.append(group) # The groups that the file is posted to

	def save(self, filename): # Save nzb file to disk
		with open(filename, 'wt') as f:
			f.write('<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>\n')
			f.write('<!DOCTYPE nzb PUBLIC \"-//newzBin//DTD NZB 1.1//EN\" \"http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd\">\n')
			f.write('<nzb xmlns=\"http://www.newzbin.com/DTD/2003/nzb\">\n')

			for file in self.files:
				f.write('    <file poster=\"' + file.poster + '\" date=\"' + file.time + '\" subject=\"' + file.subject + '\">\n')

				f.write('        <groups>\n')
				for group in self.groups: 
					f.write('            <group>' + group + '</group>\n')
				f.write('        </groups>\n')

				f.write('        <segments>\n')
				for size, partnr, messageid in file.segments:
					f.write('            <segment bytes=\"' + size + '\" number=\"' + partnr + '\">' + messageid + '</segment>\n') 
				f.write('        </segments>\n')
				f.write('    </file>\n')
			f.write('</nzb>\n')