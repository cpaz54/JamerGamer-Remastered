"""Fonts, text layout, menus and screen effects shared by every scene."""
import math
import random

import pygame

from .config import asset, NEON, NEON_DIM, WHITE, BLACK

_fonts = {}


def font(size, mono=False):
    key = (size, mono)
    if key not in _fonts:
        if mono:
            _fonts[key] = pygame.font.SysFont("couriernew,courier,monospace", size, bold=True)
        else:
            try:
                _fonts[key] = pygame.font.Font(asset("common", "PressStart2P.ttf"), size)
            except (OSError, FileNotFoundError):
                _fonts[key] = pygame.font.SysFont("courier", size, bold=True)
    return _fonts[key]


def wrap(text, fnt, max_width):
    """Split text into lines that fit max_width. Respects explicit newlines."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            trial = (line + " " + w).strip() if line else w
            if fnt.size(trial)[0] <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = w
        lines.append(line)
    return lines


def draw_text(surf, text, size, pos, color=WHITE, anchor="topleft", shadow=None, mono=False, alpha=255):
    fnt = font(size, mono)
    img = fnt.render(text, False, color)
    if alpha < 255:
        img.set_alpha(alpha)
    rect = img.get_rect(**{anchor: pos})
    if shadow:
        sh = fnt.render(text, False, shadow)
        if alpha < 255:
            sh.set_alpha(alpha)
        surf.blit(sh, rect.move(max(1, size // 8), max(1, size // 8)))
    surf.blit(img, rect)
    return rect


def draw_lines(surf, lines, size, x, y, color=WHITE, line_gap=1.6, anchor="left", shadow=None):
    h = int(size * line_gap)
    for i, line in enumerate(lines):
        if anchor == "center":
            draw_text(surf, line, size, (x, y + i * h), color, "midtop", shadow)
        else:
            draw_text(surf, line, size, (x, y + i * h), color, "topleft", shadow)
    return y + len(lines) * h


def panel(surf, rect, fill=(10, 14, 10), border=NEON, alpha=225, width=2):
    rect = pygame.Rect(rect)
    box = pygame.Surface(rect.size, pygame.SRCALPHA)
    box.fill((*fill, alpha))
    surf.blit(box, rect)
    pygame.draw.rect(surf, border, rect, width)


class Typewriter:
    """Reveals text a character at a time. Pauses briefly on punctuation."""

    def __init__(self, text, cps=38):
        self.text = text
        self.cps = cps
        self.shown = 0.0
        self.hold = 0.0

    @property
    def done(self):
        return self.shown >= len(self.text)

    def finish(self):
        self.shown = len(self.text)

    def update(self, dt):
        """Advance; returns number of new characters revealed this tick."""
        if self.done:
            return 0
        if self.hold > 0:
            self.hold -= dt
            return 0
        before = int(self.shown)
        self.shown = min(len(self.text), self.shown + self.cps * dt)
        after = int(self.shown)
        if after > before and self.text[after - 1] in ".?!":
            self.hold = 0.28
        elif after > before and self.text[after - 1] == ",":
            self.hold = 0.12
        return after - before

    @property
    def visible(self):
        return self.text[: int(self.shown)]


class Menu:
    """Vertical list of options navigated with arrows/WASD + Enter/Space."""

    def __init__(self, items, size=16, gap=34, color=NEON, dim=NEON_DIM):
        self.items = items          # list of (label, key) or callables producing label
        self.index = 0
        self.size = size
        self.gap = gap
        self.color = color
        self.dim = dim
        self.flash = 0.0

    def label(self, i):
        lbl = self.items[i][0]
        return lbl() if callable(lbl) else lbl

    @property
    def key(self):
        return self.items[self.index][1]

    def handle(self, event, audio=None):
        """Returns ('select', key) / ('left', key) / ('right', key) / None."""
        if event.type != pygame.KEYDOWN:
            return None
        k = event.key
        if k in (pygame.K_UP, pygame.K_w):
            self.index = (self.index - 1) % len(self.items)
            audio and audio.blip("move")
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.index = (self.index + 1) % len(self.items)
            audio and audio.blip("move")
        elif k in (pygame.K_LEFT, pygame.K_a):
            return ("left", self.key)
        elif k in (pygame.K_RIGHT, pygame.K_d):
            return ("right", self.key)
        elif k in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            audio and audio.blip("select")
            return ("select", self.key)
        return None

    def draw(self, surf, cx, y, t=0.0):
        for i in range(len(self.items)):
            sel = i == self.index
            text = self.label(i)
            if sel:
                text = "> " + text + " <"
            col = self.color if sel else self.dim
            if sel and int(t * 4) % 2 == 0:
                col = tuple(min(255, c + 60) for c in col)
            draw_text(surf, text, self.size, (cx, y + i * self.gap), col, "midtop", shadow=BLACK)


class CRT:
    """Scanlines + vignette overlay, cached per surface size."""

    def __init__(self):
        self._cache = {}

    def overlay(self, size, strength=60):
        key = (size, strength)
        if key not in self._cache:
            w, h = size
            s = pygame.Surface(size, pygame.SRCALPHA)
            for y in range(0, h, 3):
                pygame.draw.line(s, (0, 0, 0, strength), (0, y), (w, y))
            # vignette: concentric darkening rectangles
            steps = 24
            for i in range(steps):
                a = int(150 * (1 - i / steps) ** 2.2)
                inset = int(i * min(w, h) / (steps * 3.2))
                pygame.draw.rect(s, (0, 0, 0, a), (inset, inset, w - 2 * inset, h - 2 * inset), max(1, int(min(w, h) / (steps * 3.2)) + 1))
            self._cache[key] = s
        return self._cache[key]

    def apply(self, surf, t, glitch=0.0, strength=60):
        if glitch > 0 and random.random() < glitch:
            # horizontal tear
            h = surf.get_height()
            y = random.randrange(0, h - 8)
            band = random.randint(4, 24)
            shift = random.randint(-14, 14)
            strip = surf.subsurface((0, y, surf.get_width(), min(band, h - y))).copy()
            surf.blit(strip, (shift, y))
        surf.blit(self.overlay(surf.get_size(), strength), (0, 0))
        flick = int(8 + 6 * math.sin(t * 50))
        if flick > 0:
            surf.fill((flick, flick, flick), special_flags=pygame.BLEND_RGB_SUB)


crt = CRT()


def blink(t, rate=1.6):
    return int(t * rate * 2) % 2 == 0
