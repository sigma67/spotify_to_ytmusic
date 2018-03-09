import configparser
import sys
import types

config = configparser.ConfigParser()
config.read('settings.ini')

class settings(types.ModuleType):
    def __getitem__(self, key):
        return config[key]

sys.modules[__name__] = settings("settings")