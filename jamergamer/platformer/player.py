"""Jamer the knight."""
import pygame

from . import assets
from .physics import Body, approach

SCALE = 0.46
MAX_HEARTS = 5

RUN_SPEED = 4.6
ACCEL_GROUND = 0.9
ACCEL_AIR = 0.55
FRICTION = 0.8
JUMP_V = -13.2
COYOTE = 7
BUFFER = 8
SWING_FRAMES = 18
SWING_ACTIVE = (3, 12)
SWING_COOLDOWN = 6


def _frames():
    """name -> list of (image, anchor_x_in_source_px, native_faces_right)"""
    def f(rel, anchor, right=True):
        return (assets.img(rel, scale=SCALE), anchor * SCALE, right)
    return {
        "idle": [f("player/idle/0.png", 38), f("player/idle/1.png", 38)],
        "walk": [f("player/walk/0.png", 46), f("player/walk/1.png", 46)],
        "attack": [f("player/attack/1.png", 45), f("player/attack/0.png", 40)],
        "jump": [f("player/jump/0.png", 33, right=False)],
        "fall": [f("player/fall/0.png", 33, right=False)],
        "lose": [f("player/lose/0.png", 38)],
        "win": [f("player/win/0.png", 38)],
    }


class Player(Body):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 52)
        self.frames = _frames()
        self.facing = 1
        self.hearts = MAX_HEARTS
        self.coyote = 0
        self.buffer = 0
        self.swing = 0
        self.cooldown = 0
        self.invuln = 0
        self.stun = 0
        self.anim = 0.0
        self.state = "idle"
        self.frozen = False      # cutscenes / boss intros
        self.dead = False
        self.hit_ids = set()     # things already hit by the current swing
        self.dropping = 0

    # ------------------------------------------------------------------ input
    def control(self, keys, jump_pressed, jump_held, attack_pressed, audio):
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        if self.frozen or self.dead:
            left = right = down = False
            jump_pressed = attack_pressed = False
            jump_held = False

        if jump_pressed:
            self.buffer = BUFFER
        if self.on_ground:
            self.coyote = COYOTE
        else:
            self.coyote = max(0, self.coyote - 1)

        if self.stun > 0:
            self.stun -= 1
        else:
            move = (1 if right else 0) - (1 if left else 0)
            accel = ACCEL_GROUND if self.on_ground else ACCEL_AIR
            if move:
                self.vx = approach(self.vx, move * RUN_SPEED, accel)
                if self.swing == 0:
                    self.facing = move
            else:
                self.vx = approach(self.vx, 0, FRICTION if self.on_ground else 0.25)

            if self.buffer > 0 and (self.coyote > 0):
                if down and self.on_ground:
                    self.dropping = 10          # fall through ledges
                else:
                    self.vy = JUMP_V
                    audio.blip("jump")
                self.buffer = 0
                self.coyote = 0
            if not jump_held and self.vy < -4:
                self.vy *= 0.55                 # short hop when the button is released

        self.buffer = max(0, self.buffer - 1)
        self.dropping = max(0, self.dropping - 1)

        if attack_pressed and self.swing == 0 and self.cooldown == 0:
            self.swing = SWING_FRAMES
            self.hit_ids = set()
            audio.blip("swing")
        if self.swing > 0:
            self.swing -= 1
            if self.swing == 0:
                self.cooldown = SWING_COOLDOWN
        elif self.cooldown > 0:
            self.cooldown -= 1
        if self.invuln > 0:
            self.invuln -= 1

    # ------------------------------------------------------------------ combat
    @property
    def swing_active(self):
        elapsed = SWING_FRAMES - self.swing
        return self.swing > 0 and SWING_ACTIVE[0] <= elapsed <= SWING_ACTIVE[1]

    def sword_rect(self):
        if not self.swing_active:
            return None
        w, h = 60, 40
        x = self.cx - 6 if self.facing > 0 else self.cx - w + 6
        return pygame.Rect(int(x), int(self.y + 4), w, h)

    def hurt(self, from_x, audio, amount=1):
        if self.invuln > 0 or self.dead:
            return False
        self.hearts -= amount
        self.invuln = 80
        self.stun = 14
        self.swing = 0
        direction = -1 if from_x > self.cx else 1
        self.vx = 5.5 * direction
        self.vy = -6.5
        audio.blip("hurt")
        if self.hearts <= 0:
            self.hearts = 0
            self.dead = True
        return True

    def bounce(self):
        self.vy = JUMP_V * 0.75
        self.coyote = 0

    # ------------------------------------------------------------------ anim
    def update_anim(self):
        if self.dead:
            self.state = "lose"
        elif self.swing > 0:
            self.state = "attack"
        elif not self.on_ground:
            self.state = "jump" if self.vy < 0 else "fall"
        elif abs(self.vx) > 0.6:
            self.state = "walk"
        else:
            self.state = "idle"
        speed = {"walk": 0.12, "idle": 0.03}.get(self.state, 0.0)
        self.anim += speed

    def current_frame(self):
        if self.state == "attack":
            idx = 0 if (SWING_FRAMES - self.swing) < 4 else 1
            return self.frames["attack"][idx]
        seq = self.frames[self.state]
        return seq[int(self.anim) % len(seq)]

    def draw(self, surf, cam):
        if self.invuln > 0 and not self.dead and (self.invuln // 4) % 2 == 0:
            return
        image, anchor, native_right = self.current_frame()
        flip = (self.facing < 0) == native_right
        if flip:
            image = pygame.transform.flip(image, True, False)
            anchor = image.get_width() - anchor
        x = self.cx - anchor - cam[0]
        y = self.y + self.h - image.get_height() + 3 - cam[1]
        surf.blit(image, (int(x), int(y)))
