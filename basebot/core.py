class CorePlugin:
    def __init__(self, bot):
        self.bot = bot

    def startup(self, config):
        self.bot.registerCommand("help", self.cmd_help)
        self.bot.registerCommand("h", self.cmd_help)
        self.bot.registerCommand("plugins", self.cmd_plugins)

        self.bot.registerCommand("password", self.cmd_password, True)
        self.bot.registerCommand("login", self.cmd_login, True)
        self.bot.registerCommand("reload", self.cmd_reload, True)
        self.bot.registerCommand("die", self.cmd_die, True)

        self.bot.registerEvent("private_message", self.event_private_message)
        self.bot.registerEvent("public_message", self.event_public_message)
        self.bot.registerEvent("nick_change", self.event_nick_change)
        self.bot.registerEvent("user_part", self.event_user_part)
        self.bot.registerEvent("user_quit", self.event_user_quit)

    def shutdown(self):
        pass

    """
    #------------------------------------------#
    #             Event Handlers               #
    #------------------------------------------#
    """

    def event_private_message(self, ev):
        """
        + person who said it: ev.source
           + their nick: ev.source.nick

        + what they said: ev.arguments[0]
        """
        pass

    def event_public_message(self, ev):
        """
        + person who said it: ev.source
           + their nick: ev.source.nick

        + what they said: ev.arguments[0]
        """
        pass

    def event_nick_change(self, ev):
        """
        + old nick: ev.source.nick
        + new nick: ev.target
        """
        pass

    def event_user_part(self, ev):
        """
        + person who left: ev.source.nick
        """
        pass

    def event_user_quit(self, ev):
        """
        + person who left: ev.source.nick
        """
        pass

    """
    #------------------------------------------#
    #               Commands                   #
    #------------------------------------------#
    """

    def cmd_help(self, issuedBy, data):
        """[command] - displays this message"""
        if data == "":
            pref = self.bot.prefixes[0]
            for p in self.bot.plugins:
                cmds = [pref + c.name + ("*" if c.password else "")
                        for c in p.commands]
                self.bot.reply("[{}] {}".format(p.name, ", ".join(cmds)))
        else:
            for p in self.bot.plugins:
                for c in p.commands:
                    if data == c.name:
                        self.bot.reply(
                            "[{}] {}{} {}".format(
                                p.name, self.bot.prefixes[0],
                                c.name, c.function.__doc__)
                        )
                        return
            self.bot.reply("Command not found: " + data)

    def cmd_plugins(self, issuedBy, data):
        """lists all the currently loaded plugins"""
        self.bot.reply("Plugins: " +
                       ", ".join(p.name for p in self.bot.plugins))

    """
    #------------------------------------------#
    #             Admin Commands               #
    #------------------------------------------#
    """

    def cmd_password(self, issuedBy, data):
        """displays the bot's password"""
        self.bot.pm(issuedBy, "My password is: " + self.bot.password)

    def cmd_login(self, issuedBy, data):
        """logs you in"""
        # The login function is special in that it gets the full user object,
        # not just the nick
        host = issuedBy.host
        if host not in self.bot.loggedin:
            self.bot.loggedin.append(host)
            self.bot.reply("{} has logged in".format(issuedBy.nick))
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
