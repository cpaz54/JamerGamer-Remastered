"""Render every platformer stage to PNGs (with entity markers) for quick review.

    python tools/preview_levels.py [out_dir]
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from jamergamer.platformer.level import Level, TILE  # noqa: E402
from jamergamer.platformer.levels import ARENA, STAGES  # noqa: E402

COLORS = {"P": (0, 255, 0), "E": (255, 120, 0), "F": (255, 0, 200), "b": (200, 200, 255), "B": (150, 150, 255),
          "Y": (150, 150, 255), "H": (160, 100, 50), "V": (160, 100, 50), "~": (200, 160, 120), "h": (255, 60, 60),
          "C": (60, 255, 120), "G": (255, 230, 0), "|": (90, 90, 90)}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "level_previews"
    os.makedirs(out, exist_ok=True)
    pygame.init()
    pygame.display.set_mode((1, 1))
    font = pygame.font.SysFont(None, 22)
    stages = [(s["name"], s["rows"], s["theme"]) for s in STAGES] + [("ARENA", ARENA, "hall")]
    for i, (name, rows, theme) in enumerate(stages):
        lv = Level(rows, theme)
        surf = pygame.Surface((lv.w, lv.h))
        surf.fill((25, 30, 45))
        surf.blit(lv.render(), (0, 0))
        for ty, row in enumerate(lv.rows):
            for tx, ch in enumerate(row):
                if ch in COLORS:
                    r = pygame.Rect(tx * TILE + 8, ty * TILE + 8, TILE - 16, TILE - 16)
                    pygame.draw.rect(surf, COLORS[ch], r, 0 if ch != "|" else 2)
                    surf.blit(font.render(ch, True, (0, 0, 0)), r.move(6, 2))
        for tx in range(0, lv.cols, 10):
            surf.blit(font.render(str(tx), True, (255, 255, 255)), (tx * TILE + 2, 2))
        path = os.path.join(out, f"{i}_{name.replace(' ', '_').lower()}.png")
        pygame.image.save(surf, path)
        print(path, lv.cols, "x", lv.nrows)


if __name__ == "__main__":
    main()
