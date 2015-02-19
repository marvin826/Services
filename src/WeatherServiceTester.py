import WeatherService as ws

weatherService = ws.WeatherService()
weatherService.init()
weatherService.connect("xbee.packet", "127.0.0.1", 5250)
weatherService.loop()



