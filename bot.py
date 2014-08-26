#!/usr/bin/env python

import importlib
import inspect
import json
import pkgutil
import re
import random

import irc.bot
import sqlite3

import plugins

class Plugin:
    def __init__(self, name, module, pluginObject):
        self.name = name
        self.module = module

        self.obj = pluginObject

        self.commands = []
        self.eventHandlers = []

        self.databaseConnection = sqlite3.connect("database/{}.sqlite".format(name))

class Command:
    def __init__(self, name, function, password = False):
        self.name = name
        self.function = function
        self.password = password

class EventHandler:
    def __init__(self, event, function):
        self.event = event
        self.function = function

def genRandomString(length):
    alpha = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(alpha) for _ in range(length))

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        self.channel = config["channel"]
        self.target = self.channel
        self.prefixes = config["prefixes"]
        self.owners = config["owners"]
        self.loggedin = self.owners

        self.plugins = []
        self.loadPlugins(True)

        print("Starting bot")
        super(Bot, self).__init__([(config["server"], config["port"])], config["nick"], config["nick"])

        # Adds a Latin-1 fallback when UTF-8 decoding doesn't work
        irc.client.ServerConnection.buffer_class = irc.buffer.LenientDecodingLineBuffer

    def loadPlugins(self, first = False):
        if not first:
            importlib.reload(plugins)

        currentNames = [p.name for p in self.plugins]
        oldPlugins = self.plugins
        self.plugins = []
        for importer, mod, ispkg in pkgutil.iter_modules(plugins.__path__):
            if mod in currentNames:
                m = next((p for p in oldPlugins if p.name == mod), None)
                m.obj.shutdown()

                m = m.module
                importlib.reload(m)
            else:
                m = importlib.import_module("plugins." + mod)


            for attr in dir(m):
                if attr[-6:] == "Plugin":
                    plugClass = getattr(m, attr)
                    p = plugClass(self)

                    ourPlugin = Plugin(mod, m, p)
                    self.plugins.append(ourPlugin)

                    if first:
                        print("[{}] loaded".format(mod))
                    else:
                        self.reply("[{}] loaded".format(mod))

                    p.startup()
                    
                    break

    def registerCommand(self, name, function, password = False):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0]).__name__
        
        # This should be guaranteed not to be None, but we'll handle None anyway
        plug = next((p for p in self.plugins if p.module.__name__ == module), None)
        if plug is None:
            return

        plug.commands.append(Command(name, function, password))



    _EVENTS = [
        "private_message",
        "public_message",
        "nick_change",
        #"user_join"
        "user_part",
        "user_quit",
    ]
    def registerEvent(self, event, function):
        if event not in self._EVENTS:
            return

        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0]).__name__

        # This should be guaranteed not to be None, but we'll handle None anyway
        plug = next((p for p in self.plugins if p.module.__name__ == module), None)
        if plug is None:
               return

        plug.eventHandlers.append(EventHandler(event, function))

    def getCursor(self):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0]).__name__

        # This should be guaranteed not to be None, but we'll handle None anyway
        plug = next((p for p in self.plugins if p.module.__name__ == module), None)
        if plug is None:
            return

        return plug.databaseConnection.cursor()



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
        for p in self.plugins:
            for h in p.eventHandlers:
                if h.event == "private_message":
                    h.function(ev)
        self.parseChat(ev, True)

    def on_pubmsg(self, conn, ev):
        for p in self.plugins:
            for h in p.eventHandlers:
                if h.event == "public_message":
                    h.function(ev)
        self.parseChat(ev)
        if self.password in ev.arguments[0]:
            self.new_password()

    def parseChat(self, ev, priv = False):
        if (ev.arguments[0][0] in self.prefixes):
            self.executeCommand(ev, priv)

    def _on_nick(self, conn, ev):
        for p in self.plugins:
            for h in p.eventHandlers:
                if h.event == "nick_change":
                    h.function(ev)
        old = ev.source.nick
        new = ev.target

        if old in self.loggedin:
            self.loggedin.remove(old)
            self.loggedin.append(new)

    # def _on_join(self, conn, ev):
    #     for p in self.plugins:
    #         for h in p.eventHandlers:
    #             if h.event == "user_join":
    #                 h.function(ev)

    def _on_part(self, conn, ev):
        for p in self.plugins:
            for h in p.eventHandlers:
                if h.event == "user_part":
                    h.function(ev)

    def _on_quit(self, conn, ev):
        for p in self.plugins:
            for h in p.eventHandlers:
                if h.event == "user_quit":
                    h.function(ev)

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
                        c.function(issuedBy, data)
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
