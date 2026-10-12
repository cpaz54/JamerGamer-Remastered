"""Room building: static tile art, collision and the interactive objects in a room."""
import pygame

from .assets import T, flip

COLS, ROWS = 17, 11
ROOM_W, ROOM_H = COLS * T, ROWS * T

GROUND = {"outside": (159, 221, 98), "house": (150, 100, 60), "cave": (202, 131, 61)}

STATIC_SOLID = set("TpwWRFGrh#%Zzdc")
WALKABLE_DECOR = set(".f=,_uHgEeX")


class Obj:
    """Interactive thing in a room. `solid` blocks movement; `kind` drives behaviour."""

    def __init__(self, kind, tx, ty, data=None):
        self.kind = kind
        self.tx, self.ty = tx, ty
        self.x, self.y = tx * T, ty * T
        self.data = data or {}
        self.solid = kind not in ("door", "exit", "stairs", "pickup")
        self.alive = True
        self.anim = 0          # for doors opening / barriers moving
        self.timer = 0
        self.push = 0          # push-block pressure frames
        self.slide = None      # push-block slide target

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), T, T)


class Room:
    def __init__(self, key, data, art, flags):
        self.key = key
        self.data = data
        self.kind = data["kind"]
        self.map = data["map"]
        self.art = art
        self.flags = flags
        self.objects = []
        self.spawns = []       # (char, tx, ty) for enemies / boss
        self.water = []        # (tx, ty, frames)
        self.surface = None
        self._build()

    # ------------------------------------------------------------ helpers
    def ch(self, tx, ty):
        if 0 <= tx < COLS and 0 <= ty < ROWS:
            return self.map[ty][tx]
        return None

    def _is(self, tx, ty, chars):
        c = self.ch(tx, ty)
        return c is None or c in chars

    def floor_img(self):
        a = self.art
        return {"outside": None, "house": a.floorboard, "cave": a.cave_floor}[self.kind]

    # ------------------------------------------------------------ build
    def _build(self):
        a = self.art
        f = self.flags
        counters = {}

        def nxt(char):
            lst = self.data.get(char, [])
            i = counters.get(char, 0)
            counters[char] = i + 1
            return lst[i] if i < len(lst) else {}

        self.solid = set()
        for ty, row in enumerate(self.map):
            for tx, c in enumerate(row):
                if c in STATIC_SOLID:
                    self.solid.add((tx, ty))
                if c == "b":
                    if f"{self.key}:{tx},{ty}" not in f["cut"]:
                        self.objects.append(Obj("shrub", tx, ty))
                elif c == "C":
                    d = nxt("C")
                    o = Obj("chest", tx, ty, d)
                    o.opened = d.get("id") in f["opened"]
                    self.objects.append(o)
                elif c == "S":
                    self.objects.append(Obj("sign", tx, ty, {"text": nxt("S")}))
                elif c == "N":
                    d = nxt("N")
                    if d.get("hide_if") and f.get(d["hide_if"]):
                        continue
                    self.objects.append(Obj("npc", tx, ty, d))
                elif c == "D":
                    self.objects.append(Obj("door", tx, ty, nxt("D")))
                elif c == "M":
                    d = nxt("M")
                    o = Obj("door", tx, ty, d)
                    o.locked = bool(d.get("lock")) and d["lock"] not in f["unlocked"]
                    o.solid = o.locked
                    self.objects.append(o)
                elif c == "O":
                    self.objects.append(Obj("exit", tx, ty, nxt("O")))
                elif c == "L":
                    d = nxt("L")
                    o = Obj("lock", tx, ty, d)
                    if d.get("lock") in f["unlocked"]:
                        o.solid = False
                        o.anim = 3
                    self.objects.append(o)
                elif c in "12":
                    o = Obj("barrier", tx, ty, {"color": "red" if c == "1" else "blue"})
                    up = f["red_on"] if c == "1" else not f["red_on"]
                    o.anim = 0 if up else 3
                    o.solid = up
                    self.objects.append(o)
                elif c == "t":
                    self.objects.append(Obj("target", tx, ty))
                elif c == "P":
                    self.objects.append(Obj("block", tx, ty))
                elif c == "~":
                    # gates sit in water and are drawn as water until they open
                    self.objects.append(Obj("gate", tx, ty, {"water": self._water_dir(tx, ty)}))
                elif c == "$":
                    self.objects.append(Obj("shop", tx, ty, nxt("$")))
                elif c == "H":
                    self.objects.append(Obj("pickup", tx, ty, {"item": "heart"}))
                elif c == "g":
                    self.objects.append(Obj("pickup", tx, ty, {"item": "gem", "amount": 5}))
                elif c in "EeX":
                    self.spawns.append((c, tx, ty))
                elif c in "wW":
                    frames = a.waterfall if c == "W" else a.water[self._water_dir(tx, ty)]
                    self.water.append((tx, ty, frames))
        self.render()

    def _water_dir(self, tx, ty):
        land = lambda x, y: self.ch(x, y) is not None and self.ch(x, y) not in "wW=~"  # noqa: E731
        n, s, e, w = land(tx, ty - 1), land(tx, ty + 1), land(tx + 1, ty), land(tx - 1, ty)
        if n and e:
            return "tr"
        if n and w:
            return "tl"
        if s and e:
            return "br"
        if s and w:
            return "bl"
        if n:
            return "top"
        if s:
            return "bottom"
        if e:
            return "right"
        if w:
            return "left"
        return "mid"

    def _wall_tile(self, tx, ty, wall_char, top, right, corner):
        """Pick a wall sprite from which neighbours are floor."""
        floor = lambda x, y: self.ch(x, y) is not None and self.ch(x, y) != wall_char  # noqa: E731
        n, s, e, w = floor(tx, ty - 1), floor(tx, ty + 1), floor(tx + 1, ty), floor(tx - 1, ty)
        if s:
            return top
        if n:
            return flip(top, False, True)
        if w:
            return right
        if e:
            return flip(right)
        if floor(tx - 1, ty + 1):
            return corner                      # floor down-left: top-right corner
        if floor(tx + 1, ty + 1):
            return flip(corner)
        if floor(tx - 1, ty - 1):
            return flip(corner, False, True)
        if floor(tx + 1, ty - 1):
            return flip(corner, True, True)
        return None

    def render(self):
        a = self.art
        surf = pygame.Surface((ROOM_W, ROOM_H))
        surf.fill(GROUND[self.kind])
        floor = self.floor_img()
        for ty, row in enumerate(self.map):
            for tx, c in enumerate(row):
                x, y = tx * T, ty * T
                if floor is not None and c not in "#%":
                    surf.blit(floor, (x, y))
                img = None
                if c == "T":
                    img = a.tree
                elif c == "p":
                    img = a.palm
                elif c == "f":
                    img = a.flowers
                elif c == "=":
                    surf.blit(a.water["mid"][0], (x, y))
                    img = a.bridge
                elif c == "R":
                    img = a.mt_rock
                elif c == "M":
                    surf.fill((0, 0, 0), (x, y, T, T))
                    img = a.cave_mouth
                elif c == "F":
                    img = a.fence
                elif c == "G":
                    img = a.grave
                elif c == "r":
                    img = a.roof
                elif c == "h":
                    img = a.rug          # house front with windows
                elif c == "D":
                    surf.fill((0, 0, 0), (x, y, T, T))
                    img = a.doorway
                elif c == "#":
                    surf.fill((40, 20, 30), (x, y, T, T))
                    img = self._wall_tile(tx, ty, "#", a.wall_top, a.wall_right, a.wall_corner)
                elif c == "%":
                    surf.fill((60, 30, 10), (x, y, T, T))
                    img = self._wall_tile(tx, ty, "%", a.cave_top, a.cave_right, a.cave_corner)
                elif c == "u":
                    pygame.draw.rect(surf, (150, 40, 50), (x, y, T, T))
                    edge = [(0, -1, (x, y, T, 3)), (0, 1, (x, y + T - 3, T, 3)),
                            (-1, 0, (x, y, 3, T)), (1, 0, (x + T - 3, y, 3, T))]
                    for dx, dy, r in edge:
                        if self.ch(tx + dx, ty + dy) not in ("u", "N"):
                            pygame.draw.rect(surf, (230, 190, 90), r)
                elif c == "Z":
                    img = a.bed[0]
                elif c == "z":
                    img = a.bed[1]
                elif c == "d":
                    img = a.drawer
                elif c == "c":
                    img = a.candles
                elif c == "O":
                    surf.fill((0, 0, 0), (x, y, T, T))
                    if self.kind == "house":
                        img = flip(a.doorway, False, True)
                if img is not None:
                    surf.blit(img, (x, y))
        self.surface = surf

    # ------------------------------------------------------------ queries
    def blocked(self, rect):
        """Does `rect` overlap anything solid?"""
        x0, x1 = rect.left // T, (rect.right - 1) // T
        y0, y1 = rect.top // T, (rect.bottom - 1) // T
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if (tx, ty) in self.solid:
                    return True
                if not (0 <= tx < COLS and 0 <= ty < ROWS):
                    # off the map: only allowed if the border tile we came from is open
                    bx, by = min(max(tx, 0), COLS - 1), min(max(ty, 0), ROWS - 1)
                    if (bx, by) in self.solid:
                        return True
        for o in self.objects:
            if o.solid and o.alive and rect.colliderect(o.rect):
                return True
        return False

    def object_at(self, tx, ty, kinds=None):
        for o in self.objects:
            if o.alive and o.tx == tx and o.ty == ty and (kinds is None or o.kind in kinds):
                return o
        return None

    def free_tile(self, tx, ty):
        if not (0 <= tx < COLS and 0 <= ty < ROWS):
            return False
        if (tx, ty) in self.solid or self.ch(tx, ty) in "~12tLMDO":
            return False
        return self.object_at(tx, ty) is None

    # ------------------------------------------------------------ drawing
    def draw(self, surf, t, ox=0, oy=0):
        surf.blit(self.surface, (ox, oy))
        frame = (t // 30) % 2
        for tx, ty, frames in self.water:
            surf.blit(frames[frame], (ox + tx * T, oy + ty * T))
        a = self.art
        for o in self.objects:
            if not o.alive:
                continue
            x, y = ox + int(o.x), oy + int(o.y)
            k = o.kind
            if k == "shrub":
                surf.blit(a.shrub, (x, y))
            elif k == "chest":
                surf.blit(a.chest_open if o.opened else a.chest, (x, y))
            elif k == "sign":
                surf.blit(a.sign, (x, y))
            elif k == "npc":
                imgs = a.npc_red if o.data.get("look") == "red" else a.npc_green
                surf.blit(imgs[(t // 40) % 2], (x, y))
            elif k == "door" and getattr(o, "locked", False):
                surf.blit(a.locked_door, (x, y))
            elif k == "lock":
                if self.kind == "cave":
                    surf.blit(a.cave_floor, (x, y))
                if o.anim < 3:
                    surf.blit(a.locked_door if o.anim == 0 else a.door_open[o.anim], (x, y))
            elif k == "barrier":
                frames = a.red_barrier if o.data["color"] == "red" else a.blue_barrier
                surf.blit(frames[min(3, o.anim)], (x, y))
            elif k == "target":
                surf.blit(a.target["red" if self.flags["red_on"] else "blue"], (x, y))
            elif k == "block":
                surf.blit(a.push_block, (x, y))
            elif k == "gate":
                surf.blit(a.water[o.data.get("water", "top")][frame], (x, y))
            elif k == "stairs":
                surf.blit(a.stairs, (x, y))
            elif k == "shop":
                sold = o.data.get("once") and o.data["id"] in self.flags["bought"]
                pygame.draw.rect(surf, (90, 60, 30), (x + 2, y + 18, T - 4, 12))
                if not sold:
                    icon = a.heart_drop if o.data["id"] == "refill" else a.heart_full
                    bob = (t // 20) % 2
                    surf.blit(icon, (x, y - 4 - bob))
            elif k == "pickup":
                img = a.heart_drop if o.data["item"] == "heart" else a.gem.get(o.data.get("amount", 1), a.gem[1])
                bob = (t // 16) % 2
                surf.blit(img, (x, y - bob))
