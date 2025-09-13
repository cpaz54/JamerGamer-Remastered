# player.py
import pygame
from settings import *
from enemy import Enemy

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

        # Physics
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

        # Attack cooldown
        self.attack_cooldown = 0

    def update(self, platforms, attacks_group):
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_a]:
            self.rect.x -= 5
            self.facing_right = False
        if keys[pygame.K_d]:
            self.rect.x += 5
            self.facing_right = True

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        # Gravity
        self.vel_y += 1
        self.rect.y += self.vel_y

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y >= 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True

        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Attack
        if keys[pygame.K_j] and self.attack_cooldown == 0:
            attack = Attack(self.rect, self.facing_right)
            attacks_group.add(attack)
            self.attack_cooldown = 20


class Attack(pygame.sprite.Sprite):
    def __init__(self, player_rect, facing_right=True):
        super().__init__()
        self.image = pygame.Surface((20, 10))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        if facing_right:
            self.rect.midleft = player_rect.midright
        else:
            self.rect.midright = player_rect.midleft
        self.timer = 10

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
