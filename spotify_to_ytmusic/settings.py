import configparser
from pathlib import Path

import platformdirs

CACHE_DIR = Path(
    platformdirs.user_cache_dir(
        appname="spotify_to_ytmusic", appauthor=False, ensure_exists=True
    )
)
SPOTIPY_CACHE_FILE = CACHE_DIR / "spotipy.cache"
DEFAULT_PATH = CACHE_DIR / "settings.ini"
EXAMPLE_PATH = Path(__file__).parent / "settings.ini.example"


class Settings:
    config: configparser.ConfigParser
    filepath: Path = DEFAULT_PATH

    def __init__(self, filepath: Path | None = None):
        self.config = configparser.ConfigParser(interpolation=None)
        if filepath:
            self.filepath = filepath
        if not self.filepath.is_file():
            raise FileNotFoundError(
                "No settings.ini found! Please run \n\n spotify_to_ytmusic setup"
            )
        self.config.read(self.filepath)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, section, key, value):
        self.config.set(section, key, value)

    def save(self):
        with open(self.filepath, "w") as f:
            self.config.write(f)
