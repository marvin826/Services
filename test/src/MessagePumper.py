import json
import threading
import Queue
import paho.mqtt.client as mqttc
import datetime
import argparse

argParser = argparse.ArgumentParser("MessagePumper")
argParser.add_argument('--messageFile',
	                   required=True,
	                   help="File with messages to be delivered")
argParser.add_argument('--messageQueue',
	                   required=True,
	                   help="Name of message queue to publish on")
argParser.add_argument('--serverAddress',
	                   required=False,
	                   default="127.0.0.1",
	                   help="Address of message server. Default is localhost")
argParser.add_argument('--serverPort',
	                   required=False,
	                   default="5250",
	                   help="Port of message server. Default is 5250")
argParser.add_argument('--publishPeriod',
	                   required=False,
	                   default=60,
	                   help="Period with which messages are published. Default = 60 seconds")
arguments = argParser.parse_args()

# 
# declare a Queue to store the messages
#
q = Queue.Queue()

#
# import messages from the json file
#
try:
	msg_file = open(arguments.messageFile, 'r')
	msg_obj = json.load(msg_file)

	msg_list = msg_obj["messages"]
	print str(len(msg_list)) + " messages loaded."

	for msg in msg_list:
		q.put(json.dumps(msg))

except Exception, e:

	print "Error reading messages from file : " \
	      + arguments.messageFile + " Error: " + str(e)

#
# initialize the mqtt 
#
client = mqttc.Client()

def onConnect(client, userData, rc):
	client.subscribe("services.twitter")
client.on_connect = onConnect
client.will_set("services.event.dropped", "I've died")


try:
	client.connect(arguments.serverAddress, arguments.serverPort, 600)
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

	client.publish(arguments.messageQueue, str(msg))

	if not q.empty() :
		t = threading.Timer(arguments.publishPeriod, publishMessage)
		t.start()
	else:
		print "message queue empty..."

publishMessage()

print "Timer started"

# while True:

# 	message = raw_input("Message : ")
# 	print "Received message : " + message
# 	client.publish(arguments.messageQueue, message)
