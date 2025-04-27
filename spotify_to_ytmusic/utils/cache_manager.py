import json

from spotify_to_ytmusic.settings import CACHE_DIR


class CacheManager:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "lookup.json"

    def load_lookup_table(self):
        try:
            with self.cache_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_to_lookup_table(self, table):
        with self.cache_file.open("w", encoding="utf-8") as f:
            json.dump(table, f, ensure_ascii=False)

    def remove_cache_file(self):
        if self.cache_file.is_file():
            self.cache_file.unlink()
