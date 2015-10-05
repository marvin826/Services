import json

#
# import messages from the json file
#
try:
	msg_file = open("../data/TwitterMessages.json", 'r')
	messages = json.load(file)

	print str(messages)

except Exception, e:

	print "Error reading messages from file : " + str(e)

