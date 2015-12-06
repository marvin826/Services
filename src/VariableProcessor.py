import string
import re

class VariableProcessor(object):
	"""docstring for VariableProcessor"""
	def __init__(self):
		super(VariableProcessor, self).__init__()

		self.logger = None

	def init(self, logger) : 

		self.logger = logger

	#
	# processVariables
	#
	# This method parses a hash object (hashObj) for values based on 
	# a variableSpec. The variableSpec describes the variables, including the path
	# the value of the variable can be retrieved from in the given hashObj.
	#
	def processVariables(self, variableSpec, hashObj):
		self.logger.debug("VariableProcessor.processVariables")

		results = {}
		self.logger.debug("Variables before: ")
		for key in variableSpec.keys():
			value = variableSpec[key]
			self.logger.debug(key + " : " + str(variableSpec[key]))

			path = None
			if "path" in value:
				path = value["path"]
			else:
				logMsg = "VariableProcessor.processVariables : Error : \n" \
				         + "\"path\" not found in variable description."
				self.logger.critical(logMsg)

			path = string.split(path, '.')
			obj = hashObj
			for token in path:
				if token in obj:
					obj = obj[token]
				else:
					logMsg = "VariableProcessor.processVariables : Error : \n" \
						+ "'" + str(token) + "' token from path '" + str(path) \
						+ "' not found in message : " + str(obj)
					self.logger.critical(logMsg)
					break

			if "selector" in value:
				selector = re.compile(value["selector"])
				match = selector.search(obj)
				if match is not None:
					obj = match.group(0)
				else:
					logMsg = "VariableProcessor.processVariables : Error : \n" \
						+ "Could not find match for selector : '" \
						+ value["selector"] + "'"
					self.logger.critical(logMsg)
					break

			if "format" in value:
				self.logger.debug("Format : " + value["format"])
				self.logger.debug("Value  : " + str(obj))
				formatStr = value["format"]
				obj = formatStr.format(obj)
			else:
				obj = str(obj)
			results[key] = obj

		self.logger.debug("Variables: ")
		for key in results.keys():
			value = results[key]
			self.logger.debug(key + " : " + str(results[key]))

		return results

	
