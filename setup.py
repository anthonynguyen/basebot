#!/usr/bin/env python

import setuptools

setuptools.setup(
    name ="basebot",
    version = "1.0.9",
    license = "MIT",

    description = "a base IRC bot extensible with plugins",
    long_description = open("README.rst").read(),

    author = "Anthony Nguyen",
    author_email = "anknguyen@gmail.com",
    url = "https://github.com/clearskies/basebot",

    packages = ["basebot"],

    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Communications :: Chat :: Internet Relay Chat"
    ],

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
