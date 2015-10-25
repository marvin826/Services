import smtplib
import email.utils
from email.mime.text import MIMEText
import json

mail_config = None
try:
	config = open("../data/sendmail.json")
	js = config.read()
	print js
	config.close()

	mail_config = json.loads(js)

except Exception, e:

	print "Error reading config file: " + str(e)

kwconfig = mail_config["accounts"][0]
fromaddr = kwconfig["from_addr"]
toaddr = 'marvin826@comcast.net'

msg = MIMEText("Test Message #2")
msg['To'] = email.utils.formataddr(('Recipient',toaddr))
msg['From'] = email.utils.formataddr((kwconfig["sender"], fromaddr))
msg['Subject'] = "Test Message #2"

try:

	server = smtplib.SMTP(str(kwconfig["server"]),str(kwconfig["port"]))

	server.ehlo()
	server.starttls()

	server.login(kwconfig["username"],kwconfig["password"])

	server.sendmail(fromaddr,toaddr,msg.as_string())

	server.quit()

except Exception, e: 

	print "Error sending mail : " + str(e)

