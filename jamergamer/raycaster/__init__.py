"""Chapter V: Hell Arena - a raycasting shooter.

Rebuilt from DOOM-style-Game by Stanislav Petrov (MIT, see
assets/doom/LICENSE-DOOM-style-Game) to run inside the main window, with real
health, zones sealed by gates, waves, medkits and a HUD.
"""
import math
import os
import random
from collections import deque

import pygame

from .. import ui
from ..config import asset, BLACK, WHITE
from ..scene import Scene
from .world import CANDLES, LIGHTS, MAP, PLAYER_START, ZONES

W, H = 640, 360
HALF_W, HALF_H = W // 2, H // 2
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = W // 2
HALF_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20
SCREEN_DIST = HALF_W / math.tan(HALF_FOV)
SCALE = W // NUM_RAYS
TEX = 256
HALF_TEX = TEX // 2

PLAYER_SPEED = 3.6          # tiles / second
TURN_SPEED = 2.4            # radians / second (arrow keys)
MOUSE_SENS = 0.0026         # radians / pixel
PLAYER_SIZE = 0.22
MAX_HEALTH = 100

ENEMIES = {
    #            path          scale shift speed hp  dmg  range acc  cooldown
    "soldier": ("soldier", 0.6, 0.38, 1.6, 100, 7, 6.0, 0.30, 1.0),
    "caco": ("caco_demon", 0.7, 0.27, 2.6, 150, 14, 1.2, 0.70, 0.9),
    "cyber": ("cyber_demon", 1.0, 0.04, 2.0, 400, 16, 7.0, 0.35, 1.3),
}

_img_cache = {}


def load(rel, max_h=None, size=None):
    key = (rel, max_h, size)
    if key not in _img_cache:
        img = pygame.image.load(asset("doom", rel)).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        elif max_h and img.get_height() > max_h:
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (max(1, int(w * max_h / h)), max_h))
        _img_cache[key] = img
    return _img_cache[key]


def load_dir(rel, max_h=256):
    path = asset("doom", rel)
    names = sorted((n for n in os.listdir(path) if n.endswith(".png")),
                   key=lambda n: (0, int(n[:-4]), "") if n[:-4].isdigit() else (1, 0, n))
    return [load(f"{rel}/{n}", max_h) for n in names]


