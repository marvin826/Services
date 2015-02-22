import paho.mqtt.client as mqttc
import argparse
import logging

class ServiceBase(object):
	"""docstring for ServiceBase"""
	def __init__(self):
		super(ServiceBase, self).__init__()

		self.client = None
		self.topic = None
		self.arguments = None
		self.argumentParser = None
		self.argDescription = "ServiceBase"


	def init(self):

		# setup argument parser
		# initialize the parser, add arguments to the parser,
		# then parse the arguments
		# split out into three functions for children to 
		# override
		self.initArgParse()
		self.addArguments()
		self.parseArguments()

		# create the logger for the service
		self.logger = self.createMessageLog()

		self.client = mqttc.Client()

		def connectCB(client, userdata, rc) :
			self.onConnect(client, userdata, rc)

		def messageCB(client, userdata, msg) :
			self.onMessage(client, userdata, msg)

		self.client.on_connect = connectCB
		self.client.on_message = messageCB

	def onConnect(self, client, userdata, rc):

		if self.logger is not None:
			self.logger.debug("ServiceBase.onConnect")

		client.subscribe(self.topic)

	def onMessage(self, client, userdata, msg):

		if self.logger is not None:
			self.logger.debug("ServiceBase.onMessage")
			self.logger.debug(msg.topic + " " + str(msg.payload))

	def connect(self, timeout=60):

		if self.logger is not None:
			self.logger.debug("ServiceBase.connect")
			self.logger.debug("Connect : " + str(self.arguments.messageQueueTopic) + " " + \
				              str(self.arguments.messageQueueAddress) + " " + \
				              str(self.arguments.messageQueuePort))

		if self.client is None:
			if self.logger is not None:
				self.logger.critical("ServiceBase.connect : MQTT client is None")
			return
			
		self.client.will_set("services.event.dropped", "Sorry, I seem to have died.")
		self.topic = self.arguments.messageQueueTopic

		try :
			self.client.connect(self.arguments.messageQueueAddress, 
				                self.arguments.messageQueuePort, timeout)
		except Exception, e:
			if self.logger is not None:
				self.logger.critical("ServiceBase.connect : Error : " + str(e))
				exit(0)

	def loop(self):

		if self.logger is not None:
			self.logger.debug("ServiceBase.loop")

		self.client.loop_forever()

	def initArgParse(self):

		self.argumentParser = argparse.ArgumentParser(self.argDescription)

	def addArguments(self):

		self.argumentParser.add_argument('--logFile', 
										 required=True,
			                             help="Path to file where log messages are directed")
		self.argumentParser.add_argument('--loggingLevel', 
										 required=False, default="INFO",
			                             help="Level of logging to capture (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
		self.argumentParser.add_argument('--messageQueueTopic', 
										 required=True,
			                             help="Topic service listens on for incoming messages")
		self.argumentParser.add_argument('--messageQueueAddress', 
										 required=False, default="127.0.0.1",
			                             help="Address of message broker used for messaging")
		self.argumentParser.add_argument('--messageQueuePort', 
										 required=False, default="5250",
			                             help="Port of message broker used for messaging")

	def parseArguments(self):

		self.arguments = self.argumentParser.parse_args()

	def createMessageLog(self):

		message_log = logging.getLogger("messages")
		m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		m_log_file = logging.FileHandler(self.arguments.logFile)
		m_log_file.setFormatter(m_formatter)
		m_streamHandler = logging.StreamHandler()
		message_log.addHandler(m_log_file)
		message_log.addHandler(m_streamHandler)
		message_log.setLevel(self.arguments.loggingLevel.upper())

		return message_log
