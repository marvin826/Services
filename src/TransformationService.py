import ConsumerBase as cb 
import argparse
import json
import string

class TransformationService(cb.ConsumerBase):
	"""docstring for TransformationService"""
	def __init__(self):
		super(TransformationService, self).__init__()

		self.rulesObj = None

	def init(self):
		super(TransformationService, self).init()

		try:
			rulesFileName = self.arguments.rulesFile
			self.logger.info("TransformationService.init : Loading rules file : " + rulesFileName)
			rulesFile = open(rulesFileName)
			self.rulesObj = json.load(rulesFile)
			rulesFile.close()
		except Exception, e:
			self.logger.critical("TransformationService.init : Error : " + str(e))
			return			

	def onMessage(self, client, userdata, msg):
		super(TransformationService, self).onMessage(client, userdata, msg)

		self.logger.debug("TransformationService.onMessage : " + str(msg.payload))
		msgObj = json.loads(msg.payload)
					
		if "address" in msgObj:
			address = msgObj["address"]

			if address in self.rulesObj:

				rules = self.rulesObj[address]	
				variable = None		
				for transform in rules:
					if "variables" in transform:					
						variables = self.processVariables(address, transform["variables"], msgObj)
					else:
						print '"variables" not in transform: ' + str(transform)
						logMsg = "TransformationService.onMessage : No variables found for address : "
						logMsg += address
						self.logger.debug(logMsg)

					if "template" in transform: 
						message = self.generateMessage(address, transform["template"], \
							                           variables)

					if "topic" in transform:
						self.publishMessage(message, transform["topic"])
					else:
						logMsg = "TransformationService.onMessage : 'service' not found"
						self.logger.debug(logMsg)

	def parseArguments(self):
		
		parser = argparse.ArgumentParser(description="TransformationService")
		parser.add_argument('--logFile', 
							required=True,
			                help="Path to file where log messages are directed")
		parser.add_argument('--rulesFile', 
							required=True,
			                help="Path to file transformation rules are defined")
		arguments = parser.parse_args()

		return arguments	
		
	def processVariables(self, address, variables, msg):
		
		self.logger.debug("TransformationService.processVariables")
		self.logger.debug(msg)

		results = {}
		self.logger.debug("Variables before: ")
		for key in variables.keys():
			value = variables[key]
			self.logger.debug(key + " : " + str(variables[key]))

			path = string.split(value, '.')
			obj = msg
			for token in path:
				if token in obj:
					obj = obj[token]
				else:
					logMsg = "TransformationService.processVariables : Error : \n" \
						+ "'" + token + "' token from path '" + value \
						+ "' not found in message : " + str(msg)
					self.logger.critical(logMsg)
			results[key] = obj

		self.logger.debug("Variables: ")
		for key in results.keys():
			value = results[key]
			self.logger.debug(key + " : " + str(results[key]))

		return results

	def generateMessage(self, address, template, variables):

		self.logger.debug("TransformationService.generateMessge : ")
		self.logger.debug(str(address))
		self.logger.debug(str(template))
		self.logger.debug(str(variables))
		
		message = template
		for key in variables.keys():
			message = string.replace(message, str(key), str(variables[key]))

		self.logger.debug(str(message))

		return message


	def publishMessage(self, message, service):
		
		print "TransformationService.publishMessage : "
		print message
		print service

		self.client.publish(str(service), str(message))
		