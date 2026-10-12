"""The four guardians of the Gauntlet, fought back to back in the arena.

Every attack is telegraphed: a wind-up pose, a glow, or a floor marker.
Bosses are drawn anchored at their feet (self.x, self.y = midbottom).
"""
import math
import random

import pygame

from . import assets
from .physics import Body

FLOOR_Y = 480
LEFT, RIGHT = 40, 920
PLAT_Y = 360
PLATFORMS = [(120, 320), (640, 840)]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# =========================================================== projectiles
class Projectile:
    def __init__(self, image, x, y, vx, vy, radius=14, gravity=0.0, life=400,
                 deflect=True, spin=0.0, kind="", breakable=False, harmful=True):
        self.image = image
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.radius = radius
        self.gravity = gravity
        self.life = life
        self.deflect = deflect
        self.breakable = breakable
        self.spin = spin
        self.angle = 0.0
        self.kind = kind
        self.harmful = harmful
        self.alive = True
        self.t = 0

    @property
    def rect(self):
        r = self.radius
        return pygame.Rect(int(self.x - r), int(self.y - r), 2 * r, 2 * r)

    def update(self, scene):
        self.t += 1
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin
        self.life -= 1
        if self.kind == "rain" and self.y >= FLOOR_Y - self.radius:
            self.alive = False
            scene.particles.burst((self.x, FLOOR_Y - 4), (140, 220, 255), 10, 3)
        elif self.kind == "meteor" and self.y >= FLOOR_Y - self.radius:
            self.alive = False
            scene.particles.burst((self.x, FLOOR_Y - 4), (255, 150, 40), 16, 4)
            scene.shake(4)
            scene.projectiles.append(fire_patch(self.x, 90))
        elif self.kind == "stone":
            self.y = FLOOR_Y - self.radius
        if self.life <= 0 or self.x < LEFT - 60 or self.x > RIGHT + 60 or self.y > FLOOR_Y + 60:
            self.alive = False

    def draw(self, surf, cam):
        if self.kind == "shock":
            self._draw_shock(surf, cam)
            return
        if self.kind == "fire":
            self._draw_fire(surf, cam)
            return
        img = self.image
        if self.spin:
            img = pygame.transform.rotate(img, self.angle)
        elif self.kind in ("side", "flame"):
            ang = -math.degrees(math.atan2(self.vy, self.vx))
            img = pygame.transform.rotate(img, ang)
        surf.blit(img, img.get_rect(center=(int(self.x - cam[0]), int(self.y - cam[1]))))

    def _draw_shock(self, surf, cam):
        base = FLOOR_Y - cam[1]
        x = self.x - cam[0]
        for i in range(6):
            h = 14 + (i % 3) * 10 + random.randint(0, 6)
            px = x - 18 + i * 7
            pygame.draw.polygon(surf, (255, 230, 120), [(px, base), (px + 4, base - h), (px + 8, base)])
        pygame.draw.line(surf, (255, 255, 230), (x - 20, base - 1), (x + 22, base - 1), 3)

    def _draw_fire(self, surf, cam):
        base = FLOOR_Y - cam[1]
        x = self.x - cam[0]
        fade = min(1.0, self.life / 30)
        for i in range(4):
            h = int((18 + random.randint(0, 14)) * fade)
            px = x - 14 + i * 7
            col = (255, random.randint(90, 200), 30)
            pygame.draw.polygon(surf, col, [(px, base), (px + 4, base - h), (px + 9, base)])

    @property
    def hit_rect(self):
        if self.kind == "shock":
            return pygame.Rect(int(self.x - 18), FLOOR_Y - 30, 40, 30)
        if self.kind == "fire":
            return pygame.Rect(int(self.x - 14), FLOOR_Y - 22, 28, 22)
        return self.rect


def fire_patch(x, life=150):
    return Projectile(None, x, FLOOR_Y - 10, 0, 0, life=life, deflect=False, kind="fire")


def shockwave(x, direction, speed=6.0):
    return Projectile(None, x, FLOOR_Y - 15, speed * direction, 0, life=300, deflect=False, kind="shock")


class Warning:
    """Glowing floor marker; when it expires, `spawn()` is called."""

    def __init__(self, x, frames, spawn, color=(255, 60, 40)):
        self.x, self.timer, self.total, self.spawn, self.color = x, frames, frames, spawn, color
        self.alive = True

    def update(self, scene):
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False
            scene.projectiles.append(self.spawn(self.x))

    def draw(self, surf, cam):
        k = 1 - self.timer / self.total
        w = int(20 + 30 * k)
        a = int(80 + 120 * k * (0.6 + 0.4 * math.sin(self.timer * 0.6)))
        s = pygame.Surface((w * 2, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*self.color, a), s.get_rect())
        surf.blit(s, (int(self.x - w - cam[0]), int(FLOOR_Y - 7 - cam[1])))


