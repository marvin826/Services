import paho.mqtt.client as mqttc
import argparse
import logging

class ServiceBase(object):
	"""docstring for ServiceBase"""
	def __init__(self):
		super(ServiceBase, self).__init__()

		self.client = None
		self.topic = None
		self.arguments = self.parseArguments()
		self.logger = self.createMessageLog()

	def init(self):
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

	def connect(self, topic, address, port, timeout=60):

		if self.logger is not None:
			self.logger.debug("ServiceBase.connect")
			self.logger.debug("Connect : " + str(topic) + " " + str(address) + " " + str(port))

		if self.client is None:
			if self.logger is not None:
				self.logger.critical("ServiceBase.connect : MQTT client is None")
			return
			
		self.client.will_set("/event/dropped", "Sorry, I seem to have died.")
		self.topic = topic

		try :
			self.client.connect(address, port, timeout)
		except Exception, e:
			if self.logger is not None:
				self.logger.critical("ServiceBase.connect : Error : " + str(e))
				exit(0)

	def loop(self):

		if self.logger is not None:
			self.logger.debug("ServiceBase.loop")

		self.client.loop_forever()

	def parseArguments(self):

		return None

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
