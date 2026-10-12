"""Enemies, hazards and pickups that live in the platforming stages."""
import math
import random

import pygame

from . import assets
from .level import TILE
from .physics import Body


class Entity:
    alive = True
    hittable = False      # can be hit by the sword
    harmful = False       # hurts the player on touch
    solid_platform = False

    def update(self, scene):
        pass

    def draw(self, surf, cam):
        pass

    @property
    def rect(self):
        raise NotImplementedError


# --------------------------------------------------------------------- effects
class Particles:
    def __init__(self):
        self.items = []

    def burst(self, pos, color, n=12, speed=4.0, life=30, gravity=0.2, size=4):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(speed * 0.3, speed)
            self.items.append([pos[0], pos[1], math.cos(a) * v, math.sin(a) * v - 1.5, life, life, color, gravity, size])

    def update(self):
        for p in self.items:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += p[7]
            p[4] -= 1
        self.items = [p for p in self.items if p[4] > 0]

    def draw(self, surf, cam):
        for x, y, _vx, _vy, life, total, color, _g, size in self.items:
            s = max(1, int(size * life / total + 1))
            surf.fill(color, (int(x - cam[0]), int(y - cam[1]), s, s))


class FloatText:
    def __init__(self, text, pos, color=(255, 255, 255)):
        self.text, self.x, self.y, self.color, self.life = text, pos[0], pos[1], color, 50

    def update(self):
        self.y -= 0.7
        self.life -= 1


# --------------------------------------------------------------------- enemies
class Moth(Body, Entity):
    """Walks back and forth, turning at walls and ledges. Two hits, or stomp it."""
    hittable = True
    harmful = True

    def __init__(self, tx, ty):
        Body.__init__(self, tx * TILE + 6, ty * TILE + TILE - 40, 32, 40)
        self.image = assets.img("trap/enemy_1.png", size=(42, 54))
        self.dir = random.choice((-1, 1))
        self.speed = 1.2
        self.hp = 2
        self.flash = 0
        self.t = random.random() * 10

    def update(self, scene):
        self.t += 0.1
        self.flash = max(0, self.flash - 1)
        if self.on_ground and (self.hit_wall or not self.ground_ahead(scene.level, self.dir)):
            self.dir *= -1
        self.vx = self.dir * self.speed if self.flash == 0 else self.vx * 0.8
        self.move(scene.level, scene.platforms)
        if self.y > scene.level.h + 200:
            self.alive = False

    def take_hit(self, scene, direction):
        self.hp -= 1
        self.flash = 10
        self.vx = 4 * direction
        self.vy = -3
        scene.audio.blip("hit")
        scene.particles.burst(self.rect.center, (230, 200, 160), 6)
        if self.hp <= 0:
            self.die(scene)

    def die(self, scene):
        self.alive = False
        scene.particles.burst(self.rect.center, (240, 220, 190), 18, 5)
        scene.particles.burst(self.rect.center, (200, 60, 40), 8, 3)

    def draw(self, surf, cam):
        img = self.image if self.dir < 0 else pygame.transform.flip(self.image, True, False)
        if self.flash:
            img = assets.white(self.image)
        bob = math.sin(self.t * 1.5) * 2
        surf.blit(img, (int(self.cx - img.get_width() / 2 - cam[0]), int(self.y + self.h - img.get_height() + 6 + bob - cam[1])))


class Flyer(Entity):
    """Hovers on a figure-eight path. One hit."""
    hittable = True
    harmful = True

    def __init__(self, tx, ty):
        self.x0 = tx * TILE + TILE / 2
        self.y0 = ty * TILE + TILE / 2
        self.t = random.random() * math.tau
        self.x, self.y = self.x0, self.y0
        base = assets.img("trap/enemy_1.png", size=(38, 48))
        self.image = assets.tinted(base, (255, 140, 220))
        self.flash = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 15), int(self.y - 18), 30, 34)

    def update(self, scene):
        self.t += 0.025
        self.x = self.x0 + math.sin(self.t) * 70
        self.y = self.y0 + math.sin(self.t * 2) * 26
        self.flash = max(0, self.flash - 1)

    def take_hit(self, scene, direction):
        scene.audio.blip("hit")
        self.alive = False
        scene.particles.burst(self.rect.center, (255, 160, 230), 18, 5)

    def die(self, scene):
        self.take_hit(scene, 0)

    def draw(self, surf, cam):
        facing = math.cos(self.t) > 0
        img = pygame.transform.flip(self.image, True, False) if facing else self.image
        flap = abs(math.sin(self.t * 14)) * 6
        img = pygame.transform.scale(img, (img.get_width(), int(img.get_height() - flap)))
        surf.blit(img, img.get_rect(center=(int(self.x - cam[0]), int(self.y - cam[1]))))


