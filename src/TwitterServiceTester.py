import TwitterService as ts

twitterService = ts.TwitterService()
twitterService.init()
twitterService.connect("twitter_service", "127.0.0.1", 5250)
twitterService.loop()



