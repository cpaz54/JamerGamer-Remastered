"""Jamer, his sword and arrows, spiders, and the ghost of the family dungeon."""
import math
import random

import pygame

from .assets import T, flip
from .world import ROOM_W, ROOM_H

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
SWING = 14
SHOOT = 10
MAX_ARROWS = 2


def move_body(room, rect, dx, dy, nudge=True):
    """Move a rect through the room with wall collision and corner-sliding.
    Returns the new rect and whether we bumped into something."""
    bumped = False
    for axis, d in (("x", dx), ("y", dy)):
        if d == 0:
            continue
        r = rect.move(d, 0) if axis == "x" else rect.move(0, d)
        if not room.blocked(r):
            rect = r
            continue
        bumped = True
        if nudge:
            # slide around corners: try shifting a few pixels sideways
            for off in (1, 2, 3, 4, 5, 6, -1, -2, -3, -4, -5, -6):
                rr = r.move(0, off) if axis == "x" else r.move(off, 0)
                side = rect.move(0, off) if axis == "x" else rect.move(off, 0)
                if not room.blocked(rr) and not room.blocked(side):
                    step = 1 if off > 0 else -1
                    rect = rect.move(0, step) if axis == "x" else rect.move(step, 0)
                    break
    return rect, bumped


class Player:
    def __init__(self, art, x, y):
        self.art = art
        self.hit = pygame.Rect(0, 0, 18, 14)        # feet hitbox
        self.hit.midbottom = (x, y)
        self.dir = "down"
        self.anim = 0
        self.moving = False
        self.use = 0            # frames left in an item use pose
        self.using = None       # "sword" / "bow"
        self.invuln = 0
        self.knock = (0, 0, 0)  # dx, dy, frames
        self.push_dir = None
        self.push_t = 0
        self.speed = 2
        self.sword_hit = set()

    @property
    def body(self):
        """Larger rect used for taking damage."""
        return pygame.Rect(self.hit.x - 4, self.hit.y - 14, self.hit.w + 8, self.hit.h + 14)

    @property
    def sprite_pos(self):
        return self.hit.centerx - T // 2, self.hit.bottom - T

    def facing_tile(self):
        """Tile just beyond the edge of the feet hitbox we're facing."""
        h = self.hit
        x, y = {"up": (h.centerx, h.top - 18), "down": (h.centerx, h.bottom + 8),
                "left": (h.left - 8, h.centery), "right": (h.right + 8, h.centery)}[self.dir]
        return x // T, y // T

    def update(self, room, keys, frozen=False):
        self.invuln = max(0, self.invuln - 1)
        bumped = False
        dx = dy = 0
        if self.knock[2] > 0:
            kx, ky, n = self.knock
            self.hit, _ = move_body(room, self.hit, kx, ky, nudge=False)
            self.knock = (kx, ky, n - 1)
        elif not frozen and self.use == 0:
            up, down = keys[pygame.K_UP], keys[pygame.K_DOWN]
            left, right = keys[pygame.K_LEFT], keys[pygame.K_RIGHT]
            dx = (1 if right else 0) - (1 if left else 0)
            dy = (1 if down else 0) - (1 if up else 0)
            if dx or dy:
                # keep facing if it's still one of the held directions
                held = [d for d, on in (("up", up), ("down", down), ("left", left), ("right", right)) if on]
                if self.dir not in held:
                    self.dir = held[0]
                sp = self.speed
                if dx and dy:
                    sx, sy = dx * sp, dy * sp
                    # alternate frames so diagonal speed ~ straight speed
                    if self.anim % 3 == 0:
                        sx = sy = 0
                    self.hit, bumped = move_body(room, self.hit, sx, sy)
                else:
                    self.hit, bumped = move_body(room, self.hit, dx * sp, dy * sp)
        self.moving = bool(dx or dy)
        if self.moving:
            self.anim += 1
        if self.use > 0:
            self.use -= 1
        return bumped and self.moving

    def start_use(self, item):
        self.use = SWING if item == "sword" else SHOOT
        self.using = item
        self.sword_hit = set()

    def sword(self):
        """(image, pos, hitbox) for the current swing frame, or None."""
        if self.use <= 0 or self.using != "sword":
            return None
        a = self.art
        k = (SWING - self.use) * 3 // SWING      # 0, 1, 2 phase of the arc
        px, py = self.sprite_pos
        d = self.dir
        if d == "right":
            imgs = [a.sword_diag, a.sword_right, flip(a.sword_diag, False, True)]
            offs = [(22, -18), (24, 0), (22, 16)]
        elif d == "left":
            imgs = [flip(a.sword_diag), flip(a.sword_right), flip(a.sword_diag, True, True)]
            offs = [(-22, -18), (-24, 0), (-22, 16)]
        elif d == "up":
            imgs = [flip(a.sword_diag), a.sword_up, a.sword_diag]
            offs = [(-18, -22), (0, -24), (18, -22)]
        else:
            imgs = [flip(a.sword_diag, False, True), flip(a.sword_up, False, True), flip(a.sword_diag, True, True)]
            offs = [(18, 20), (0, 24), (-18, 20)]
        ox, oy = offs[k]
        pos = (px + ox, py + oy)
        hb = pygame.Rect(pos[0] + 4, pos[1] + 4, T - 8, T - 8)
        return imgs[k], pos, hb

    def hurt(self, amount, src, room):
        if self.invuln > 0:
            return False
        sx, sy = src
        cx, cy = self.hit.center
        vx, vy = cx - sx, cy - sy
        if abs(vx) > abs(vy):
            kx, ky = (4 if vx > 0 else -4), 0
        else:
            kx, ky = 0, (4 if vy > 0 else -4)
        self.knock = (kx, ky, 8)
        self.invuln = 90
        self.use = 0
        return True

    def draw(self, surf, t, ox=0, oy=0, holding=None):
        a = self.art
        if self.invuln and (self.invuln // 5) % 2 == 0 and holding is None:
            return
        if holding is not None:
            img = a.p_hold
        elif self.use > 0:
            img = a.p_use[self.dir]
        elif self.moving:
            img = a.p_walk[self.dir][(self.anim // 10) % 2]
        else:
            img = a.p_walk[self.dir][0] if self.dir != "down" else a.p_stand
        x, y = self.sprite_pos
        sw = self.sword()
        if sw and self.dir == "up":
            surf.blit(sw[0], (sw[1][0] + ox, sw[1][1] + oy))
        surf.blit(img, (x + ox, y + oy))
        if sw and self.dir != "up":
            surf.blit(sw[0], (sw[1][0] + ox, sw[1][1] + oy))
        if holding is not None:
            surf.blit(holding, (x + ox, y - 26 + oy))


class Arrow:
    def __init__(self, art, player):
        self.dir = player.dir
        self.img = art.arrow[self.dir]
        dx, dy = DIRS[self.dir]
        cx, cy = player.hit.centerx, player.hit.centery - 10
        self.x, self.y = cx - T / 2 + dx * 10, cy - T / 2 + dy * 10
        self.vx, self.vy = dx * 8, dy * 8
        self.alive = True

    @property
    def tip(self):
        """Small hitbox at the arrow head."""
        cx, cy = self.x + T / 2, self.y + T / 2
        if self.vx:
            return pygame.Rect(int(cx + (10 if self.vx > 0 else -14)), int(cy - 3), 6, 6)
        return pygame.Rect(int(cx - 3), int(cy + (10 if self.vy > 0 else -14)), 6, 6)

    def update(self, room):
        self.x += self.vx
        self.y += self.vy
        tip = self.tip
        if tip.right < 0 or tip.left > ROOM_W or tip.bottom < 0 or tip.top > ROOM_H:
            self.alive = False
            return "gone"
        tx, ty = tip.centerx // T, tip.centery // T
        for o in room.objects:
            if o.alive and o.kind == "target" and o.rect.colliderect(tip):
                self.alive = False
                return ("target", o)
        if (tx, ty) in room.solid and room.ch(tx, ty) not in "w=W":
            self.alive = False
            return "wall"
        for o in room.objects:
            if o.alive and o.solid and o.kind not in ("gate", "barrier") and o.rect.colliderect(tip):
                self.alive = False
                return "wall"
        return None

    def draw(self, surf, ox=0, oy=0):
        surf.blit(self.img, (int(self.x) + ox, int(self.y) + oy))


class Spider:
    """Wanders randomly (red) or hunts the player when close (green)."""

    def __init__(self, art, tx, ty, hunter=False):
        self.art = art
        self.rect = pygame.Rect(tx * T + 4, ty * T + 4, T - 8, T - 8)
        self.hunter = hunter
        self.hp = 2 if hunter else 1
        self.dir = random.choice(list(DIRS))
        self.timer = random.randint(10, 60)
        self.anim = random.randint(0, 30)
        self.flash = 0
        self.alive = True

    def update(self, room, player):
        self.anim += 1
        self.flash = max(0, self.flash - 1)
        speed = 1
        px, py = player.hit.center
        if self.hunter and math.hypot(px - self.rect.centerx, py - self.rect.centery) < 5 * T:
            speed = 1 if self.anim % 3 else 2
            if self.timer <= 0:
                vx, vy = px - self.rect.centerx, py - self.rect.centery
                self.dir = ("right" if vx > 0 else "left") if abs(vx) > abs(vy) else ("down" if vy > 0 else "up")
                self.timer = 20
        if self.timer <= 0:
            self.dir = random.choice(["up", "down", "left", "right", "stop", "stop"])
            self.timer = random.randint(T // 2, T * 3 // 2)
        self.timer -= 1
        if self.dir != "stop" and self.flash == 0:
            dx, dy = DIRS[self.dir]
            r = self.rect.move(dx * speed, dy * speed)
            if room.blocked(r) or r.left < 0 or r.right > ROOM_W or r.top < 0 or r.bottom > ROOM_H:
                self.timer = 0
            else:
                self.rect = r

    def draw(self, surf, ox=0, oy=0):
        if self.hunter:
            frames = [self.art.spider_green, flip(self.art.spider_green)]
            img = frames[(self.anim // 15) % 2]
        else:
            d = self.dir if self.dir in DIRS else "down"
            img = self.art.spider[d][(self.anim // 15) % 2]
        if self.flash and self.flash % 4 < 2:
            return
        surf.blit(img, (self.rect.x - 4 + ox, self.rect.y - 4 + oy))


class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x) - 2, int(y), 4, 16)
        self.alive = True

    def update(self):
        self.rect.y += 4
        if self.rect.top > ROOM_H:
            self.alive = False

    def draw(self, surf, ox=0, oy=0):
        pygame.draw.rect(surf, (255, 40, 40), self.rect.move(ox, oy))
        pygame.draw.rect(surf, (255, 200, 200), self.rect.move(ox + 1, oy + 2).inflate(-2, -6))


class Orb:
    def __init__(self, t):
        self.t = t
        self.hp = 3
        self.x = self.y = 0.0
        self.blink = 0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x) + 2, int(self.y) + 2, T - 4, T - 4)

    def update(self, ghost):
        ox, oy = ghost.x + T / 2, ghost.y + T / 2
        if ghost.health == 3:
            self.t += 0.02
            self.x = ox + math.cos(self.t) * T * 3
            self.y = oy + 0.3 * math.sin(self.t) * T * 3
        elif ghost.health == 2:
            self.t += 0.035
            self.x = ox + math.cos(self.t) * T * 3
            self.y = oy + 0.3 * math.sin(self.t) * T * 3
        else:
            self.t += 0.018
            k = 3 * self.t
            self.x = ox + (math.cos(k) * 1.5 + math.sin(self.t) / 3) * T * 1.4
            self.y = oy + (math.sin(k) * 1.5 + math.cos(self.t) / 3) * T * 1.1
        if self.blink:
            self.blink -= 1
        elif random.random() < 0.0045:
            self.blink = 10

    def draw(self, surf, art, ox=0, oy=0):
        if self.blink:
            img = art.orb["closed"]
        else:
            img = art.orb[{3: "white", 2: "yellow", 1: "red"}[self.hp]]
        surf.blit(img, (int(self.x) + ox, int(self.y) + oy))


class Ghost:
    """Hovers, laughing, while its eye orbs protect it. Shoot every orb and the
    ghost turns solid - then an arrow (or a sword, if you can reach) hurts it."""

    def __init__(self, art, tx, ty):
        self.art = art
        self.x0, self.y0 = tx * T - T / 2, ty * T
        self.x, self.y = self.x0, self.y0
        self.t = 0.0
        self.health = 3
        self.solid = False
        self.orbs = [Orb(i * math.pi / 2) for i in range(4)]
        self.lasers = []
        self.anim = 0
        self.dead = False
        self.flash = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x) + 8, int(self.y) + 8, 2 * T - 16, 2 * T - 16)

    def laser_rate(self):
        if len(self.orbs) == 1:
            return 0.03
        return {3: 0.005, 2: 0.007, 1: 0.004}[self.health]

    def update(self, scene):
        self.anim += 1
        self.flash = max(0, self.flash - 1)
        if not self.solid:
            self.t = (self.t + 0.02) % math.tau
            self.x = self.x0 + math.sin(self.t) * T * 5
            self.y = self.y0 + math.cos(self.t) * math.sin(self.t) * T // 2
        for o in self.orbs:
            o.update(self)
            if random.random() < self.laser_rate():
                self.lasers.append(Laser(o.x + T / 2, o.y + T / 2))
                scene.sfx("laser", 0.35)
                scene.puff(o.x, o.y + T // 2, small=True)
        for las in self.lasers:
            las.update()
        self.lasers = [las for las in self.lasers if las.alive]
        if not self.orbs and not self.solid:
            self.solid = True

    def hit_orb(self, orb, scene):
        orb.hp -= 1
        if orb.hp <= 0:
            orb.alive = False
            self.orbs.remove(orb)
            scene.sfx("eye_hurt", 0.6)
            scene.puff(orb.x, orb.y)
        else:
            scene.sfx("eye_injure", 0.5)

    def hit_body(self, scene):
        if not self.solid:
            return False
        self.health -= 1
        self.flash = 20
        scene.shake = 10
        if self.health <= 0:
            self.dead = True
            self.lasers.clear()
            scene.sfx("eye_hurt", 0.8)
            for i in range(6):
                scene.puff(self.x + random.randint(0, T), self.y + random.randint(0, T))
            return True
        scene.sfx("laughing", 0.6)
        n = 4 if self.health == 2 else 8
        self.orbs = [Orb(i * math.tau / n) for i in range(n)]
        self.solid = False
        return True

    def draw(self, surf, ox=0, oy=0):
        a = self.art
        if self.solid:
            img = a.ghost_solid[(self.anim // 20) % 2]
        else:
            from .assets import alpha
            img = alpha(a.ghost_laugh[(self.anim // 20) % 2], 150)
        if self.flash and self.flash % 4 < 2:
            img = img.copy()
            img.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
        surf.blit(img, (int(self.x) + ox, int(self.y) + oy))
        for o in self.orbs:
            o.draw(surf, a, ox, oy)
        for las in self.lasers:
            las.draw(surf, ox, oy)
