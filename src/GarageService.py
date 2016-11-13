from SensorService import SensorService
import argparse
import logging
import json
import time

class GarageService(SensorService):
	"""docstring for GarageService"""
	def __init__(self):
		super(GarageService, self).__init__()

	def init(self):
		super(GarageService, self).init()

		self.logger.info("GarageService.init")

	def processMessage(self, msg):
		super(GarageService, self).processMessage(msg)

		try:
			self.logger.debug("GarageService.processMessage : " + str(msg))

			updateTime = time.localtime()

			packet = msg

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

			self.readingsLog.info(garageLogMessage)

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

			self.publishMessage(json.dumps(messageObject), self.arguments.outputQueueTopic)

		except Exception, e: 

			self.logger.critical("GarageService.processMessage : " + str(e))
