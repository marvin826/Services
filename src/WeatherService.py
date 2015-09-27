from SensorService import SensorService
import argparse
import logging
import json
import time

class WeatherService(SensorService):
	"""docstring for WeatherService"""
	def __init__(self):
		super(WeatherService, self).__init__()

	def init(self):
		super(WeatherService, self).init()

		self.logger.info("WeatherService.init")

	def processMessage(self, msg):
		super(WeatherService, self).processMessage(msg)

		try:
			self.logger.debug("WeatherService.processMessage : " + str(msg))

			updateTime = time.localtime()

			packet = msg

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
			self.logger.debug("Logging message: " + tempLogMessage)
			self.readingsLog.info(tempLogMessage)

			# now publish this out
			messageObject = {}

			messageObject["name"] = "WeatherSensor"
			messageObject["address"] = packet['Components']['64-bit Source Address']['address']
			messageObject["time_stamp"] = packetTimeStamp
			messageObject["supply_voltage"] = { "value" : supplyVoltage, "units": "volts" }
			readings = {}
			readings["temperature"] = { "value" : tempReading, "units" : "degrees F" }
			messageObject["readings"] = readings

			self.logger.debug("WeatherService.processMessage publish: " + json.dumps(messageObject))
			self.publishMessage(json.dumps(messageObject), self.arguments.outputQueueTopic)

		except Exception, e:
			
			self.logger.critical("WeatherService.processMessage : " + str(e))