class Blade(Entity):
    """Spinning saw. Optionally slides between | markers."""
    harmful = True

    def __init__(self, level, tx, ty, mode="static"):
        self.frames = assets.frames("trap/blade", size=(36, 36))
        self.x = tx * TILE + TILE / 2
        self.y = ty * TILE + TILE / 2
        self.mode = mode
        self.speed = 2.2
        self.dir = 1
        self.anim = random.random() * 8
        if mode == "h":
            lo, hi = level.marker_range(tx, ty, vertical=False)
            self.lo, self.hi = lo * TILE + TILE / 2, hi * TILE + TILE / 2
        elif mode == "v":
            lo, hi = level.marker_range(tx, ty, vertical=True)
            self.lo, self.hi = lo * TILE + TILE / 2, hi * TILE + TILE / 2

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 13), int(self.y - 13), 26, 26)

    def update(self, scene):
        self.anim += 0.5
        if self.mode == "h":
            self.x += self.speed * self.dir
            if self.x >= self.hi or self.x <= self.lo:
                self.dir *= -1
        elif self.mode == "v":
            self.y += self.speed * self.dir
            if self.y >= self.hi or self.y <= self.lo:
                self.dir *= -1

    def draw(self, surf, cam):
        if self.mode != "static":
            # rail
            if self.mode == "h":
                pygame.draw.line(surf, (60, 60, 70), (self.lo - cam[0], self.y - cam[1]), (self.hi - cam[0], self.y - cam[1]), 3)
            else:
                pygame.draw.line(surf, (60, 60, 70), (self.x - cam[0], self.lo - cam[1]), (self.x - cam[0], self.hi - cam[1]), 3)
        img = self.frames[int(self.anim) % len(self.frames)]
        surf.blit(img, img.get_rect(center=(int(self.x - cam[0]), int(self.y - cam[1]))))


# --------------------------------------------------------------------- platforms
class MovingPlatform(Entity):
    solid_platform = True
    alive_platform = True

    def __init__(self, level, tx, ty, vertical=False):
        self.w = TILE * 3
        self.h = 14
        self.x = float(tx * TILE)
        self.y = float(ty * TILE)
        self.vertical = vertical
        lo, hi = level.marker_range(tx, ty, vertical)
        if vertical:
            self.lo, self.hi = lo * TILE, hi * TILE
        else:
            self.lo, self.hi = lo * TILE, (hi - 2) * TILE
        self.speed = 1.6
        self.dir = 1
        self.dx = self.dy = 0.0
        self.stood_on = False
        self.image = assets.img("terrain/wood_platform.png", size=(self.w, 40)).subsurface((0, 14, self.w, 14))

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, scene):
        self.stood_on = False
        ox, oy = self.x, self.y
        if self.vertical:
            self.y += self.speed * self.dir
            if self.y >= self.hi or self.y <= self.lo:
                self.y = max(self.lo, min(self.hi, self.y))
                self.dir *= -1
        else:
            self.x += self.speed * self.dir
            if self.x >= self.hi or self.x <= self.lo:
                self.x = max(self.lo, min(self.hi, self.x))
                self.dir *= -1
        self.dx, self.dy = self.x - ox, self.y - oy

    def draw(self, surf, cam):
        surf.blit(self.image, (int(self.x - cam[0]), int(self.y - cam[1])))
        pygame.draw.rect(surf, (60, 35, 20), (int(self.x - cam[0]), int(self.y - cam[1]), self.w, self.h), 1)


class Crumble(Entity):
    """A ledge that shakes when stood on, then drops away and later returns."""
    solid_platform = True

    def __init__(self, tx, ty):
        self.home = (tx * TILE, ty * TILE)
        self.x, self.y = self.home
        self.w, self.h = TILE, 14
        self.dx = self.dy = 0.0
        self.state = "idle"
        self.timer = 0
        self.vy = 0.0
        self.stood_on = False
        plank = assets.img("terrain/wood_platform.png", size=(TILE, 40)).subsurface((0, 14, TILE, 14)).copy()
        plank.fill((200, 170, 150), special_flags=pygame.BLEND_RGB_MULT)
        pygame.draw.line(plank, (50, 30, 20), (12, 0), (18, 13), 2)
        pygame.draw.line(plank, (50, 30, 20), (28, 0), (24, 13), 2)
        self.image = plank

    @property
    def alive_platform(self):
        return self.state in ("idle", "shaking")

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, scene):
        if self.state == "idle" and self.stood_on:
            self.state, self.timer = "shaking", 28
            scene.audio.play(scene.audio.synth("crumble", freq=120, dur=0.3, wave="saw", vol=0.2, noise=0.8))
        elif self.state == "shaking":
            self.timer -= 1
            if self.timer <= 0:
                self.state, self.timer, self.vy = "falling", 160, 0
        elif self.state == "falling":
            self.vy += 0.5
            self.y += self.vy
            self.timer -= 1
            if self.timer <= 0:
                self.state = "idle"
                self.x, self.y = self.home
        self.stood_on = False

    def draw(self, surf, cam):
        if self.state == "falling" and self.y > self.home[1] + 400:
            # ghost outline of where it'll come back
            if self.timer < 40:
                pygame.draw.rect(surf, (120, 90, 70), (self.home[0] - cam[0], self.home[1] - cam[1], self.w, self.h), 1)
            return
        jx = random.randint(-2, 2) if self.state == "shaking" else 0
        surf.blit(self.image, (int(self.x + jx - cam[0]), int(self.y - cam[1])))


