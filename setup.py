#!/usr/bin/env python

import setuptools

setuptools.setup(
    name ="basebot",
    version = "1.0.3",
    license = "MIT",

    description = "a base IRC bot extensible with plugins",
    long_description = open("README.rst").read(),

    author = "Anthony Nguyen",
    author_email = "anknguyen@gmail.com",
    url = "https://github.com/clearskies/basebot",

    packages = ["basebot"],

    entry_points = {
        "console_scripts": ["basebot=basebot.bot:main"]
    }
)
