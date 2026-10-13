"""Persistent progress and settings, stored as JSON next to the game
(or in the browser's localStorage for the web build)."""
import json
import os
import sys

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


WEB = sys.platform == "emscripten"
WEB_KEY = "jamergamer_save"


def _local_storage():
    import platform          # pygbag's browser bridge
    return platform.window.localStorage


class Save:
    def __init__(self, path=SAVE_FILE):
        self.path = path
        self.data = dict(DEFAULTS)
        try:
            if WEB:
                raw = _local_storage().getItem(WEB_KEY)
                if raw:
                    self.data.update(json.loads(str(raw)))
            else:
                with open(path) as f:
                    self.data.update(json.load(f))
        except Exception:
            pass

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.write()

    def write(self):
        if WEB:
            try:
                _local_storage().setItem(WEB_KEY, json.dumps(self.data))
            except Exception:
                pass
            return
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(self.data, f, indent=2)
            os.replace(tmp, self.path)
        except OSError:
            pass
