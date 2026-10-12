"""Axis-separated AABB movement against the tile grid and one-way platforms."""
import math

import pygame

from .level import TILE

GRAVITY = 0.62
MAX_FALL = 13.0


class Body:
    def __init__(self, x, y, w, h):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.platform = None       # moving platform currently stood on
        self.hit_wall = 0          # -1 / 1 when blocked horizontally this frame

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def bottom(self):
        return self.y + self.h

    def move(self, level, platforms=(), drop=False, gravity=GRAVITY):
        # ride moving platforms
        if self.platform is not None and self.platform.alive_platform:
            self.x += self.platform.dx
            self.y += self.platform.dy
        self.vy = min(MAX_FALL, self.vy + gravity)

        # ---- horizontal
        self.hit_wall = 0
        self.x += self.vx
        top = int(self.y) // TILE
        bot = int(self.y + self.h - 1) // TILE
        if self.vx > 0:
            tx = int(self.x + self.w - 1) // TILE
            if any(level.solid(tx, ty) for ty in range(top, bot + 1)):
                self.x = tx * TILE - self.w
                self.vx = 0
                self.hit_wall = 1
        elif self.vx < 0:
            tx = int(self.x) // TILE
            if any(level.solid(tx, ty) for ty in range(top, bot + 1)):
                self.x = (tx + 1) * TILE
                self.vx = 0
                self.hit_wall = -1

        # ---- vertical
        prev_bottom = self.y + self.h
        self.y += self.vy
        self.on_ground = False
        self.platform = None
        left = int(self.x) // TILE
        right = int(self.x + self.w - 1) // TILE
        if self.vy > 0:
            ty = int(self.y + self.h) // TILE
            land = None
            for tx in range(left, right + 1):
                if level.solid(tx, ty):
                    land = ty * TILE
                elif not drop and level.oneway(tx, ty) and prev_bottom <= ty * TILE + 0.01:
                    land = ty * TILE
            if land is not None:
                self.y = land - self.h
                self.vy = 0
                self.on_ground = True
            elif not drop:
                r = self.rect
                for p in platforms:
                    if not p.alive_platform:
                        continue
                    pr = p.rect
                    if r.right > pr.left and r.left < pr.right and prev_bottom <= pr.top + max(0.5, p.dy + 0.5) \
                            and self.y + self.h >= pr.top:
                        self.y = pr.top - self.h
                        self.vy = 0
                        self.on_ground = True
                        self.platform = p
                        p.stood_on = True
                        break
        elif self.vy < 0:
            ty = int(self.y) // TILE
            if any(level.solid(tx, ty) for tx in range(left, right + 1)):
                self.y = (ty + 1) * TILE
                self.vy = 0

    def ground_ahead(self, level, direction):
        """Is there floor just in front of our feet? (for edge-turning enemies)"""
        fx = self.x + self.w + 2 if direction > 0 else self.x - 2
        ty = int(self.y + self.h + 2) // TILE
        tx = int(fx) // TILE
        return level.solid(tx, ty) or level.oneway(tx, ty)


def approach(value, target, step):
    if value < target:
        return min(target, value + step)
    return max(target, value - step)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])
