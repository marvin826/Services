from ServiceBase import ServiceBase
import smtplib
import email.utils
from email.mime.text import MIMEText
import json

class SendMailService(ServiceBase):
	"""docstring for SendMailService"""
	def __init__(self):
		super(SendMailService, self).__init__()

		self.config = None

	def init(self):
		
		try:
			self.logger.info("SendMailService.init : Loading config file : " \
				      + self.arguments.configFile)
			cfile = open(self.arguments.configFile)
			self.config = json.load(cfile)
			cfile.close()
			loadConfiguration()

		except Exception, e:
			self.logger.critical("SendMailService.init : Error reading file : " \
				self.arguments.configFile) + " : " + str(e)
			return			

	def loadConfiguration(self):


	def onMessage(self, client, userdata, msg):
		super(SendMailService, self).onMessage(client, userdata, msg)
		self.logger.debug("SendMailService.onMessage")

		
	def addArguments(self):
		super(SendMailService, self).addArguments()

		self.argumentParser.add_argument('--configFile',
									     required=True,
									     help="File that contains mail services definitions")

