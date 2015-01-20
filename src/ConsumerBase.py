import paho.mqtt.client as mqttc

class ConsumerBase(object):
	"""docstring for ConsumerBase"""
	def __init__(self):
		super(ConsumerBase, self).__init__()

		self.client = None
		self.topic = None

	def init(self):
		print "ConsumerBase:init"
		self.client = mqttc.Client()

		def connectCB(client, userdata, rc) :
			self.onConnect(client, userdata, rc)

		def messageCB(client, userdata, msg) :
			self.onMessage(client, userdata, msg)


		self.client.on_connect = connectCB
		self.client.on_message = messageCB

	def onConnect(self, client, userdata, rc):
		print "ConsumerBase:onConnect"
		client.subscribe(self.topic)
		pass

	def onMessage(self, client, userdata, msg):
		print "ConsumerBase:onMessage"
		print(msg.topic + " " + str(msg.payload))

	def connect(self, topic, address, port, timeout=60):
		print "ConsumerBase:connect"

		if self.client is None:
			print "ConsumerBase.connect : MQTT client is None"
			return
			
		self.client.will_set("/event/dropped", "Sorry, I seem to have died.")
		self.topic = topic
		self.client.connect(address, port, timeout)

	def loop(self):
		print "ConsumerBase:loop"

		self.client.loop_forever()

