import TransformationService as ts

transformService = ts.TransformationService()
transformService.init()
transformService.connect("sensor_reading", "127.0.0.1", 5250)
transformService.loop()



