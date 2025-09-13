import pygame
from settings import *
import random

# -------------------
# Player
# -------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Asset/player.png").convert_alpha()  # red knight
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.speed = 5
        self.jump_power = -15
        self.health = 5

    def update(self, platforms, enemies, hazards):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        # Gravity
        self.vel_y += 1
        self.rect.y += self.vel_y

        # Platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y >= 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True

        # Enemy collisions
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.health -= 1
                # Knockback
                self.rect.x -= 20 if enemy.rect.centerx < self.rect.centerx else -20

        # Hazard collisions
        for hazard in hazards:
            if self.rect.colliderect(hazard.rect):
                self.health -= 1

# -------------------
# Platforms
# -------------------
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image="Asset/platform.png"):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

# -------------------
# Hazards (spikes, lava)
# -------------------
class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image="Asset/spike.png"):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

# -------------------
# Enemies
# -------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image="Asset/enemy.png"):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.direction = 1
        self.health = 3

    def update(self):
        # Move left/right automatically (basic patrol)
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1

# -------------------
# Boss
# -------------------
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Asset/boss.png").convert_alpha()  # big red dragon
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_health = 15
        self.health = self.max_health
        self.phase = 0  # tracks if he jumps away
        self.minions = pygame.sprite.Group()
        self.jump_timer = 0
        self.on_screen = True

    def update(self, player_group, enemies_group):
        # Aggressive AI: move toward player
        if self.on_screen:
            if player_group.sprites():
                player = player_group.sprites()[0]
                if player.rect.x > self.rect.x:
                    self.rect.x += 3
                elif player.rect.x < self.rect.x:
                    self.rect.x -= 3

            # Phase logic: spawn minions at 2/3 and 1/3 health
            if self.health <= (self.max_health * (2 - self.phase)/3) and self.phase < 2:
                self.spawn_minions(enemies_group)
                self.phase += 1
                self.on_screen = False  # jump away

        else:
            # wait for minions to be killed
            if not enemies_group.sprites():
                self.on_screen = True  # jump back down

    def spawn_minions(self, enemies_group):
        for i in range(3):
            minion = Enemy(self.rect.x + i*60, self.rect.bottom - 50, "Asset/boss_minion.png")
            enemies_group.add(minion)

# -------------------
# Reward Item
# -------------------
class RewardItem(pygame.sprite.Sprite):
    def __init__(self, x, y, image="Asset/reward_item.png"):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(topleft=(x, y))
