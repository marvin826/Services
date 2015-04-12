import argparse
import glob 
import threading
import json
import paho.mqtt.client as mqttc
from collections import deque

# This function will read temperatures from a csv file that has the following format:
#
# HH:MM:SS,YYYY-MM-DD,temerpature (f2.xx),supply voltage (f2.xx), light sensor (integer)
#
# Once read, this file will create a MQTT message with a JSON payload and publish
# the message via the given MQTT topic.
#
argumentParser = argparse.ArgumentParser("TemperaturePumper")

argumentParser.add_argument('--fileName', 
							required=True,
			                help="Fully qualified filename for temperature file")

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

argumentParser.add_argument('--interval', 
							required=False,
							type=int,
							default=60,
			                help="Interval messages are sent out on, in seconds")

argumentParser.add_argument('--sensorAddress', 
							required=False,
							default="FFFF FFFF FFFF FFFF",
			                help="Address of sensor to add to messages")

arguments = argumentParser.parse_args()

temperatures = deque()
fileName = arguments.fileName

client = mqttc.Client()

def onConnect(client, userData, rc):
	client.subscribe(arguments.topic)
client.on_connect = onConnect
client.will_set("services.event.dropped", "I've died")


try:
	client.connect(arguments.brokerAddress, arguments.brokerPort, 60)
except Exception, e:
	print "Error: " + str(e)

f = open(fileName)

for line in f:
	tokens = line.split(',')
	
	message = {}
	readings = {}
	temperature = {}
	supply_voltage = {}
	
	temperature["value"] = tokens[2]
	temperature["units"] = "degrees F"

	readings["temperature"] = temperature

	supply_voltage["value"] = tokens[3]
	supply_voltage["units"] = "volts"

	message["readings"] = readings
	message["time_stamp"] = tokens[1] + "T" + tokens[0]
	message["supply_voltage"] = supply_voltage
	message["name"] = "WeatherSensor"
	message["address"] = arguments.sensorAddress

	temperatures.append(message)


def t_func() :

	if temperatures:
		temp_message = json.dumps(temperatures.popleft())
		client.publish(arguments.topic, temp_message)

	t = threading.Timer(arguments.interval,t_func)
	t.start()

t = threading.Timer(arguments.interval,t_func)
t.start()

client.loop_forever()



