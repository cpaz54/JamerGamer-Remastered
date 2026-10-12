"""Slice the huge Jamer Quest sprite sheets into small native-resolution frames.

The original sheets are 1024px-per-frame upscales of 16/32px pixel art (one
sheet is 9216x9216, ~340MB once decoded). This samples every frame back down
to 32x32 and writes them to assets/adventure/sprites/, which is what the game
actually loads.

Run from the project root:  python tools/slice_adventure_sprites.py
"""
import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "adventure", "source", "sheets")
OUT = os.path.join(ROOT, "assets", "adventure", "sprites")
SIZE = 32

SHEETS = {
    "TileSprites": "tile",
    "EnemySprites": "enemy",
    "Items": "item",
    "NPCSprites": "char",
    "AnimationSprites": "fx",
}
SINGLES = ["NPC", "Misc", "gravestone", "fence", "gold_key", "locked_door", "new_tree",
           "rock", "smoke", "spdr_ball", "green_bridge", "brown_bridge", "tree"]


def downsample(surface, rect):
    """Nearest-sample `rect` of `surface` to SIZE x SIZE, black -> transparent."""
    x0, y0, w, h = rect
    out = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for j in range(SIZE):
        sy = y0 + int((j + 0.5) * h / SIZE)
        for i in range(SIZE):
            sx = x0 + int((i + 0.5) * w / SIZE)
            c = surface.get_at((sx, sy))
            if c.a < 128 or (c.r < 6 and c.g < 6 and c.b < 6):
                continue
            out.set_at((i, j), (c.r, c.g, c.b, 255))
    return out


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    os.makedirs(OUT, exist_ok=True)
    for sheet, prefix in SHEETS.items():
        img = pygame.image.load(os.path.join(SRC, sheet + ".png"))
        with open(os.path.join(SRC, sheet + ".json")) as f:
            frames = json.load(f)["frames"]
        for name, data in frames.items():
            idx = int("".join(ch for ch in name.replace(".png", "") if ch.isdigit()))
            r = data["frame"]
            surf = downsample(img, (r["x"], r["y"], r["w"], r["h"]))
            pygame.image.save(surf, os.path.join(OUT, f"{prefix}{idx:02d}.png"))
        print(f"{sheet}: {len(frames)} frames")
    for name in SINGLES:
        img = pygame.image.load(os.path.join(SRC, name + ".png"))
        surf = downsample(img, (0, 0) + img.get_size())
        pygame.image.save(surf, os.path.join(OUT, name.lower() + ".png"))
    menu = os.path.join(ROOT, "assets", "adventure", "source", "menu")
    for name in ["full_heart", "half_heart", "no_heart"]:
        img = pygame.image.load(os.path.join(menu, name + ".png"))
        pygame.image.save(downsample(img, (0, 0) + img.get_size()), os.path.join(OUT, name + ".png"))
    print("done ->", OUT)


if __name__ == "__main__":
    main()
