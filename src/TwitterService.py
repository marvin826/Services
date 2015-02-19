import ServiceBase as sb
import json
import Queue
import twitter
import argparse

class TwitterService(sb.ServiceBase):
	"""docstring for TwitterService"""
	def __init__(self):
		super(TwitterService, self).__init__()
		self.credentials = None
		self.api = None
		self.messageQueue = None
		self.nextMessage = None
		self.consumer_key = None
		self.consumer_secret = None
		self.access_token = None
		self.access_token_secret = None

	def init(self):
		super(TwitterService, self).init()

		twitterKeys = None
		try:
			keyFileName = self.arguments.keyFile
			self.logger.info("TwitterService.init : Loading key file : " + keyFileName)
			keyFile = open(keyFileName)
			twitterKeys = json.load(keyFile)
			keyFile.close()
		except Exception, e:
			self.logger.critical("TwitterService.init : Error reading file : " + str(e))
			return

		if 'kwtester' not in twitterKeys:
			self.logger.critical("TwitterService.init : kwtester credentials not found")
			return
		credentials = twitterKeys['kwtester']

		if ('consumer key' not in credentials) :
			self.logger.critical("TwitterHelper.init 'consumer key' missing")	
			return
		self.consumer_key = credentials['consumer key']
		
		if ('consumer secret' not in credentials) :
			self.logger.critical("TwitterHelper.init 'consumer secret' missing")	
			return
		self.consumer_secret = credentials['consumer secret']

		if ('access token' not in credentials) :
			self.logger.critical("TwitterHelper.init 'access token' missing")	
			return
		self.access_token = credentials['access token']

		if('access token secret' not in credentials) :
			self.logger.critical("TwitterHelper.init 'access token secret' missing")
			return
		self.access_token_secret = credentials['access token secret']

		self.credentials = credentials

		self.api = twitter.Api(self.consumer_key,
							   self.consumer_secret,
							   self.access_token,
							   self.access_token_secret)

		self.messageQueue = Queue.Queue(25)
		self.logger.info("TwitterHelper initialized successfully")

	def onMessage(self, client, userdata, msg):
		super(TwitterService, self).onMessage(client, userdata, msg)
		self.logger.debug("TwitterService.onMessage")
		self.logger.debug("Payload : " + msg.payload)

		if (self.messageQueue is not None):

			msgObj = json.loads(msg.payload)

			service = msgObj['service']
			payload = msgObj['message']

			self.messageQueue.put(payload)

		try:
			while not self.messageQueue.empty():
				if self.nextMessage is None:
					self.nextMessage = self.messageQueue.get(False)

				try:
					self.api.PostUpdate(self.nextMessage)
					self.nextMessage = None

				except twitter.error.TwitterError, te:

					# see if this is a duplicate status -- if so, dump
					# the existing message
					if te["code"] == 187:
						self.nextMessage = None
						logMsg = "TwitterService.onMessage : Duplicate message : "
						logMsg += str(te)
						logMsg += " Message removed."
						self.logger.critical(logMsg)
					else :
						logMsg = "TwitterService.onMessage : PostUpdate failed : " 
						logMsg += str(te)
						logMsg += " Tweet queued."
						self.logger.critical(logMsg)

		except Exception, e:
			self.logger.critical("TwitterService.onMessage : Exception : " + str(e))
		else:
			self.logger.debug("TwitterService : message tweeted successfully")


	def parseArguments(self):
		
		parser = argparse.ArgumentParser(description="TwitterService")
		parser.add_argument('--logFile', 
							required=True,
			                help="Path to file where log messages are directed")
		parser.add_argument('--loggingLevel', 
							required=False, default="INFO",
			                help="Level of logging to capture (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
		parser.add_argument('--keyFile', 
							required=True,
			                help="File that contains keys for Twitter accounts")
		arguments = parser.parse_args()

		return arguments