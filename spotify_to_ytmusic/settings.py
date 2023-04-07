import configparser
import sys
import types
import os

config = configparser.ConfigParser(interpolation=None)
filepath = os.path.dirname(os.path.realpath(__file__)) + '/settings.ini'
config.read(filepath)


class Settings(types.ModuleType):

    def __getitem__(self, key):
        return config[key]

    def __setitem__(self, section, key, value):
        config.set(section, key, value)

    def save(self):
        with open(filepath, 'w') as f:
            config.write(f)



sys.modules[__name__] = Settings("settings")