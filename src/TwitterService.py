from ServiceBase import ServiceBase
import json
import Queue
import twitter
import argparse
import requests

# disable InsecurePlatformWarning (need to upgrade to python 2.7.9 to fix correctly)
#
# see:
# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
requests.packages.urllib3.disable_warnings()

class TwitterService(ServiceBase):
	"""docstring for TwitterService"""
	def __init__(self):
		super(TwitterService, self).__init__()
		self.credentials = None
		self.api = None

		# declare a dictionary that will be used to keep track
		# of the data and state associated with each twitter service
		# provided in the twitter keys file
		#
		# credentials and tweet_window are supplied in the services
		# file.
		#
		# we add the following items as state information:
		#
		# api - pointer to the Twitter API object for the given service
		# last_tweet_time - specifies the last time a tweet was made
		# message_queue - queue of messages that need to be tweeted
		# next_message - next message to be tweeted out
		self.twitter_services = None

		# declare a dictionary that will index into the services
		# specified in the twitter_services dictionary
		self.service_index = None

	def init(self):
		super(TwitterService, self).init()

		try:
			servicesFileName = self.arguments.servicesFile
			self.logger.info("TwitterService.init : Loading services file : " \
				+ servicesFileName)
			servicesFile = open(servicesFileName)
			self.twitter_services = json.load(servicesFile)
			servicesFile.close()
		except Exception, e:
			self.logger.critical("TwitterService.init : Error reading file : " \
				+ str(e))
			return

		if not self.loadTwitterServices():
			self.logger.critical("TwitterService.init : Error loading services")
			return

	def loadTwitterServices(self):

		if 'services' not in self.twitter_services :
			self.logger.critical("TwitterService.loadTwitterServices : " \
				+ "'services' not in services file")
			return False

		self.service_index = {}
		services = self.twitter_services['services']
		for service in services :

			# make sure this service has a name
			if 'name' not in service:
				self.logger.critical("TwitterService.loadTwitterServices : " \
					+ "'name' not in service")
			else:
				self.logger.info("TwitterService.loadTwitterServices : " \
					+ 'Loading service : ' + service['name'])

			# add this to the service_index for faster access
			self.service_index[service['name']] = service

			# verify that the Twitter credentials were provided
			if 'credentials' not in service:
				self.logger.critical("TwitterService.loadTwitterServices : " \
					+ "'credentials' not in service : " \
					+ service['name'])
				return False
			credentials = service['credentials']

			if ('consumer key' not in credentials) :
				self.logger.critical("TwitterService.loadTwitterServices : " \
					+ " 'consumer key' not provided for service : " \
					+ service['name'])	
				return False
			
			if ('consumer secret' not in credentials) :
				self.logger.critical("TwitterService.loadTwitterServices : " \
					+ " 'consumer secret' not provided for service : " \
					+ service['name'])	
				return False

			if ('access token' not in credentials) :
				self.logger.critical("TwitterService.loadTwitterServices : " \
					+ " 'access token' not provided for service : " \
					+ service['name'])	
				return False

			if('access token secret' not in credentials) :
				self.logger.critical("TwitterService.loadTwitterServices : " \
					+ " 'access token secret' not provided for service : " \
					+ service['name'])
				return False

			# create the Twitter API
			api = twitter.Api( credentials['consumer key'],
							   credentials['consumer secret'],
							   credentials['access token'],
							   credentials['access token secret'] )
			service['api'] = api

			# add a message queue for this service
			service['message_queue'] = Queue.Queue(25)
			service['next_message'] = None

			self.logger.info("TwitterService.loadTwitterServices : " \
				+ "Service '" + service['name'] + "'" \
				+ " initialized successfully")

		return True

	def onMessage(self, client, userdata, msg):
		super(TwitterService, self).onMessage(client, userdata, msg)
		self.logger.info("TwitterService.onMessage")
		self.logger.info("Payload : " + msg.payload)

		try :
			msgObj = json.loads(msg.payload)
		except Exception, e:
			self.logger.critical("TwitterService.onMessage : " \
				+ " Error loading json object : " \
				+ str(e))
			return
		
		if 'service' not in msgObj:
			self.logger.critical("TwitterService.onMessage : " \
				+ "'service' not provided in message : " \
				+ str(msg))
			return
		service_name = msgObj['service']

		if 'message' not in msgObj : 
			self.logger.critical("TwitterService.onMessage : " \
				+ "'message' not provided in message : " \
				+ str(msg))
			return
		payload = msgObj['message']

		# get the service that corresponds to this message
		if service_name not in self.service_index :
			self.logger.critical("TwitterService.onMessage : " \
				+ "Service '" + service_name + "' not found in service file")
			return
		service = self.service_index[service_name]

		# get the message queue
		messageQueue = service['message_queue']
		messageQueue.put(payload)

		# get the next_message pointer
		nextMessage = service['next_message']

		while not messageQueue.empty():

			try:
				nextMessage = messageQueue.get(False)

			except Exception, e:
				msg = "TwitterService.onMessage : Error with message queue : " \
					  + str(e)
				self.logger.critical(msg)
				nextMessage = None
				break

			try:
				service['api'].PostUpdate(nextMessage)
				nextMessage = None

			except twitter.error.TwitterError, te:

				# see if this is a duplicate status -- if so, dump
				# the existing message
				errCode = te[0][0]['code']
				errMsg = te[0][0]['message']

				logMsg = "TwitterService.onMessage : PostUpdate failed : " 
				logMsg += str(errMsg)

				if errCode == 187:
					self.nextMessage = None
					logMsg += " Tweet dropped."
				else :
					# put the message back so we can try to tweet
					# later
					messageQueue.put(nextMessage)
					logMsg += " Tweet queued."

				self.logger.critical(logMsg)

			except Exception, e:
				msg = "TwitterService.onMessage : Error posting to Twitter : " \
						+ str(e)
				self.logger.critical(msg)


	def addArguments(self):
		super(TwitterService, self).addArguments()

		self.argumentParser.add_argument('--servicesFile', 
							              required=True,
			                              help="File that contains service definitions")

	