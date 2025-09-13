import pygame
from settings import *

# ----- Player -----
class PlatPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Asset/player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.attack_group = pygame.sprite.Group()
        self.speed = 5
        self.jump_power = 15

    def update(self, platforms, enemies, hazards):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        self.vel_y += 1
        self.rect.y += self.vel_y

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y >= 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True

        # Attack
        if keys[pygame.K_j]:
            attack = Attack(self.rect)
            self.attack_group.add(attack)
        self.attack_group.update()

# ----- Attack -----
class Attack(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = pygame.Surface((20, 10))
        self.image.fill((160, 32, 240))
        self.rect = self.image.get_rect(midleft=player_rect.midright)
        self.timer = 10

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# ----- Platforms -----
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, img_path):
        super().__init__()
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

# ----- Hazards -----
class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, img_path):
        super().__init__()
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

# ----- Enemies -----
class PlatEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, img_path):
        super().__init__()
        self.image = pygame.image.load(img_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left < 100 or self.rect.right > 700:
            self.direction *= -1

# ----- Boss -----
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Asset/boss.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 30
        self.minions = pygame.sprite.Group()
        self.phase = 0

    def update(self, player_group, enemies_group):
        # Simple jump/spawn minions logic
        if self.health <= 20 and self.phase == 0:
            self.spawn_minions(enemies_group)
            self.phase += 1
            self.rect.y -= 100  # jump out of reach
        elif self.health <= 10 and self.phase == 1:
            self.spawn_minions(enemies_group)
            self.phase += 1
            self.rect.y -= 100
        # Boss comes back down
        if self.phase > 0 and len(self.minions) == 0:
            self.rect.y = min(self.rect.y + 5, HEIGHT//2 - 75)

    def spawn_minions(self, enemies_group):
        for i in range(3):
            minion = PlatEnemy(self.rect.x + i*50, self.rect.bottom, "Asset/enemy1.png")
            self.minions.add(minion)
            enemies_group.add(minion)

# ----- Reward -----
class RewardItem(pygame.sprite.Sprite):
    def __init__(self, x, y, img_path):
        super().__init__()
        self.image = pygame.image.load(img_path).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

# ----- Platformer setup functions -----
player = None
def init_platformer():
    global player
    player = PlatPlayer(50, HEIGHT-100)

def setup_stage(stage_num):
    pass  # Will be handled in main.py
