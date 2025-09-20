import pygame
import math
from settings import *

# ----- Player -----
class PlatPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            image_loaded = pygame.image.load("Asset/player.png").convert_alpha()
            # Scale the player to a reasonable, uniform size
            self.image = pygame.transform.scale(image_loaded, (32, 48))
        except pygame.error:
            # Create a placeholder rectangle if image doesn't exist
            self.image = pygame.Surface((32, 48))
            self.image.fill(NEON_GREEN)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.attack_group = pygame.sprite.Group()
        self.speed = 5
        # Tighter, snappier jump: higher initial impulse, stronger gravity, with coyote/leeway
        self.jump_power = 18
        self.gravity = 1.2
        self.terminal_velocity = 22
        self.coyote_time_frames = 6
        self.coyote_timer = 0
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
        # Coyote time allows a short grace period for jump after leaving ground
        if self.on_ground:
            self.coyote_timer = self.coyote_time_frames
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and (self.on_ground or self.coyote_timer > 0):
            self.vel_y = -self.jump_power
            self.on_ground = False
            self.coyote_timer = 0

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0

        # Gravity (stronger for tighter jump arc); apply light variable jump cut if key released
        jump_key_down = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        self.vel_y += self.gravity
        if not jump_key_down and self.vel_y < 0:
            # Cut upward velocity when releasing jump for less float
            self.vel_y += self.gravity * 1.5
        if self.vel_y > self.terminal_velocity:
            self.vel_y = self.terminal_velocity
            
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
        
        # Upward slash
        if (keys[pygame.K_k] or keys[pygame.K_z]) and self.attack_cooldown == 0:
            attack = Attack(self.rect, self.facing_right, "upward")
            self.attack_group.add(attack)
            self.attack_cooldown = 15  # prevent spamming

        self.attack_group.update()

# ----- Attack -----
class Attack(pygame.sprite.Sprite):
    def __init__(self, player_rect, facing_right=True, attack_type="horizontal"):
        super().__init__()
        # Create red rectangle attack visual
        if attack_type == "upward":
            self.image = pygame.Surface((20, 40))  # Taller for upward slash
            self.rect = self.image.get_rect(midbottom=player_rect.midtop)
        else:  # horizontal
            self.image = pygame.Surface((40, 20))  # Wider for horizontal slash
            if facing_right:
                self.rect = self.image.get_rect(midleft=player_rect.midright)
            else:
                self.rect = self.image.get_rect(midright=player_rect.midleft)
        
        self.image.fill((255, 0, 0))  # Red attack rectangle
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
            image_loaded = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(image_loaded, (w, h))
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
            image_loaded = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(image_loaded, (w, h))
        except pygame.error:
            # Create placeholder hazard
            self.image = pygame.Surface((w, h))
            self.image.fill((255, 0, 0))  # Red hazard
        
        self.rect = self.image.get_rect(topleft=(x, y))

# ----- Enemies -----
class PlatEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, img_path, patrol_range=120, aggro_range=80):
        super().__init__()
        try:
            image_loaded = pygame.image.load(img_path).convert_alpha()
            # Scale enemy to a uniform size
            self.image = pygame.transform.scale(image_loaded, (32, 32))
        except pygame.error:
            # Create placeholder enemy
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 100, 100))  # Light red enemy
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_speed = 1
        self.speed = self.base_speed
        self.direction = 1
        self.original_x = x
        self.patrol_left = x - patrol_range
        self.patrol_right = x + patrol_range
        self.aggro_range = aggro_range
        self.move_timer = 0
        self.aggro_timer = 0
        self.is_aggro = False
        self.aggro_duration = 120  # frames to stay aggro
        self.patrol_pattern = "back_forth"  # "back_forth", "circle", "stationary"
        self.patrol_timer = 0
        self.original_y = y
        self.vertical_amplitude = 20  # for circle pattern
        self.vertical_speed = 0.1

    def update(self, player=None):
        self.move_timer += 1
        self.patrol_timer += 1
        
        # Check for player aggro
        if player:
            distance_to_player = abs(self.rect.centerx - player.rect.centerx)
            if distance_to_player <= self.aggro_range and not self.is_aggro:
                self.is_aggro = True
                self.aggro_timer = self.aggro_duration
                self.speed = self.base_speed * 2  # Move faster when aggro
            elif self.is_aggro:
                self.aggro_timer -= 1
                if self.aggro_timer <= 0:
                    self.is_aggro = False
                    self.speed = self.base_speed
        
        # Movement patterns
        if self.is_aggro and player:
            # When aggro, move toward player regardless of pattern
            if self.move_timer % 2 == 0:
                if player.rect.centerx < self.rect.centerx:
                    self.rect.x -= self.speed
                else:
                    self.rect.x += self.speed
        else:
            # Normal patrol behavior when not aggro
            if self.patrol_pattern == "back_forth":
                self._patrol_back_forth()
            elif self.patrol_pattern == "circle":
                self._patrol_circle()
            elif self.patrol_pattern == "stationary":
                self._patrol_stationary()
        
        # Keep within screen bounds
        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.direction = -1

    def _patrol_back_forth(self):
        if self.move_timer % 2 == 0:
            self.rect.x += self.speed * self.direction
        
        # Turn around at patrol boundaries
        if self.rect.centerx <= self.patrol_left or self.rect.centerx >= self.patrol_right:
            self.direction *= -1

    def _patrol_circle(self):
        # Circular movement pattern
        if self.move_timer % 2 == 0:
            self.rect.x += self.speed * self.direction
        
        # Vertical oscillation
        self.rect.y = self.original_y + int(math.sin(self.patrol_timer * self.vertical_speed) * self.vertical_amplitude)
        
        # Turn around at boundaries
        if self.rect.centerx <= self.patrol_left or self.rect.centerx >= self.patrol_right:
            self.direction *= -1

    def _patrol_stationary(self):
        # Stationary enemy that only moves when aggro
        if self.is_aggro and self.move_timer % 2 == 0:
            # This will be handled in the main update method with player reference
            pass

