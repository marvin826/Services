import ConsumerBase as cb
import json

class SupplyVoltageService(cb.ConsumerBase):
	"""docstring for SupplyVoltageService"""
	def __init__(self):
		super(SupplyVoltageService, self).__init__()
	
	def onMessage(self, client, userdata, msg):
		print "SupplyVoltageService:onMessage"

		jsonStr = msg.payload
		jsonObj = json.loads(jsonStr)

		supply_voltage_dict = jsonObj["supply_voltage"]
		supply_voltage = supply_voltage_dict["value"]

		if supply_voltage < 2.5:
			print "Warning: Supply voltage getting low: " + str(supply_voltage)
			return

		if supply_voltage <= 2.3:
			print "Critical: Supply voltage exhausted: " + str(supply_voltage)
			return

		print "Voltage is good: " + str(supply_voltage)


