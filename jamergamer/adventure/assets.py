"""Jamer Quest sprites (32px native frames sliced by tools/slice_adventure_sprites.py)."""
import pygame

from ..config import asset

T = 32
_cache = {}


def spr(name):
    if name not in _cache:
        try:
            _cache[name] = pygame.image.load(asset("adventure", "sprites", name + ".png")).convert_alpha()
        except (pygame.error, FileNotFoundError):
            s = pygame.Surface((T, T), pygame.SRCALPHA)
            s.fill((255, 0, 255, 160))
            _cache[name] = s
    return _cache[name]


def flip(img, x=True, y=False):
    key = ("flip", id(img), x, y)
    if key not in _cache:
        _cache[key] = pygame.transform.flip(img, x, y)
    return _cache[key]


def rot(img, deg):
    key = ("rot", id(img), deg)
    if key not in _cache:
        _cache[key] = pygame.transform.rotate(img, deg)
    return _cache[key]


def scaled(img, size):
    key = ("scale", id(img), size)
    if key not in _cache:
        _cache[key] = pygame.transform.scale(img, size)
    return _cache[key]


def alpha(img, a):
    key = ("alpha", id(img), a)
    if key not in _cache:
        s = img.copy()
        s.set_alpha(a)
        _cache[key] = s
    return _cache[key]


class Art:
    """Named sprite lookups, built once per scene."""

    def __init__(self):
        t = lambda i: spr(f"tile{i:02d}")  # noqa: E731
        c = lambda i: spr(f"char{i:02d}")  # noqa: E731
        e = lambda i: spr(f"enemy{i:02d}")  # noqa: E731
        it = lambda i: spr(f"item{i:02d}")  # noqa: E731

        # --- player: down/up/right/left walk cycles, item-use poses, hold-up pose
        self.p_stand = c(0)
        self.p_walk = {
            "down": [c(1), flip(c(1))],
            "up": [c(2), flip(c(2))],
            "right": [c(3), c(4)],
            "left": [flip(c(3)), flip(c(4))],
        }
        self.p_use = {"down": c(5), "up": c(6), "right": c(7), "left": flip(c(7))}
        self.p_hold = c(9)
        self.npc_green = [c(8), flip(c(8))]
        self.npc_red = [spr("npc"), flip(spr("npc"))]

        # --- weapons
        up, diag, right = it(2), it(0), it(1)
        self.sword_up, self.sword_diag, self.sword_right = up, diag, right
        self.arrow = {"up": it(3), "right": it(4), "down": flip(it(3), False, True), "left": flip(it(4))}
        self.arrow_break = [it(5), it(6)]
        self.bow = it(9)
        self.sword_icon = it(0)

        # --- terrain
        self.tree = t(4)
        self.palm = t(5)
        self.shrub = t(6)
        self.chest = t(8)
        self.chest_open = t(9)
        self.sign = t(10)
        self.bed = [t(11), t(12)]
        self.drawer = t(13)
        self.candles = t(14)
        self.stairs = t(16)
        self.doorway = t(17)
        self.rug = t(18)
        self.roof = t(19)
        self.wall_top, self.wall_corner, self.wall_right = t(20), t(21), t(22)
        self.floorboard = t(23)
        self.mt_rock = t(25)
        self.cave_mouth = t(26)
        self.cave_top, self.cave_right, self.cave_corner = t(27), t(28), t(29)
        self.cave_floor = t(30)
        self.cave_edge = t(31)
        self.waterfall = [t(32), t(33)]
        self.water = {
            "mid": [t(34), t(35)], "top": [t(36), t(37)], "right": [t(38), t(39)],
            "bottom": [t(40), t(41)], "left": [t(42), t(43)], "tr": [t(44), t(45)],
            "br": [t(46), t(47)], "bl": [t(48), t(49)], "tl": [t(50), t(51)],
        }
        self.locked_door = t(52)
        self.door_open = [t(53), t(54), t(55), t(56)]
        self.target = {"red": t(57), "blue": t(58)}
        self.gem = {1: t(59), 5: t(60), 20: t(61)}
        self.heart_drop = t(62)
        self.red_barrier = [t(67), t(68), t(69), t(70)]     # up -> down
        self.blue_barrier = [t(71), t(72), t(73), t(74)]
        self.push_block = t(75)
        self.lamps = [t(0), t(1), t(2), t(3)]
        self.flowers = spr("misc")
        self.fence = spr("fence")
        self.grave = spr("gravestone")
        self.bridge = rot(spr("green_bridge"), 90)
        self.key = spr("gold_key")
        self.rock = spr("rock")
        self.smoke = spr("smoke")
        self.tree2 = spr("new_tree")

        # --- enemies
        self.spider = {"up": [flip(e(0), False, True), flip(e(1), False, True)], "down": [e(0), e(1)],
                       "left": [flip(e(2)), flip(e(3))], "right": [e(2), e(3)]}
        self.spider_green = e(4)
        self.ghost_laugh = [scaled(e(5), (64, 64)), scaled(e(6), (64, 64))]
        self.ghost_solid = [scaled(e(17), (64, 64)), scaled(e(18), (64, 64))]
        self.orb = {"white": e(7), "closed": e(8), "red": e(9), "yellow": e(10)}

        # --- hud
        self.heart_full = spr("full_heart")
        self.heart_half = spr("half_heart")
        self.heart_empty = spr("no_heart")
