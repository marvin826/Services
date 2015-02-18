import XbeeEndpointService as xb

xbeeEndpoint = xb.XbeeEndpointService()
xbeeEndpoint.init()
xbeeEndpoint.connect("xbee.endpoint", "127.0.0.1", 5250)
xbeeEndpoint.loop()