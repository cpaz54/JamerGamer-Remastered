"""Chapter IV: Jamer Quest - a little Zelda-like.

Arrows move, A swings the sword, Q fires the bow, E talks / opens / reads.
"""
import copy
import random

import pygame

from .. import ui
from ..config import asset, BLACK, WHITE
from ..scene import Scene
from .actors import Arrow, Ghost, MAX_ARROWS, Player, Spider
from .assets import Art, T, scaled
from .rooms import ENTRY_ROOM, NPC_THANKS_1, NPC_THANKS_2, ROOMS, START_POS, START_ROOM, T_BOW
from .world import ROOM_W, ROOM_H, Obj, Room

HUD_H = 32
W, H = ROOM_W, ROOM_H + HUD_H

SWORD_KEYS = (pygame.K_a, pygame.K_j)
BOW_KEYS = (pygame.K_q, pygame.K_k)
TALK_KEYS = (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE)

MUSIC = {
    "village": "adventure/sounds/Music/village_theme_quieter.mp3",
    "overworld": "adventure/sounds/Music/overworld_music_quieter.mp3",
    "shop": "adventure/sounds/Music/shop_theme.mp3",
    "dungeon": "adventure/sounds/Music/8-Bit Fantasy & Adventure Music (mashup of stuff).mp3",
    "boss": "adventure/sounds/Music/boss_battle_theme.mp3",
    "title": "adventure/sounds/Music/title_theme.mp3",
}

