import ConsumerBase as cb
import json
import Queue
import twitter

class TwitterService(cb.ConsumerBase):
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

			keysFile = open("/home/gkaiser/Projects/Services/data/twitter_keys.json")
			twitterKeys = json.load(keysFile)
			keysFile.close()
		except Exception, e:
			print "TwitterService.init : Error reading file : " + str(e)
			return

		if 'kwtester' not in twitterKeys:
			print "TwitterService.init : kwtester credentials not found"
			return
		credentials = twitterKeys['kwtester']

		if ('consumer key' not in credentials) :
			self.message_log.critical("TwitterHelper.init 'consumer key' missing")	
			return
		self.consumer_key = credentials['consumer key']
		
		if ('consumer secret' not in credentials) :
			self.message_log.critical("TwitterHelper.init 'consumer secret' missing")	
			return
		self.consumer_secret = credentials['consumer secret']

		if ('access token' not in credentials) :
			self.message_log.critical("TwitterHelper.init 'access token' missing")	
			return
		self.access_token = credentials['access token']

		if('access token secret' not in credentials) :
			self.message_log.critical("TwitterHelper.init 'access token secret' missing")
			return
		self.access_token_secret = credentials['access token secret']

		self.credentials = credentials

		self.api = twitter.Api(self.consumer_key,
							   self.consumer_secret,
							   self.access_token,
							   self.access_token_secret)

		self.messageQueue = Queue.Queue(25)
		print "TwitterHelper initialized successfully"

	def onMessage(self, client, userdata, msg):

		if (self.messageQueue is not None):

			msgObj = json.loads(msg.payload)

			twitMsg = msgObj['time_stamp'] + " " \
			          + str(msgObj['readings']['temperature']['value'])
			self.messageQueue.put(twitMsg)

		try:
			while not self.messageQueue.empty():
				if self.nextMessage is None:
					self.nextMessage = self.messageQueue.get(False)

				self.api.PostUpdate(self.nextMessage)
				self.nextMessage = None
		except twitter.error.TwitterError, te:
			print "TwitterService.onMessage : PostUpdate failed. Tweet queued."
		except Exception, e:
			print "TwitterService.onMessage : Exception : " + str(e)
		else:
			print "TwitterService : message tweeted successfully"