# =========================================================== base boss
class Boss:
    name = "BOSS"
    title_image = None
    music = None
    max_hp = 10

    def __init__(self, scene):
        self.scene = scene
        self.hp = self.max_hp
        self.x, self.y = 760.0, -200.0
        self.vx = self.vy = 0.0
        self.state = "enter"
        self.timer = 0
        self.facing = -1
        self.flash = 0
        self.iframes = 0
        self.image = None
        self.dead = False          # finished dying -> scene moves on
        self.dying = False
        self.t = 0
        self.alpha = 255

    # ---------------------------------------------------------- helpers
    def set(self, state, frames=0):
        self.state = state
        self.timer = frames

    def face_player(self):
        self.facing = 1 if self.scene.player.cx > self.x else -1

    def dist_to_player(self):
        return abs(self.scene.player.cx - self.x)

    @property
    def phase2(self):
        return self.hp <= self.max_hp // 2

    def hurtbox(self):
        """Rect the player's sword can hit (None if untouchable)."""
        return pygame.Rect(int(self.x - 26), int(self.y - 100), 52, 100)

    def harm_rects(self):
        """Rects that hurt the player on touch."""
        return []

    def parts(self):
        """[(part_id, hurtbox)] — bosses with several bodies override this."""
        hb = self.hurtbox()
        return [(None, hb)] if hb is not None and not self.dying else []

    def take_hit(self, part, direction):
        if self.iframes > 0 or self.dying:
            return False
        self.hp -= 1
        self.flash = 8
        self.iframes = 14
        s = self.scene
        s.audio.blip("hit")
        s.shake(3)
        s.particles.burst((self.x, self.y - 60), (255, 255, 255), 8, 4)
        if self.hp <= 0:
            self.on_zero_hp()
        return True

    def on_zero_hp(self):
        self.dying = True
        self.set("dying", 110)
        self.scene.audio.blip("boom")
        self.scene.shake(10)

    def update(self, scene):
        self.t += 1
        self.timer -= 1
        self.flash = max(0, self.flash - 1)
        self.iframes = max(0, self.iframes - 1)
        handler = getattr(self, "st_" + self.state.split(":")[0])
        handler(scene)

    def st_dying(self, scene):
        if self.t % 6 == 0:
            scene.particles.burst((self.x + random.randint(-30, 30), self.y - random.randint(10, 100)),
                                  random.choice([(255, 255, 255), (200, 200, 200), (255, 200, 120)]), 6, 3)
        self.alpha = max(0, int(255 * self.timer / 110))
        if self.timer <= 0:
            self.dead = True

    def blit(self, surf, cam, image, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        if self.flash and self.flash % 4 < 2:
            image = assets.white(image)
        if self.alpha < 255:
            image = image.copy()
            image.set_alpha(self.alpha)
        rect = image.get_rect(midbottom=(int(x - cam[0]), int(y - cam[1])))
        surf.blit(image, rect)

    def draw(self, surf, cam):
        if self.image is not None:
            self.blit(surf, cam, self.image)

    def bars(self):
        """[(label, hp, max_hp)] for the HUD."""
        return [(self.name, max(0, self.hp), self.max_hp)]


# =========================================================== BIG WILLIG
class BigWillig(Boss):
    name = "BIG WILLIG"
    title_image = "bosses/BIG_WILLIG/ari_title.png"
    music = "platformer/music/ari_music.mp3"
    max_hp = 14

    def __init__(self, scene):
        super().__init__(scene)
        h = lambda rel: assets.img("bosses/BIG_WILLIG/" + rel, scale=0.95, crop=True)  # noqa: E731
        self.stand = [h("stand/stand.png"), h("stand/stand2.png")]
        self.cast = [h("stand_cast/cast1.png"), h("stand_cast/cast2.png")]
        self.float = [h("float_cast/float.png"), h("float_cast/float_cast.png")]
        self.death = [h("death/death.png"), h("death/death2.png")]
        self.fireball = assets.img("bosses/BIG_WILLIG/fire_ball_side.png", size=(44, 50), crop=True)
        self.icefire = assets.img("bosses/BIG_WILLIG/fire_ball_rain.png", size=(34, 46), crop=True)
        self.x, self.y = 760.0, -160.0
        self.image = self.float[0]
        self.cycle = 0
        self.shots = 0
        self.target = (0, 0)
        self.hidden = False

    def hurtbox(self):
        if self.hidden:
            return None
        return pygame.Rect(int(self.x - 24), int(self.y - 110), 48, 110)

    def st_enter(self, scene):
        self.image = self.float[0]
        self.y = min(FLOOR_Y, self.y + 4)
        if self.y >= FLOOR_Y:
            self.set("idle", 50)

    def st_idle(self, scene):
        self.face_player()
        self.image = self.stand[(self.t // 25) % 2]
        if self.timer <= 0:
            order = ["volley", "rain", "volley", "teleport"]
            nxt = order[self.cycle % len(order)]
            self.cycle += 1
            if nxt == "volley":
                self.set("volley_wind", 40 if not self.phase2 else 28)
            elif nxt == "rain":
                self.target = (480, FLOOR_Y - 250)
                self.set("rise")
            else:
                self.set("vanish", 24)
                scene.particles.burst((self.x, self.y - 60), (180, 120, 255), 24, 4)
                scene.audio.blip("swing")

    def st_volley_wind(self, scene):
        self.face_player()
        self.image = self.cast[0]
        if self.timer <= 0:
            self.shots = 5 if self.phase2 else 3
            self.set("volley", 0)

    def st_volley(self, scene):
        self.image = self.cast[1]
        if self.timer <= 0:
            if self.shots <= 0:
                self.set("idle", 70 if not self.phase2 else 45)
                return
            self.shots -= 1
            p = scene.player
            sx, sy = self.x + self.facing * 40, self.y - 80
            ang = math.atan2(p.y + 26 - sy, p.cx - sx)
            speed = 5.5 if not self.phase2 else 6.5
            scene.projectiles.append(Projectile(self.fireball, sx, sy, math.cos(ang) * speed,
                                                math.sin(ang) * speed, radius=16, kind="side"))
            scene.audio.play(scene.audio.synth("fireball", freq=200, dur=0.25, wave="saw", vol=0.25, slide=-120, noise=0.6))
            self.set("volley", 20 if not self.phase2 else 14)

    def st_rise(self, scene):
        self.image = self.float[0]
        tx, ty = self.target
        self.x += clamp(tx - self.x, -5, 5)
        self.y += clamp(ty - self.y, -4, 4)
        if abs(self.x - tx) < 6 and abs(self.y - ty) < 6:
            self.shots = 14 if self.phase2 else 9
            self.set("rain", 10)

    def st_rain(self, scene):
        self.image = self.float[1]
        self.y = self.target[1] + math.sin(self.t * 0.08) * 6
        if self.timer <= 0:
            if self.shots <= 0:
                self.target = (random.choice((180, 780)), FLOOR_Y)
                self.set("descend", 60)
                return
            self.shots -= 1
            p = scene.player
            x = clamp(p.cx + random.randint(-160, 160) if self.shots % 3 == 0 else random.randint(LEFT + 30, RIGHT - 30), LEFT + 20, RIGHT - 20)
            img = self.icefire
            scene.warnings.append(Warning(x, 45, lambda xx: Projectile(img, xx, -30, 0, 7.5, radius=14, deflect=True, kind="rain"),
                                          color=(90, 200, 255)))
            self.set("rain", 12 if not self.phase2 else 8)

    def st_descend(self, scene):
        self.image = self.float[0]
        tx, ty = self.target
        self.x += clamp(tx - self.x, -6, 6)
        self.y += clamp(ty - self.y, -6, 6)
        if abs(self.x - tx) < 7 and abs(self.y - ty) < 7:
            self.x, self.y = tx, ty
            self.set("idle", 80 if not self.phase2 else 55)

    def st_vanish(self, scene):
        self.hidden = True
        if self.timer <= 0:
            p = scene.player
            self.x = 800 if p.cx < 480 else 160
            self.y = FLOOR_Y
            self.hidden = False
            scene.particles.burst((self.x, self.y - 60), (180, 120, 255), 24, 4)
            self.set("volley_wind", 30)

    def st_dying(self, scene):
        self.image = self.death[(self.t // 10) % 2]
        super().st_dying(scene)

    def draw(self, surf, cam):
        if self.hidden:
            return
        if self.state == "volley_wind":
            # charging orb on the staff
            k = 1 - self.timer / 40
            r = int(4 + 12 * k)
            ox = self.x + self.facing * 38 - cam[0]
            oy = self.y - 105 - cam[1]
            glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 140, 40, 90), (r * 2, r * 2), r * 2)
            pygame.draw.circle(glow, (255, 230, 150, 220), (r * 2, r * 2), r)
            surf.blit(glow, (ox - r * 2, oy - r * 2))
        img = self.image
        if self.facing > 0 and self.state in ("volley_wind", "volley"):
            img = pygame.transform.flip(img, True, False)
        self.blit(surf, cam, img)


# =========================================================== JESTER CARS
class Jester(Boss):
    name = "JESTER CARS"
    title_image = "bosses/JESTER/carson_title.png"
    music = "platformer/music/carson_music.mp3"
    max_hp = 16

    def __init__(self, scene):
        super().__init__(scene)
        j = lambda rel, **kw: assets.img("bosses/JESTER/" + rel, scale=0.95, crop=True, **kw)  # noqa: E731
        self.stand = {1: j("stand/facing_right.png"), -1: j("attack_left/facing_left.png")}
        self.walk = {1: [j("walk_right/walk_right.png"), j("walk_right/walk_right2.png")],
                     -1: [j("walk_left/walk_left.png"), j("walk_left/walk_left2.png")]}
        self.attack = {1: j("attack_right/attack_right.png"), -1: j("attack_left/attack_left.png")}
        self.slash = {1: assets.img("bosses/JESTER/attack_right/slash_right.png", size=(130, 130), crop=True),
                      -1: assets.img("bosses/JESTER/attack_left/slash_left.png", size=(130, 130), crop=True)}
        self.jump = {1: j("jump/jump.png"), -1: j("jump/jump.png", flip=True)}
        self.squat = {1: j("jump/squat.png", flip=True), -1: j("jump/squat.png")}
        self.stone = assets.img("bosses/JESTER/stone.png", size=(40, 40), crop=True)
        self.body = Body(780, -200, 50, 110)
        self.x, self.y = 780.0, -200.0
        self.image = self.jump[-1]
        self.shots = 0
        self.combo = 0
        self.last = None

    # body <-> anchor sync
    def _sync(self):
        self.x = self.body.cx
        self.y = self.body.bottom

    def _physics(self, scene):
        self.body.move(scene.level, ())
        self._sync()

    def hurtbox(self):
        return pygame.Rect(int(self.x - 26), int(self.y - 105), 52, 105)

    def harm_rects(self):
        if self.state in ("walk", "leap_air"):
            return [self.hurtbox().inflate(-12, -10)]
        if self.state == "swing" and self.timer > 4:
            r = pygame.Rect(0, 0, 120, 110)
            r.midbottom = (int(self.x + self.facing * 70), int(self.y))
            return [r]
        return []

    def st_enter(self, scene):
        self.image = self.jump[-1]
        self._physics(scene)
        if self.body.on_ground:
            scene.shake(6)
            self.set("idle", 40)

    def choose(self):
        d = self.dist_to_player()
        if d < 150:
            return "swing"
        options = ["walk", "leap", "bowl"]
        if self.last in options and random.random() < 0.7:
            options.remove(self.last)
        return random.choice(options)

    def st_idle(self, scene):
        self.face_player()
        self.body.vx = 0
        self._physics(scene)
        self.image = self.stand[self.facing]
        if self.timer <= 0:
            nxt = self.choose()
            self.last = nxt
            if nxt == "swing":
                self.combo = 2 if self.phase2 else 1
                self.set("swing_wind", 22)
            elif nxt == "walk":
                self.set("walk", 100)
            elif nxt == "leap":
                self.combo = 2 if self.phase2 else 1
                self.set("leap_squat", 26)
            else:
                self.shots = 5 if self.phase2 else 3
                self.set("bowl_wind", 30)

    def st_walk(self, scene):
        self.face_player()
        self.body.vx = self.facing * (3.1 if self.phase2 else 2.3)
        self._physics(scene)
        self.image = self.walk[self.facing][(self.t // 10) % 2]
        if self.dist_to_player() < 120:
            self.combo = 2 if self.phase2 else 1
            self.set("swing_wind", 20)
        elif self.timer <= 0:
            self.set("idle", 20)

    def st_swing_wind(self, scene):
        self.body.vx = 0
        self._physics(scene)
        self.image = self.stand[self.facing]
        if self.timer <= 0:
            self.set("swing", 14)
            scene.audio.blip("swing")

    def st_swing(self, scene):
        self.body.vx = self.facing * 2
        self._physics(scene)
        self.image = self.attack[self.facing]
        if self.timer <= 0:
            self.combo -= 1
            if self.combo > 0:
                self.face_player()
                self.set("swing_wind", 12)
            else:
                self.set("recover", 34)

    def st_recover(self, scene):
        self.body.vx = 0
        self._physics(scene)
        self.image = self.stand[self.facing]
        if self.timer <= 0:
            self.set("idle", 16 if self.phase2 else 30)

    def st_leap_squat(self, scene):
        self.face_player()
        self.body.vx = 0
        self._physics(scene)
        self.image = self.squat[self.facing]
        if self.timer <= 0:
            target = clamp(scene.player.cx, LEFT + 40, RIGHT - 40)
            air = 2 * 14 / 0.62
            self.body.vy = -14
            self.body.vx = clamp((target - self.x) / air, -9, 9)
            self.set("leap_air")
            self.body.on_ground = False

    def st_leap_air(self, scene):
        self.image = self.jump[self.facing]
        self._physics(scene)
        if self.body.on_ground and self.body.vy == 0:
            self.body.vx = 0
            scene.shake(8)
            scene.audio.blip("boom")
            scene.projectiles.append(shockwave(self.x - 30, -1))
            scene.projectiles.append(shockwave(self.x + 30, 1))
            self.combo -= 1
            if self.combo > 0:
                self.set("leap_squat", 20)
            else:
                self.set("recover", 40)

    def st_bowl_wind(self, scene):
        self.face_player()
        self.body.vx = 0
        self._physics(scene)
        self.image = self.squat[self.facing]
        if self.timer <= 0:
            self.set("bowl", 0)

    def st_bowl(self, scene):
        self.image = self.squat[self.facing]
        self._physics(scene)
        if self.timer <= 0:
            if self.shots <= 0:
                self.set("recover", 30)
                return
            self.shots -= 1
            speed = 5.5 if not self.phase2 else 6.5
            scene.projectiles.append(Projectile(self.stone, self.x + self.facing * 40, FLOOR_Y - 20, self.facing * speed, 0,
                                                radius=18, deflect=False, breakable=True, spin=-self.facing * 9, kind="stone"))
            scene.audio.play(scene.audio.synth("roll", freq=70, dur=0.3, wave="saw", vol=0.3, noise=0.7))
            self.set("bowl", 30 if not self.phase2 else 22)

    def st_dying(self, scene):
        self.image = self.stand[self.facing]
        self._physics(scene)
        super().st_dying(scene)

    def draw(self, surf, cam):
        if self.state == "swing" and self.timer > 3:
            img = self.slash[self.facing]
            surf.blit(img, img.get_rect(midbottom=(int(self.x + self.facing * 70 - cam[0]), int(self.y + 6 - cam[1]))))
        if self.state in ("swing_wind", "leap_squat", "bowl_wind") and self.t % 8 < 4:
            pygame.draw.circle(surf, (255, 220, 80), (int(self.x - cam[0]), int(self.y - 125 - cam[1])), 5)
        super().draw(surf, cam)


# =========================================================== LAURTNEY (two bodies)
class Laurtney(Boss):
    name = "LAURTNEY"
    title_image = "bosses/LAURTNEY/laurtney_title.png"
    music = "platformer/music/laurtney_music.mp3"
    max_hp = 9   # each

    def __init__(self, scene):
        super().__init__(scene)
        L = lambda rel, **kw: assets.img("bosses/LAURTNEY/" + rel, height=104, crop=True, **kw)  # noqa: E731
        self.l_stand = {1: L("l_stand/l_face_right.png"), -1: L("l_stand/l_face_right.png", flip=True)}
        self.l_throw = {1: [L("l_attack_right/l_throw_right.png"), L("l_attack_right/l_throw_right2.png")],
                        -1: [L("l_attack_left/l_attack_left.png"), L("l_attack_right/l_throw_right2.png", flip=True)]}
        self.c_stand = {1: L("c_stand/c_face_right.png"), -1: L("c_stand/c_face_left.png")}
        self.c_attack = {1: L("c_attack_right/c_attack_right.png"), -1: L("c_attack_left/c_attack_left.png")}
        self.shuriken = assets.img("bosses/LAURTNEY/shurikin.png", size=(34, 34), crop=True)

        self.l = Body(200, -260, 40, 100)
        self.c = Body(740, -160, 44, 100)
        self.l_hp = self.c_hp = self.max_hp
        self.l_state, self.l_timer, self.l_face = "enter", 0, 1
        self.c_state, self.c_timer, self.c_face = "enter", 0, -1
        self.l_flash = self.c_flash = 0
        self.l_iframes = self.c_iframes = 0
        self.l_alpha = self.c_alpha = 255
        self.l_shots = 0
        self.l_bursts = 0
        self.l_perch = 0      # which platform L is on
        self.c_below = 0
        self.hp = self.l_hp + self.c_hp
        self.x, self.y = 480, FLOOR_Y
        self.state = "active"     # each body runs its own state machine

    # combined hp drives the generic phase2 property; each body tracks its own
    @property
    def enraged(self):
        return self.l_hp <= 0 or self.c_hp <= 0

    def bars(self):
        return [("L", max(0, self.l_hp), self.max_hp), ("C", max(0, self.c_hp), self.max_hp)]

    def parts(self):
        out = []
        if self.l_hp > 0:
            out.append(("L", pygame.Rect(int(self.l.x - 4), int(self.l.y), 48, 100)))
        if self.c_hp > 0:
            out.append(("C", pygame.Rect(int(self.c.x - 4), int(self.c.y), 52, 100)))
        return out

    def harm_rects(self):
        out = []
        if self.c_hp > 0 and self.c_state == "dash":
            r = self.c.rect.inflate(30, -10)
            out.append(r)
        return out

    def take_hit(self, part, direction):
        s = self.scene
        if part == "L" and self.l_iframes == 0 and self.l_hp > 0:
            self.l_hp -= 1
            self.l_flash, self.l_iframes = 8, 14
            pos = self.l.rect.center
        elif part == "C" and self.c_iframes == 0 and self.c_hp > 0:
            self.c_hp -= 1
            self.c_flash, self.c_iframes = 8, 14
            self.c.vx = direction * 4
            pos = self.c.rect.center
        else:
            return False
        s.audio.blip("hit")
        s.shake(3)
        s.particles.burst(pos, (255, 255, 255), 8, 4)
        if self.l_hp <= 0 and self.l_state != "down":
            self.l_state, self.l_timer = "down", 90
            s.audio.blip("boom")
            s.float_text("L DOWN!", (self.l.cx, self.l.y - 10), (255, 200, 120))
        if self.c_hp <= 0 and self.c_state != "down":
            self.c_state, self.c_timer = "down", 90
            s.audio.blip("boom")
            s.float_text("C DOWN!", (self.c.cx, self.c.y - 10), (255, 200, 120))
        self.hp = max(0, self.l_hp) + max(0, self.c_hp)
        if self.hp <= 0:
            self.dying = True
            self.state, self.timer = "dying", 100
        return True

    def update(self, scene):
        self.t += 1
        self.timer -= 1
        self.l_flash = max(0, self.l_flash - 1)
        self.c_flash = max(0, self.c_flash - 1)
        self.l_iframes = max(0, self.l_iframes - 1)
        self.c_iframes = max(0, self.c_iframes - 1)
        self._update_l(scene)
        self._update_c(scene)
        if self.dying and self.timer <= 0 and self.l_alpha == 0 and self.c_alpha == 0:
            self.dead = True

    # ---------------------------------------------------------------- L
    def _update_l(self, scene):
        L, p = self.l, scene.player
        self.l_timer -= 1
        st = self.l_state
        if st == "down":
            self.l_alpha = max(0, int(255 * self.l_timer / 90))
            if self.l_timer % 6 == 0 and self.l_alpha:
                scene.particles.burst(L.rect.center, (230, 230, 230), 5, 3)
            L.vx = 0
            L.move(scene.level, ())
            return
        self.l_face = 1 if p.cx > L.cx else -1
        if st == "enter":
            L.move(scene.level, ())
            if L.on_ground:
                self.l_state, self.l_timer = "perch", 50
        elif st == "perch":
            L.vx = 0
            L.move(scene.level, ())
            if self.l_timer <= 0:
                self.l_shots = 5 if self.enraged else 3
                self.l_state, self.l_timer = "throw", 16
        elif st == "throw":
            L.move(scene.level, ())
            if self.l_timer <= 0:
                if self.l_shots <= 0:
                    self.l_bursts += 1
                    if self.l_bursts >= 2:
                        self.l_bursts = 0
                        self._hop()
                    else:
                        self.l_state, self.l_timer = "perch", 95 if not self.enraged else 65
                    return
                self.l_shots -= 1
                sx, sy = L.cx + self.l_face * 20, L.y + 34
                ang = math.atan2(p.y + 26 - sy, p.cx - sx)
                spd = 6.0 if not self.enraged else 7.2
                scene.projectiles.append(Projectile(self.shuriken, sx, sy, math.cos(ang) * spd, math.sin(ang) * spd,
                                                    radius=12, spin=18, kind="shuriken"))
                scene.audio.play(scene.audio.synth("shuriken", freq=1400, dur=0.08, wave="sine", vol=0.18, slide=-700, noise=0.4))
                self.l_timer = 18 if not self.enraged else 13
        elif st == "hop":
            L.move(scene.level, ())
            if L.on_ground and L.vy == 0:
                L.vx = 0
                self.l_state, self.l_timer = "perch", 60

    def _hop(self):
        L = self.l
        self.l_perch = 1 - self.l_perch
        lo, hi = PLATFORMS[self.l_perch]
        target = (lo + hi) / 2
        air = 2 * 14 / 0.62
        L.vy = -14
        L.vx = (target - L.cx) / air
        L.on_ground = False
        self.l_state = "hop"

    # ---------------------------------------------------------------- C
    def _update_c(self, scene):
        C, p = self.c, scene.player
        self.c_timer -= 1
        st = self.c_state
        if st == "down":
            self.c_alpha = max(0, int(255 * self.c_timer / 90))
            if self.c_timer % 6 == 0 and self.c_alpha:
                scene.particles.burst(C.rect.center, (230, 230, 230), 5, 3)
            C.vx *= 0.8
            C.move(scene.level, ())
            return
        if st not in ("dash",):
            self.c_face = 1 if p.cx > C.cx else -1
        fast = self.enraged
        if st == "enter":
            C.move(scene.level, ())
            if C.on_ground:
                scene.shake(5)
                self.c_state, self.c_timer = "stalk", 50
        elif st == "stalk":
            C.vx = self.c_face * (2.8 if fast else 2.0)
            C.move(scene.level, ())
            # chase the player up onto a ledge if they camp there
            if p.y + p.h < PLAT_Y + 4 and C.on_ground:
                self.c_below += 1
            else:
                self.c_below = 0
            if self.c_below > 70:
                self.c_below = 0
                C.vy = -13.5
                C.on_ground = False
            # c_timer doubles as the cooldown before the next dash
            if self.c_timer <= 0 and abs(p.cx - C.cx) < 160 and abs((p.y + p.h) - C.bottom) < 60:
                self.c_state, self.c_timer = "wind", 22 if not fast else 14
                C.vx = 0
        elif st == "wind":
            C.vx = 0
            C.move(scene.level, ())
            if self.c_timer <= 0:
                self.c_state, self.c_timer = "dash", 16
                scene.audio.blip("swing")
        elif st == "dash":
            C.vx = self.c_face * (11 if fast else 9)
            C.move(scene.level, ())
            if self.c_timer <= 0 or C.hit_wall:
                C.vx = 0
                self.c_state, self.c_timer = "recover", 34 if fast else 50
        elif st == "recover":
            C.vx = 0
            C.move(scene.level, ())
            if self.c_timer <= 0:
                self.c_state, self.c_timer = "stalk", 50 if fast else 75

    # ---------------------------------------------------------------- draw
    def _blit_part(self, surf, cam, image, body, flash, alpha):
        if flash and flash % 4 < 2:
            image = assets.white(image)
        if alpha < 255:
            image = image.copy()
            image.set_alpha(alpha)
        surf.blit(image, image.get_rect(midbottom=(int(body.cx - cam[0]), int(body.bottom + 2 - cam[1]))))

    def draw(self, surf, cam):
        if self.l_alpha > 0:
            if self.l_state == "throw":
                img = self.l_throw[self.l_face][0 if self.l_timer > 8 else 1]
            else:
                img = self.l_stand[self.l_face]
            self._blit_part(surf, cam, img, self.l, self.l_flash, self.l_alpha)
        if self.c_alpha > 0:
            if self.c_state == "dash":
                img = self.c_attack[self.c_face]
            else:
                img = self.c_stand[self.c_face]
            if self.c_state == "wind" and self.t % 6 < 3:
                pygame.draw.circle(surf, (255, 80, 80), (int(self.c.cx - cam[0]), int(self.c.y - 18 - cam[1])), 5)
            self._blit_part(surf, cam, img, self.c, self.c_flash, self.c_alpha)


# =========================================================== DREAD KNIGHT KEV
# phase-change timeline (frames counting down): rise + refill, hover in flames, drop
TF_TOTAL, TF_IGNITE, TF_DESCEND = 190, 90, 36
TF_PEAK_Y = FLOOR_Y - 230


class DreadKnight(Boss):
    name = "DREAD KNIGHT KEV"
    title_image = "bosses/DREAD_KNIGHT/kev_title.png"
    music = "platformer/music/kev_phase_1.mp3"
    max_hp = 20
    max_hp2 = 22

    def __init__(self, scene, start_phase2=False):
        super().__init__(scene)
        k = lambda rel, **kw: assets.img("bosses/DREAD_KNIGHT/" + rel, height=150, crop=True, **kw)  # noqa: E731
        self.stand = {1: k("facing_right.png"), -1: k("facing_right.png", flip=True)}
        self.charge = {1: [k("charging_right.png"), k("charging_right_2.png")],
                       -1: [k("charge_left/charge_left.png"), k("charge_left/char_left2.png")]}
        self.swing = {1: k("sword_right/sword_swing_right.png"), -1: k("sword_swing_left.png")}
        self.backswing = {1: k("sword_right_backswing.png"), -1: k("sword_right_backswing.png", flip=True)}
        f = lambda rel: assets.img("bosses/DREAD_KNIGHT/" + rel, height=210, crop=True)  # noqa: E731
        self.flame = {1: [f("flame_right/flame_right1.png"), f("flame_right/flame_right_2.png")],
                      -1: [f("flame_left/flame_left_1.png"), f("flame_left/flame_left_2.png")]}
        self.fireball = assets.img("bosses/DREAD_KNIGHT/flame_throw.png", size=(64, 28), crop=True)
        self.meteor = assets.img("bosses/DREAD_KNIGHT/flame_rain.png", size=(52, 52), crop=True)
        self.second = False
        self.x, self.y = 480.0, -220.0
        self.image = self.stand[-1]
        self.shots = 0
        self.volleys = 0
        self.last = None
        self.dash_dir = 1
        self.trail_x = 0
        if start_phase2:
            self.second = True
            self.max_hp = self.max_hp2
            self.hp = self.max_hp2
            self.music = "platformer/music/kev_phase_2.mp3"

    def hurtbox(self):
        if self.state in ("transform",):
            return None
        return pygame.Rect(int(self.x - 34), int(self.y - 118), 68, 118)

    def head_box(self):
        """Phase 2: a wide box over his head, reachable from the raised platforms."""
        return pygame.Rect(int(self.x - 55), int(self.y - 215), 110, 100)

    def parts(self):
        hb = self.hurtbox()
        if hb is None or self.dying:
            return []
        if self.second:
            # same part id, so one swing still counts as one hit
            return [(None, hb), (None, self.head_box())]
        return [(None, hb)]

    def harm_rects(self):
        if self.state in ("charge", "flame_dash"):
            return [self.hurtbox().inflate(-10, -16).move(0, 8)]
        if self.state == "slash" and self.timer > 3:
            r = pygame.Rect(0, 0, 150, 100)
            r.midbottom = (int(self.x + self.facing * 80), int(self.y))
            return [r]
        return []

    def on_zero_hp(self):
        if not self.second:
            self.rise_from = (self.x, self.y)
            self.max_hp = self.max_hp2
            self.hp = 0
            self.set("transform", TF_TOTAL)
            self.scene.audio.stop_music(300)
            self.scene.audio.blip("boom")
            self.scene.shake(12)
            self.scene.flash(25)
            return
        super().on_zero_hp()

    # ------------------------------------------------------------- phase 1
    def st_enter(self, scene):
        self.image = self.stand[-1]
        self.y = min(FLOOR_Y, self.y + 9)
        if self.y >= FLOOR_Y:
            scene.shake(10)
            scene.audio.blip("boom")
            self.set("idle" if not self.second else "idle2", 50)

    def st_idle(self, scene):
        self.face_player()
        self.image = self.stand[self.facing]
        if self.timer <= 0:
            options = ["charge", "slash", "charge", "slash"]
            nxt = random.choice(options)
            if nxt == self.last and random.random() < 0.6:
                nxt = "slash" if nxt == "charge" else "charge"
            self.last = nxt
            if nxt == "charge":
                self.dash_dir = 1 if self.x < 480 else -1
                self.facing = self.dash_dir
                self.set("charge_wind", 44 if self.hp > 10 else 32)
            else:
                self.set("slash_walk", 90)

    def st_charge_wind(self, scene):
        self.image = self.charge[self.facing][0]
        if self.t % 5 == 0:
            scene.particles.burst((self.x - self.facing * 40, FLOOR_Y - 4), (150, 140, 130), 3, 2)
        if self.timer <= 0:
            self.set("charge", 140)
            scene.audio.play(scene.audio.synth("charge", freq=90, dur=0.5, wave="saw", vol=0.35, slide=60, noise=0.5))

    def st_charge(self, scene):
        self.image = self.charge[self.facing][(self.t // 6) % 2]
        self.x += self.facing * (10.5 if self.hp > 10 else 12.5)
        if self.x <= LEFT + 50 or self.x >= RIGHT - 50:
            self.x = clamp(self.x, LEFT + 50, RIGHT - 50)
            scene.shake(12)
            scene.audio.blip("boom")
            scene.particles.burst((self.x + self.facing * 40, self.y - 70), (200, 200, 200), 18, 5)
            self.set("stunned", 80)

    def st_stunned(self, scene):
        self.image = self.stand[self.facing]
        if self.timer <= 0:
            self.set("idle", 25)

    def st_slash_walk(self, scene):
        self.face_player()
        self.image = self.charge[self.facing][(self.t // 10) % 2]
        self.x = clamp(self.x + self.facing * 2.6, LEFT + 50, RIGHT - 50)
        if self.dist_to_player() < 150:
            self.set("slash_wind", 26 if self.hp > 10 else 18)
        elif self.timer <= 0:
            self.set("idle", 20)

    def st_slash_wind(self, scene):
        self.image = self.backswing[self.facing]
        if self.timer <= 0:
            self.set("slash", 12)
            scene.audio.blip("swing")

    def st_slash(self, scene):
        self.image = self.swing[self.facing]
        self.x = clamp(self.x + self.facing * 3, LEFT + 50, RIGHT - 50)
        if self.timer <= 0:
            self.set("recover", 34)

    def st_recover(self, scene):
        self.image = self.swing[self.facing]
        if self.timer <= 0:
            self.set("idle" if not self.second else "idle2", 20)

    # ------------------------------------------------------------- transform
    def st_transform(self, scene):
        # rise to the top-centre while the bar refills, ignite, then drop back down
        k = self.timer
        if k > TF_IGNITE:
            u = (TF_TOTAL - k) / (TF_TOTAL - TF_IGNITE)
            e = u * u * (3 - 2 * u)
            fx, fy = self.rise_from
            self.x = fx + (480 - fx) * e
            self.y = fy + (TF_PEAK_Y - fy) * e
            self.hp = max(1, round(self.max_hp2 * u))
            self.image = self.stand[self.facing]
        elif k > TF_DESCEND:
            self.y = TF_PEAK_Y + math.sin(self.t * 0.08) * 5
            self.image = self.flame[self.facing][(self.t // 5) % 2]
        else:
            u = 1 - k / TF_DESCEND
            self.y = TF_PEAK_Y + (FLOOR_Y - TF_PEAK_Y) * u * u
            self.image = self.flame[self.facing][(self.t // 5) % 2]
        if k == TF_IGNITE:
            self.hp = self.max_hp2
            scene.flash(30)
            scene.audio.blip("boom")
            scene.shake(14)
            scene.set_arena_bg("terrain/burning_cathedral.png")
            scene.float_text("PHASE II", (480, 200), (255, 120, 40), big=True)
        if k % 4 == 0:
            scene.particles.burst((self.x + random.randint(-40, 40), self.y - random.randint(20, 140)),
                                  random.choice([(255, 120, 30), (255, 220, 80), (200, 40, 20)]), 5, 4)
        if k <= 0:
            self.x, self.y = 480, FLOOR_Y
            scene.shake(10)
            scene.audio.blip("boom")
            self.second = True
            self.hp = self.max_hp2
            self.music = "platformer/music/kev_phase_2.mp3"
            scene.audio.music(self.music, fade_ms=200)
            scene.checkpoint_phase2()
            self.set("idle2", 30)

    # ------------------------------------------------------------- phase 2
    def st_idle2(self, scene):
        self.face_player()
        self.image = self.flame[self.facing][(self.t // 8) % 2]
        if self.timer <= 0:
            options = ["flame_dash", "fireballs", "meteors"]
            if self.last in options:
                options.remove(self.last)
            nxt = random.choice(options)
            self.last = nxt
            if nxt == "flame_dash":
                self.dash_dir = 1 if self.x < 480 else -1
                self.facing = self.dash_dir
                self.set("flame_wind", 36)
            elif nxt == "fireballs":
                self.volleys = 3 if self.hp <= 11 else 2
                self.set("fireballs", 30)
            else:
                self.shots = 16 if self.hp <= 11 else 12
                self.set("meteors", 20)

    def st_flame_wind(self, scene):
        self.image = self.flame[self.facing][(self.t // 4) % 2]
        if self.t % 3 == 0:
            scene.particles.burst((self.x - self.facing * 30, self.y - 30), (255, 140, 30), 3, 3)
        if self.timer <= 0:
            self.trail_x = self.x
            self.set("flame_dash", 120)
            scene.audio.play(scene.audio.synth("charge", freq=90, dur=0.5, wave="saw", vol=0.35, slide=60, noise=0.5))

    def st_flame_dash(self, scene):
        self.image = self.flame[self.facing][(self.t // 4) % 2]
        self.x += self.facing * 12.5
        if abs(self.x - self.trail_x) >= 44:
            self.trail_x = self.x
            scene.projectiles.append(fire_patch(self.x - self.facing * 20, 130))
        if self.x <= LEFT + 60 or self.x >= RIGHT - 60:
            self.x = clamp(self.x, LEFT + 60, RIGHT - 60)
            scene.shake(8)
            self.set("idle2", 60)

    def st_fireballs(self, scene):
        self.face_player()
        self.image = self.flame[self.facing][(self.t // 8) % 2]
        if self.timer <= 0:
            if self.volleys <= 0:
                self.set("idle2", 50)
                return
            self.volleys -= 1
            p = scene.player
            sx, sy = self.x + self.facing * 50, self.y - 100
            base = math.atan2(p.y + 26 - sy, p.cx - sx)
            for spread in (-0.28, 0.0, 0.28):
                a = base + spread
                scene.projectiles.append(Projectile(self.fireball, sx, sy, math.cos(a) * 6.2, math.sin(a) * 6.2,
                                                    radius=14, kind="flame"))
            scene.audio.play(scene.audio.synth("fireball", freq=200, dur=0.25, wave="saw", vol=0.25, slide=-120, noise=0.6))
            self.set("fireballs", 40)

    def st_meteors(self, scene):
        self.image = self.flame[self.facing][(self.t // 6) % 2]
        if self.timer <= 0:
            if self.shots <= 0:
                self.set("idle2", 70)
                return
            self.shots -= 1
            p = scene.player
            x = p.cx + random.randint(-60, 60) if self.shots % 4 == 0 else random.randint(LEFT + 30, RIGHT - 30)
            x = clamp(x, LEFT + 20, RIGHT - 20)
            img = self.meteor
            scene.warnings.append(Warning(x, 50, lambda xx: Projectile(img, xx + 60, -40, -1.2, 9, radius=18, deflect=False, kind="meteor")))
            self.set("meteors", 9)

    def st_dying(self, scene):
        self.image = self.flame[self.facing][(self.t // 6) % 2]
        super().st_dying(scene)

    def draw(self, surf, cam):
        if self.state == "charge_wind" and self.t % 6 < 3:
            pygame.draw.circle(surf, (255, 40, 40), (int(self.x + self.facing * 8 - cam[0]), int(self.y - 128 - cam[1])), 4)
        if self.state == "stunned":
            for i in range(3):
                a = self.t * 0.15 + i * math.tau / 3
                pygame.draw.circle(surf, (255, 240, 120),
                                   (int(self.x + math.cos(a) * 26 - cam[0]), int(self.y - 150 + math.sin(a) * 8 - cam[1])), 4)
        if self.state == "transform" and self.timer > TF_IGNITE and self.t % 4 < 2:
            dx = random.randint(-4, 4)
            self.blit(surf, cam, self.image, x=self.x + dx)
            return
        super().draw(surf, cam)


BOSS_ORDER = [BigWillig, Jester, Laurtney, DreadKnight]
