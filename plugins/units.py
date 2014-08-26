import re

import pint

class UnitsPlugin:
    def __init__(self, bot):
        self.bot = bot

    def startup(self, config):
        self.registry = pint.UnitRegistry()

        self.bot.registerCommand("convert", self.cmd_convert)

        #self.registerEvent("public_message", self.chatHandler)

    def shutdown(self):
        pass

    def strToUnit(self, string):
        try:
            unit = self.registry[string]
            return unit
        except pint.unit.UndefinedUnitError:
            return None
    
    def cmd_convert(self, issuedBy, data):
        if not data:
            return

        if len(data.split(" ")) != 2:
            self.bot.reply("Usage: convert [quantity] [unit]")
            return

        fromQ = data.split(" ")[0]
        toU = data.split(" ")[1]

        match = re.match("([-+]?\d*\.\d+|\d+)([A-Za-z]+)", fromQ)
        if match is None:
            self.bot.reply("'{}' is not a valid quantity".format(fromQ))
            return

        quant = match.group(1)
        quant = float(quant)

        unit = match.group(2)

        u = self.strToUnit(unit)
        if u is None:
            self.bot.reply("'{}' is not a valid unit".format(unit))
            return

        u2 = self.strToUnit(toU)
        if u2 is None:
            self.bot.reply("'{}' is not a valid unit".format(toU))

        try:
            result = (quant * u).to(u2)
        except pint.unit.DimensionalityError:
            self.bot.reply("{} and {} are incompatible units".format(unit, toU))
            return

        self.bot.reply("{0} -> {1} = {2:.2f}".format(fromQ, toU, result))
