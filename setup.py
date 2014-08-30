#!/usr/bin/env python

import setuptools

setuptools.setup(
    name ="basebot",
    version = "1.0.4",
    license = "MIT",

    description = "a base IRC bot extensible with plugins",
    long_description = open("README.rst").read(),

    author = "Anthony Nguyen",
    author_email = "anknguyen@gmail.com",
    url = "https://github.com/clearskies/basebot",

    packages = ["basebot"],

    install_requires = [
        "irc == 8.9.1",
        "jaraco.timing == 1.0",
        "jaraco.util == 10.2",
        "more-itertools == 2.2",
        "six == 1.7.3"
    ],

    entry_points = {
        "console_scripts": ["basebot=basebot.bot:main"]
    }
)
