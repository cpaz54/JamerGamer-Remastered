"""Chapter II: The Gauntlet - three stages, then a four-boss rush."""
import math
import random

import pygame

from .. import ui
from ..config import BLACK, WHITE
from ..scene import Scene
from . import assets
from .bosses import BOSS_ORDER, DreadKnight, FLOOR_Y, PLATFORMS, PLAT_Y
from .entities import FloatText, Moth, Particles, spawn
from .level import Level, TILE
from .levels import ARENA, STAGES
from .player import MAX_HEARTS, Player

VIEW_W, VIEW_H = 960, 540
JUMP_KEYS = (pygame.K_w, pygame.K_SPACE, pygame.K_UP)
ATTACK_KEYS = (pygame.K_j, pygame.K_k)
STAGE_MUSIC = "platformer/music/world.mp3"


class PlatformerScene(Scene):
    size = (VIEW_W, VIEW_H)
    title = "THE GAUNTLET"

    def __init__(self, app):
        super().__init__(app)
        self.particles = Particles()
        self.texts = []
        self.jump_pressed = False
        self.attack_pressed = False
        self.shake_amt = 0.0
        self.flash_t = 0
        self.banner = None          # (text, sub, frames_left)
        self.cam = [0.0, 0.0]
        self.heart_img = assets.img("life/life.png", size=(26, 26))
        self.heart_empty = assets.tinted(self.heart_img, (60, 50, 60))
        cp = app.story.checkpoint("platformer") or {}
        if "boss" in cp:
            self.start_arena(cp["boss"], cp.get("kev2", False))
        else:
            self.start_stage(cp.get("stage", 0))

    # =============================================================== setup
    def start_stage(self, index):
        self.mode = "stage"
        self.stage_index = index
        info = STAGES[index]
        self.level = Level(info["rows"], info["theme"])
        self.level.render()
        self.bg = assets.background(info["bg"], (VIEW_W, VIEW_H))
        sx, sy = self.level.start
        self.checkpoint_pos = (sx * TILE + TILE / 2, sy * TILE + TILE)
        self.player = None
        self._spawn_player(full=True)
        self._build_entities()
        self.state = "play"
        self.timer = 0
        self.banner = (f"STAGE {index + 1}", info["name"], 150)
        self.cam = [max(0, self.player.cx - VIEW_W * 0.35), self._cam_y_target()]
        self.audio.music(STAGE_MUSIC)
        self.app.story.checkpoint("platformer", {"stage": index})

    def _build_entities(self, keep_checkpoints_before=None):
        self.entities = []
        for ch, tx, ty in self.level.spawns:
            e = spawn(self.level, ch, tx, ty)
            if e is None:
                continue
            if keep_checkpoints_before is not None and hasattr(e, "active") and e.x <= keep_checkpoints_before + 1:
                e.active = True
            self.entities.append(e)

    def _spawn_player(self, full):
        x, base = self.checkpoint_pos
        hearts = MAX_HEARTS if full or self.player is None else self.player.hearts
        self.player = Player(x - 12, base - 52)
        self.player.hearts = hearts

    def start_arena(self, boss_index, kev_phase2=False):
        self.mode = "arena"
        self.boss_index = boss_index
        self.banner = None
        self.level = Level(ARENA, "hall")
        self.level.render()
        self.entities = []
        self.projectiles = []
        self.warnings = []
        self.pickups = []
        self.pickup_timer = 0
        self.arena_bg = "terrain/cathedral.png" if boss_index == 3 else "terrain/throne_hall.png"
        if boss_index == 3 and kev_phase2:
            self.arena_bg = "terrain/burning_cathedral.png"
        self.bg = assets.background(self.arena_bg, (VIEW_W, VIEW_H))
        self.checkpoint_pos = (480, FLOOR_Y)
        if not hasattr(self, "player"):
            self.player = None
        self._spawn_player(full=True)
        cls = BOSS_ORDER[boss_index]
        self.boss = cls(self, start_phase2=True) if cls is DreadKnight and kev_phase2 else cls(self)
        self.kev_phase2 = kev_phase2
        self.state = "intro"
        self.timer = 170
        self.title_img = assets.img(self.boss.title_image, size=(560, 560))
        self.cam = [0.0, 20.0]
        self.player.frozen = True
        self.audio.music(self.boss.music, fade_ms=300)
        self.app.story.checkpoint("platformer", {"boss": boss_index, "kev2": kev_phase2})

    # =============================================================== hooks used by bosses/entities
    def shake(self, amount):
        self.shake_amt = max(self.shake_amt, amount)

    def flash(self, frames):
        self.flash_t = max(self.flash_t, frames)

    def float_text(self, text, pos, color=WHITE, big=False):
        ft = FloatText(text, pos, color)
        ft.big = big
        if big:
            ft.life = 110
        self.texts.append(ft)

    def set_checkpoint(self, x, base):
        self.checkpoint_pos = (x, base)
        self.audio.blip("checkpoint")
        self.float_text("CHECKPOINT", (x, base - 100), (120, 255, 140))
        if self.player.hearts < MAX_HEARTS:
            self.player.hearts = MAX_HEARTS
            self.float_text("HEARTS RESTORED", (x, base - 80), (255, 140, 140))

    def set_arena_bg(self, rel):
        self.arena_bg = rel
        self.bg = assets.background(rel, (VIEW_W, VIEW_H))

    def checkpoint_phase2(self):
        self.kev_phase2 = True
        self.app.story.checkpoint("platformer", {"boss": 3, "kev2": True})

    def stage_clear(self):
        if self.state != "play":
            return
        self.state = "clear"
        self.timer = 140
        self.player.frozen = True
        self.player.vx = 0
        self.audio.blip("win")
        self.banner = ("STAGE CLEAR", STAGES[self.stage_index]["name"], 140)

    # =============================================================== input
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in JUMP_KEYS:
                self.jump_pressed = True
            elif event.key in ATTACK_KEYS:
                self.attack_pressed = True
            elif event.key == pygame.K_F1:
                self.dev_skip()

    def skip(self):
        self.app.story.checkpoint("platformer", clear=True)
        self.app.story.complete()

    def dev_skip(self):
        if self.mode == "stage":
            self.stage_clear()
        elif self.state == "fight" and not self.boss.dying:
            if isinstance(self.boss, DreadKnight) and not self.boss.second:
                self.boss.hp = 0
                self.boss.on_zero_hp()
            else:
                self.boss.hp = 0
                self.boss.dying = True
                self.boss.set("dying", 60)
                if hasattr(self.boss, "l_hp"):
                    self.boss.l_hp = self.boss.c_hp = 0
                    self.boss.l_state = self.boss.c_state = "down"
                    self.boss.l_timer = self.boss.c_timer = 60

    # =============================================================== update
    def update(self, dt):
        super().update(dt)
        keys = pygame.key.get_pressed()
        jump_held = any(keys[k] for k in JUMP_KEYS)
        jp, ap = self.jump_pressed, self.attack_pressed
        self.jump_pressed = self.attack_pressed = False
        self.shake_amt = max(0.0, self.shake_amt * 0.88 - 0.1)
        self.flash_t = max(0, self.flash_t - 1)
        if self.banner:
            t, s, n = self.banner
            self.banner = (t, s, n - 1) if n > 1 else None

        p = self.player
        p.control(keys, jp, jump_held, ap, self.audio)
        if self.mode == "stage":
            self._update_stage(p)
        else:
            self._update_arena(p)
        p.update_anim()
        self.particles.update()
        for t in self.texts:
            t.update()
        self.texts = [t for t in self.texts if t.life > 0]

    # ------------------------------------------------------------- stage
    def _update_stage(self, p):
        platforms = self.platforms = [e for e in self.entities if e.solid_platform]
        for e in platforms:
            e.update(self)
        p.move(self.level, platforms, drop=p.dropping > 0)
        p.x = max(0.0, min(self.level.w - p.w, p.x))
        for e in self.entities:
            if not e.solid_platform:
                e.update(self)

        if not p.dead and self.state == "play":
            self._combat_stage(p)
            if p.y > self.level.h + 60:
                self._fell(p)

        self.entities = [e for e in self.entities if e.alive]

        if p.dead and self.state == "play":
            self.state = "dead"
            self.timer = 110
            self.audio.blip("die")
        if self.state == "dead":
            self.timer -= 1
            if self.timer <= 0:
                self._respawn()
        elif self.state == "clear":
            self.timer -= 1
            if self.timer <= 0:
                if self.stage_index + 1 < len(STAGES):
                    self.start_stage(self.stage_index + 1)
                else:
                    self.start_arena(0)
                return
        self._update_camera(p)

    def _combat_stage(self, p):
        sword = p.sword_rect()
        body = p.rect.inflate(-6, -4)
        for e in self.entities:
            if not e.alive:
                continue
            er = e.rect
            if sword and e.hittable and id(e) not in p.hit_ids and sword.colliderect(er):
                p.hit_ids.add(id(e))
                e.take_hit(self, p.facing)
                self.shake(2)
                continue
            if e.harmful and body.colliderect(er):
                if isinstance(e, Moth) and p.vy > 1.5 and p.bottom - er.top < 20:
                    e.die(self)
                    p.bounce()
                    self.audio.blip("hit")
                    continue
                if p.hurt(er.centerx, self.audio):
                    self.shake(5)
        for r in self.level.spike_rects:
            if body.colliderect(r):
                if p.hurt(p.cx - p.facing, self.audio):
                    p.vy = -9
                    self.shake(5)
                break

    def _fell(self, p):
        self.audio.blip("hurt")
        p.hearts -= 1
        if p.hearts <= 0:
            p.hearts = 0
            p.dead = True
            return
        hearts = p.hearts
        self._spawn_player(full=False)
        self.player.hearts = hearts
        self.player.invuln = 90
        self.float_text("-1", (self.player.cx, self.player.y - 10), (255, 90, 90))

    def _respawn(self):
        self._spawn_player(full=True)
        self._build_entities(keep_checkpoints_before=self.checkpoint_pos[0])
        self.state = "play"
        self.player.invuln = 60

    def _cam_y_target(self):
        return max(0.0, min(self.level.h - VIEW_H, self.player.y + 26 - VIEW_H * 0.55))

    def _update_camera(self, p):
        look = p.facing * 70
        tx = p.cx - VIEW_W * 0.42 + look
        tx = max(0.0, min(self.level.w - VIEW_W, tx))
        self.cam[0] += (tx - self.cam[0]) * 0.1
        self.cam[1] += (self._cam_y_target() - self.cam[1]) * 0.1

    # ------------------------------------------------------------- arena
    def _update_arena(self, p):
        p.move(self.level, (), drop=p.dropping > 0)
        boss = self.boss

        if self.state == "intro":
            self.timer -= 1
            boss.update(self)
            if self.timer == 70:
                p.frozen = False
            if self.timer <= 0 and boss.state not in ("enter",):
                self.state = "fight"
            return

        if self.state in ("fight", "dead"):
            boss.update(self)
            for w in self.warnings:
                w.update(self)
            for pr in self.projectiles:
                pr.update(self)
            for h in self.pickups:
                h.update(self)
            self.warnings = [w for w in self.warnings if w.alive]
            self.projectiles = [pr for pr in self.projectiles if pr.alive]
            self.pickups = [h for h in self.pickups if h.alive]

        if self.state == "fight":
            if not p.dead:
                self._combat_arena(p, boss)
                self._heart_spawner(p)
            if p.dead:
                self.state = "dead"
                self.timer = 120
                self.audio.blip("die")
            elif boss.dead:
                self._boss_down()
        elif self.state == "dead":
            self.timer -= 1
            if self.timer <= 0:
                self.player = None
                self.start_arena(self.boss_index, getattr(self, "kev_phase2", False))
        elif self.state == "between":
            self.timer -= 1
            if self.timer <= 0:
                hearts = p.hearts
                self.start_arena(self.boss_index + 1)
                self.player.hearts = min(MAX_HEARTS, hearts + 2)
        elif self.state == "victory":
            self._update_reward(p)

    def _combat_arena(self, p, boss):
        sword = p.sword_rect()
        body = p.rect.inflate(-8, -6)
        if sword:
            for part, rect in boss.parts():
                key = ("boss", part)
                if key not in p.hit_ids and sword.colliderect(rect):
                    p.hit_ids.add(key)
                    boss.take_hit(part, p.facing)
            for pr in self.projectiles:
                if (pr.deflect or pr.breakable) and pr.alive and sword.colliderect(pr.hit_rect):
                    pr.alive = False
                    self.particles.burst((pr.x, pr.y), (255, 240, 200), 10, 4)
                    self.audio.play(self.audio.synth("clink", freq=1800, dur=0.08, wave="square", vol=0.2, slide=-900))
        for r in boss.harm_rects():
            if body.colliderect(r):
                if p.hurt(r.centerx, self.audio):
                    self.shake(6)
        for pr in self.projectiles:
            if pr.alive and pr.harmful and body.colliderect(pr.hit_rect):
                if p.hurt(pr.x, self.audio):
                    self.shake(5)
                    if pr.kind not in ("shock", "fire"):
                        pr.alive = False

    def _heart_spawner(self, p):
        self.pickup_timer += 1
        delay = 720 if self.kev_phase2 else 1200
        if p.hearts < MAX_HEARTS and not self.pickups and self.pickup_timer > delay:
            self.pickup_timer = 0
            from .entities import Heart
            lo, hi = random.choice(PLATFORMS)
            h = Heart(0, 0)
            h.x, h.y = (lo + hi) / 2, PLAT_Y - 30
            self.pickups.append(h)

    def _boss_down(self):
        self.projectiles.clear()
        self.warnings.clear()
        self.audio.stop_music(800)
        self.audio.blip("win")
        if self.boss_index + 1 < len(BOSS_ORDER):
            self.state = "between"
            self.timer = 170
            self.banner = (f"{self.boss.name}", "DEFEATED", 160)
            self.app.story.checkpoint("platformer", {"boss": self.boss_index + 1})
        else:
            self.state = "victory"
            self.timer = 0
            self.banner = ("DREAD KNIGHT KEV", "DEFEATED", 200)
            self.reward = {"x": 480.0, "y": -120.0, "vy": 0.0, "landed": False, "t": 0}

    def _update_reward(self, p):
        r = self.reward
        r["t"] += 1
        if not r["landed"]:
            r["vy"] = min(12, r["vy"] + 0.4)
            r["y"] += r["vy"]
            if r["y"] >= FLOOR_Y:
                r["y"] = FLOOR_Y
                r["landed"] = True
                self.shake(6)
                self.particles.burst((480, FLOOR_Y - 10), (255, 230, 150), 30, 5)
        elif r.get("claimed"):
            self.timer -= 1
            if self.timer <= 0:
                self.app.story.checkpoint("platformer", clear=True)
                self.app.story.complete()
        else:
            rect = pygame.Rect(0, 0, 90, 70)
            rect.midbottom = (480, FLOOR_Y)
            if p.rect.colliderect(rect):
                r["claimed"] = True
                p.frozen = True
                self.timer = 150
                self.audio.blip("heal")
                self.banner = ("REWARD CLAIMED", "YOU HAVE BESTED US ALL", 150)

    # =============================================================== draw
    def draw(self, surf):
        sx = random.uniform(-1, 1) * self.shake_amt
        sy = random.uniform(-1, 1) * self.shake_amt
        cam = (int(self.cam[0] - sx), int(self.cam[1] - sy))

        # parallax background
        bw = self.bg.get_width()
        off = -int(self.cam[0] * 0.15) % bw if self.mode == "stage" else 0
        surf.blit(self.bg, (off - bw if off else 0, 0))
        if off:
            surf.blit(self.bg, (off, 0))
        shade = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 10, 70))
        surf.blit(shade, (0, 0))

        surf.blit(self.level.surface, (0, 0), area=pygame.Rect(cam[0], cam[1], VIEW_W, VIEW_H))

        if self.mode == "stage":
            for e in self.entities:
                if e.solid_platform:
                    e.draw(surf, cam)
            for e in self.entities:
                if not e.solid_platform:
                    e.draw(surf, cam)
            self.player.draw(surf, cam)
        else:
            for w in self.warnings:
                w.draw(surf, cam)
            for h in self.pickups:
                h.draw(surf, cam)
            if self.state == "victory":
                self._draw_reward(surf, cam)
            if not self.boss.dead:
                self.boss.draw(surf, cam)
            self.player.draw(surf, cam)
            for pr in self.projectiles:
                pr.draw(surf, cam)

        self.particles.draw(surf, cam)
        for t in self.texts:
            size = 24 if getattr(t, "big", False) else 10
            a = max(0, min(255, t.life * 8))
            ui.draw_text(surf, t.text, size, (int(t.x - cam[0]), int(t.y - cam[1])), t.color, "center", shadow=BLACK, alpha=a)

        self._draw_hud(surf)
        if self.mode == "arena" and self.state == "intro":
            self._draw_title_card(surf)
        if self.state == "dead":
            veil = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
            veil.fill((60, 0, 0, min(160, (120 - self.timer) * 3)))
            surf.blit(veil, (0, 0))
            ui.draw_text(surf, "YOU DIED", 32, (VIEW_W // 2, VIEW_H // 2 - 30), (220, 40, 40), "midtop", shadow=BLACK)
            ui.draw_text(surf, "THE CHALLENGE AWAITS AGAIN", 10, (VIEW_W // 2, VIEW_H // 2 + 20), WHITE, "midtop", shadow=BLACK)
        if self.flash_t:
            veil = pygame.Surface((VIEW_W, VIEW_H))
            veil.fill(WHITE)
            veil.set_alpha(min(255, self.flash_t * 14))
            surf.blit(veil, (0, 0))

    def _draw_reward(self, surf, cam):
        r = self.reward
        img = assets.img("bosses/DREAD_KNIGHT/reward.png", size=(110, 110))
        bob = math.sin(r["t"] * 0.08) * 4 if r["landed"] else 0
        glow = pygame.Surface((220, 220), pygame.SRCALPHA)
        a = int(70 + 50 * math.sin(r["t"] * 0.1))
        pygame.draw.circle(glow, (255, 230, 140, a), (110, 110), 100)
        pos = (int(r["x"] - cam[0]), int(r["y"] - 55 + bob - cam[1]))
        surf.blit(glow, glow.get_rect(center=pos))
        surf.blit(img, img.get_rect(center=pos))
        if r["landed"] and not r.get("claimed") and ui.blink(self.t, 1.5):
            ui.draw_text(surf, "CLAIM YOUR REWARD", 12, (pos[0], pos[1] - 90), (255, 230, 150), "midtop", shadow=BLACK)

    def _draw_title_card(self, surf):
        k = self.timer
        a = 255
        if k > 140:
            a = int(255 * (170 - k) / 30)
        elif k < 40:
            a = int(255 * k / 40)
        img = self.title_img.copy()
        img.set_alpha(max(0, a))
        surf.blit(img, img.get_rect(center=(VIEW_W // 2, VIEW_H // 2 - 70)))

    def _draw_hud(self, surf):
        p = self.player
        for i in range(MAX_HEARTS):
            img = self.heart_img if i < p.hearts else self.heart_empty
            surf.blit(img, (14 + i * 30, 12))
        if self.mode == "stage":
            ui.draw_text(surf, f"STAGE {self.stage_index + 1}/{len(STAGES)}", 10, (VIEW_W - 14, 12), WHITE, "topright", shadow=BLACK)
            ui.draw_text(surf, STAGES[self.stage_index]["name"], 8, (VIEW_W - 14, 28), (200, 200, 210), "topright", shadow=BLACK)
        else:
            ui.draw_text(surf, f"GUARDIAN {self.boss_index + 1}/{len(BOSS_ORDER)}", 10, (VIEW_W - 14, 12), WHITE, "topright", shadow=BLACK)
            if self.state in ("fight", "dead") or (self.state == "intro" and self.timer < 60):
                self._draw_boss_bars(surf)
        if self.banner:
            text, sub, n = self.banner
            a = min(255, n * 6)
            ui.draw_text(surf, text, 28, (VIEW_W // 2, 120), (255, 220, 120), "midtop", shadow=BLACK, alpha=a)
            ui.draw_text(surf, sub, 12, (VIEW_W // 2, 162), WHITE, "midtop", shadow=BLACK, alpha=a)

    def _draw_boss_bars(self, surf):
        bars = self.boss.bars()
        total_w = 520
        gap = 16
        each = (total_w - gap * (len(bars) - 1)) // len(bars)
        x = (VIEW_W - total_w) // 2
        y = VIEW_H - 36
        if len(bars) > 1:
            ui.draw_text(surf, self.boss.name, 10, (VIEW_W // 2, y - 30), (255, 210, 120), "midtop", shadow=BLACK)
        for label, hp, mx in bars:
            if len(bars) == 1:
                ui.draw_text(surf, label, 10, (VIEW_W // 2, y - 18), (255, 210, 120), "midtop", shadow=BLACK)
            else:
                ui.draw_text(surf, label, 8, (x, y - 14), (255, 210, 120), shadow=BLACK)
            pygame.draw.rect(surf, (30, 10, 10), (x, y, each, 14))
            pygame.draw.rect(surf, (200, 30, 40), (x + 2, y + 2, int((each - 4) * hp / mx), 10))
            pygame.draw.rect(surf, (240, 220, 200), (x, y, each, 14), 2)
            x += each + gap
