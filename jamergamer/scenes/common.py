"""Bits shared by the story screens (puppet master art)."""
import pygame

from ..config import asset, NEON

_puppet = {}


def puppet(size):
    """Returns (closed, open) puppet faces scaled to `size` px tall, tinted green-ish."""
    if size not in _puppet:
        out = []
        for name in ("puppet_closed", "puppet_open"):
            try:
                img = pygame.image.load(asset("common", name + ".png")).convert_alpha()
            except (pygame.error, FileNotFoundError):
                img = pygame.Surface((100, 120))
                img.fill(NEON)
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * size / h), size))
            out.append(img)
        # make both frames identical size so the mouth flap doesn't jitter
        w = max(o.get_width() for o in out)
        frames = []
        for o in out:
            s = pygame.Surface((w, size), pygame.SRCALPHA)
            s.blit(o, ((w - o.get_width()) // 2, 0))
            frames.append(s)
        _puppet[size] = tuple(frames)
    return _puppet[size]


def tint(img, color):
    s = img.copy()
    s.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return s
