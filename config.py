#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError


class Config:
    def __init__(self):
        # class variables
        self.content = None

        # select config file
        self.conf_file = Path("config.yml")
        if not Path.exists(self.conf_file):
            self.conf_file = Path("/etc/retiredmuc-bot.yml")

        # read config file
        self._read()

    def _read(self):
        """init the config object with this method"""
        self._check()

        # open file as an iostream
        with open(self.conf_file, "r", encoding="utf-8") as f:
            try:
                self.content = YAML(typ="safe").load(f)

            # catch decoding errors
            except (ParserError, ScannerError) as err:
                print(err, file=sys.stderr)
                exit(1)

    def _check(self):
        """internal method to check if the config file exists"""
        try:
            # if file is present continue
            if self.conf_file.exists():
                return

            # if not create a blank file
            else:
                self.conf_file.touch(mode=0o640)

        # catch permission exceptions as this tries to write to /etc/
        except PermissionError as err:
            print(err, file=sys.stderr)
            sys.exit(err.errno)

    def get(self, key: str = None, default: (str, int) = None) -> (dict, str, int, None):
        """method to retrieve the whole config data, a single value or the optional default value"""
        # if a special key is request, return only that value
        if key is not None:

            # safety measure
            if key in self.content:
                return self.content[key]

            # if a default value is given return that
            if default is not None:
                return default

            # if the key isn't part if self.content return None
            else:
                return None

        # else return everything
        return self.content