# ----- Boss -----
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            image_loaded = pygame.image.load("Asset/boss.png").convert_alpha()
            # Scale boss to a uniform size
            self.image = pygame.transform.scale(image_loaded, (100, 100))
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
        # Simple horizontal movement in boss stage
        self.horizontal_speed = 2
        self.horizontal_direction = 1
        self.left_bound = 80
        self.right_bound = WIDTH - 80 - self.rect.width
        
        # Attack patterns
        self.attack_timer = 0
        self.attack_cooldown = 90  # frames between attacks
        self.current_attack = None
        self.attack_duration = 0
        self.attack_patterns = ["charge", "spawn_wave", "teleport_strike"]
        self.charge_speed = 0
        self.charge_direction = 1
        self.teleport_timer = 0

    def update(self, player_group, enemies_group):
        self.spawn_timer += 1
        self.attack_timer += 1
        
        # Get player for targeting
        player = None
        if player_group:
            player = player_group.sprites()[0]
        
        # Horizontal patrol movement (only when not attacking)
        if not self.current_attack:
            self.rect.x += self.horizontal_speed * self.horizontal_direction
            if self.rect.x <= self.left_bound or self.rect.x >= self.right_bound:
                self.rect.x = max(self.left_bound, min(self.rect.x, self.right_bound))
                self.horizontal_direction *= -1
        
        # Attack pattern execution
        if self.current_attack:
            self._execute_attack(player, enemies_group)
        elif self.attack_timer >= self.attack_cooldown:
            self._start_attack()
        
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

    def _start_attack(self):
        import random
        self.current_attack = random.choice(self.attack_patterns)
        self.attack_timer = 0
        
        if self.current_attack == "charge":
            self.attack_duration = 60
            self.charge_speed = 8
        elif self.current_attack == "spawn_wave":
            self.attack_duration = 30
        elif self.current_attack == "teleport_strike":
            self.attack_duration = 45
            self.teleport_timer = 0

    def _execute_attack(self, player, enemies_group):
        self.attack_duration -= 1
        
        if self.current_attack == "charge":
            # Charge attack - move quickly in one direction
            self.rect.x += self.charge_speed * self.charge_direction
            if self.rect.x <= self.left_bound or self.rect.x >= self.right_bound:
                self.charge_direction *= -1
                self.rect.x = max(self.left_bound, min(self.rect.x, self.right_bound))
                
        elif self.current_attack == "spawn_wave":
            # Spawn wave of minions
            if self.attack_duration == 15:  # Mid-attack
                self.spawn_minions(enemies_group)
                
        elif self.current_attack == "teleport_strike":
            # Teleport near player and strike
            self.teleport_timer += 1
            if self.teleport_timer == 20 and player:  # Teleport after delay
                # Teleport to player's side
                if player.rect.centerx < WIDTH // 2:
                    self.rect.x = player.rect.right + 20
                else:
                    self.rect.x = player.rect.left - 120
                self.rect.y = player.rect.y - 50
        
        # End attack
        if self.attack_duration <= 0:
            self.current_attack = None
            self.attack_timer = 0

    def spawn_minions(self, enemies_group):
        # Clear existing minions first
        for minion in self.minions:
            minion.kill()
        self.minions.empty()
        
        # Spawn new minions with varied patterns
        minion_count = 2 if self.phase < 2 else 3
        patterns = ["back_forth", "circle", "stationary"]
        for i in range(minion_count):
            spawn_x = self.rect.x + (i - minion_count//2) * 60
            spawn_y = self.rect.bottom
            minion = PlatEnemy(spawn_x, spawn_y, "Asset/enemy1.png", patrol_range=100, aggro_range=90)
            minion.patrol_pattern = patterns[i % len(patterns)]
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
        self.rect.centery = self.original_y + int(math.sin(self.float_timer * 0.1) * 5)