import SendMailService as svs

sendMailService = svs.SendMailService()
sendMailService.init()
sendMailService.connect()
sendMailService.loop()



