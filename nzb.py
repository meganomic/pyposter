'''
	Ultra simple mega ez nzb creator
'''

import time, random, html

def base36(number): # Stole this function from https://github.com/tonyseek/python-base36/blob/master/base36.py
	'''
	The MIT License (MIT)
	Copyright (c) 2014 Jiangge Zhang

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
	IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
	DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
	OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
	OR OTHER DEALINGS IN THE SOFTWARE.
	'''
	alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
	value = ''
	while number != 0:
		number, index = divmod(number, len(alphabet))
		value = alphabet[index] + value

	return value

class nzb_file:
	def __init__(self, poster, subject):
		self.poster = html.escape(poster, True)
		self.subject = html.escape(subject, True)
		self.time = str(int(time.time()))
		self.segments = []
	
	def add_segment(self, size, partnr): # The segments of the file that was posted
		# Make sure id is fucking unique, using 4x random numbers + current time. converting it to base36 for the lulz
		messageid = base36(int(random.SystemRandom().randint(10000000, 99999999))) + base36(int(random.SystemRandom().randint(10000000, 99999999))) + base36(int(random.SystemRandom().randint(10000000, 99999999))) + base36(int(time.time()*1000000)) + base36(int(random.SystemRandom().randint(10000000, 99999999))) + '@' + self.poster.split(' ')[0].split('@')[1] # Create a message id using poster email and current posix time
		self.segments.append((str(size), str(partnr), messageid))
		return messageid # Return the Message-ID for use when posting
	
class nzb:
	def __init__(self, poster, subject):
		self.groups = []
		self.files = []

	def add_file(self, poster, subject):
		self.files.append(nzb_file(poster, subject)) # Add a nzb_file object to the files list
		return self.files[-1] # Return the last object in the list

	def add_group(self, group):
		self.groups.append(group) # The groups that the file is posted to

	def save(self, filename): # Save nzb file to disk
		with open(filename, 'wt') as f:
			f.write('<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>\n')
			f.write('<!DOCTYPE nzb PUBLIC \"-//newzBin//DTD NZB 1.1//EN\" \"http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd\">\n')
			f.write('<nzb xmlns=\"http://www.newzbin.com/DTD/2003/nzb\">\n')

			for file in self.files:
				f.write('    <file poster=\"' + file.poster + '\" date=\"' + str(int(time.time())) + '\" subject=\"' + file.subject + '\">\n')

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