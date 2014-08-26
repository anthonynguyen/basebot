class CorePlugin:
    def __init__(self, bot):
        self.bot = bot


    def startup(self):
        self.bot.registerCommand("help", self.cmd_help)
        self.bot.registerCommand("h", self.cmd_help)
        self.bot.registerCommand("plugins", self.cmd_plugins)

        self.bot.registerCommand("login", self.cmd_login, True)
        self.bot.registerCommand("reload", self.cmd_reload, True)
        self.bot.registerCommand("die", self.cmd_die, True)

    def shutdown(self):
        pass

    """
    #------------------------------------------#
    #             Event Handlers               #
    #------------------------------------------#
    """

    """
    #------------------------------------------#
    #               Commands                   #
    #------------------------------------------#
    """

    def cmd_help(self, issuedBy, data):
        """[command] - displays this message"""
        if data == "":
            for p in self.bot.plugins:
                for c in p.commands:
                    self.bot.reply("[{}] {}{} {}".format(p.name, self.bot.prefixes[0], c.name, c.function.__doc__))
        else:
            for p in self.bot.plugins:
                for c in p.commands:
                    if data == c.name:
                        self.bot.reply("[{}] {}{} {}".format(p.name, self.bot.prefixes[0], c.name, c.function.__doc__))
                        return
            self.bot.reply("Command not found: " + data)

    def cmd_plugins(self, issuedBy, data):
        """lists all the currently loaded plugins"""
        self.bot.reply("Plugins: " + ", ".join(p.name for p in self.bot.plugins))



    """
    #------------------------------------------#
    #             Admin Commands               #
    #------------------------------------------#
    """

    def cmd_login(self, issuedBy, data):
        """logs you in"""
        if issuedBy not in bot.loggedin:
            self.bot.loggedin.append(issuedBy)
            self.bot.reply("{} has logged in".format(issuedBy))
        else:
            self.bot.reply("You are already logged in")

    def cmd_die(self, issuedBy, data):
        """kills the bot"""
        if data:
            self.bot.die("{}".format(data))
        else:
            self.bot.die("Leaving")

    def cmd_reload(self, issuedBy, data):
        """reloads plugins"""
        self.bot.loadPlugins()
