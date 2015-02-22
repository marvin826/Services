import XbeeEndpointService as xb

xbeeEndpoint = xb.XbeeEndpointService()
xbeeEndpoint.init()
xbeeEndpoint.connect()
xbeeEndpoint.loop()