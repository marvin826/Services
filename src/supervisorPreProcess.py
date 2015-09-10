import argparse
import re
import os
import time
from getvalues import resolve_values

argParse = argparse.ArgumentParser("supervisorPreProcess")
argParse.add_argument('--input',
						required=True,
						help="supervisord configuration file template")
argParse.add_argument('--output',
						required=True,
						help="name of output configuration file")
arguments = argParse.parse_args()

try:
	infile = open(arguments.input)

	# create a tmp file that we'll delete later
	tmpfilename = "/tmp/sprvdpp" + str(int(time.time())) + ".tmp"
	tmpfile = open(tmpfilename, 'w')

	# parse each section
	pattern = re.compile("\[[a-zA-Z0-9\:\-_]+\]")
	for line in infile:
		match = pattern.match(line)
		if match != None:
			
			# handle the preprocessor section
			if line.startswith("[preprocessor]") :
				lines = []
				for line2 in infile:
					match = pattern.match(line2)
					if match == None:
						lines.append(line2.rstrip())
					else:
					 	tmpfile.write(line2)
					 	break
			else:
				tmpfile.write(line)
		else:
			tmpfile.write(line)

	# close the files
	infile.close()
	tmpfile.close()

	# how do we deal with date/time?

except Exception, e:
	print e


# build the variables dictionary
vars = {}
pattern = re.compile("([a-zA-Z0-9_\-]+)=(.+)")
for line in lines:
	match = pattern.match(line)
	if match != None:
		vars[match.group(1)] = match.group(2)


# process the variables from the preprocessor section
try:

	# search for ${var} strings and replace with variables
	# from the preprocessor section
	resolve_values(vars)

except Exception, e:
	print e

# go through the tmp file and replace all the variables and
# write the results to the out file
try:

	tmpfile = open(tmpfilename)
	outfile = open(arguments.output, "w")

	linecnt = 0
	dtstamppat = re.compile("\$\{DTSTAMP=\"(\%[aAbBcdHIjmMpSUwWxXyYZ\%]+)\"")
	pattern = re.compile("\$\{[a-zA-Z0-9_]+\}")
	for line in tmpfile:
		match = pattern.findall(line)
		if len(match) > 0 :
			for var in match:
				pat = "\$\{" + var[2:-1] + "\}"
				line = re.sub(pat, vars[var[2:-1]], line)

		# see if there is a timestamp
		match = dtstamppat.findall(line)
		if len(match) > 0 :
			for var in match:
				pat = "\$\{DTSTAMP=\"" + var + "\"\}";
				line = re.sub(pat, time.strftime(var), line)

		outfile.write(line)
		linecnt += 1

except Exception, e:
	print e


os.remove(tmpfilename)
