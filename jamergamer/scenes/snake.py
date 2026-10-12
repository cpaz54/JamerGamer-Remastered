"""Chapter I: Snake. Eat 20 apples."""
import math
import random

import pygame

from .. import ui
from ..config import BLACK, NEON, NEON_DIM, RED
from ..scene import Scene

CELL = 30
COLS, ROWS = 32, 17
TOP = 30          # HUD strip height
GOAL = 20

DIRS = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}


class SnakeScene(Scene):
    size = (COLS * CELL, ROWS * CELL + TOP)
    title = "SNAKE"

    def __init__(self, app):
        super().__init__(app)
        self.best = 0
        self.particles = []
        self.reset()

    def enter(self):
        self.audio.music("adventure/sounds/Music/shop_theme.mp3")

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir = (1, 0)
        self.queue = []
        self.eaten = 0
        self.state = "ready"        # ready -> play -> dead / won
        self.timer = 0.0
        self.shake = 0.0
        self.won_t = 0.0
        self.apple = self._spawn_apple()

    @property
    def speed(self):
        return min(15.0, 8.0 + self.eaten * 0.3)

    def _spawn_apple(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in self.body]
        return random.choice(free)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in DIRS:
            if self.state == "ready":
                self.state = "play"
            if self.state == "play" and len(self.queue) < 3:
                last = self.queue[-1] if self.queue else self.dir
                d = DIRS[event.key]
                if d != last and d != (-last[0], -last[1]):
                    self.queue.append(d)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
            if self.state == "dead":
                self.reset()
            elif self.state == "won" and self.won_t > 0.6:
                self.app.story.complete()
            elif self.state == "ready":
                self.state = "play"

    def update(self, dt):
        super().update(dt)
        self.shake = max(0.0, self.shake - dt * 3)
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 300 * dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]
        if self.state == "won":
            self.won_t += dt
            return
        if self.state != "play":
            return
        self.timer += dt
        step = 1.0 / self.speed
        while self.timer >= step and self.state == "play":
            self.timer -= step
            self._step()

    def _step(self):
        if self.queue:
            self.dir = self.queue.pop(0)
        hx, hy = self.body[0]
        new = ((hx + self.dir[0]) % COLS, (hy + self.dir[1]) % ROWS)
        grow = new == self.apple
        body = self.body if grow else self.body[:-1]
        if new in body:
            self.state = "dead"
            self.shake = 1.0
            self.best = max(self.best, self.eaten)
            self.audio.blip("die")
            return
        self.body.insert(0, new)
        if grow:
            self.eaten += 1
            self._burst(new)
            self.audio.blip("eat")
            if self.eaten >= GOAL:
                self.state = "won"
                self.audio.blip("win")
                return
            self.apple = self._spawn_apple()
        else:
            self.body.pop()

    def _burst(self, cell):
        cx, cy = cell[0] * CELL + CELL / 2, cell[1] * CELL + CELL / 2 + TOP
        for _ in range(14):
            a = random.uniform(0, math.tau)
            v = random.uniform(60, 220)
            self.particles.append([cx, cy, math.cos(a) * v, math.sin(a) * v - 80, random.uniform(0.3, 0.6)])

    def draw(self, surf):
        w, h = surf.get_size()
        surf.fill((4, 8, 4))
        ox = int(random.uniform(-8, 8) * self.shake)
        oy = int(random.uniform(-8, 8) * self.shake)
        # grid
        for x in range(COLS + 1):
            pygame.draw.line(surf, (12, 26, 12), (x * CELL + ox, TOP + oy), (x * CELL + ox, h + oy))
        for y in range(ROWS + 1):
            pygame.draw.line(surf, (12, 26, 12), (ox, TOP + y * CELL + oy), (w + ox, TOP + y * CELL + oy))

        # apple
        if self.state != "won":
            ax, ay = self.apple
            pulse = 3 + 2 * math.sin(self.t * 8)
            r = pygame.Rect(ax * CELL + ox, TOP + ay * CELL + oy, CELL, CELL).inflate(-6 + pulse, -6 + pulse)
            pygame.draw.rect(surf, RED, r, border_radius=6)
            pygame.draw.rect(surf, (255, 140, 140), (r.x + 4, r.y + 4, 5, 5))
            pygame.draw.line(surf, (90, 200, 40), (r.centerx, r.y), (r.centerx + 4, r.y - 6), 3)

        # snake
        n = len(self.body)
        dead = self.state == "dead"
        for i, (x, y) in reversed(list(enumerate(self.body))):
            k = 1 - i / max(1, n) * 0.6
            col = (int(57 * k), int(255 * k), int(20 * k)) if not dead else (int(120 * k), int(120 * k), int(120 * k))
            r = pygame.Rect(x * CELL + ox, TOP + y * CELL + oy, CELL, CELL).inflate(-2, -2)
            pygame.draw.rect(surf, col, r, border_radius=7 if i == 0 else 4)
            if i == 0:
                dx, dy = self.dir
                for side in (-1, 1):
                    ex = r.centerx + dx * 6 + (-dy) * side * 7
                    ey = r.centery + dy * 6 + dx * side * 7
                    pygame.draw.circle(surf, BLACK, (ex, ey), 3)

        for p in self.particles:
            pygame.draw.rect(surf, (255, 120, 100), (p[0] + ox, p[1] + oy, 4, 4))

        # HUD
        pygame.draw.rect(surf, BLACK, (0, 0, w, TOP))
        pygame.draw.line(surf, NEON_DIM, (0, TOP - 1), (w, TOP - 1))
        ui.draw_text(surf, f"APPLES {self.eaten}/{GOAL}", 12, (10, 9), NEON)
        bar = pygame.Rect(230, 10, 300, 10)
        pygame.draw.rect(surf, NEON_DIM, bar, 1)
        pygame.draw.rect(surf, NEON, (bar.x + 2, bar.y + 2, int((bar.w - 4) * self.eaten / GOAL), bar.h - 4))
        if self.best:
            ui.draw_text(surf, f"BEST {self.best}", 12, (w - 10, 9), NEON_DIM, "topright")

        cx, cy = w // 2, h // 2 + TOP // 2
        if self.state == "ready":
            ui.panel(surf, (cx - 220, cy - 40, 440, 80))
            ui.draw_text(surf, "PRESS AN ARROW KEY", 14, (cx, cy - 10), NEON, "midtop")
        elif self.state == "dead":
            ui.panel(surf, (cx - 300, cy - 60, 600, 120))
            ui.draw_text(surf, "TRY AGAIN", 24, (cx, cy - 40), NEON, "midtop")
            ui.draw_text(surf, f"REACH {GOAL} APPLES TO CONTINUE", 10, (cx, cy + 2), NEON_DIM, "midtop")
            if ui.blink(self.t):
                ui.draw_text(surf, "PRESS ENTER", 10, (cx, cy + 28), NEON, "midtop")
        elif self.state == "won":
            if ui.blink(self.t, 2):
                ui.draw_text(surf, "YOU WIN!", 40, (cx, cy - 40), NEON, "midtop", shadow=BLACK)
            if self.won_t > 0.6:
                ui.draw_text(surf, "PRESS ENTER TO CONTINUE...", 12, (cx, h - 30), NEON, "midtop", shadow=BLACK)
        ui.crt.apply(surf, self.t, strength=40)
