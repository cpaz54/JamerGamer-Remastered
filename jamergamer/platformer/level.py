"""ASCII level parsing, tile collision queries and pre-rendered terrain.

Legend
  X  stone (solid)            -  wooden ledge (jump up through, S+jump drops)
  S  spikes                   ~  crumbling ledge
  P  player start             C  checkpoint banner
  G  exit gate                h  heart
  E  moth (walks, turns at edges)        F  flying moth
  b  spinning blade           B  blade moving horizontally between | markers
  Y  blade moving vertically between | markers
  H  3-wide platform moving horizontally between | markers
  V  3-wide platform moving vertically between | markers
  |  path marker (invisible)
"""
import random

import pygame

from . import assets

TILE = 40


class Level:
    def __init__(self, rows, theme="forest"):
        width = max(len(r) for r in rows)
        self.rows = [r.ljust(width) for r in rows]
        self.cols = width
        self.nrows = len(rows)
        self.w = self.cols * TILE
        self.h = self.nrows * TILE
        self.theme = theme
        self.spawns = []        # (char, tx, ty)
        self.start = (2, self.nrows - 3)
        for ty, row in enumerate(self.rows):
            for tx, ch in enumerate(row):
                if ch == "P":
                    self.start = (tx, ty)
                elif ch not in " X-S|":
                    self.spawns.append((ch, tx, ty))
        self.spike_rects = [pygame.Rect(tx * TILE + 4, ty * TILE + TILE // 2, TILE - 8, TILE // 2)
                            for ty, row in enumerate(self.rows) for tx, ch in enumerate(row) if ch == "S"]
        self.surface = None

    def char(self, tx, ty):
        if ty < 0 or ty >= self.nrows:
            return " "
        if tx < 0 or tx >= self.cols:
            return "X"
        return self.rows[ty][tx]

    def solid(self, tx, ty):
        return self.char(tx, ty) == "X"

    def oneway(self, tx, ty):
        return self.char(tx, ty) == "-"

    def marker_range(self, tx, ty, vertical):
        """Find the nearest | markers either side of (tx, ty) along a row/column."""
        if vertical:
            lo = hi = ty
            while lo > 0 and self.char(tx, lo - 1) != "|":
                lo -= 1
            while hi < self.nrows - 1 and self.char(tx, hi + 1) != "|":
                hi += 1
            return lo, hi
        lo = hi = tx
        while lo > 0 and self.char(lo - 1, ty) != "|":
            lo -= 1
        while hi < self.cols - 1 and self.char(hi + 1, ty) != "|":
            hi += 1
        return lo, hi

    # ------------------------------------------------------------ rendering
    def render(self):
        rng = random.Random(7)
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        stone = assets.img("terrain/stone.jpg", size=(TILE, TILE))
        shades = []
        for k in (255, 205, 165, 135):
            s = stone.copy()
            s.fill((k, k, min(255, k + 12)), special_flags=pygame.BLEND_RGB_MULT)
            shades.append(s)
        plank = assets.img("terrain/wood_platform.png", size=(TILE, TILE))
        plank_strip = plank.subsurface((0, int(TILE * 0.38), TILE, int(TILE * 0.32))).copy()
        moss = (60, 120, 50) if self.theme == "forest" else (120, 70, 140)
        for ty, row in enumerate(self.rows):
            for tx, ch in enumerate(row):
                x, y = tx * TILE, ty * TILE
                if ch == "X":
                    exposed_top = not self.solid(tx, ty - 1)
                    depth = 0
                    while depth < 3 and self.solid(tx, ty - depth - 1):
                        depth += 1
                    surf.blit(shades[depth], (x, y))
                    if not self.solid(tx - 1, ty):
                        pygame.draw.line(surf, (40, 40, 50), (x, y), (x, y + TILE - 1), 2)
                    if not self.solid(tx + 1, ty):
                        pygame.draw.line(surf, (40, 40, 50), (x + TILE - 1, y), (x + TILE - 1, y + TILE - 1), 2)
                    if not self.solid(tx, ty + 1):
                        pygame.draw.line(surf, (30, 30, 40), (x, y + TILE - 2), (x + TILE, y + TILE - 2), 3)
                    if exposed_top:
                        pygame.draw.rect(surf, moss, (x, y, TILE, 5))
                        for _ in range(3):
                            gx = x + rng.randrange(2, TILE - 2)
                            pygame.draw.line(surf, moss, (gx, y), (gx + rng.choice((-2, 2)), y - rng.randrange(2, 6)), 2)
                elif ch == "-":
                    surf.blit(plank_strip, (x, y))
                elif ch == "S":
                    self._spikes(surf, x, y)
        self.surface = surf
        return surf

    @staticmethod
    def _spikes(surf, x, y):
        base = y + TILE
        for i in range(4):
            sx = x + i * 10
            pts = [(sx, base), (sx + 5, base - 18), (sx + 10, base)]
            pygame.draw.polygon(surf, (175, 180, 195), pts)
            pygame.draw.polygon(surf, (90, 90, 105), pts, 1)
            pygame.draw.line(surf, (235, 235, 245), (sx + 5, base - 18), (sx + 3, base - 6))
