import ServiceBase as sb
import argparse
import logging
import json
import time

class WeatherService(sb.ServiceBase):
	"""docstring for WeatherService"""
	def __init__(self):
		super(WeatherService, self).__init__()
		
		self.temperatureLog = None
		self.temperatureLogFile = None
		self.outTopic = None

	def init(self):
		super(WeatherService, self).init()

		self.logger.debug("WeatherService.init")

		# grab my arguments
		self.temperatureLogFile = self.arguments.temperatureLogFile
		self.outTopic = self.arguments.outTopic

		# setup the temperature log		
		temperatureLog = logging.getLogger("temperatures")
		t_log_file = logging.FileHandler(self.temperatureLogFile)
		temperatureLog.addHandler(t_log_file)
		temperatureLog.setLevel(logging.INFO)
		self.temperatureLog = temperatureLog

		pass

	def onMessage(self, client, userdata, msg):
		super(WeatherService, self).onMessage(client, userdata, msg)

		self.logger.debug("WeatherService.onMessage : " + str(msg.payload))
		msgObj = json.loads(msg.payload)

		updateTime = time.localtime()

		packet = msgObj

		comps = packet["Components"]
		packetTimeStamp = packet["TimeStamp"]
		packetTime = packetTimeStamp.split("T")[1]
		packetDate = packetTimeStamp.split("T")[0]

		analog_values = comps["Analog Samples"]["values"]

		rTempReading = analog_values["AD0"]
		self.logger.debug("temp raw: " + str(rTempReading))
		rVoltage = analog_values["Supply Voltage"]
		self.logger.debug("supply raw: " + str(rVoltage))

		tempReading = (rTempReading * 1200.0) / 1023.0
		tempReading = (tempReading - 500.0) / 10.0
		tempReading = ((tempReading * 9.0) / 5.0) + 32.0
		self.logger.debug("temperature (F): " + str(tempReading))

		supplyVoltage = (rVoltage * 1200.0) / 1023.0
		supplyVoltage = supplyVoltage / 1000.0
		self.logger.debug("supply voltage (V): " + str(supplyVoltage))

		tempLogMessage = "{0},{1},{2},{3}"
		tempLogMessage = tempLogMessage.format(packetTime,
		                                       packetDate,
		                                       tempReading,
		                                       supplyVoltage)
		self.temperatureLog.info(tempLogMessage)

		# now publish this out
		messageObject = {}

		messageObject["name"] = "WeatherSensor"
		messageObject["address"] = packet['Components']['64-bit Source Address']['address']
		messageObject["time_stamp"] = packetTimeStamp
		messageObject["supply_voltage"] = { "value" : supplyVoltage, "units": "volts" }
		readings = {}
		readings["temperature"] = { "value" : tempReading, "units" : "degrees F" }
		messageObject["readings"] = readings

		self.publishMessage(json.dumps(messageObject), self.outTopic)


	def parseArguments(self):
		super(WeatherService, self).parseArguments()
		
		parser = argparse.ArgumentParser(description="WeatherService")
		parser.add_argument('--logFile', 
							required=True,
			                help="Path to file where log messages are directed")
		parser.add_argument('--loggingLevel', 
							required=False, default="INFO",
			                help="Level of logging to capture (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
		parser.add_argument('--temperatureLogFile', 
							required=True,
			                help="Path to file where temperatures are logged")
		parser.add_argument('--outTopic', 
							required=True,
			                help="MQTT topic used to send out weather messages")
		arguments = parser.parse_args()

		return arguments	

	def publishMessage(self, message, topic):

		logMsg = "WeatherService.publishMessage : \n" \
		         + str(message) + "\n" \
		         + str(topic) + "\n"
		self.logger.debug(logMsg)

		self.client.publish(str(topic), str(message))