DEFAULT_FLAGS = {
    "sword": False, "bow": False, "keys": 0, "boss_key": False, "gems": 0,
    "hp": 6, "max_hp": 6, "opened": [], "cut": [], "unlocked": [], "talked": [],
    "bought": [], "boss_dead": False, "red_on": True,
    "room": list(START_ROOM), "pos": [START_POS[0] * T + T // 2, START_POS[1] * T + T - 2],
}


class TextBox:
    def __init__(self, pages, on_close=None, holding=None):
        self.pages = [p for p in pages if p]
        self.page = 0
        self.writer = ui.Typewriter(self.pages[0], cps=45)
        self.on_close = on_close
        self.holding = holding
        self.done = False

    def advance(self):
        if not self.writer.done:
            self.writer.finish()
            return
        self.page += 1
        if self.page >= len(self.pages):
            self.done = True
        else:
            self.writer = ui.Typewriter(self.pages[self.page], cps=45)


class AdventureScene(Scene):
    size = (W, H)
    title = "JAMER QUEST"

    def __init__(self, app):
        super().__init__(app)
        self.art = Art()
        saved = app.story.checkpoint("adventure")
        self.flags = copy.deepcopy(DEFAULT_FLAGS)
        if saved:
            self.flags.update(copy.deepcopy(saved))
        self.state = "title" if not saved else "play"
        self.title_img = None
        self.text = None
        self.effects = []          # [img, x, y, frames]
        self.arrows = []
        self.enemies = []
        self.ghost = None
        self.drops = []
        self.shake = 0
        self.lock_msg_cd = 0
        self.slide = None          # room transition info
        self.fade = None           # (frames_left, total, callback)
        self.death_t = 0
        self.banner = None
        self.player = Player(self.art, *self.flags["pos"])
        room, pos = tuple(self.flags["room"]), self.flags["pos"]
        if room not in ROOMS:
            # checkpoint from an older dungeon layout: restart at the dungeon entrance
            room, pos = ENTRY_ROOM, (8 * T + T // 2, 9 * T + T - 2)
        self.load_room(room, pos)

    # ================================================================= helpers
    def sfx(self, name, vol=0.6):
        self.audio.sfx(f"adventure/sounds/Sound Effects/{name}.wav", vol)

    def music(self, key):
        self.audio.music(MUSIC[key], fade_ms=400)

    def puff(self, x, y, small=False):
        self.effects.append([self.art.smoke if not small else scaled(self.art.smoke, (16, 16)), x, y, 18])

    def say(self, pages, on_close=None, holding=None):
        self.text = TextBox(pages, on_close, holding)

    def save_checkpoint(self):
        f = self.flags
        f["room"] = list(self.room.key)
        f["pos"] = list(self.entry_pos)
        self.app.story.checkpoint("adventure", copy.deepcopy(f))

    def enter(self):
        if self.state == "title":
            self.music("title")
        else:
            self._room_music()

    def exit(self):
        pass

    # ================================================================= rooms
    def load_room(self, key, pos=None):
        data = ROOMS[key]
        self.room = Room(key, data, self.art, self.flags)
        if pos is not None:
            self.player.hit.midbottom = (int(pos[0]), int(pos[1]))
        self.entry_pos = self.player.hit.midbottom
        self.arrows = []
        self.drops = []
        self.effects = []
        self.enemies = []
        self.ghost = None
        for c, tx, ty in self.room.spawns:
            if c in "Ee":
                self.enemies.append(Spider(self.art, tx, ty, hunter=(c == "e")))
            elif c == "X":
                if not self.flags["boss_dead"]:
                    self.ghost = Ghost(self.art, tx, ty)
                elif not self._has_exit():
                    self.room.objects.append(Obj("stairs", tx, ty, {"to": ("house", "fan"), "spawn": (8, 9)}))
        if key == ("house", "fan") and self.flags["boss_dead"]:
            self.room.objects.append(Obj("npc", 7, 5, {"id": "thanks1", "look": "green", "text": NPC_THANKS_1}))
            self.room.objects.append(Obj("npc", 9, 5, {"id": "thanks2", "look": "red", "text": NPC_THANKS_2}))
        self._update_gates(silent=True)
        for o in self.room.objects:
            if o.kind == "gate" and o.rect.colliderect(self.player.hit):
                o.alive = False          # never close a gate on top of the player
        if self.state != "title":
            self._room_music()
        self.save_checkpoint()

    def _room_music(self):
        if self.ghost is not None:
            self.music("boss")
        else:
            self.music(self.room.data["music"])

    def _update_gates(self, silent=False):
        hostile = bool(self.enemies) or (self.ghost is not None and not self.ghost.dead)
        for o in self.room.objects:
            if o.kind == "gate" and o.alive and not hostile:
                o.alive = False
                if not silent:
                    self.sfx("switch_flipped", 0.6)
                    self.puff(o.x, o.y)

    def _neighbor(self, dx, dy):
        area, x, y = self.room.key if len(self.room.key) == 3 else (None, 0, 0)
        if area is None:
            return None
        k = (area, x + dx, y + dy)
        return k if k in ROOMS else None

    def _check_edges(self):
        p = self.player.hit
        d = None
        if p.centerx < 0:
            d = (-1, 0)
        elif p.centerx > ROOM_W:
            d = (1, 0)
        elif p.bottom - 4 < 0:
            d = (0, -1)
        elif p.bottom > ROOM_H + 2:
            d = (0, 1)
        if not d:
            return
        nk = self._neighbor(*d)
        if nk is None:
            p.clamp_ip(pygame.Rect(0, 0, ROOM_W, ROOM_H))
            return
        old = self._snapshot()
        self.load_room(nk)
        if d[0] == -1:
            p.right = ROOM_W - 2
        elif d[0] == 1:
            p.left = 2
        elif d[1] == -1:
            p.bottom = ROOM_H - 2
        else:
            p.top = 6
        self.entry_pos = p.midbottom
        self.save_checkpoint()
        self.slide = {"old": old, "dir": d, "t": 0, "n": 22}

    def _snapshot(self):
        s = pygame.Surface((ROOM_W, ROOM_H))
        self._draw_world(s, 0, 0)
        return s

    def teleport(self, key, spawn):
        def go():
            tx, ty = spawn
            self.load_room(key, (tx * T + T // 2, ty * T + T - 2))
        self.fade = [24, 24, go]

    # ================================================================= input
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        k = event.key
        if self.state == "title":
            # the title art says PRESS START: any key does it
            self.state = "play"
            self.sfx("cool_sound", 0.5)
            self._room_music()
            return
        if self.text is not None:
            if k in TALK_KEYS or k in SWORD_KEYS:
                self.text.advance()
                self.sfx("text_beep", 0.3)
            return
        if self.state != "play" or self.slide or self.fade:
            return
        p = self.player
        if k in SWORD_KEYS and self.flags["sword"] and p.use == 0 and p.knock[2] == 0:
            p.start_use("sword")
            self.sfx("sword_swipe", 0.5)
        elif k in BOW_KEYS and self.flags["bow"] and p.use == 0 and p.knock[2] == 0:
            if len(self.arrows) < MAX_ARROWS:
                p.start_use("bow")
                self.arrows.append(Arrow(self.art, p))
                self.sfx("arrow", 0.5)
        elif k in TALK_KEYS:
            self.interact()

    def interact(self):
        p = self.player
        tx, ty = p.facing_tile()
        o = self.room.object_at(tx, ty)
        if o is None:
            # also check the tile overlapping the player's front edge
            cx, cy = p.hit.center
            for ox, oy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                o = self.room.object_at((cx // T) + ox, (cy // T) + oy, ("sign", "npc", "chest", "shop"))
                if o and o.rect.inflate(8, 8).colliderect(p.hit):
                    break
                o = None
        if o is None:
            return
        if o.kind == "sign":
            self.say(o.data["text"])
        elif o.kind == "npc":
            self._talk(o)
        elif o.kind == "chest" and not o.opened:
            self._open_chest(o)
        elif o.kind == "shop":
            self._buy(o)
        elif o.kind == "lock":
            self._try_lock(o)
        elif o.kind == "door" and getattr(o, "locked", False):
            self._try_lock(o)

    def _talk(self, o):
        d = o.data
        f = self.flags
        nid = d.get("id")
        if d.get("gives") == "bow" and not f["bow"]:
            def give():
                f["bow"] = True
                self.say(T_BOW, holding=self.art.bow)
                self.sfx("pickup", 0.6)
            self.say(d["text"], on_close=give)
        elif d.get("gives") == "bow":
            self.say(d.get("after_text", d["text"]))
        elif nid == "thanks1" and "thanks1" not in f["talked"]:
            def reward():
                f["gems"] += 20
                f["talked"].append("thanks1")
                self.sfx("coin_get", 0.6)
                self._check_complete()
            self.say(d["text"], on_close=reward)
        elif nid == "thanks2" and "thanks2" not in f["talked"]:
            def done():
                f["talked"].append("thanks2")
                self._check_complete()
            self.say(d["text"], on_close=done)
        else:
            self.say(d["text"])

    def _check_complete(self):
        if "thanks1" in self.flags["talked"] and "thanks2" in self.flags["talked"]:
            self.state = "complete"
            self.banner = 240
            self.audio.stop_music(1500)
            self.sfx("cool_sound", 0.7)

    def _open_chest(self, o):
        f = self.flags
        d = o.data
        o.opened = True
        f["opened"].append(d.get("id"))
        self.sfx("open_chest", 0.6)
        item = d.get("item")
        a = self.art
        icon = None
        if item == "sword":
            f["sword"] = True
            icon = a.sword_up
        elif item == "bow":
            f["bow"] = True
            icon = a.bow
        elif item == "gems":
            f["gems"] += d.get("amount", 1)
            icon = a.gem[20] if d.get("amount", 1) >= 50 else a.gem[5] if d.get("amount", 1) >= 10 else a.gem[1]
        elif item == "key":
            f["keys"] += 1
            icon = a.key
        elif item == "boss_key":
            f["boss_key"] = True
            icon = a.key
        elif item == "container":
            f["max_hp"] += 2
            f["hp"] = f["max_hp"]
            icon = a.heart_full
        self.say(d.get("text", ["You found something."]), holding=icon)
        self.save_checkpoint()

    def _buy(self, o):
        f = self.flags
        d = o.data
        if d.get("once") and d["id"] in f["bought"]:
            self.say(["SOLD OUT. Come back... never."])
            return
        if f["gems"] < d["price"]:
            self.say([f"{d['name']}: {d['price']} gems. You only have {f['gems']}. Go smash some pots. Or spiders."])
            return
        if d["id"] == "refill" and f["hp"] >= f["max_hp"]:
            self.say(["You're already in perfect health!"])
            return
        f["gems"] -= d["price"]
        self.sfx("coin_get", 0.6)
        if d["id"] == "refill":
            f["hp"] = f["max_hp"]
            self.say([f"You bought a {d['name']}. Health restored!"], holding=self.art.heart_drop)
        else:
            f["max_hp"] += 2
            f["hp"] = f["max_hp"]
            f["bought"].append(d["id"])
            self.say([f"You bought a {d['name']}! Your health went up by one heart."], holding=self.art.heart_full)
        self.save_checkpoint()

    def _try_lock(self, o):
        f = self.flags
        if self.lock_msg_cd > 0:
            return
        self.lock_msg_cd = 40
        lock_id = o.data.get("lock")
        need = o.data.get("needs", "key")
        has = f["boss_key"] if need == "boss_key" else f["keys"] > 0
        if not has:
            self.say(["It's locked." if need == "key" else "A huge lock. It needs a special key."])
            return
        if need == "boss_key":
            f["boss_key"] = False
        else:
            f["keys"] -= 1
        f["unlocked"].append(lock_id)
        self.sfx("switch_flipped", 0.7)
        if o.kind == "lock":
            o.timer = 1
        else:
            o.locked = False
            o.solid = False
            self.puff(o.x, o.y)
        self.save_checkpoint()

    # ================================================================= update
    def update(self, dt):
        super().update(dt)
        tick = int(self.t * 60)
        self.lock_msg_cd = max(0, self.lock_msg_cd - 1)
        self.shake = max(0, self.shake - 1)
        for e in self.effects:
            e[3] -= 1
        self.effects = [e for e in self.effects if e[3] > 0]

        if self.state == "title":
            return
        if self.slide:
            self.slide["t"] += 1
            if self.slide["t"] >= self.slide["n"]:
                self.slide = None
            return
        if self.fade:
            self.fade[0] -= 1
            if self.fade[0] == self.fade[1] // 2:
                self.fade[2]()
            if self.fade[0] <= 0:
                self.fade = None
            return
        if self.text is not None:
            n = self.text.writer.update(dt)
            if n and int(self.text.writer.shown) % 3 == 0:
                self.sfx("text_beep", 0.15)
            if self.text.done:
                cb = self.text.on_close
                self.text = None
                if cb:
                    cb()
            return
        if self.state == "complete":
            self.banner -= 1
            if self.banner <= 0:
                self.app.story.checkpoint("adventure", clear=True)
                self.app.story.complete()
            return
        if self.state == "dead":
            self.death_t -= 1
            if self.death_t <= 0:
                self.flags["hp"] = self.flags["max_hp"]
                self.state = "play"
                self.player = Player(self.art, *self.entry_pos)
                self.load_room(self.room.key, self.entry_pos)
            return

        keys = pygame.key.get_pressed()
        p = self.player
        bumped = p.update(self.room, keys)
        self._push_blocks(bumped)
        self._doors()
        self._animate_objects()
        self._sword_hits()
        self._arrows()
        self._enemies(tick)
        self._pickups()
        self._check_edges()
        if self.flags["hp"] <= 0 and self.state == "play":
            self.state = "dead"
            self.death_t = 110
            self.sfx("explosion", 0.5)

    def _push_blocks(self, bumped):
        p = self.player
        if not bumped:
            p.push_dir = None
            p.push_t = 0
            return
        tx, ty = p.facing_tile()
        o = self.room.object_at(tx, ty, ("block", "lock", "door"))
        if o is None:
            return
        if o.kind in ("lock", "door"):
            if (o.kind == "lock" and o.solid) or getattr(o, "locked", False):
                if self.flags["keys"] > 0 or (o.data.get("needs") == "boss_key" and self.flags["boss_key"]):
                    self._try_lock(o)
            return
        if p.push_dir != p.dir:
            p.push_dir = p.dir
            p.push_t = 0
        p.push_t += 1
        if p.push_t >= 18 and o.slide is None:
            dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[p.dir]
            if self.room.free_tile(o.tx + dx, o.ty + dy):
                o.slide = (dx, dy, 16)
                o.tx += dx
                o.ty += dy
                self.sfx("slam_wood", 0.5)
            p.push_t = 0

    def _doors(self):
        p = self.player
        feet = pygame.Rect(p.hit.centerx - 4, p.hit.top, 8, p.hit.h)
        for o in self.room.objects:
            if not o.alive or o.kind not in ("door", "exit", "stairs") or getattr(o, "locked", False):
                continue
            if o.rect.inflate(-12, -8).colliderect(feet):
                d = o.data
                self.sfx("cool_sound" if o.kind == "stairs" else "pickup", 0.3)
                self.teleport(d["to"], d["spawn"])
                return

    def _animate_objects(self):
        f = self.flags
        p = self.player
        for o in self.room.objects:
            if o.kind == "barrier":
                up = f["red_on"] if o.data["color"] == "red" else not f["red_on"]
                target = 0 if up else 3
                if up and o.anim == 3 and o.rect.colliderect(p.hit):
                    continue      # don't raise a barrier on top of the player
                if o.anim != target:
                    o.timer += 1
                    if o.timer % 4 == 0:
                        o.anim += 1 if target > o.anim else -1
                o.solid = o.anim < 2
            elif o.kind == "lock" and o.timer and o.anim < 3:
                o.timer += 1
                if o.timer % 8 == 0:
                    o.anim += 1
                if o.anim >= 3:
                    o.solid = False
            elif o.kind == "block" and o.slide:
                dx, dy, n = o.slide
                o.x += dx * 2
                o.y += dy * 2
                o.slide = (dx, dy, n - 1) if n > 1 else None

    def _sword_hits(self):
        p = self.player
        sw = p.sword()
        if not sw:
            return
        hb = sw[2]
        for o in self.room.objects:
            if o.kind == "shrub" and o.alive and hb.colliderect(o.rect):
                o.alive = False
                self.flags["cut"].append(f"{self.room.key}:{o.tx},{o.ty}")
                self.sfx("bush_cut", 0.5)
                self.puff(o.x, o.y)
                self._maybe_drop(o.x, o.y, 0.25)
        for e in self.enemies:
            if id(e) not in p.sword_hit and hb.colliderect(e.rect):
                p.sword_hit.add(id(e))
                self._hit_enemy(e)
        g = self.ghost
        if g and not g.dead:
            for orb in list(g.orbs):
                if id(orb) not in p.sword_hit and hb.colliderect(orb.rect):
                    p.sword_hit.add(id(orb))
                    g.hit_orb(orb, self)
            if g.solid and "ghost" not in p.sword_hit and hb.colliderect(g.rect):
                p.sword_hit.add("ghost")
                if g.hit_body(self) and g.dead:
                    self._ghost_dead()

    def _hit_enemy(self, e):
        e.hp -= 1
        e.flash = 12
        if e.hp <= 0:
            e.alive = False
            self.sfx("spider_death", 0.5)
            self.puff(e.rect.x, e.rect.y)
            self._maybe_drop(e.rect.x, e.rect.y, 0.4)
        else:
            self.sfx("eye_injure", 0.4)

    def _maybe_drop(self, x, y, chance):
        if random.random() > chance:
            return
        tx, ty = int(x + T / 2) // T, int(y + T / 2) // T
        f = self.flags
        if f["hp"] < f["max_hp"] and random.random() < 0.5:
            o = Obj("pickup", tx, ty, {"item": "heart"})
        else:
            o = Obj("pickup", tx, ty, {"item": "gem", "amount": random.choice((1, 1, 1, 5))})
        o.life = 600
        self.room.objects.append(o)

    def _arrows(self):
        g = self.ghost
        for a in self.arrows:
            res = a.update(self.room)
            if res is None and a.alive:
                tip = a.tip
                for e in self.enemies:
                    if e.alive and tip.colliderect(e.rect):
                        self._hit_enemy(e)
                        a.alive = False
                        break
                if a.alive and g and not g.dead:
                    for orb in list(g.orbs):
                        if tip.colliderect(orb.rect):
                            g.hit_orb(orb, self)
                            a.alive = False
                            break
                    if a.alive and g.solid and tip.colliderect(g.rect):
                        a.alive = False
                        if g.hit_body(self) and g.dead:
                            self._ghost_dead()
            elif isinstance(res, tuple) and res[0] == "target":
                self.flags["red_on"] = not self.flags["red_on"]
                self.sfx("switch_flipped", 0.7)
                self.effects.append([self.art.arrow_break[0], a.x, a.y, 10])
            elif res == "wall":
                self.sfx("arrow_break", 0.4)
                self.effects.append([self.art.arrow_break[0], a.x, a.y, 10])
        self.arrows = [a for a in self.arrows if a.alive]

    def _enemies(self, tick):
        p = self.player
        f = self.flags
        for e in self.enemies:
            if e.alive:
                e.update(self.room, p)
                if e.flash == 0 and e.rect.inflate(-6, -6).colliderect(p.body):
                    if p.hurt(1, e.rect.center, self.room):
                        f["hp"] -= 1
                        self.sfx("eye_injure", 0.4)
        before = len(self.enemies)
        self.enemies = [e for e in self.enemies if e.alive]
        g = self.ghost
        if g and not g.dead:
            g.update(self)
            for las in g.lasers:
                if las.rect.colliderect(p.body):
                    if p.hurt(1, (p.hit.centerx, p.hit.centery - 20), self.room):
                        f["hp"] -= 1
                        self.sfx("eye_injure", 0.4)
                    las.alive = False
        if before and not self.enemies:
            self._update_gates()

    def _ghost_dead(self):
        g = self.ghost
        self.flags["boss_dead"] = True
        self.audio.stop_music(800)
        self._update_gates()
        self.save_checkpoint()
        if self._has_exit():
            self.say(["The ghost lets out one last shriek and fades away. The dungeon falls silent.",
                      "The water parts. The brothers will want to hear about this."])
            return
        tx, ty = int(g.x0 + T) // T, int(g.y0 + T // 2) // T
        self.room.objects.append(Obj("stairs", tx, ty + 1, {"to": ("house", "fan"), "spawn": (8, 9)}))
        self.say(["The ghost lets out one last shriek and fades away. The dungeon falls silent.",
                  "A staircase appears. The brothers will want to hear about this."])

    def _has_exit(self):
        return any(o.kind == "exit" for o in self.room.objects)

    def _pickups(self):
        p = self.player
        f = self.flags
        for o in self.room.objects:
            if o.kind != "pickup" or not o.alive:
                continue
            if hasattr(o, "life"):
                o.life -= 1
                if o.life <= 0:
                    o.alive = False
                    continue
            if o.rect.inflate(-10, -10).colliderect(p.body):
                o.alive = False
                if o.data["item"] == "heart":
                    f["hp"] = min(f["max_hp"], f["hp"] + 2)
                    self.sfx("pickup", 0.5)
                else:
                    f["gems"] += o.data.get("amount", 1)
                    self.sfx("coin_get", 0.4)

    def skip(self):
        self.app.story.checkpoint("adventure", clear=True)
        self.app.story.complete()

    # ================================================================= draw
    def _draw_world(self, surf, ox, oy):
        tick = int(self.t * 60)
        self.room.draw(surf, tick, ox, oy)
        for e in self.enemies:
            e.draw(surf, ox, oy)
        holding = self.text.holding if self.text else None
        self.player.draw(surf, tick, ox, oy, holding=holding)
        for a in self.arrows:
            a.draw(surf, ox, oy)
        if self.ghost and not self.ghost.dead:
            self.ghost.draw(surf, ox, oy)
        for img, x, y, n in self.effects:
            surf.blit(img, (int(x) + ox, int(y) + oy))

    def draw(self, surf):
        surf.fill(BLACK)
        if self.state == "title":
            self._draw_title(surf)
            return
        world = surf.subsurface((0, HUD_H, ROOM_W, ROOM_H))
        sx = random.randint(-3, 3) if self.shake else 0
        sy = random.randint(-3, 3) if self.shake else 0
        if self.slide:
            d = self.slide["dir"]
            k = self.slide["t"] / self.slide["n"]
            k = k * k * (3 - 2 * k)
            dx, dy = int(-d[0] * ROOM_W * k), int(-d[1] * ROOM_H * k)
            world.blit(self.slide["old"], (dx, dy))
            self._draw_world(world, dx + d[0] * ROOM_W, dy + d[1] * ROOM_H)
        else:
            self._draw_world(world, sx, sy)
        if self.fade:
            n, total, _ = self.fade
            a = int(255 * (1 - abs(n - total / 2) / (total / 2)))
            veil = pygame.Surface((ROOM_W, ROOM_H))
            veil.set_alpha(a)
            world.blit(veil, (0, 0))
        self._draw_hud(surf)
        if self.text:
            self._draw_textbox(surf)
        if self.state == "dead":
            veil = pygame.Surface((ROOM_W, ROOM_H), pygame.SRCALPHA)
            veil.fill((80, 0, 0, min(180, (110 - self.death_t) * 4)))
            world.blit(veil, (0, 0))
            ui.draw_text(surf, "YOU DIED", 16, (W // 2, H // 2 - 10), WHITE, "midtop", shadow=BLACK)
        if self.state == "complete":
            ui.panel(surf, (W // 2 - 170, H // 2 - 40, 340, 80), fill=(20, 10, 0), border=(255, 210, 90))
            ui.draw_text(surf, "QUEST COMPLETE!", 16, (W // 2, H // 2 - 22), (255, 220, 120), "midtop", shadow=BLACK)
            ui.draw_text(surf, "THE ANCESTORS REST IN PEACE", 8, (W // 2, H // 2 + 8), WHITE, "midtop")

    def _draw_title(self, surf):
        if self.title_img is None:
            # fit the (nearly square) title art to the screen height, centred on black
            self.title_img = pygame.Surface((W, H))
            try:
                img = pygame.image.load(asset("adventure", "source", "menu", "jamerquest_title.png")).convert()
                iw, ih = img.get_size()
                scale = min(W / iw, H / ih)
                img = pygame.transform.smoothscale(img, (round(iw * scale), round(ih * scale)))
                self.title_img.blit(img, img.get_rect(center=(W // 2, H // 2)))
            except (pygame.error, FileNotFoundError):
                self.title_img.fill(WHITE)
        surf.blit(self.title_img, (0, 0))

    def _draw_hud(self, surf):
        a = self.art
        f = self.flags
        pygame.draw.rect(surf, (12, 12, 16), (0, 0, W, HUD_H))
        pygame.draw.line(surf, (60, 60, 70), (0, HUD_H - 1), (W, HUD_H - 1))
        # hearts
        for i in range(f["max_hp"] // 2):
            v = f["hp"] - i * 2
            img = a.heart_full if v >= 2 else a.heart_half if v == 1 else a.heart_empty
            surf.blit(scaled(img, (16, 16)), (8 + i * 18, 8))
        # items
        x = 8 + (f["max_hp"] // 2) * 18 + 12
        surf.blit(scaled(a.gem[1], (16, 16)), (x, 8))
        ui.draw_text(surf, f"{f['gems']:03d}", 8, (x + 18, 12), WHITE)
        x += 52
        surf.blit(scaled(a.key, (16, 16)), (x, 8))
        ui.draw_text(surf, f"x{f['keys']}", 8, (x + 18, 12), WHITE)
        if f["boss_key"]:
            surf.blit(scaled(a.key, (20, 20)), (x + 40, 6))
            ui.draw_text(surf, "B", 8, (x + 56, 18), (255, 200, 60), shadow=BLACK)
        for i, (label, owned, icon) in enumerate((("A", f["sword"], a.sword_up), ("Q", f["bow"], a.bow))):
            bx = W - 78 + i * 38
            pygame.draw.rect(surf, (70, 70, 90), (bx, 3, 26, 26), 2)
            if owned:
                surf.blit(scaled(icon, (22, 22)), (bx + 2, 5))
            ui.draw_text(surf, label, 8, (bx - 9, 12), (200, 200, 120))
        ui.draw_text(surf, self.room.data["name"], 8, (W // 2 + 30, 12), (150, 150, 170), "midtop")

    def _draw_textbox(self, surf):
        tb = self.text
        top = self.player.hit.bottom > ROOM_H * 0.55
        rect = pygame.Rect(16, HUD_H + (12 if top else ROOM_H - 108), W - 32, 96)
        pygame.draw.rect(surf, (102, 51, 0), rect)
        pygame.draw.rect(surf, (137, 87, 46), rect.inflate(-8, -8))
        pygame.draw.rect(surf, (60, 30, 0), rect, 2)
        lines = ui.wrap(tb.pages[tb.page], ui.font(8), rect.width - 32)
        remaining = len(tb.writer.visible)
        y = rect.y + 14
        for line in lines[:6]:
            if remaining <= 0:
                break
            part = line[:remaining]
            remaining -= len(line) + 1
            ui.draw_text(surf, part, 8, (rect.x + 16, y), WHITE, shadow=(60, 30, 0))
            y += 14
        if tb.writer.done and ui.blink(self.t, 2):
            ui.draw_text(surf, "E", 8, (rect.right - 18, rect.bottom - 16), WHITE)

