import json
import threading
import Queue

# 
# declare a Queue to store the messages
#
q = Queue.Queue()

#
# import messages from the json file
#
try:
	msg_file = open("../data/TwitterMessages.json", 'r')
	msg_obj = json.load(msg_file)

	msg_list = msg_obj["messages"]
	print str(len(msg_list)) + " messages loaded."

	for msg in msg_list:
		q.put(msg)

except Exception, e:

	print "Error reading messages from file : " + str(e)

#
# Setup a timer to push these messages every 
# five minutes
#
def publishMessage():
	print "Publish message..."
	msg = q.get()
	print str(msg)
	if not q.empty() :
		t = threading.Timer(60.0, publishMessage)
		t.start()
	else:
		print "message queue empty..."

t = threading.Timer(60.0, publishMessage)
t.start()

print "Timer started"

