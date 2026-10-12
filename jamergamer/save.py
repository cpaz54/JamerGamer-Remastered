"""Persistent progress and settings, stored as JSON next to the game."""
import json
import os

from .config import SAVE_FILE

DEFAULTS = {
    "reached": 0,          # furthest story step index the player has unlocked
    "music_volume": 0.7,
    "sfx_volume": 0.8,
    "fullscreen": False,
    "rhythm_offset_ms": 0,
    "rhythm_tap_mode": False,
    "completed": False,
}


class Save:
    def __init__(self, path=SAVE_FILE):
        self.path = path
        self.data = dict(DEFAULTS)
        try:
            with open(path) as f:
                self.data.update(json.load(f))
        except (OSError, ValueError):
            pass

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.write()

    def write(self):
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(self.data, f, indent=2)
            os.replace(tmp, self.path)
        except OSError:
            pass
