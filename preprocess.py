import os, sys, subprocess, re, platform

def splitfiles(partsize, outputdir, filename, numberofparts):
	parts = list()
	with open(filename, "rb") as f:
		data = bytearray(partsize) # Read partsize of dataz
		partnr = 1
		while True: # Just go forever bro
			if partnr < 10: # Annoying naming thing, probably 100 better way to do it but I'm too stupid
				if numberofparts < 10:
					partname = filename + ".%d" % partnr
				elif numberofparts >= 10 and numberofparts < 100:
					partname = filename + ".0%d" % partnr
				elif numberofparts > 100:
					partname = filename + ".00%d" % partnr
			elif partnr >= 10 and partnr < 100:
				if numberofparts >= 10 and numberofparts < 100:
					partname = filename + ".%d" % partnr
				elif numberofparts > 100:
					partname = filename + ".0%d" % partnr
			elif partnr > 100:
				partname = filename + ".%d" % partnr

			partnr = partnr + 1
			length = f.readinto(data) # Read more data

			if length == 0: # No data left? Then move on
				break

			parts.append(os.path.join(outputdir, partname))

			with open(os.path.join(outputdir, partname), "wb") as f2: # Write split bit to disk
				f2.write(data[0:length])

	return parts

def createpar2(blocksize, outputdir, outputfile, filelist, verbose):
	if type(filelist) == str: # filelist MUST be a list or bad things happen
		filelist = [filelist] # Make filelist a list containing only filelist =) hahah

	if platform.system() == 'Windows': # Check if it's windows
		par2_exec = os.path.join(sys.path[0], 'par2.exe')
	else:
		par2_exec = 'par2'

	if verbose:
		return subprocess.call(par2_exec + ' c -r20 -s' + str(blocksize) + ' \"' +
							os.path.join(outputdir, outputfile) + '\" ' + subprocess.list2cmdline(filelist), shell=True)
	else:
		return subprocess.call(par2_exec + ' c -r20 -s' + str(blocksize) + ' \"' +
							os.path.join(outputdir, outputfile) + '\" ' + subprocess.list2cmdline(filelist), stdout=subprocess.DEVNULL, shell=True)

def createrars(rarsize, outputdir, outputfile, filelist):
	if platform.system() == 'Windows': # Check if it's windows
		rar_exec = os.path.join(sys.path[0], 'rar.exe')
	else:
		rar_exec = 'rar'

	rar = subprocess.Popen(rar_exec + ' a -m0 -v' + \
							str(rarsize) + 'b -mt2 \"' + os.path.join(outputdir, outputfile) + '\" ' + \
							subprocess.list2cmdline(filelist), stdout=subprocess.PIPE, shell=True)
	stdout = rar.communicate()[0]

	result = re.findall(".*?Creating archive (.*?.rar).*?", str(stdout)) # Parse the output to get the filenames of created rars

	#Fix for cases where there are only a single rar file
	if len(result) == 1:
		return result

	#For some stupid reason the name of part1 is always .rar
	if 'part2' in result[1]:
		result[0] = result[0].replace('.rar', '.part1.rar')
		return result
	elif 'part02' in result[1]:
		result[0] = result[0].replace('.rar', '.part01.rar')
		return result
	elif 'part002' in result[1]:
		result[0] = result[0].replace('.rar', '.part001.rar')
		return result

def process(files, split, verbose, blocksize, desiredsize, outputdir):
	#desiredsize = 19200000 # Results in 30 parts, nice default I guess
	#blocksize = 640000 # 5000 lines long * 128 chars wide
	numberofparts = round(desiredsize / blocksize) # Number of parts to divide the file into
	partsize = numberofparts * blocksize # Size of part after splitting original file
	# os.path.join(os.getcwd(), 'tmp') # Set output to ./tmp

	#if not os.path.exists(outputdir): # Check if ./tmp exists and if not, create it
	#	os.makedirs(outputdir)

	if split == True: # Should we split the files?
		filename = files
		print('Splitting file(s)...')
		filelist = splitfiles(partsize, outputdir, filename, numberofparts)
		print(filename + ' done.')
		print('Creating par2 files... (This may take several minutes)')
		print('Creating par2 for ' + filename + '...')
		createpar2(blocksize, outputdir, filename + '.par2', filename, verbose)
	else:
		print('Creating rar(s)...')
		rarfile = os.path.splitext(files[0])[0] + '.rar'
		filelist = createrars(desiredsize, outputdir, rarfile, files)

		print('Creating par2 files... (This may take several minutes)')
		print('Creating par2 for ' + rarfile + '...')
		createpar2(blocksize, outputdir, rarfile + '.par2', filelist, verbose)

	allfiles = [] # Need a list of all the files we made
	for filename in os.listdir(outputdir): # Go through all entries in the output directory
		path = os.path.join(outputdir, filename) # Make a absolute path
		if os.path.isfile(path): # Check that it's really a file before adding
			allfiles.append(path)

	print('Preprocessing done!')
	return allfiles # Return a list of all processed files
