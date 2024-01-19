import configparser
import shutil
import warnings
from pathlib import Path
from typing import Optional

import platformdirs

CACHE_DIR = Path(
    platformdirs.user_cache_dir(appname="spotify_to_ytmusic", appauthor=False, ensure_exists=True)
)
DEFAULT_PATH = CACHE_DIR.joinpath("settings.ini")
EXAMPLE_PATH = Path(__file__).parent.joinpath("settings.ini.example")


class Settings:
    config: configparser.ConfigParser
    filepath: Path = DEFAULT_PATH

    def __init__(self, filepath: Optional[Path] = None):
        self.config = configparser.ConfigParser(interpolation=None)
        if filepath:
            self.filepath = filepath
        if not self.filepath.is_file():
            try:
                # Migration path for pre 0.3.0
                shutil.copy(EXAMPLE_PATH.with_suffix(""), DEFAULT_PATH)
                warnings.warn(f"Moved {filepath} to {DEFAULT_PATH}", DeprecationWarning)
            except Exception as exc:
                raise FileNotFoundError(
                    f"No settings.ini found! Please run \n\n spotify_to_ytmusic setup"
                )
        self.config.read(self.filepath)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, section, key, value):
        self.config.set(section, key, value)

    def save(self):
        with open(self.filepath, "w") as f:
            self.config.write(f)
