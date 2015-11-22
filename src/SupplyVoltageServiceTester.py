import SupplyVoltageService as svs

supplyVoltageService = svs.SupplyVoltageService()
supplyVoltageService.init()
supplyVoltageService.connect()
supplyVoltageService.loop()



