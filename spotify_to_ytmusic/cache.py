import bz2
import json
from pathlib import Path
from typing import Dict


class Cache:
    _cache: Dict[str, str]
    filepath: Path = Path(__file__).parent.joinpath("cache.bin")

    def __init__(self):
        self._cache = {}
        if self.filepath.is_file():
            self._load(self.filepath)

    def __contains__(self, item):
        return item in self._cache

    def __getitem__(self, key):
        return self._cache[key]

    def __setitem__(self, key, value):
        self._cache[key] = value

    def save(self):
        self._save(self.filepath)

    def _load(self, path: Path):
        with open(path, "rb") as file:
            data = bz2.decompress(file.read())

        self._cache.update(json.loads(data))

    def _save(self, path: Path):
        byte_data = json.dumps(self._cache)
        compressed_byte_data = bz2.compress(byte_data.encode("utf8"))
        with open(path, "wb") as file:
            file.write(compressed_byte_data)
