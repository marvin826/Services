import ServiceBase as sb
import argparse
import logging
import json
import time

class GarageService(sb.ServiceBase):
	"""docstring for GarageService"""
	def __init__(self):
		super(GarageService, self).__init__()
		
		self.garageLog = None
		self.garageLogFile = None
		self.outTopic = None

	def init(self):
		super(GarageService, self).init()

		self.logger.debug("GarageService.init")

		# grab my arguments
		self.garageLogFile = self.arguments.garageLogFile
		self.outTopic = self.arguments.outTopic

		# setup the temperature log		
		garageLog = logging.getLogger("garage_readings")
		t_log_file = logging.FileHandler(self.garageLogFile)
		garageLog.addHandler(t_log_file)
		garageLog.setLevel(logging.INFO)
		self.garageLog = garageLog

		pass

	def onMessage(self, client, userdata, msg):
		super(GarageService, self).onMessage(client, userdata, msg)

		try:
			self.logger.debug("GarageService.onMessage : " + str(msg.payload))
			msgObj = json.loads(msg.payload)

			updateTime = time.localtime()

			packet = msgObj

			comps = packet["Components"]
			packetTimeStamp = packet["TimeStamp"]
			packetTime = packetTimeStamp.split("T")[1]
			packetDate = packetTimeStamp.split("T")[0]

			analog_values = comps["Analog Samples"]["values"]
			rVoltage = analog_values["Supply Voltage"]
			self.logger.debug("supply raw: " + str(rVoltage))
			rTempReading = analog_values["AD2"]
			self.logger.debug("temp raw: " + str(rTempReading))

			tempReading = (rTempReading * 1200.0) / 1023.0
			tempReading = (tempReading - 500.0) / 10.0
			tempReading = ((tempReading * 9.0) / 5.0) + 32.0
			self.logger.debug("temperature (F): " + str(tempReading))

			supplyVoltage = (rVoltage * 1200.0) / 1023.0
			supplyVoltage = supplyVoltage / 1000.0
			self.logger.debug("supply voltage (V): " + str(supplyVoltage))

			digital_values = comps["Digital Samples"]["values"]
			doorA = "Open"
			if(digital_values["AD1/DI O1"]):
			    doorA = "Closed"
			doorB = "Open"
			if(digital_values["AD0/DI O0"] ):
			    doorB = "Closed"

			garageLogMessage = "{0},{1},{2},{3},{4},{5}"
			garageLogMessage = garageLogMessage.format(packetTime,
			                                           packetDate,
			                                           tempReading,
			                                           doorA,
			                                           doorB,
			                                           supplyVoltage)

			self.garageLog.info(garageLogMessage)

			# now publish this out
			messageObject = {}

			messageObject["name"] = "GarageSensor"
			messageObject["address"] = packet['Components']['64-bit Source Address']['address']
			messageObject["time_stamp"] = packetTimeStamp
			messageObject["supply_voltage"] = { "value" : supplyVoltage, "units": "volts" }
			readings = {}
			readings["temperature"] = { "value" : tempReading, "units" : "degrees F" }
			readings["door_a"] = { "value" : doorA }
			readings["door_b"] = { "value" : doorB }
			messageObject["readings"] = readings

			self.publishMessage(json.dumps(messageObject), self.outTopic)

		except Exception, e:
			self.logger.critical("GarageService.onMessage : " + str(e))

	def addArguments(self):
		super(GarageService, self).addArguments()
		
		self.argumentParser.add_argument('--garageLogFile', 
							             required=True,
			                             help="Path to file where garage readings are logged")
		self.argumentParser.add_argument('--outTopic', 
							             required=True,
			                             help="MQTT topic used to send out garage messages")

	def publishMessage(self, message, topic):

		logMsg = "GarageService.publishMessage : \n" \
		         + str(message) + "\n" \
		         + str(topic) + "\n"
		self.logger.debug(logMsg)

		self.client.publish(str(topic), str(message))

