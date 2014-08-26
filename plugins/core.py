"""
#------------------------------------------#
#               Commands                   #
#------------------------------------------#
"""

def cmd_help(bot, issuedBy, data):
    """[command] - displays this message"""
    if data == "":
        for p in bot.plugins:
            for c in p.commands:
                bot.reply("[{}] {}{} {}".format(p.name, bot.prefixes[0], c.name, c.function.__doc__))
    else:
        for p in bot.plugins:
            for c in p.commands:
                if data == c.name:
                    bot.reply("[{}] {}{} {}".format(p.name, bot.prefixes[0], c.name, c.function.__doc__))
                    return
        bot.reply("Command not found: " + data)


"""
#------------------------------------------#
#             Admin Commands               #
#------------------------------------------#
"""

def pw_cmd_login(bot, issuedBy, data):
    """logs you in"""
    if issuedBy not in bot.loggedin:
        bot.loggedin.append(issuedBy)
        bot.reply("{} has logged in".format(issuedBy))
    else:
        bot.reply("You are already logged in")

def pw_cmd_die(bot, issuedBy, data):
    """kills the bot"""
    if data:
        bot.die("{}".format(data))
    else:
        bot.die("Leaving")

def cmd_reload(bot, issuedBy, data):
    """reloads plugins"""
    bot.loadPlugins()