import ConsumerBase as cb

consumerBase = cb.ConsumerBase()
consumerBase.init()
consumerBase.connect("sensor_reading", "127.0.0.1", 5250)
consumerBase.loop()



