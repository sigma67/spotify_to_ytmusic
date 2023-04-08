import configparser
from pathlib import Path
from typing import Optional


class Settings:
    config: configparser.ConfigParser
    filepath: Path = Path(__file__).parent.joinpath("settings.ini")

    def __init__(self, filepath: Optional[Path] = None):
        self.config = configparser.ConfigParser(interpolation=None)
        if filepath:
            self.filepath = filepath
        if not self.filepath.is_file():
            raise FileNotFoundError(
                f"No settings.ini not found! Please run \n\n spotify_to_ytmusic setup"
            )
        self.config.read(self.filepath)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, section, key, value):
        self.config.set(section, key, value)

    def save(self):
        with open(self.filepath, "w") as f:
            self.config.write(f)
