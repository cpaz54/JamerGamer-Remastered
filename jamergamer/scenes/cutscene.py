"""The puppet master speaks between chapters."""
import math
import random

import pygame

from .. import ui
from ..config import BLACK, NEON, NEON_DIM
from ..scene import Scene
from .common import puppet

ADVANCE_KEYS = (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER, pygame.K_e)


class CutsceneScene(Scene):
    size = (960, 540)

    def __init__(self, app, sid, pages, controls=None, final=False):
        super().__init__(app)
        self.sid = sid
        self.pages = pages
        self.controls = controls or []
        self.final = final
        self.page = 0
        self.writer = ui.Typewriter(pages[0], cps=34)
        self.mouth = 0.0
        self.mouth_open = False
        self.leaving = False
        self.glitch = 0.0
        self.drone = None
        self.card_t = 0.0

    def enter(self):
        self.audio.stop_music(800)
        self.drone = self.audio.synth("cutscene_drone", freq=48, dur=4.0, wave="saw", vol=0.10,
                                      attack=1.0, decay=40.0, noise=0.12)
        if self.drone:
            self.drone.set_volume(0.5 * self.app.save["sfx_volume"])
            self.drone.play(loops=-1, fade_ms=1500)
        self.glitch = 0.6

    def exit(self):
        if self.drone:
            self.drone.fadeout(400)

    @property
    def last_page(self):
        return self.page == len(self.pages) - 1

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or event.key not in ADVANCE_KEYS or self.leaving:
            return
        if not self.writer.done:
            self.writer.finish()
            return
        if self.last_page:
            self.leaving = True
            self.audio.blip("select")
            self.app.story.complete()
        else:
            self.page += 1
            self.writer = ui.Typewriter(self.pages[self.page], cps=34)
            self.glitch = 0.35
            self.audio.blip("move")

    def update(self, dt):
        super().update(dt)
        new = self.writer.update(dt)
        if new:
            ch = self.writer.visible[-1:]
            if ch.strip() and int(self.writer.shown) % 2 == 0:
                self.audio.blip("type")
        # mouth flaps only while speaking
        talking = not self.writer.done and self.writer.hold <= 0
        self.mouth += dt
        if talking and self.mouth > 0.11:
            self.mouth = 0
            self.mouth_open = not self.mouth_open
        elif not talking:
            self.mouth_open = False
        self.glitch = max(0.0, self.glitch - dt * 0.8)
        if random.random() < 0.004:
            self.glitch = 0.4
        if self.writer.done and self.last_page:
            self.card_t += dt

    def draw(self, surf):
        w, h = surf.get_size()
        surf.fill(BLACK)
        # puppet with a slow breathing bob
        closed, opened = puppet(250)
        face = opened if self.mouth_open else closed
        bob = math.sin(self.t * 1.3) * 3
        jitter = random.randint(-3, 3) if self.glitch > 0.2 else 0
        rect = face.get_rect(midtop=(w // 2 + jitter, 26 + bob))
        surf.blit(face, rect)
        # chromatic ghost while glitching
        if self.glitch > 0.15:
            ghost = face.copy()
            ghost.fill((0, 255, 60), special_flags=pygame.BLEND_RGB_MULT)
            ghost.set_alpha(70)
            surf.blit(ghost, rect.move(6, 0))

        # dialogue
        box = pygame.Rect(60, 300, w - 120, 150)
        fnt = ui.font(16)
        lines = ui.wrap(self.pages[self.page], fnt, box.width - 40)
        remaining = len(self.writer.visible)
        y = box.y + 18
        cursor = (box.x + 20, y)
        for line in lines:
            if remaining <= 0:
                break
            part = line[:remaining]
            remaining -= len(line) + 1
            ui.draw_text(surf, part, 16, (box.x + 20, y), NEON, shadow=(0, 60, 0))
            cursor = (box.x + 20 + fnt.size(part)[0], y)
            y += 32
        if not self.writer.done and ui.blink(self.t, 2.5):
            ui.draw_text(surf, "_", 16, cursor, NEON)

        # page dots
        for i in range(len(self.pages)):
            col = NEON if i <= self.page else NEON_DIM
            pygame.draw.rect(surf, col, (w // 2 - len(self.pages) * 10 + i * 20, 462, 10, 4))

        if self.writer.done:
            if self.last_page and self.controls and self.card_t > 0.2:
                self._draw_controls(surf)
            if ui.blink(self.t, 1.2):
                label = "PRESS ENTER" if not self.last_page else ("PRESS ENTER TO BEGIN" if not self.final else "PRESS ENTER")
                ui.draw_text(surf, label, 10, (w // 2, h - 22), NEON_DIM, "midtop")

        ui.crt.apply(surf, self.t, glitch=self.glitch * 0.5)

    def _draw_controls(self, surf):
        w, _ = surf.get_size()
        a = min(1.0, self.card_t * 3)
        items = self.controls
        width = max(ui.font(10).size(c)[0] for c in items) + 40
        width = max(width, 180)
        x = w - width - 30
        rect = pygame.Rect(x, 26, width, 30 + 20 * len(items))
        ui.panel(surf, rect, alpha=int(200 * a))
        ui.draw_text(surf, "CONTROLS", 8, (rect.centerx, rect.y + 8), NEON_DIM, "midtop")
        for i, c in enumerate(items):
            ui.draw_text(surf, c, 10, (rect.x + 16, rect.y + 26 + i * 20), NEON)