# --------------------------------------------------------------------- pickups / markers
class Heart(Entity):
    def __init__(self, tx, ty):
        self.x = tx * TILE + TILE / 2
        self.y = ty * TILE + TILE / 2
        self.t = random.random() * 6
        self.image = assets.img("life/life.png", size=(24, 24))

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 12), int(self.y - 12), 24, 24)

    def update(self, scene):
        self.t += 0.08
        p = scene.player
        if p.rect.colliderect(self.rect) and p.hearts < 5:
            p.hearts += 1
            self.alive = False
            scene.audio.blip("heal")
            scene.particles.burst(self.rect.center, (255, 80, 90), 14, 3)
            scene.float_text("+1", self.rect.center, (255, 120, 120))

    def draw(self, surf, cam):
        bob = math.sin(self.t) * 4
        s = 1 + 0.08 * math.sin(self.t * 2)
        img = pygame.transform.scale(self.image, (int(24 * s), int(24 * s)))
        surf.blit(img, img.get_rect(center=(int(self.x - cam[0]), int(self.y + bob - cam[1]))))


class Checkpoint(Entity):
    def __init__(self, tx, ty):
        self.x = tx * TILE + TILE / 2
        self.base = ty * TILE + TILE
        self.active = False
        self.t = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 20), int(self.base - 90), 40, 90)

    def update(self, scene):
        self.t += 0.1
        if not self.active and scene.player.rect.colliderect(self.rect):
            self.active = True
            scene.set_checkpoint(self.x, self.base)

    def draw(self, surf, cam):
        x, b = int(self.x - cam[0]), int(self.base - cam[1])
        pygame.draw.rect(surf, (70, 60, 50), (x - 2, b - 84, 4, 84))
        pygame.draw.circle(surf, (200, 180, 90), (x, b - 86), 4)
        color = (60, 220, 90) if self.active else (170, 40, 40)
        wave = [(x + 2, b - 80)]
        for i in range(0, 34, 4):
            wave.append((x + 2 + i, b - 80 + math.sin(self.t + i * 0.2) * 3))
        for i in range(34, -1, -4):
            wave.append((x + 2 + i, b - 58 + math.sin(self.t + i * 0.2) * 3))
        pygame.draw.polygon(surf, color, wave)


class Gate(Entity):
    def __init__(self, tx, ty):
        self.image = assets.img("goal/gate.png", size=(110, 70))
        self.x = tx * TILE + TILE / 2
        self.base = ty * TILE + TILE
        self.t = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 30), int(self.base - 70), 60, 70)

    def update(self, scene):
        self.t += 0.05
        if scene.player.rect.colliderect(self.rect):
            scene.stage_clear()

    def draw(self, surf, cam):
        glow = pygame.Surface((140, 100), pygame.SRCALPHA)
        a = int(60 + 40 * math.sin(self.t * 2))
        pygame.draw.ellipse(glow, (255, 230, 140, a), glow.get_rect())
        surf.blit(glow, glow.get_rect(midbottom=(int(self.x - cam[0]), int(self.base - cam[1] + 15))))
        surf.blit(self.image, self.image.get_rect(midbottom=(int(self.x - cam[0]), int(self.base - cam[1]))))


def spawn(level, ch, tx, ty):
    if ch == "E":
        return Moth(tx, ty)
    if ch == "F":
        return Flyer(tx, ty)
    if ch == "b":
        return Blade(level, tx, ty)
    if ch == "B":
        return Blade(level, tx, ty, "h")
    if ch == "Y":
        return Blade(level, tx, ty, "v")
    if ch == "H":
        return MovingPlatform(level, tx, ty)
    if ch == "V":
        return MovingPlatform(level, tx, ty, vertical=True)
    if ch == "~":
        return Crumble(tx, ty)
    if ch == "h":
        return Heart(tx, ty)
    if ch == "C":
        return Checkpoint(tx, ty)
    if ch == "G":
        return Gate(tx, ty)
    return None
