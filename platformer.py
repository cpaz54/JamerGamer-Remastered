import pygame
from settings import *

# ----- Player -----
class PlatPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("Asset/player.png").convert_alpha()
            # Scale the player to a reasonable size
            self.image = pygame.transform.scale(self.image, (32, 48))
        except pygame.error:
            # Create a placeholder rectangle if image doesn't exist
            self.image = pygame.Surface((32, 48))
            self.image.fill(NEON_GREEN)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.attack_group = pygame.sprite.Group()
        self.speed = 5
        self.jump_power = 15
        self.facing_right = True
        self.attack_cooldown = 0

    def update(self, platforms, enemies, hazards):
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0

        # Gravity
        self.vel_y += 1  # Gravity constant
        if self.vel_y > 20:  # Terminal velocity
            self.vel_y = 20
            
        self.rect.y += self.vel_y

        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping up into platform
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Prevent falling through bottom of screen
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True

        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Attack
        if (keys[pygame.K_j] or keys[pygame.K_x]) and self.attack_cooldown == 0:
            attack = Attack(self.rect, self.facing_right)
            self.attack_group.add(attack)
            self.attack_cooldown = 15  # prevent spamming

        self.attack_group.update()

# ----- Attack -----
class Attack(pygame.sprite.Sprite):
    def __init__(self, player_rect, facing_right=True):
        super().__init__()
        try:
            if facing_right:
                self.image = pygame.image.load("Asset/slash_right.png").convert_alpha()
            else:
                self.image = pygame.image.load("Asset/slash_left.png").convert_alpha()
        except pygame.error:
            # Create placeholder attack visual
            self.image = pygame.Surface((40, 30))
            self.image.fill((255, 255, 0))  # Yellow for attack
            
        if facing_right:
            self.rect = self.image.get_rect(midleft=player_rect.midright)
        else:
            self.rect = self.image.get_rect(midright=player_rect.midleft)
        self.timer = 10

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# ----- Platforms -----
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, img_path):
        super().__init__()
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (w, h))
        except pygame.error:
            # Create placeholder platform
            self.image = pygame.Surface((w, h))
            self.image.fill((100, 100, 100))  # Gray platform
        
        self.rect = self.image.get_rect(topleft=(x, y))

# ----- Hazards -----
class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, img_path):
        super().__init__()
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (w, h))
        except pygame.error:
            # Create placeholder hazard
            self.image = pygame.Surface((w, h))
            self.image.fill((255, 0, 0))  # Red hazard
        
        self.rect = self.image.get_rect(topleft=(x, y))

# ----- Enemies -----
class PlatEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, img_path):
        super().__init__()
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
            # Scale enemy to reasonable size
            self.image = pygame.transform.scale(self.image, (32, 32))
        except pygame.error:
            # Create placeholder enemy
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 100, 100))  # Light red enemy
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 1  # Slower speed for better control
        self.direction = 1
        self.patrol_left = x - 80
        self.patrol_right = x + 80
        self.move_timer = 0

    def update(self):
        self.move_timer += 1
        # Only move every few frames for smoother animation
        if self.move_timer % 2 == 0:
            self.rect.x += self.speed * self.direction
        
        # Patrol behavior - turn around at boundaries
        if self.rect.centerx <= self.patrol_left or self.rect.centerx >= self.patrol_right:
            self.direction *= -1
        
        # Also turn around at screen edges
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

# ----- Boss -----
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("Asset/boss.png").convert_alpha()
            # Scale boss to reasonable size
            self.image = pygame.transform.scale(self.image, (100, 100))
        except pygame.error:
            # Create placeholder boss
            self.image = pygame.Surface((100, 100))
            self.image.fill((150, 0, 150))  # Purple boss
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_health = 30
        self.health = self.max_health
        self.minions = pygame.sprite.Group()
        self.phase = 0
        self.spawn_timer = 0
        self.original_y = y

    def update(self, player_group, enemies_group):
        self.spawn_timer += 1
        
        # Phase transitions based on health
        if self.health <= 20 and self.phase == 0:
            self.spawn_minions(enemies_group)
            self.phase += 1
            self.rect.y = self.original_y - 100  # Move boss up
            
        elif self.health <= 10 and self.phase == 1:
            self.spawn_minions(enemies_group)
            self.phase += 1
            self.rect.y = self.original_y - 200  # Move boss further up

        # Boss returns to original position when minions are defeated
        if self.phase > 0 and len(self.minions) == 0:
            if self.rect.y < self.original_y:
                self.rect.y += 3  # Slowly descend back down
            else:
                self.rect.y = self.original_y

        # Spawn minions periodically in higher phases
        if self.phase >= 2 and self.spawn_timer % 180 == 0 and len(self.minions) < 2:
            self.spawn_minions(enemies_group)

    def spawn_minions(self, enemies_group):
        # Clear existing minions first
        for minion in self.minions:
            minion.kill()
        self.minions.empty()
        
        # Spawn new minions
        minion_count = 2 if self.phase < 2 else 3
        for i in range(minion_count):
            spawn_x = self.rect.x + (i - minion_count//2) * 60
            spawn_y = self.rect.bottom
            minion = PlatEnemy(spawn_x, spawn_y, "Asset/enemy1.png")
            self.minions.add(minion)
            enemies_group.add(minion)

# ----- Reward -----
class RewardItem(pygame.sprite.Sprite):
    def __init__(self, x, y, img_path):
        super().__init__()
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except pygame.error:
            # Create placeholder reward
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 215, 0))  # Gold reward
        
        self.rect = self.image.get_rect(center=(x, y))
        self.float_timer = 0
        self.original_y = y

    def update(self):
        # Floating animation
        self.float_timer += 1
        self.rect.centery = self.original_y + int(pygame.math.sin(self.float_timer * 0.1) * 5)