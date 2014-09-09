#!/usr/bin/env python

import importlib
import inspect
import json
import os
import pkgutil
import re
import random
import sqlite3
import sys
import time

import irc.bot

from . import configloader
from . import core

def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate

class PluginContainer:
    def __init__(self, name, module, pluginObject, basepath):
        self.name = name
        self.module = module

        self.obj = pluginObject

        self.commands = []
        self.eventHandlers = []

        if not os.path.exists(basepath + "/database"):
            os.makedirs(basepath + "/database")
        self.databaseConnection = sqlite3.connect(basepath + "/database/{}.sqlite".format(name))


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

        self.basepath = config["path"]
        sys.path.insert(0, self.basepath + "/plugins")

        try:
            self.autoRun = config["on_connect"]
        except:
            self.autoRun = None

        print("Starting bot")
        super(Bot, self).__init__([(config["server"], config["port"])], config["nick"], config["nick"])

        self.plugins = []
        self.loadPlugins(True)

        # Adds a Latin-1 fallback when UTF-8 decoding doesn't work
        irc.client.ServerConnection.buffer_class = irc.buffer.LenientDecodingLineBuffer

    def loadPlugins(self, first = False):
        currentNames = [p.name for p in self.plugins]
        oldPlugins = self.plugins
        self.plugins = []
        
        importlib.reload(core)
        p = core.CorePlugin(self)

        self.plugins.append(PluginContainer("core", core, p, self.basepath))

        p.startup(None)

        if first:
            print("[core] loaded")
        else:
            self.reply("[core] loaded")

        for importer, mod, ispkg in pkgutil.iter_modules(path = [self.basepath +
                                                         "/plugins"]):
            if mod in currentNames:
                m = next((p for p in oldPlugins if p.name == mod), None)
                m.obj.shutdown()

                m = m.module
                importlib.reload(m)
            else:
                m = importlib.import_module(mod)


            for attr in dir(m):
                if attr[-6:] == "Plugin":
                    plugClass = getattr(m, attr)

                    p = plugClass(self)

                    ourPlugin = PluginContainer(mod, m, p, self.basepath)
                    self.plugins.append(ourPlugin)
                    
                    # Try to load the plugin's config file
                    try:
                        pluginConf = open(
                            self.basepath + "/config/{}.json".format(mod))
                        conf = json.loads(pluginConf.read())
                        pluginConf.close()
                    except:
                        conf = None

                    p.startup(conf)

                    if first:
                        print("[{}] loaded".format(mod))
                    else:
                        self.reply("[{}] loaded".format(mod))

                    
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

    def getDatabase(self):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0]).__name__

        # This should be guaranteed not to be None, but we'll handle None anyway
        plug = next((p for p in self.plugins if p.module.__name__ == module), None)
        if plug is None:
            return None

        return plug.databaseConnection



    """
    #------------------------------------------#
    #            IRC-Related Stuff             #
    #------------------------------------------#
    """
    
    def on_nicknameinuse(self, conn, ev):
        conn.nick(conn.get_nickname() + "_")
    
    def on_ping(self, conn, ev):
        self.connection.pong(ev.target)

    @RateLimited(1.5)
    def say(self, msg):
        self.connection.privmsg(self.channel, msg)
    
    @RateLimited(1.5)
    def pm(self, nick, msg):
        self.connection.privmsg(nick, msg)
    
    @RateLimited(1.5)
    def reply(self, msg):
        self.connection.privmsg(self.target, msg)

    def on_welcome(self, conn, e):
        if self.autoRun is not None:
            for cmd in self.autoRun:
                conn.send_raw(cmd)
                print("Autorun command sent: " + cmd)
            time.sleep(5)

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
                        try:
                            c.function(issuedBy, data)
                        except Exception as e:
                            self.reply("The command failed:")
                            self.reply(e.__str__())
                        return
                    else:
                        self.reply("WRONG PASSWORD, NOB!")
                        return

        self.reply("Command not found: " + command)

def main():
    config = configloader.load_config()
    if config is None:
        quit()

    bot = Bot(config)
    bot.start()

if __name__ == "__main__":
    main()
