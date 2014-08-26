from twython import Twython

class TwitterPlugin:
    def __init__(self, bot):
        self.bot = bot

    def startup(self, config):
        self.API_KEY = config["API_KEY"]
        self.API_SECRET = config["API_SECRET"]
        self.OAUTH_TOKEN = config["OAUTH_TOKEN"]
        self.OAUTH_SECRET = config["OAUTH_SECRET"]

        self.username = config["username"]
        self.userid = config["userid"]

        self.twitter = Twython(self.API_KEY, self.API_SECRET,
                               self.OAUTH_TOKEN, self.OAUTH_SECRET)

    def shutdown(self):
        pass