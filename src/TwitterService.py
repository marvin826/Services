from ServiceBase import ServiceBase
import json
import Queue
import twitter
import argparse
#import urllib3

# disable InsecurePlatformWarning (need to upgrade to python 2.7.9 to fix correctly)
#
# see:
# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
#rllib3.disable_warnings()

class TwitterService(ServiceBase):
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
			self.logger.critical("TwitterService.init 'consumer key' missing")	
			return
		self.consumer_key = credentials['consumer key']
		
		if ('consumer secret' not in credentials) :
			self.logger.critical("TwitterService.init 'consumer secret' missing")	
			return
		self.consumer_secret = credentials['consumer secret']

		if ('access token' not in credentials) :
			self.logger.critical("TwitterService.init 'access token' missing")	
			return
		self.access_token = credentials['access token']

		if('access token secret' not in credentials) :
			self.logger.critical("TwitterService.init 'access token secret' missing")
			return
		self.access_token_secret = credentials['access token secret']

		self.credentials = credentials

		self.api = twitter.Api(self.consumer_key,
							   self.consumer_secret,
							   self.access_token,
							   self.access_token_secret)

		self.messageQueue = Queue.Queue(25)
		self.logger.info("TwitterService initialized successfully")

	def onMessage(self, client, userdata, msg):
		super(TwitterService, self).onMessage(client, userdata, msg)
		self.logger.debug("TwitterService.onMessage")
		self.logger.debug("Payload : " + msg.payload)

		if (self.messageQueue is not None):

			msgObj = json.loads(msg.payload)

			service = msgObj['service']
			payload = msgObj['message']

			self.messageQueue.put(payload)

			while not self.messageQueue.empty():

				try:
					self.nextMessage = self.messageQueue.get(False)

				except Exception, e:
					msg = "TwitterService.onMessage : Error with message queue : " + str(e)
					self.logger.critical(msg)
					self.nextMessage = None
					break

				try:
					self.api.PostUpdate(self.nextMessage)
					self.nextMessage = None

				except twitter.error.TwitterError, te:

					# see if this is a duplicate status -- if so, dump
					# the existing message
					logMsg = ""
					if te[0]["code"] == 187:
						self.nextMessage = None

						logMsg = "TwitterService.onMessage : PostUpdate failed : " 
						logMsg += str(te[0]['message'])
						logMsg += " Tweet dropped."
					else :
						# put the message back so we can try to tweet
						# later
						self.messageQueue.put(self.nextMessage)

						logMsg = "TwitterService.onMessage : PostUpdate failed : " 
						logMsg += str(te[0]['message'])
						logMsg += " Tweet queued."

					self.logger.critical(logMsg)

				except Exception, e:
					msg = "TwitterService.onMessage : Error posting to Twitter : " \
							+ str(e)
					self.logger.critical(msg)


	def addArguments(self):
		super(TwitterService, self).addArguments()

		self.argumentParser.add_argument('--keyFile', 
							              required=True,
			                              help="File that contains keys for Twitter accounts")