# =============================================================== sprites
class Sprite:
    def __init__(self, game, image, pos, scale=0.7, shift=0.27):
        self.game = game
        self.image = image
        self.x, self.y = pos
        self.scale = scale
        self.shift = shift
        self.screen_x = 0
        self.dist = 1
        self.norm_dist = 1
        self.half_w = 0
        self.theta = 0
        self.alive_sprite = True

    def project(self):
        p = self.game.player
        dx, dy = self.x - p.x, self.y - p.y
        self.theta = math.atan2(dy, dx)
        delta = (self.theta - p.angle + math.pi) % math.tau - math.pi
        self.screen_x = (HALF_RAYS + delta / DELTA_ANGLE) * SCALE
        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        img = self.image
        ratio = img.get_width() / img.get_height()
        if -img.get_width() < self.screen_x < W + img.get_width() and self.norm_dist > 0.4:
            proj = SCREEN_DIST / self.norm_dist * self.scale
            pw, ph = int(proj * ratio), int(proj)
            if pw <= 0 or ph <= 0 or ph > H * 6:
                return
            self.half_w = pw // 2
            sprite = pygame.transform.scale(img, (pw, ph))
            pos = (self.screen_x - self.half_w, HALF_H - ph // 2 + ph * self.shift)
            self.game.render_list.append((self.norm_dist, sprite, pos))


class Animated(Sprite):
    def __init__(self, game, frames, pos, scale=0.8, shift=0.16, period=0.12):
        super().__init__(game, frames[0], pos, scale, shift)
        self.frames = frames
        self.period = period
        self.t = random.random()

    def update(self, dt):
        self.t += dt
        self.image = self.frames[int(self.t / self.period) % len(self.frames)]


class Medkit(Sprite):
    def __init__(self, game, pos):
        s = pygame.Surface((64, 48), pygame.SRCALPHA)
        pygame.draw.rect(s, (230, 230, 230), (0, 6, 64, 42), border_radius=6)
        pygame.draw.rect(s, (90, 90, 90), (22, 0, 20, 8))
        pygame.draw.rect(s, (210, 20, 20), (26, 14, 12, 30))
        pygame.draw.rect(s, (210, 20, 20), (17, 23, 30, 12))
        super().__init__(game, s, pos, scale=0.3, shift=1.1)

    def update(self, dt):
        p = self.game.player
        if math.hypot(p.x - self.x, p.y - self.y) < 0.6 and p.health < MAX_HEALTH:
            p.health = min(MAX_HEALTH, p.health + 50)
            self.alive_sprite = False
            self.game.audio.blip("heal")
            self.game.message("+50 HEALTH", 1.2)


# =============================================================== enemies
class NPC(Sprite):
    def __init__(self, game, kind, pos):
        folder, scale, shift, speed, hp, dmg, rng, acc, cd = ENEMIES[kind]
        base = f"sprites/npc/{folder}"
        self.anims = {k: load_dir(f"{base}/{k}") for k in ("attack", "death", "idle", "pain", "walk")}
        super().__init__(game, self.anims["idle"][0], pos, scale, shift)
        self.kind = kind
        self.speed, self.hp, self.damage = speed, hp, dmg
        self.attack_range, self.accuracy, self.cooldown = rng, acc, cd
        self.attack_t = random.uniform(0.3, cd)
        self.alive = True
        self.pain = 0.0
        self.anim_t = 0.0
        self.death_frame = 0
        self.sees_player = False
        self.alerted = False
        self.path_t = 0.0
        self.next_tile = None
        self.flash = 0.6        # teleport-in glow

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def update(self, dt):
        self.anim_t += dt
        self.flash = max(0.0, self.flash - dt)
        g = self.game
        if not self.alive:
            if self.death_frame < len(self.anims["death"]) - 1 and self.anim_t > 0.08:
                self.anim_t = 0
                self.death_frame += 1
            self.image = self.anims["death"][self.death_frame]
            return
        self.sees_player = g.line_of_sight(self.x, self.y)
        if self.sees_player:
            self.alerted = True
        dist = math.hypot(g.player.x - self.x, g.player.y - self.y)
        if self.pain > 0:
            self.pain -= dt
            self.image = self.anims["pain"][0]
        elif self.sees_player and dist < self.attack_range:
            self._anim("attack", 0.18)
            self.attack_t -= dt
            if self.attack_t <= 0:
                self.attack_t = self.cooldown
                g.sound("npc_attack", 0.25)
                if random.random() < self.accuracy * (1.0 if dist < 3 else 0.75):
                    g.player_hurt(self.damage)
        elif self.alerted:
            self._anim("walk", 0.16)
            self._move(dt)
        else:
            self._anim("idle", 0.18)

    def _anim(self, name, period):
        frames = self.anims[name]
        self.image = frames[int(self.anim_t / period) % len(frames)]

    def _move(self, dt):
        g = self.game
        self.path_t -= dt
        if self.path_t <= 0 or self.next_tile is None:
            self.path_t = 0.25
            self.next_tile = g.next_step(self.map_pos, g.player.map_pos)
        nx, ny = self.next_tile
        if (nx, ny) in g.npc_tiles(exclude=self):
            return
        ang = math.atan2(ny + 0.5 - self.y, nx + 0.5 - self.x)
        step = self.speed * dt
        dx, dy = math.cos(ang) * step, math.sin(ang) * step
        if g.free(int(self.x + dx * 4), int(self.y)):
            self.x += dx
        if g.free(int(self.x), int(self.y + dy * 4)):
            self.y += dy

    def hit(self, damage):
        g = self.game
        self.hp -= damage
        self.pain = 0.15
        self.alerted = True
        g.sound("npc_pain", 0.3)
        if self.hp <= 0:
            self.alive = False
            self.anim_t = 0
            g.sound("npc_death", 0.3)

    def project(self):
        g = self.game
        before = len(g.render_list)
        super().project()
        if self.flash > 0 and len(g.render_list) > before:
            # green teleport-in glow over the freshly projected sprite
            d, spr, pos = g.render_list[-1]
            glow = spr.copy()
            glow.fill((40, 255, 80, 0), special_flags=pygame.BLEND_RGBA_MAX)
            glow.set_alpha(int(255 * self.flash / 0.6))
            g.render_list.append((d - 0.01, glow, pos))


# =============================================================== player
class Player:
    def __init__(self, x, y, angle):
        self.x, self.y, self.angle = x, y, angle
        self.health = MAX_HEALTH
        self.since_hurt = 99.0
        self.regen_t = 0.0

    @property
    def map_pos(self):
        return int(self.x), int(self.y)


# =============================================================== scene
class DoomScene(Scene):
    size = (W, H)
    grab_mouse = True
    title = "HELL ARENA"

    def __init__(self, app):
        super().__init__(app)
        self.walls = {i: load(f"textures/{i}.png", size=(TEX, TEX)) for i in range(1, 6)}
        gate = self.walls[1].copy()
        gate.fill((150, 40, 40), special_flags=pygame.BLEND_RGB_MULT)
        for x in range(16, TEX, 40):
            pygame.draw.rect(gate, (20, 10, 10), (x, 0, 14, TEX))
            pygame.draw.rect(gate, (110, 30, 20), (x + 3, 0, 4, TEX))
        self.walls[6] = gate
        self.sky = load("textures/sky.png", size=(W, HALF_H))
        self.blood = load("textures/blood_screen.png", size=(W, H))
        self.digits = {str(i): load(f"textures/digits/{i}.png", size=(28, 28)) for i in range(11)}
        self.win_img = load("textures/win.png", size=(W, H))
        self.lose_img = load("textures/game_over.png", size=(W, H))
        gun = load_dir("sprites/weapon/shotgun", max_h=1050)
        gw = int(W * 0.34)
        self.gun = [pygame.transform.smoothscale(g, (gw, int(g.get_height() * gw / g.get_width()))) for g in gun]
        self.light_frames = {"green": load_dir("sprites/animated_sprites/green_light", 200),
                             "red": load_dir("sprites/animated_sprites/red_light", 200)}
        self.candle = load("sprites/static_sprites/candlebra.png", max_h=256)
        self.sounds = {}
        self.reset_world()
        self.cp = app.story.checkpoint("doom") or {}
        start_zone = self.cp.get("zone", 0)
        for z in range(start_zone):
            self._open_gate(z, silent=True)
        self.zone = start_zone
        if start_zone:
            x, y, a = ZONES[start_zone]["respawn"]
            self.player = Player(x, y, a)
        self.zone_state = "waiting"      # waiting -> fighting -> cleared
        self.wave = 0
        self.wave_delay = 0.0
        self.state = "play"              # play / dead / won
        self.state_t = 0.0
        self.msg = None
        self.hurt_flash = 0.0
        self.shot_t = 0.0
        self.firing = False
        self.minimap = False
        self.mouse_dx = 0
        self.render_list = []
        if self.zone == 0:
            self._start_zone()

    def reset_world(self):
        self.world = {}
        for y, row in enumerate(MAP):
            for x, v in enumerate(row):
                if v:
                    self.world[(x, y)] = v
        self.player = Player(*PLAYER_START)
        self.npcs = []
        self.items = []
        self.decor = [Animated(self, self.light_frames[c], p) for c, p in LIGHTS]
        self.decor += [Sprite(self, self.candle, p, 0.7, 0.27) for p in CANDLES]

    def enter(self):
        self.audio.music("doom/sound/Mick Gordon - 11. BFG Division.mp3", fade_ms=800)
        self.message(ZONES[self.zone]["name"], 2.5)

    # ------------------------------------------------------------ helpers
    def sound(self, name, vol=0.3):
        self.audio.sfx(f"doom/sound/{name}.wav", vol)

    def message(self, text, secs=2.0):
        self.msg = [text, secs]

    def free(self, x, y):
        return (x, y) not in self.world

    def npc_tiles(self, exclude=None):
        return {n.map_pos for n in self.npcs if n.alive and n is not exclude}

    def next_step(self, start, goal):
        """BFS one step along the shortest path from start to goal."""
        if start == goal:
            return goal
        prev = {start: None}
        q = deque([start])
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            cx, cy = cur
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                nxt = (cx + dx, cy + dy)
                if nxt in prev or not self.free(*nxt):
                    continue
                if dx and dy and (not self.free(cx + dx, cy) or not self.free(cx, cy + dy)):
                    continue
                prev[nxt] = cur
                q.append(nxt)
        if goal not in prev:
            return start
        step = goal
        while prev[step] != start and prev[step] is not None:
            step = prev[step]
        return step

    def line_of_sight(self, x, y):
        p = self.player
        dx, dy = p.x - x, p.y - y
        dist = math.hypot(dx, dy)
        steps = int(dist * 8) + 1
        for i in range(1, steps):
            t = i / steps
            if not self.free(int(x + dx * t), int(y + dy * t)):
                return False
        return True

    def player_hurt(self, dmg):
        if self.state != "play":
            return
        p = self.player
        p.health -= dmg
        p.since_hurt = 0.0
        self.hurt_flash = 0.35
        self.sound("player_pain", 0.3)
        if p.health <= 0:
            p.health = 0
            self.state = "dead"
            self.state_t = 0.0
            self.audio.blip("die")

    # ------------------------------------------------------------ zones & waves
    def _zone_tiles(self, zone):
        r0, r1 = ZONES[zone]["rows"]
        return [(x, y) for y in range(r0, r1 + 1) for x in range(len(MAP[0])) if self.free(x, y)]

    def _start_zone(self):
        self.zone_state = "fighting"
        self.wave = 0
        self._spawn_wave()

    def _spawn_wave(self):
        z = ZONES[self.zone]
        p = self.player
        fixed = list(z.get("fixed", []))
        tiles = [t for t in self._zone_tiles(self.zone) if math.hypot(t[0] + 0.5 - p.x, t[1] + 0.5 - p.y) > 4]
        random.shuffle(tiles)
        for kind, count in z["waves"][self.wave]:
            for _ in range(count):
                if fixed:
                    pos = fixed.pop(0)
                else:
                    tx, ty = tiles.pop() if tiles else (8, z["rows"][0] + 1)
                    pos = (tx + 0.5, ty + 0.5)
                n = NPC(self, kind, pos)
                if self.zone > 0:
                    n.alerted = True
                self.npcs.append(n)
        if len(z["waves"]) > 1:
            self.message(f"WAVE {self.wave + 1}/{len(z['waves'])}", 1.8)
        if self.zone > 0 or self.wave > 0:
            self.sound("npc_attack", 0.15)

    def _open_gate(self, zone, silent=False):
        for pos in ZONES[zone]["gate"]:
            self.world.pop(pos, None)
        if not silent:
            self.audio.blip("checkpoint")

    def _update_zones(self, dt):
        p = self.player
        alive = [n for n in self.npcs if n.alive]
        if self.zone_state == "waiting":
            if p.y >= ZONES[self.zone]["trigger_row"]:
                self._start_zone()
                self.message(ZONES[self.zone]["name"], 2.0)
        elif self.zone_state == "fighting" and not alive:
            if self.wave_delay <= 0:
                z = ZONES[self.zone]
                if self.wave + 1 < len(z["waves"]):
                    self.wave_delay = 3.0
                else:
                    self._zone_cleared()
            else:
                self.wave_delay -= dt
                if self.wave_delay <= 0:
                    self.wave += 1
                    self._spawn_wave()

    def _zone_cleared(self):
        z = ZONES[self.zone]
        if z["medkit"]:
            self.items.append(Medkit(self, z["medkit"]))
        if self.zone + 1 >= len(ZONES):
            self.state = "won"
            self.state_t = 0.0
            self.audio.blip("win")
            self.app.story.checkpoint("doom", clear=True)
            return
        self._open_gate(self.zone)
        self.message("A GATE GRINDS OPEN...", 2.5)
        self.zone += 1
        self.zone_state = "waiting"
        self.app.story.checkpoint("doom", {"zone": self.zone})

    def _respawn(self):
        # clear the zone's enemies and replay its current wave from the start
        z = ZONES[self.zone]
        x, y, a = z["respawn"]
        self.player = Player(x, y, a)
        self.npcs = [n for n in self.npcs if not n.alive]
        self.state = "play"
        self.wave_delay = 0
        if self.zone_state == "fighting":
            self._spawn_wave()
        self.message("TRY AGAIN", 1.5)

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_dx += event.rel[0]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.firing = True
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_f):
                self.firing = True
            elif event.key == pygame.K_TAB:
                self.minimap = not self.minimap
            elif event.key in (pygame.K_RETURN,) and self.state == "won" and self.state_t > 1.5:
                self.app.story.complete()

    def on_pause(self):
        self.mouse_dx = 0

    def skip(self):
        self.app.story.checkpoint("doom", clear=True)
        self.app.story.complete()

    # ------------------------------------------------------------ update
    def update(self, dt):
        super().update(dt)
        self.hurt_flash = max(0.0, self.hurt_flash - dt)
        if self.msg:
            self.msg[1] -= dt
            if self.msg[1] <= 0:
                self.msg = None
        if self.state != "play":
            self.state_t += dt
            self.mouse_dx = 0
            self.firing = False
            if self.state == "dead" and self.state_t > 2.2:
                self._respawn()
            return
        self._move_player(dt)
        p = self.player
        p.since_hurt += dt
        if p.since_hurt > 4 and p.health < MAX_HEALTH:
            p.regen_t += dt
            if p.regen_t > 0.5:
                p.regen_t = 0
                p.health += 1
        for d in self.decor:
            if isinstance(d, Animated):
                d.update(dt)
        for it in self.items:
            it.update(dt)
        self.items = [i for i in self.items if i.alive_sprite]
        for n in self.npcs:
            n.update(dt)
        self._shoot(dt)
        self._update_zones(dt)

    def _move_player(self, dt):
        p = self.player
        keys = pygame.key.get_pressed()
        p.angle = (p.angle + self.mouse_dx * MOUSE_SENS) % math.tau
        self.mouse_dx = 0
        if keys[pygame.K_LEFT]:
            p.angle -= TURN_SPEED * dt
        if keys[pygame.K_RIGHT]:
            p.angle += TURN_SPEED * dt
        sin_a, cos_a = math.sin(p.angle), math.cos(p.angle)
        fwd = (1 if keys[pygame.K_w] or keys[pygame.K_UP] else 0) - (1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0)
        side = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        dx = fwd * cos_a - side * sin_a
        dy = fwd * sin_a + side * cos_a
        n = math.hypot(dx, dy)
        if n:
            step = PLAYER_SPEED * dt / n
            dx, dy = dx * step, dy * step
            r = PLAYER_SIZE if dx > 0 else -PLAYER_SIZE
            if self.free(int(p.x + dx + r), int(p.y)):
                p.x += dx
            r = PLAYER_SIZE if dy > 0 else -PLAYER_SIZE
            if self.free(int(p.x), int(p.y + dy + r)):
                p.y += dy

    def _shoot(self, dt):
        self.shot_t = max(0.0, self.shot_t - dt)
        if not self.firing:
            return
        self.firing = False
        if self.shot_t > 0:
            return
        self.shot_t = 0.55
        self.sound("shotgun", 0.3)
        target = None
        for n in sorted((n for n in self.npcs if n.alive), key=lambda n: n.dist):
            if n.sees_player and abs(n.screen_x - HALF_W) < max(10, n.half_w * 0.8) and n.norm_dist > 0.4:
                target = n
                break
        if target:
            dmg = 60 if target.dist < 3 else 45 if target.dist < 6 else 30
            target.hit(dmg)

    # ------------------------------------------------------------ rendering
    def _raycast(self):
        p = self.player
        ox, oy = p.x, p.y
        mx, my = int(ox), int(oy)
        angle = p.angle - HALF_FOV + 0.0001
        world = self.world
        out = self.render_list
        for ray in range(NUM_RAYS):
            sin_a, cos_a = math.sin(angle), math.cos(angle)
            # horizontals
            y_hor, dy = (my + 1, 1) if sin_a > 0 else (my - 1e-6, -1)
            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a
            delta = dy / sin_a
            dx = delta * cos_a
            tex_h = 1
            for _ in range(MAX_DEPTH):
                tile = (int(x_hor), int(y_hor))
                if tile in world:
                    tex_h = world[tile]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta
            # verticals
            x_vert, dx = (mx + 1, 1) if cos_a > 0 else (mx - 1e-6, -1)
            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a
            delta = dx / cos_a
            dy = delta * sin_a
            tex_v = 1
            for _ in range(MAX_DEPTH):
                tile = (int(x_vert), int(y_vert))
                if tile in world:
                    tex_v = world[tile]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta
            if depth_vert < depth_hor:
                depth, tex = depth_vert, tex_v
                y_vert %= 1
                offset = y_vert if cos_a > 0 else 1 - y_vert
            else:
                depth, tex = depth_hor, tex_h
                x_hor %= 1
                offset = 1 - x_hor if sin_a > 0 else x_hor
            depth *= math.cos(p.angle - angle)
            proj = SCREEN_DIST / (depth + 0.0001)
            texture = self.walls.get(tex, self.walls[1])
            if proj < H:
                col = texture.subsurface(offset * (TEX - SCALE), 0, SCALE, TEX)
                col = pygame.transform.scale(col, (SCALE, int(proj)))
                pos = (ray * SCALE, HALF_H - int(proj) // 2)
            else:
                th = TEX * H / proj
                col = texture.subsurface(offset * (TEX - SCALE), HALF_TEX - th // 2, SCALE, th)
                col = pygame.transform.scale(col, (SCALE, H))
                pos = (ray * SCALE, 0)
            # distance fog
            if depth > 4:
                fog = min(170, int((depth - 4) * 18))
                col = col.copy()
                col.fill((fog, fog, fog), special_flags=pygame.BLEND_RGB_SUB)
            out.append((depth, col, pos))
            angle += DELTA_ANGLE

    def draw(self, surf):
        p = self.player
        # sky + floor
        off = int((p.angle / math.tau) * W * 3) % W
        surf.blit(self.sky, (-off, 0))
        surf.blit(self.sky, (W - off, 0))
        for i in range(0, HALF_H, 6):
            k = i / HALF_H
            c = int(14 + 26 * k)
            pygame.draw.rect(surf, (c, c - 4, c - 6), (0, HALF_H + i, W, 6))
        self.render_list = []
        self._raycast()
        for sprite in self.decor + self.items + self.npcs:
            sprite.project()
        for depth, img, pos in sorted(self.render_list, key=lambda t: -t[0]):
            surf.blit(img, pos)

        # weapon
        k = 0
        if self.shot_t > 0:
            k = min(len(self.gun) - 1, int((0.55 - self.shot_t) / 0.55 * len(self.gun)))
        bob = int(math.sin(self.t * 8) * 4) if pygame.key.get_pressed()[pygame.K_w] else 0
        g = self.gun[k]
        surf.blit(g, (HALF_W - g.get_width() // 2, H - g.get_height() + abs(bob)))
        # crosshair
        pygame.draw.line(surf, (255, 255, 255), (HALF_W - 6, HALF_H), (HALF_W - 2, HALF_H))
        pygame.draw.line(surf, (255, 255, 255), (HALF_W + 2, HALF_H), (HALF_W + 6, HALF_H))
        pygame.draw.line(surf, (255, 255, 255), (HALF_W, HALF_H - 6), (HALF_W, HALF_H - 2))
        pygame.draw.line(surf, (255, 255, 255), (HALF_W, HALF_H + 2), (HALF_W, HALF_H + 6))

        if self.hurt_flash > 0:
            b = self.blood.copy()
            b.set_alpha(int(200 * self.hurt_flash / 0.35))
            surf.blit(b, (0, 0))
        self._draw_hud(surf)
        if self.minimap:
            self._draw_minimap(surf)
        if self.state == "dead":
            img = self.lose_img.copy()
            img.set_alpha(min(255, int(self.state_t * 300)))
            surf.blit(img, (0, 0))
        elif self.state == "won":
            img = self.win_img.copy()
            img.set_alpha(min(255, int(self.state_t * 200)))
            surf.blit(img, (0, 0))
            if self.state_t > 1.5 and ui.blink(self.t):
                ui.draw_text(surf, "PRESS ENTER", 10, (HALF_W, H - 30), WHITE, "midtop", shadow=BLACK)

    def _draw_hud(self, surf):
        hp = str(max(0, int(self.player.health)))
        for i, ch in enumerate(hp):
            surf.blit(self.digits[ch], (8 + i * 28, 8))
        surf.blit(self.digits["10"], (8 + len(hp) * 28, 8))
        z = ZONES[self.zone]
        left = sum(1 for n in self.npcs if n.alive)
        ui.draw_text(surf, z["name"], 8, (W - 10, 10), (230, 200, 160), "topright", shadow=BLACK)
        if self.zone_state == "fighting":
            ui.draw_text(surf, f"WAVE {self.wave + 1}/{len(z['waves'])}  DEMONS {left}", 8, (W - 10, 24), WHITE, "topright", shadow=BLACK)
        elif self.zone_state == "waiting":
            ui.draw_text(surf, "PRESS ON...", 8, (W - 10, 24), (200, 200, 200), "topright", shadow=BLACK)
        ui.draw_text(surf, "TAB MAP", 8, (W - 10, H - 16), (140, 140, 140), "topright")
        if self.msg:
            a = min(255, int(self.msg[1] * 400))
            ui.draw_text(surf, self.msg[0], 16, (HALF_W, 70), (255, 80, 60), "midtop", shadow=BLACK, alpha=a)

    def _draw_minimap(self, surf):
        s = 5
        ox, oy = 10, 50
        m = pygame.Surface((len(MAP[0]) * s, len(MAP) * s), pygame.SRCALPHA)
        m.fill((0, 0, 0, 150))
        for (x, y), v in self.world.items():
            m.fill((200, 60, 60) if v == 6 else (150, 150, 150), (x * s, y * s, s, s))
        for n in self.npcs:
            if n.alive:
                pygame.draw.circle(m, (255, 60, 60), (int(n.x * s), int(n.y * s)), 2)
        p = self.player
        pygame.draw.circle(m, (60, 255, 60), (int(p.x * s), int(p.y * s)), 2)
        pygame.draw.line(m, (60, 255, 60), (p.x * s, p.y * s), (p.x * s + math.cos(p.angle) * 8, p.y * s + math.sin(p.angle) * 8))
        surf.blit(m, (ox, oy))
