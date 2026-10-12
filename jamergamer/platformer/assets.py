"""Image loading for the platformer (scaled once, cached)."""
import os

import pygame

from ..config import asset

_cache = {}


def img(rel, scale=None, height=None, size=None, flip=False, crop=False):
    """Load assets/platformer/<rel>, optionally cropped to its visible pixels
    and scaled by factor/height/size."""
    key = (rel, scale, height, size, flip, crop)
    if key in _cache:
        return _cache[key]
    path = asset("platformer", rel)
    try:
        surf = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 200))
    if crop:
        surf = surf.subsurface(surf.get_bounding_rect(min_alpha=40)).copy()
    w, h = surf.get_size()
    if size:
        surf = pygame.transform.smoothscale(surf, size)
    elif height:
        surf = pygame.transform.smoothscale(surf, (max(1, round(w * height / h)), height))
    elif scale:
        surf = pygame.transform.smoothscale(surf, (max(1, round(w * scale)), max(1, round(h * scale))))
    if flip:
        surf = pygame.transform.flip(surf, True, False)
    _cache[key] = surf
    return surf


def frames(folder, **kw):
    path = asset("platformer", folder)
    names = sorted(n for n in os.listdir(path) if n.endswith(".png"))
    return [img(f"{folder}/{n}", **kw) for n in names]


def white(surf):
    """Solid white silhouette (for hit flashes)."""
    key = ("white", id(surf))
    if key not in _cache:
        s = surf.copy()
        s.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
        _cache[key] = s
    return _cache[key]


def tinted(surf, color):
    key = ("tint", id(surf), color)
    if key not in _cache:
        s = surf.copy()
        s.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        _cache[key] = s
    return _cache[key]


def background(rel, size):
    key = ("bg", rel, size)
    if key not in _cache:
        surf = pygame.image.load(asset("platformer", rel)).convert()
        w, h = surf.get_size()
        scale = max(size[0] / w, size[1] / h)
        _cache[key] = pygame.transform.smoothscale(surf, (int(w * scale) + 1, int(h * scale) + 1))
    return _cache[key]
