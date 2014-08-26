"""
#------------------------------------------#
#               Commands                   #
#------------------------------------------#
"""

def cmd_help(bot, issuedBy, data):
    """[command] - displays this message"""
    if data == "":
        for c in bot.commands:
            bot.reply("{}{} {}".format(bot.prefixes[0], c.name, c.function.__doc__))
    else:
        for c in bot.commands:
            if data == c.name:
                bot.reply("{}{} {}".format(bot.prefixes[0], c.name, c.function.__doc__))
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
    if issuedBy in bot.loggedin:
        if data:
            bot.die("{}".format(data))
        else:
            bot.die("Leaving")
    else:
        bot.reply("You don't have access to that command")

def cmd_reload(bot, issuedBy, data):
    """reloads commands"""
    bot.loadCommands()
    bot.reply("Commands reloaded")