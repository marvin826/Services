from xbeeframework import XBeeReader as xbr
from xbeeframework import XBeeConnection as xbc
from xbeeframework import XBeePacketHandler as xbph
from xbeeframework import XBeeFrameDatabase as xbfdb
from ServiceBase import ServiceBase
import traceback
import thread
import argparse
import json
import Queue

class XbeeEndpointService(ServiceBase):
	"""docstring for XbeeEndpointService"""
	def __init__(self):
		super(XbeeEndpointService, self).__init__()

		self.m_XBeeReader = None
		self.m_XBeeConnection = xbc.XBeeConnection()
		self.m_PacketQueue = Queue.Queue()
		self.m_MessageQueue = Queue.Queue()

		self.argDescription = "XbeeEndpointService"

		return

	def init(self):
		super(XbeeEndpointService, self).init()

		self.logger.info("XbeeEndpointService.init")

		# initialize the XBeeFramework components
		frameDB = xbfdb.XBeeFrameDatabase()
		frameDB.setLogger(self.logger)
		frameDB.read(self.arguments.frameDBFile)

		logString = "Successfully read database: " \
		    + self.arguments.frameDBFile
		self.logger.info(logString)

		handler = xbph.XBeePacketHandler()
		handler.setLogger(self.logger)
		handler.setDatabase(frameDB)

		self.m_XBeeReader = xbr.XBeeReader()
		self.m_XBeeReader.setLogger(self.logger)
		self.m_XBeeReader.setHandler(handler)

		thread.start_new_thread(self.runXBeeThread, (0,))

		return

	def addArguments(self):
		super(XbeeEndpointService, self).addArguments()

		print "XbeeEndpointService.addArguments"

		self.argumentParser.add_argument('--frameDBFile', 
									     required=True,
			                             help="Path to frame database for XBeeFramework")
		self.argumentParser.add_argument('--xbeeTopic', 
							             required=True,
			                             help="Topic used to send out recieved Xbee packets")
		self.argumentParser.add_argument('--commPort', 
							             required=True,
			                             help="Port Xbee radio is connected to")

	def runXBeeThread(self, threadID):

		try:
			self.m_XBeeConnection.open(self.arguments.commPort)

			logString = "Successfully opened COMM port : " \
			            + self.arguments.commPort
			self.logger.info(logString)

			self.m_XBeeReader.setConnection(self.m_XBeeConnection)
			self.m_XBeeReader.setPacketCallback(self.handleXbeePacket)
			self.m_XBeeReader.read(True)

		except Exception, e:
		    logString = "XbeeMain: Caught exception: " + str(e)
		    traceback.print_exc()
		    self.logger.critical(logString)
		    self.m_XBeeConnection.close()

		finally:
			self.m_XBeeConnection.close()

	def loop(self):

		# override parent loop so that we can look for outgoing messages
		self.logger.debug("XbeeEndpointService.init")

		while True:
			self.client.loop(timeout=1.0) # loop for one second

			while not self.m_PacketQueue.empty():
				packet = self.m_PacketQueue.get()
				self.client.publish(self.arguments.xbeeTopic, packet)
				dbgmsg = "XbeeEndpointService.loop : Message published to topic " \
				         + self.arguments.xbeeTopic + "; Message : " \
				         + packet
				self.logger.debug(dbgmsg)

	def onMessage(self, client, userdata, msg):

		logMsg = "XbeeEndpointService.onMessage" + msg.topic + " " + str(msg.payload)
		self.logger.info(logMsg)

	def handleXbeePacket(self, packet, env):

		self.logger.debug("XbeeEndpointService.handleXbeePacket")

		# check the frame type and make sure it's what we want
		frameType = packet["FrameType"]
		address = packet['Components']['64-bit Source Address']['address']

		self.logger.debug("received frame type: " + frameType)
		self.logger.debug("from address: " + address)

		self.m_PacketQueue.put(json.dumps(packet))

		return

