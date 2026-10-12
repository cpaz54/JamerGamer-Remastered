"""Paths, window settings and shared colours."""
import os
import sys


def _user_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, "JamerGamer")
    os.makedirs(path, exist_ok=True)
    return path


if getattr(sys, "frozen", False):
    # packaged build (PyInstaller): assets ship inside the bundle, saves go to the user's data folder
    ROOT = sys._MEIPASS
    SAVE_FILE = os.path.join(_user_data_dir(), "save.json")
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SAVE_FILE = os.path.join(ROOT, "save.json")
ASSETS = os.path.join(ROOT, "assets")

WINDOW_SIZE = (1280, 720)
FPS = 60
STEP = 1.0 / FPS
TITLE = "JamerGamer"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON = (57, 255, 20)
NEON_DIM = (20, 110, 10)
RED = (220, 30, 40)
GOLD = (255, 200, 60)
GREY = (140, 140, 150)


def asset(*parts):
    return os.path.join(ASSETS, *parts)
