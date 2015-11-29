import VariableProcessor as vp
import logging
import sys

def createMessageLog(level):

	loggingLevels = { "CRITICAL": 50,
				       "ERROR" : 40,
				       "WARNING" : 30,
				       "INFO" : 20, 
				       "DEBUG" : 10 }

	message_log = logging.getLogger("messages")
	m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	m_streamHandler = logging.StreamHandler()
	message_log.addHandler(m_streamHandler)

	# set the logging level
	lvlStr = level.upper()
	if lvlStr in loggingLevels:
		message_log.setLevel(loggingLevels[lvlStr])
		print "ServiceBase.createMessageLog : Level set to : " \
		      + lvlStr
		sys.stdout.flush()
		sys.stderr.flush()
	else:
		print "ServiceBase.createMessageLog : Error : " \
		      + "Log level given: " + lvlStr + " is not a valid level!"
		sys.stdout.flush()
		sys.stderr.flush()

	return message_log



varp = vp.VariableProcessor()
varp.init(createMessageLog("DEBUG"))

hashObj = {	
	"supply_voltage": {
		"units": "volts", 
		"value": 2.6087976539589444
	}, 
	"time_stamp": "2015-11-15T16:28:19", 
	"readings": {
		"temperature": {
			"units": "degrees F", 
			"value": 83.2551319648094
		}
	}, 
	"name": "WeatherSensor", 
	"address": "0013 a200 408b 4307"	
}

variableSpec = {
   "${VOLTS}" : { 
   		"path" : "supply_voltage.value", 
   		"format" : "{0:03.2f}" 
   	},
   "${VOLTSRAW}" : { 
   		"path" : "supply_voltage.value" 
   	},
   "${TIME}" : { 
   		"path" : "time_stamp", 
   		"selector" : "[012][0-9]:[0-5][0-9]:[0-5][0-9]" 
   	},
   "${ADDR}" : { 
   		"path" : "address" 
   	}
}


vrs = varp.processVariables(variableSpec, hashObj)

print vrs
