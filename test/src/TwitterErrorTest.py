import twitter
import time
import requests

# disable InsecurePlatformWarning (need to upgrade to python 2.7.9 to fix correctly)
#
# see:
# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
requests.packages.urllib3.disable_warnings()

#
# Test script to test the TwitterError exception
#

consumer_key = "HgChkVvwAr7jsveLXdgV39UbS"
consumer_secret = "EfZHb6s9YNAnBy2h2ZxCtW4smmLgqw4Jksk0loZ4JH7WoDA7TS"
access_token = "2902173967-IIE5Z1RoL749PnJBjRBqhz0ubhbd3LIRf1IPdiC"
access_token_secret = "wK4k2O135VtaafVW12Squ7gXkO2uiewYMBMU7L4LZc6Ds"


# initialize the API
print "TwitterTester : initializing API"
try:
	api = twitter.Api(consumer_key,
					  consumer_secret,
					  access_token,
					  access_token_secret)
except Exception, e:
	print "Error initializing API : " + str(e)
	exit(0)

print "TwitterTester : API initialized"

def postMessage (message):

	print "Posting message : " + message
	try:
		api.PostUpdate(message)

	except twitter.error.TwitterError, te:

		# see if this is a duplicate status -- if so, dump
		# the existing message
		print "TwitterTester : TwitterError caught: " + str(te)
		print "List[0] : " + str(te[0][0])
		print "Type : " + str(type(te))
		logMsg = ""
		if te[0][0]["code"] == 187:
			nextMessage = None

			logMsg = "TwitterTester.postMessage : PostUpdate failed : " 
			logMsg += str(te[0][0]['message'])
			logMsg += " Tweet dropped."

		print "Exception caught : " + logMsg

	except Exception, e:
		msg = "TwitterTester.postMessage : Error posting to Twitter : " \
				+ str(e)
		print "Exception caught : " + msg



# post a single message once
msg = "TwitterTester : posting single message : " + str(time.time())
postMessage(msg)

# post the same message twice
msg = "TwitterTester : Duplicate Test Message : " + str(time.time())
postMessage(msg)
postMessage(msg)