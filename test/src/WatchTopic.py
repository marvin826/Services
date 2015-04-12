import paho.mqtt.client as mqttc
import argparse

#
# This is a utility function what will watch a given MQTT broker topic
# and dump any messages received to stdout
#

argumentParser = argparse.ArgumentParser("WatchTopic")

argumentParser.add_argument('--brokerAddress', 
							required=False,
							default="127.0.0.1",
			                help="IP address of MQTT broker for topic")

argumentParser.add_argument('--brokerPort', 
							required=True,
			                help="Port number of MQTT broker for topic")

argumentParser.add_argument('--topic', 
							required=True,
			                help="Topic to monitor")

arguments = argumentParser.parse_args()

client = mqttc.Client()

def onConnect (client, userData, rc):
	client.subscribe(arguments.topic)

def onMessage(client, userdata, msg):
	print msg.payload

client.on_connect = onConnect
client.on_message = onMessage
client.will_set("services.event.dropped", "Sorry, I seem to have died")

try:
	client.connect(arguments.brokerAddress, arguments.brokerPort, 60)
except Exception, e:
	print "Error: " + str(e)

client.loop_forever()

