import json
import os
import sys

_CONFIG = {
    "server": "irc.quakenet.org",
    "port": 6667,
    "prefixes": ".",
    "channel": "#channel",
    "nick": "basebot",
    "owners": ["owner"]
}

_DEFAULT_PATH = "~/.basebot/"


def try_create(path):
    print("Trying to create a config.json in " + path)

    try:
        configFile = open(path + "/config.json", "w")
    except:
        print("Unable to write to config.json in " + path)
        return False

    configFile.write(json.dumps(_CONFIG, indent=4))
    print("Wrote default config to config.json in " + path)
    return True


def try_basepath(path):
    fullPath = os.path.abspath(os.path.expanduser(path))
    print("Trying to load config from" + fullPath)

    try:
        configFile = open(fullPath + "/config.json")
    except FileNotFoundError:
        if try_create(fullPath):
            configFile = open(fullPath + "/config.json")
        else:
            return None
    except PermissionError:
        if fullPath == os.path.abspath(os.path.expanduser(_DEFAULT_PATH)):
            print("Cannot read from " + fullPath + ", exiting")
            return None
        else:
            return try_basepath(_DEFAULT_PATH)

    try:
        config = json.loads(configFile.read())
        config["path"] = fullPath
        print("Config loaded from " + fullPath)
        return config
    except:
        print("Invalid JSON in config file")
        return None


def load_config():
    if len(sys.argv) < 2:
        print("No runtime directory specified")
        tryPath = _DEFAULT_PATH
    else:
        tryPath = sys.argv[1]

    return try_basepath(tryPath)
