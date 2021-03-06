from ServiceBase import ServiceBase
from VariableProcessor import VariableProcessor
import paho.mqtt.client as mqtt
import json

class LimitsService(ServiceBase):
	"""docstring for LimitsService"""
	def __init__(self):
		super(LimitsService, self).__init__()

		self.subscribedTopics = {}
		self.operators = { "lt" : self.lessThan,
		                   "gt" : self.greaterThan,
		                   "eq" : self.equal,
		                   "le" : self.lessThanEqual,
		                   "ge" : self.greaterThanEqual,
		                   "in" : self.within,
		                   "out" : self.outside }
		self.varTypes = [ "float",
		                  "string", 
		                  "time",
		                  "integer" ]
       	self.limitTypes = [ "last",
                            "ave",
                            "max",
                            "min" ]
		self.setParams = [ "topic",
						   "limits", 
						   "variables" ]
		self.params = [ "op", 
		                "limit", 
		                "variable",
		                "type" ]

		# keep track of the variables listed in the limits. allows the 
		# calculation of statistics on each variable over time to allow
		# more complex limits
		self.variables = {}
		self.varStatistics = [ "last",
		                       "ave", 
		                       "max",
		                       "min" ]

	def init(self):
		super(LimitsService, self).init()

		self.logger.info("LimitsService.init")

		# load my configuration file
		limitsFile = self.arguments.limitsFile
		self.loadConfiguration(limitsFile)

		self.logger.info("LimitsService.init : Output topic : " + self.arguments.outputQueueTopic)

	def loadConfiguration(self, filename):
		confObj = None
		try:
			self.logger.info("LimitsService.loadConfiguration : Loading config file : " \
				      + filename)
			cfile = open(filename)
			confObj = json.load(cfile)
		except Exception, e:
			msg = "Could not load configuration file : " + filename + " : " + str(e)
			self.logger.critical("LimitsService.init : " + msg)
			return

		# configuration file consists of multiple limit sets. each
		# set is associated with a messaging topic, a set of variables, 
		# and a set of limits.
		for namedLimitSet in confObj.keys():

			setObj = confObj[namedLimitSet]

			# make sure all the limit set parameters have been specified
			for param in self.setParams:
				if param not in setObj:
					msg = "LimitsService.loadConfiguration : Error : " \
					   	  + param + " not found in limit set: " + namedLimitSet
					self.logger.critical(msg)
					return

			topic = setObj["topic"]
			if topic not in self.subscribedTopics:
				self.subscribedTopics[topic] = []

			limits = { "name" : namedLimitSet,
			           "limits" : setObj["limits"],
			           "variables" : setObj["variables"] }
			self.subscribedTopics[topic].append(limits)

	def onConnect(self, client, userdata, rc):
		self.logger.info("LimitsService.onConnect")

		# loop through the topics and subscribe
		for topic in self.subscribedTopics.keys():
			self.logger.info("LimitsService.onConnect : subscribing to topic : " + topic)
			try:
				client.subscribe(str(topic))
			except Exception, e:
				logMsg = "LimitsService.onConnect : Error subscribing to topic : " \
				          + topic + " : " + str(e)
				self.logger.critical(logMsg)

	def onMessage(self, client, userdata, msg):
		self.logger.debug("LimitsService.onMessage")
		
		if msg.topic not in self.subscribedTopics:
			logMsg = "LimitsService.onMessage : Received topic " \
			    + msg.topic + " which is not in limit file"
			self.logger.debug(logMsg)
			return

		msgObj = json.loads(msg.payload)

		limitsList = self.subscribedTopics[msg.topic]
		for limit in limitsList:

			# process the variables
			vp = VariableProcessor()
			vp.init(self.logger)
			if "variables" not in limit:
				logMsg = "LimitsService.onMessage : Error : \"variables\" not found."
				self.logger.critical(logMsg)
				return
			variables = vp.processVariables(limit["variables"], msgObj)
			# update the statistics of the variables if their type is "float"

			self.logger.debug("LimitsService.onMessage : variables : " + str(variables))

			# process the limits
			if "limits" not in limit:
				logMsg = "LimitsService.onMessage : Error : \"limits\" not found."
				self.logger.critical(logMsg)
				return
			limits = limit["limits"]

			if "name" not in limit:
				logMsg = "LimitsService.onMessage : Error : \"name\" not found."
				self.logger.critical(logMsg)
				return

			# now that we have the variables, we can process the limits
			self.processLimits(limit["name"], limits, variables, msgObj)


	def addArguments(self):
		super(LimitsService, self).addArguments()

		self.argumentParser.add_argument('--limitsFile',
										 required=True,
										 help="File that specifies the limits to be monitored")

	def publishMessage(self, topic, msgObj, key, desc) :
		self.logger.debug("LimitsService.publishMessage")

		try:
			msg = { "message" : topic,
					"content" : msgObj,
			        "limit" : key,
			        "description" : desc
			      }
			self.client.publish(self.arguments.outputQueueTopic,json.dumps(msg))
		except Exception, e:
			logMsg = "LimitsService.publishMessage : Error publishing limit message : " \
				+ str(e)
			self.logger.critical(logMsg)

		return

	def lessThan(self, limit, value):
		self.logger.debug("LimitsService.lessThan : " + str(limit) + "," + str(value))
		if value < limit:
			return True
		return False

	def greaterThan(self, limit, value):
		self.logger.debug("LimitsService.greaterThan : " + str(limit) + "," + str(value))
		if value > limit:
			return True
		return False

	def within(self, lower, upper, value):
		self.logger.debug("LimitsService.within : " + str(lower) + "," + str(upper) \
			+ "," + str(value))
		if value >= lower and value <= upper:
			return True
		return False

	def outside(self, lower, upper, value):
		self.logger.debug("LimitsService.outside : " + str(lower) + "," + str(upper) \
			+ "," + str(value))
		if value < lower or value > upper:
			return True
		return False

	def equal(self, limit, value):
		self.logger.debug("LimitsService.equal : " + str(limit) + "," + str(value))
		if value == limit:
			return True
		return False

	def lessThanEqual(self, limit, value):
		self.logger.debug("LimitsService.lessThanEqual : " + str(limit) + "," + str(value))
		if value <= limit:
			return True
		return False

	def greaterThanEqual(self, limit, value):
		self.logger.debug("LimitsService.greaterThanEqual : " + str(limit) + "," + str(value))
		if value >= limit:
			return True
		return False

	# process the limits for a given topic 
	def processLimits(self, topic, limits, variables, msgObj):
		self.logger.debug("LimitsService:processLimits")

		for key in limits:
			desc = limits[key]
			self.logger.debug("LimitsService.processLimits : " \
				+ "Processing " + str(key) + " : " + str(desc))

			for param in self.params:
				
				if param not in desc:
					logMsg = "LimitsService.processLimits : Error : " \
					    + param + " parameter not provided in limit : " + key
					self.logger.critical(logMsg)
					return

			if desc["op"] not in self.operators:
				logMsg = "LimitsService.processLimits : Error : " \
					+ desc["op"] + " is not a valid operator : " + key
				self.logger.critical(logMsg)
				return

			self.logger.debug("LimitsService.processLimits : op : " + desc["op"])
			func = self.operators[desc["op"]]

			if desc["variable"] not in variables:
				logMsg = "LimitsService.processLimits : Error : " \
					+ "Variable " + desc["variable"] + " from limit " + key \
					+ " not found in message."
				self.logger.critical(logMsg)
				return

			if desc["type"] not in self.limitTypes:
				logMsg = "LimitsService.processLimits : Error : " \
					+ "Type " + desc["type"] + " from limit " + key \
					+ " is not a valid limit type."
				self.logger.critical(logMsg)
				return

			# grab the value of the variable provided in the message
			# the value depends on the type given in the limits file
			value = 0.0
			try:
				value = float(variables[desc["variable"]])
			except Exception, e:
				logMsg = "LimitsService.processLimits : Error : " \
					+ "Error converting variable " + desc["variable"] + " value : " \
					+ variables[desc["variables"]] + " : " + str(e)
				self.logger.critical(logMsg)

			status = False
			limit = desc["limit"]
			if type(limit) is not list:
				logMsg = "LimitsService.processLimits : Error : " \
					+ "\"limit\" parameter is not a list : " + limit
				self.logger.critical(logMsg)
				return

			if len(limit) == 1 :				
				try:
					limit = float(limit[0])
				except Exception, e:
					logMsg = "LimitsService.processLimits : Error : " \
						+ "Error converting limit " + key + " value : " \
						+ limit[i] + " : " + str(e)
					self.logger.critical(logMsg)
					return

				status = func(limit,value)

			elif len(limit) == 2 : 

				for i in [0,1]:
					try:
						limit[i] = float(limit[i])
					except Exception, e:
						logMsg = "LimitsService.processLimits : Error : " \
							+ "Error converting limit " + key + " value : " \
							+ limit[i] + " : " + str(e)
						self.logger.critical(logMsg)
						return

				status = func(limit[0],limit[1],value)


			if status:
				self.publishMessage(topic, msgObj, key, desc)

