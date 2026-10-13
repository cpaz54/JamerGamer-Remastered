"""Title screen: continue / new game / chapter select / settings."""
import math
import random
import sys

import pygame

from .. import ui
from ..config import BLACK, NEON, NEON_DIM
from ..scene import Scene
from ..story import CHAPTERS, INDEX
from .common import puppet, tint

WEB = sys.platform == "emscripten"   # browser build: no quit / fullscreen options


class TitleScene(Scene):
    size = (960, 540)
    pausable = False

    def __init__(self, app):
        super().__init__(app)
        self.mode = "main"
        self.glitch = 0.0
        self.stars = [(random.randrange(960), random.randrange(540), random.random()) for _ in range(90)]
        self.started = False
        self._build()

    def enter(self):
        self.audio.stop_music(300)

    def _build(self):
        s = self.app.save
        story = self.app.story
        if self.mode == "main":
            items = []
            if s["reached"] > 0:
                items.append(("CONTINUE", "continue"))
            items += [("NEW GAME", "new")]
            if s["reached"] > 0:
                items.append(("CHAPTERS", "chapters"))
            items += [("SETTINGS", "settings")] + ([] if WEB else [("QUIT", "quit")])
        elif self.mode == "chapters":
            items = []
            for label, sid in CHAPTERS:
                if story.unlocked(sid):
                    items.append((label, sid))
                else:
                    items.append(("???", None))
            items.append(("BACK", "back"))
        else:
            items = [
                (lambda: f"MUSIC  < {int(round(s['music_volume'] * 10))} >", "music"),
                (lambda: f"SOUND  < {int(round(s['sfx_volume'] * 10))} >", "sfx"),
                *([] if WEB else [(lambda: f"FULLSCREEN  {'ON' if self.app.fullscreen else 'OFF'}", "full")]),
                ("RESET PROGRESS", "reset"),
                ("BACK", "back"),
            ]
        self.menu = ui.Menu(items, size=16, gap=34)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.mode != "main":
                self.mode = "main"
                self._build()
                self.audio.blip("back")
            return
        res = self.menu.handle(event, self.audio)
        if not res or self.started:
            return
        action, key = res
        s = self.app.save
        if key in ("music", "sfx"):
            field = "music_volume" if key == "music" else "sfx_volume"
            step = {"left": -0.1, "right": 0.1, "select": 0.1}[action]
            val = round(s[field] + step, 2)
            if action == "select" and s[field] >= 1.0:
                val = 0.0
            s[field] = max(0.0, min(1.0, val))
            self.audio.apply_volume()
            self.audio.blip("move")
            return
        if action != "select":
            return
        story = self.app.story
        if key == "continue":
            self.started = True
            story.goto(story.continue_index())
        elif key == "new":
            self.started = True
            story.new_run("intro")
        elif key in ("chapters", "settings"):
            self.mode = key
            self._build()
        elif key == "back":
            self.mode = "main"
            self._build()
        elif key == "full":
            self.app.toggle_fullscreen()
        elif key == "reset":
            s["reached"] = 0
            s["checkpoints"] = {}
            s["completed"] = False
            self.mode = "main"
            self._build()
            self.glitch = 1.0
            self.audio.blip("die")
        elif key == "quit":
            self.app.quit()
        elif key in INDEX:
            self.started = True
            story.new_run(key)

    def update(self, dt):
        super().update(dt)
        self.glitch = max(0.0, self.glitch - dt)
        if random.random() < 0.006:
            self.glitch = 0.5

    def draw(self, surf):
        w, h = surf.get_size()
        surf.fill(BLACK)
        for x, y, d in self.stars:
            b = int(40 + 60 * d * (0.6 + 0.4 * math.sin(self.t * 2 + x)))
            surf.set_at((x, int(y + self.t * 8 * d) % h), (0, b, 0))
        # faint watching face
        closed, opened = puppet(420)
        face = tint(opened if int(self.t * 0.5) % 7 == 0 else closed, (40, 120, 40))
        face.set_alpha(55 + int(20 * math.sin(self.t)))
        surf.blit(face, face.get_rect(center=(w // 2, h // 2 + 10)))

        # logo
        logo = "JAMERGAMER"
        jitter = random.randint(-4, 4) if self.glitch > 0.2 else 0
        if self.glitch > 0.1:
            ui.draw_text(surf, logo, 44, (w // 2 + 5 + jitter, 74), (255, 0, 80), "midtop")
            ui.draw_text(surf, logo, 44, (w // 2 - 5 - jitter, 74), (0, 200, 255), "midtop")
        ui.draw_text(surf, logo, 44, (w // 2 + jitter, 72), NEON, "midtop", shadow=(0, 50, 0))
        sub = {"main": "A TEST OF SKILL, LUCK AND PATIENCE",
               "chapters": "CHAPTER SELECT",
               "settings": "SETTINGS"}[self.mode]
        ui.draw_text(surf, sub, 10, (w // 2, 136), NEON_DIM, "midtop")

        self.menu.draw(surf, w // 2, 214 if self.mode != "chapters" else 186, self.t)
        hint = "ARROWS + ENTER    ESC PAUSES IN GAME" if WEB else "ARROWS + ENTER    F11 FULLSCREEN    ESC PAUSES IN GAME"
        if self.app.save.data.get("completed"):
            hint = "WE ARE WATCHING. ALWAYS."
        ui.draw_text(surf, hint, 8, (w // 2, h - 22), NEON_DIM, "midtop")
        ui.crt.apply(surf, self.t, glitch=self.glitch * 0.6)
