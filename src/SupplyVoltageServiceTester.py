import SupplyVoltageService as svs

supplyVoltageService = svs.SupplyVoltageService()
supplyVoltageService.init()
supplyVoltageService.connect("sensor_reading", "127.0.0.1", 5250)
supplyVoltageService.loop()



