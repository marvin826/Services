from ServiceBase import ServiceBase
import smtplib
import email.utils
from email.mime.text import MIMEText
import json
import os

class SendMailService(ServiceBase):
	"""docstring for SendMailService"""
	def __init__(self):
		super(SendMailService, self).__init__()

		self.mailConfig = None
		self.accounts = None
		self.templates = None
		self.templateDir = None

	def init(self):
		super(SendMailService, self).init()
		
		try:
			self.logger.info("SendMailService.init : Loading config file : " \
				      + self.arguments.configFile)
			cfile = open(self.arguments.configFile)
			self.mailConfig = json.load(cfile)
			cfile.close()

		except Exception, e:
			self.logger.critical("SendMailService.init : Error reading file : " \
				+ self.arguments.configFile + " : " + str(e))
			return	

		# get the template directory from my arguments and
		# make sure that directory exists
		self.templateDir = self.arguments.templateDir
		if not os.path.isdir(self.templateDir) :
			self.logger.critical("SendMailService.init : Error : " \
				+ "Given template directory \'" + self.templateDir \
				+ "\' does not exist")
			return
		
		self.loadConfiguration()		

	def loadConfiguration(self):

		self.logger.info("SendMailService.loadConfiguration")

		# make sure the right items where loaded from the file
		if "accounts" not in self.mailConfig :
			self.logger.critical("SendMailService.loadConfiguration : " \
				+ "Error : \"accounts\" objects not in config file : \n" \
				+ self.arguments.configFile)
			return

		if "templates" not in self.mailConfig : 
			self.logger.critical("SendMailService.loadConfiguration : " \
				+ "Error : \"templates\" objects not in config file : \n" \
				+ self.arguments.configFile)
			return

		# load the accounts listed in the config file.
		# we reference the accounts by the account name provided
		# in the json object
		self.accounts = {}
		for account in self.mailConfig["accounts"] :
			if "name" in account:
				self.accounts[account["name"]] = account
			else:
				self.logger.critical("SendMailService.loadConfiguration : " \
					+ "Error : \"name\" not in account")
				return

		# load the tempates list in the config file.
		# we reference the templates by the template name
		# provided in the json object
		for template in self.mailConfig["templates"] :
			self.accounts[template["name"]] = template

			# get the file name of the template to use and load it
			# in. We store the contents of the template as a string
			if "template" in template:
				try:
					template_file = open(self.templateDir + "/" + template["template"])
					template["template_string"] = template_file.read()

				except Exception, e:
					self.logger.critical("SendMailService.loadConfiguration : " \
						+ "Error reading template file : " + str(e))
					return

			else:
				self.logger.critical("SendMailService.loadConfiguration : " \
					+ "Error : \"template\" not in template : " \
					+ template["name"])
				return

	def onMessage(self, client, userdata, msg):
		super(SendMailService, self).onMessage(client, userdata, msg)
		self.logger.debug("SendMailService.onMessage : " + str(msg.payload))
		msgObj = json.loads(msg.payload)

		if "message" in msgObj : 
			message = msgObj["message"]

			if message in self.templates :

				template = self.templates[message]
				if "variables" in template :
					variables = self.processVariables(template["variables"],msgObj)
				else:
					self.logger.critical("SendMailService.onMessage : " \
						+ "Error : variables not provided in template for : " \
						+ message)
					return

				if "template_string" in template:
					body = self.generateMessage(template["template_string"], variables)
				else:
					self.logger.critical("SendMailService.onMessage : " \
						+ "Error : email template not provided in template for : " \
						+ message)
					return

				if "account" in template:
					self.sendMail(template["account"], body)
				else:
					self.logger.critical("SendMailService.onMessage : " \
						+ "Error : \"account\" not found in template for : " \
						+ message)
					return
			else:
				self.logger.critical("SendMailService.onMessage : " \
					+ "Error : Could not find \"" + message + "\" in templates")
				return
		else:
			self.logger.critical("SendMailService.onMessage : " \
				+ "Error : could not find \"message\" attribute in received message.")
			return

	def generateMessage(self, template, variables):
		self.logger.info("SendMailService.generateMessage")
		pass

	def sendMail(self, account, body):
		self.logger.info("SendMailService.sendMail")
		pass
		
	def addArguments(self):
		super(SendMailService, self).addArguments()

		self.argumentParser.add_argument('--configFile',
									     required=True,
									     help="File that contains mail services definitions")

		self.argumentParser.add_argument('--templateDir',
									     required=True,
									     help="Directory of template files")


		
	def processVariables(self, variables, msg):
		
		self.logger.debug("SendMail.processVariables")
		self.logger.debug(body)

		results = {}
		self.logger.debug("Variables before: ")
		for key in variables.keys():
			value = variables[key]
			self.logger.debug(key + " : " + str(variables[key]))

			path = None
			if "path" in value:
				path = value["path"]
			else:
				logMsg = "SendMail.processVariables : Error : \n" \
				         + "\"path\" not found in variable description."
				self.logger.critical(logMsg)

			path = string.split(path, '.')
			obj = msg
			for token in path:
				if token in obj:
					obj = obj[token]
				else:
					logMsg = "SendMail.processVariables : Error : \n" \
						+ "'" + token + "' token from path '" + value \
						+ "' not found in message : " + str(msg)
					self.logger.critical(logMsg)
					break

			if "selector" in value:
				selector = re.compile(value["selector"])
				match = selector.search(obj)
				if match is not None:
					obj = match.group(0)
				else:
					logMsg = "SendMail.processVariables : Error : \n" \
						+ "Could not find match for selector : '" \
						+ value["selector"] + "'"
					self.logger.critical(logMsg)
					break

			if "format" in value:
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

