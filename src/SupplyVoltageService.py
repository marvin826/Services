from ServiceBase import ServiceBase
import json

class SupplyVoltageService(ServiceBase):
	"""docstring for SupplyVoltageService"""
	def __init__(self):
		super(SupplyVoltageService, self).__init__()
	
	def init(self):
		super(SupplyVoltageService, self).init()

		self.logger.info("SupplyVoltageService.init")

	def onMessage(self, client, userdata, msg):
		self.logger.info("SupplyVoltageService:processMessage")

		jsonStr = msg.payload
		jsonObj = json.loads(jsonStr)

		supply_voltage_dict = jsonObj["supply_voltage"]
		supply_voltage = supply_voltage_dict["value"]

		if supply_voltage < 2.5:
			self.logger.info("Warning: Supply voltage getting low: " + str(supply_voltage))
			return

		if supply_voltage <= 2.3:
			self.logger.info("Critical: Supply voltage exhausted: " + str(supply_voltage))
			return

		self.logger.info("Voltage is good: " + str(supply_voltage))


