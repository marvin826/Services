import WeatherService as ws

weatherService = ws.WeatherService()
weatherService.init()
weatherService.connect()
weatherService.loop()



