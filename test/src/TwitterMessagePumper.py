import json
import threading
import Queue
import paho.mqtt.client as mqttc
import datetime

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
		q.put(json.dumps(msg))

except Exception, e:

	print "Error reading messages from file : " + str(e)

#
# initialize the mqtt 
#
client = mqttc.Client()

def onConnect(client, userData, rc):
	client.subscribe("services.twitter")
client.on_connect = onConnect
client.will_set("services.event.dropped", "I've died")


try:
	client.connect("127.0.0.1", 5250, 600)
except Exception, e:
	print "Error: " + str(e)

#
# Setup a timer to push these messages every 
# five minutes
#
def publishMessage():
	print "Publish message..."
	msg = q.get()
	print str(msg)

	client.publish("services.twitter", str(msg))

	if not q.empty() :
		t = threading.Timer(300.0, publishMessage)
		t.start()
	else:
		print "message queue empty..."

#publishMessage()

#print "Timer started"

while True:

	message = raw_input("Message : ")
	print "Received message : " + message
	client.publish("services.twitter", message)
