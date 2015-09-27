from ServiceBase import ServiceBase
import argparse
import logging
import json
import time

class SensorService(ServiceBase):
	"""Base class for sensor processing. This class is intended to receive sensor packets and process them into sensor values."""
	def __init__(self):
		super(SensorService, self).__init__()
		
		self.readingsLog = None
		self.packetAddressFilter = None

	def init(self):
		super(SensorService, self).init()

		self.logger.info("SensorService.init")

		# setup the reading log		
		readingsLog = logging.getLogger("readings")
		t_log_file = logging.FileHandler(self.arguments.readingsLogFile)
		readingsLog.addHandler(t_log_file)
		readingsLog.setLevel(logging.INFO)
		self.readingsLog = readingscd Log

		# get the list of addresses to filter on
		packetFilterArg = self.arguments.packetAddrs
		packetAddressFilter = packetFilterArg.split(',')

		self.logger.debug("SensorService.init : packet filters : " \
			                + str(self.packetAddressFilter))


	def addArguments(self):
		super(SensorService, self).addArguments()
		
		self.argumentParser.add_argument('--readingsLogFile', 
							             required=True,
			                             help="Path to file where sensor readings are logged")
		self.argumentParser.add_argument('--packetAddrs', 
							             required=True,
			                             help="List of packet addresses to listen for")

	def publishMessage(self, message, topic):

		logMsg = "SensorService.publishMessage : \n" \
		         + str(message) + "\n" \
		         + str(topic) + "\n"
		self.logger.debug(logMsg)

		self.client.publish(str(topic), str(message))		

	def onMessage(self, client, userdata, msg):
		super(SensorService, self).onMessage(client, userdata, msg)

		try:
			self.logger.debug("SensorService.onMessage : " + str(msg.payload))
			msgObj = json.loads(msg.payload)

			# grab the packet address out of the packet and see if this is 
			# in our filter
			address = msgObj['Components']['64-bit Source Address']['address']

			if address in self.packetAddressFilter:
				self.processMessage(msgObj)
			else:
				self.logger.debug("SensorService.onMessage : filtered message : " + \
					str(msg))
		except Exception, e:
			self.logger.critical("SensorService.onMessage : Error : " + str(e))

	def processMessage(self, msg):

		self.logger.debug("SensorService.processMessage")


		