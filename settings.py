import configparser
import sys
import types
import os

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '/settings.ini')

class settings(types.ModuleType):
    def __getitem__(self, key):
        return config[key]

sys.modules[__name__] = settings("settings")