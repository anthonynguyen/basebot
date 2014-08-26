#!/usr/bin/env python

import importlib
import json
import pkgutil
import re
import random

import irc.bot

import plugins

class Plugin:
    def __init__(self, name, module, commands):
        self.name = name
        self.module = module

        self.commands = commands

class Command:
    def __init__(self, name, function, password = False):
        self.name = name
        self.function = function
        self.password = password

def genRandomString(length):
    alpha = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(alpha) for _ in range(length))

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        super(Bot, self).__init__([(config["server"], config["port"])], config["nick"], config["nick"])
        self.channel = config["channel"]
        self.target = self.channel
        self.prefixes = config["prefixes"]
        self.owners = config["owners"]
        self.loggedin = self.owners

        self.plugins = []
        self.loadPlugins(True)

        # Adds a Latin-1 fallback when UTF-8 decoding doesn't work
        irc.client.ServerConnection.buffer_class = irc.buffer.LenientDecodingLineBuffer

    def loadPlugins(self, first = False):
        if not first:
            importlib.reload(plugins)

        currentNames = [p.name for p in self.plugins]
        newPlugins = []
        for importer, mod, ispkg in pkgutil.iter_modules(plugins.__path__):
            cmds = []
            if mod in currentNames:
                m = next((p for p in self.plugins if p.name == mod), None).module
                importlib.reload(m)
                if not first:
                    self.reply("[{}] reloaded".format(mod))
            else:
                m = importlib.import_module("plugins." + mod)
                if not first:
                    self.reply("[{}] loaded".format(mod))

            for attr in dir(m):
                if "cmd_" in attr:
                    offset = 4
                    pw = False
                    if "pw_" in attr:
                        offset += 3
                        pw = True

                    cmds.append(Command(attr[offset:], getattr(m, attr), pw))

            newPlugins.append(Plugin(mod, m, cmds))

        self.plugins = newPlugins


    """
    #------------------------------------------#
    #            IRC-Related Stuff             #
    #------------------------------------------#
    """
    
    def on_nicknameinuse(self, conn, ev):
        conn.nick(conn.get_nickname() + "_")
    
    def on_ping(self, conn, ev):
        self.connection.pong(ev.target)

    def say(self, msg):
        self.connection.privmsg(self.channel, msg)

    def pm(self, nick, msg):
        self.connection.privmsg(nick, msg)
    
    def reply(self, msg):
        self.connection.privmsg(self.target, msg)

    def on_welcome(self, conn, e):
        conn.join(self.channel)
        self.new_password()

    def _msg_owners(self, message):
        for owner in self.owners:
            self.pm(owner, message)

    def on_privmsg(self, conn, ev):
        self.parseChat(ev, True)

    def on_pubmsg(self, conn, ev):
        self.parseChat(ev)
        if self.password in ev.arguments[0]:
            self.new_password()

    def parseChat(self, ev, priv = False):
        if (ev.arguments[0][0] in self.prefixes):
            self.executeCommand(ev, priv)

    def _on_nick(self, conn, ev):
        old = ev.source.nick
        new = ev.target

        if old in self.loggedin:
            self.loggedin.remove(old)
            self.loggedin.append(new)

    def new_password(self):
        self.password = genRandomString(5)
        self._msg_owners("My password is: " + self.password)
        print("The password is: " + self.password)

    """
    #------------------------------------------#
    #            Command Execution             #
    #------------------------------------------#
    """

    def executeCommand(self, ev, priv):
        issuedBy = ev.source.nick
        text = ev.arguments[0][1:].split(" ")
        command = text[0].lower()
        data = " ".join(text[1:])

        if priv:
            self.target = issuedBy
        else:
            self.target = self.channel

        for p in self.plugins:
            for c in p.commands:
                if command == c.name:
                    if c.password and (data[:5] == self.password or issuedBy in self.loggedin) or\
                        not c.password:
                        c.function(self, issuedBy, data)
                        return
                    else:
                        self.reply("WRONG PASSWORD, NOB!")
                        return

        self.reply("Command not found: " + command)

def main():
    try:
        configFile = open("config.json", "r")
        config = json.loads(configFile.read())
    except:
        print("Invalid or missing config file. Check if config.json exists and follows the correct format")
        return

    bot = Bot(config)
    bot.start()

if __name__ == "__main__":
    main()
