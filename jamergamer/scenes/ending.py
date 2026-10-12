"""After the final words: a quiet end card, then back to the title."""
import math

import pygame

from .. import ui
from ..config import BLACK, NEON, NEON_DIM
from ..scene import Scene
from .common import puppet, tint


class EndScene(Scene):
    size = (960, 540)
    title = "THE END"

    def enter(self):
        self.app.save["completed"] = True
        self.audio.music("platformer/music/world.mp3", fade_ms=3000)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.t > 3:
            self.audio.stop_music(1500)
            self.app.story.to_title()

    def skip(self):
        self.app.story.to_title()

    def draw(self, surf):
        w, h = surf.get_size()
        surf.fill(BLACK)
        a = min(255, int(self.t * 60))
        closed, _ = puppet(300)
        face = tint(closed, (60, 160, 60))
        face.set_alpha(min(90, a))
        surf.blit(face, face.get_rect(center=(w // 2, h // 2 - 20)))
        ui.draw_text(surf, "THANKS FOR PLAYING", 28, (w // 2, 150), NEON, "midtop", shadow=BLACK, alpha=a)
        if self.t > 1.5:
            b = min(255, int((self.t - 1.5) * 80))
            ui.draw_text(surf, "SNAKE  -  THE GAUNTLET  -  TURN AND COUGH", 10, (w // 2, 250), NEON_DIM, "midtop", alpha=b)
            ui.draw_text(surf, "JAMER QUEST  -  HELL ARENA", 10, (w // 2, 272), NEON_DIM, "midtop", alpha=b)
        if self.t > 3:
            c = min(255, int((self.t - 3) * 80))
            ui.draw_text(surf, "NOW GO. THE DOOR IS UNLOCKED.", 14, (w // 2, 360), NEON, "midtop", alpha=c)
            if ui.blink(self.t, 1):
                ui.draw_text(surf, "PRESS ENTER", 10, (w // 2, h - 40), NEON_DIM, "midtop")
        ui.crt.apply(surf, self.t, glitch=0.01 + 0.02 * (math.sin(self.t) > 0.95))
