import pygame
import math
from settings import WIDTH

class BigWilligBoss(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        
        # Boss properties
        self.max_health = 10
        self.health = self.max_health
        self.alive = True
        
        # Position - spawn on elevated blocks (right side, higher up)
        self.rect = pygame.Rect(pos[0], pos[1], size, size)
        self.start_pos = pos
        
        # Cinematic introduction state
        self.intro_state = "waiting"  # waiting, health_bar, boss_appear, title_show, title_hide, falling, fighting
        self.intro_timer = 0
        self.title_timer = 0
        self.title_duration = 300  # 5 seconds at 60 FPS
        
        # Physics properties (same as player)
        self.direction = pygame.math.Vector2(0, 0)  # For gravity like player
        self.on_ground = False
        self.on_ceiling = False
        
        # Animation properties
        self.stand_frames = []
        self.stand_cast_frames = []
        self.float_frames = []
        self.float_cast_frames = []
        self.death_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.05  # 50% slower (was 0.1, now 0.05)
        
        # Attack system
        self.attack_state = "idle"  # idle, moving_left, casting_left, shooting_left, returning, moving_right, casting_right, shooting_right, moving_center, floating_up, float_casting, float_rain, floating_down, vulnerable, next_attack
        self.attack_timer = 0
        self.attack_delay = 30  # 0.5 seconds delay
        self.move_speed = 3
        self.original_x = self.rect.x
        self.original_y = self.rect.y  # Store original height for floating return
        self.fireballs = pygame.sprite.Group()
        self.fireball_count = 0
        self.fireball_delay = 60  # 1 second delay between fireballs
        self.fireball_timer = 0
        
        # Load animation frames
        self._load_stand_frames()
        self._load_stand_cast_frames()
        self._load_float_frames()
        self._load_float_cast_frames()
        self._load_death_frames()
        
        # Set initial image
        self.image = self.stand_frames[0] if self.stand_frames else self._create_fallback_image(size)
        
        # Title image
        self.title_image = None
        self._load_title_image()
        
        # Health bar properties (positioned like player health in upper right, moved up and right)
        self.health_bar_rect = pygame.Rect(WIDTH - 200, 20, 200, 20)  # Moved up (y=20) and right (x=WIDTH-200)
        self.health_bar_bg_color = (50, 0, 0)  # Dark red background
        self.health_bar_color = (200, 0, 0)  # Dark red health bar
        
    def _load_stand_frames(self):
        """Load stand animation frames"""
        try:
            stand1 = pygame.image.load("assets/bosses/BIG_WILLIG/stand/stand.png").convert_alpha()
            stand2 = pygame.image.load("assets/bosses/BIG_WILLIG/stand/stand2.png").convert_alpha()
            
            # Scale frames to boss size (20% bigger)
            boss_size = 120  # 20% bigger than original 100
            stand1 = pygame.transform.scale(stand1, (boss_size, boss_size))
            stand2 = pygame.transform.scale(stand2, (boss_size, boss_size))
            
            self.stand_frames = [stand1, stand2]
        except:
            print("Warning: Could not load BIG_WILLIG stand frames")
            self.stand_frames = []
    
    def _load_stand_cast_frames(self):
        """Load stand_cast animation frames"""
        try:
            cast1 = pygame.image.load("assets/bosses/BIG_WILLIG/stand_cast/cast1.png").convert_alpha()
            cast2 = pygame.image.load("assets/bosses/BIG_WILLIG/stand_cast/cast2.png").convert_alpha()
            
            # Scale frames to boss size (20% bigger)
            boss_size = 120  # 20% bigger than original 100
            cast1 = pygame.transform.scale(cast1, (boss_size, boss_size))
            cast2 = pygame.transform.scale(cast2, (boss_size, boss_size))
            
            self.stand_cast_frames = [cast1, cast2]
        except:
            print("Warning: Could not load BIG_WILLIG stand_cast frames")
            self.stand_cast_frames = []
    
    def _load_float_frames(self):
        """Load float animation frames"""
        try:
            float_img = pygame.image.load("assets/bosses/BIG_WILLIG/float_cast/float.png").convert_alpha()
            
            # Scale frame to boss size (20% bigger)
            boss_size = 120  # 20% bigger than original 100
            float_img = pygame.transform.scale(float_img, (boss_size, boss_size))
            
            self.float_frames = [float_img]
        except:
            print("Warning: Could not load BIG_WILLIG float frames")
            self.float_frames = []
    
    def _load_float_cast_frames(self):
        """Load float_cast animation frames"""
        try:
            float_cast_img = pygame.image.load("assets/bosses/BIG_WILLIG/float_cast/float_cast.png").convert_alpha()
            
            # Scale frame to boss size (20% bigger)
            boss_size = 120  # 20% bigger than original 100
            float_cast_img = pygame.transform.scale(float_cast_img, (boss_size, boss_size))
            
            self.float_cast_frames = [float_cast_img]
        except:
            print("Warning: Could not load BIG_WILLIG float_cast frames")
            self.float_cast_frames = []
    
    def _load_death_frames(self):
        """Load death animation frames"""
        try:
            death1 = pygame.image.load("assets/bosses/BIG_WILLIG/death/death.png").convert_alpha()
            death2 = pygame.image.load("assets/bosses/BIG_WILLIG/death/death2.png").convert_alpha()
            
            # Scale frames to boss size (20% bigger)
            boss_size = 120  # 20% bigger than original 100
            death1 = pygame.transform.scale(death1, (boss_size, boss_size))
            death2 = pygame.transform.scale(death2, (boss_size, boss_size))
            
            self.death_frames = [death1, death2]
        except:
            print("Warning: Could not load BIG_WILLIG death frames")
            self.death_frames = []
    
    def _load_title_image(self):
        """Load boss title image"""
        try:
            self.title_image = pygame.image.load("assets/bosses/BIG_WILLIG/ari_title.png").convert_alpha()
            # Scale title to be double the size and centered
            title_width = 1200  # Double the size (600 * 2)
            title_height = 600  # Double the size (300 * 2)
            self.title_image = pygame.transform.scale(self.title_image, (title_width, title_height))
        except:
            print("Warning: Could not load BIG_WILLIG title image")
            self.title_image = None
    
    def _create_fallback_image(self, size):
        """Create fallback image if sprites can't be loaded"""
        image = pygame.Surface((size, size))
        image.fill((255, 100, 100))  # Red color for BIG_WILLIG
        return image
    
    def trigger_intro(self):
        """Trigger the cinematic introduction"""
        if self.intro_state == "waiting":
            self.intro_state = "health_bar"
            self.intro_timer = 0
    
    def update_intro(self):
        """Update the cinematic introduction sequence"""
        if self.intro_state == "waiting":
            return False  # Player can still move
        
        self.intro_timer += 1
        
        if self.intro_state == "health_bar":
            # Show health bar for a moment
            if self.intro_timer >= 30:  # 0.5 seconds
                self.intro_state = "boss_appear"
                self.intro_timer = 0
        
        elif self.intro_state == "boss_appear":
            # Boss appears and starts standing animation
            if self.intro_timer >= 60:  # 1 second
                self.intro_state = "title_show"
                self.intro_timer = 0
                self.title_timer = 0
        
        elif self.intro_state == "title_show":
            # Show title for 3 seconds
            self.title_timer += 1
            if self.title_timer >= self.title_duration:
                self.intro_state = "title_hide"
                self.intro_timer = 0
        
        elif self.intro_state == "title_hide":
            # Hide title and start falling
            if self.intro_timer >= 30:  # 0.5 seconds
                self.intro_state = "falling"
                self.intro_timer = 0
        
        elif self.intro_state == "falling":
            # Boss falls using player gravity system - no manual movement needed
            # The world will handle gravity and collision
            pass
        
        # Animate based on state
        if self.intro_state in ["boss_appear", "title_show", "title_hide", "falling"]:
            self._animate_stand()
        elif self.intro_state == "fighting":
            if self.attack_state in ["idle", "moving_left", "moving_right", "returning", "next_attack", "moving_center", "floating_up", "floating_down"]:
                self._animate_stand()
            elif self.attack_state in ["casting_left", "shooting_left", "casting_right", "shooting_right"]:
                self._animate_stand_cast()
            elif self.attack_state in ["float_casting", "float_rain"]:
                self._animate_float_cast()
            elif self.attack_state == "floating_up":
                self._animate_float()
            elif self.attack_state == "floating_down":
                self._animate_float()
            elif self.attack_state == "vulnerable":
                self._animate_death()
        
        # Player cannot move during intro until title disappears
        return self.intro_state in ["waiting", "health_bar", "boss_appear", "title_show", "title_hide", "falling"]
    
    def _animate_stand(self):
        """Animate the stand frames"""
        if not self.stand_frames:
            return
        
        self.animation_timer += self.animation_speed
        if self.animation_timer >= len(self.stand_frames):
            self.animation_timer = 0
        
        self.image = self.stand_frames[int(self.animation_timer)]
    
    def _animate_stand_cast(self):
        """Animate the stand_cast frames"""
        if not self.stand_cast_frames:
            return
        
        # Use cast2 for casting, cast1 for shooting
        if "casting" in self.attack_state:
            self.image = self.stand_cast_frames[1]  # cast2
        else:  # shooting
            self.image = self.stand_cast_frames[0]  # cast1
    
    def _animate_float(self):
        """Animate the float frames"""
        if not self.float_frames:
            return
        
        self.image = self.float_frames[0]  # float.png
    
    def _animate_float_cast(self):
        """Animate the float_cast frames"""
        if not self.float_cast_frames:
            return
        
        self.image = self.float_cast_frames[0]  # float_cast.png
    
    def _animate_death(self):
        """Animate the death frames"""
        if not self.death_frames:
            print("Warning: No death frames loaded")
            return
        
        # Alternate between death frames
        self.animation_timer += self.animation_speed
        if self.animation_timer >= len(self.death_frames):
            self.animation_timer = 0
        
        self.image = self.death_frames[int(self.animation_timer)]
    
    def is_intro_complete(self):
        """Check if the introduction is complete"""
        return self.intro_state == "fighting"
    
    def take_damage(self):
        """Boss takes damage from sword"""
        if self.alive and self.is_intro_complete():
            self.health -= 1
            print(f"BIG_WILLIG health: {self.health}")
            
            if self.health <= 0:
                self.alive = False
                self.kill()
                return "defeated"
        return None
    
    def draw_health_bar(self, screen):
        """Draw the boss health bar"""
        if self.intro_state in ["health_bar", "boss_appear", "title_show", "title_hide", "falling", "fighting"]:
            # Draw health bar background (upper right, dark red)
            pygame.draw.rect(screen, self.health_bar_bg_color, self.health_bar_rect)
            
            # Draw health bar (decreases as health goes down)
            health_width = int((self.health / self.max_health) * self.health_bar_rect.width)
            health_rect = pygame.Rect(self.health_bar_rect.x, self.health_bar_rect.y, health_width, self.health_bar_rect.height)
            pygame.draw.rect(screen, self.health_bar_color, health_rect)
            
            # No health text - just the bar
    
    def draw_title(self, screen):
        """Draw the boss title (only during title_show state)"""
        if self.intro_state == "title_show" and self.title_image:
            # Center the title on screen
            screen_width, screen_height = screen.get_size()
            title_rect = self.title_image.get_rect()
            title_rect.center = (screen_width // 2, screen_height // 2)
            screen.blit(self.title_image, title_rect)
    
    def update(self, x_shift, tiles=None):
        """Update boss"""
        if not self.alive:
            return
        
        # Update introduction sequence
        self.update_intro()
        
        # Apply world shift
        self.rect.x += x_shift
        
        # Add collision physics with tiles if provided (only after falling)
        if tiles and self.intro_state in ["falling", "fighting"]:
            self._handle_vertical_collision(tiles)
            self._handle_horizontal_collision(tiles)
        
        # Update attack system if in fighting state
        if self.intro_state == "fighting":
            self._update_attack()
        
        # Update fireballs
        self.fireballs.update()
    
    def _handle_vertical_collision(self, tiles):
        """Handle vertical collision with tiles (exactly like player)"""
        for sprite in tiles.sprites():
            if sprite.rect.colliderect(self.rect):
                # Handle vertical collision (exactly like player)
                if self.direction.y > 0:  # Falling down
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                    # Transition to fighting state when landing
                    if self.intro_state == "falling":
                        self.intro_state = "fighting"
                        self.intro_timer = 0
                elif self.direction.y < 0:  # Moving up
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0
                    self.on_ceiling = True
    
    def _handle_horizontal_collision(self, tiles):
        """Handle horizontal collision with tiles (exactly like player)"""
        for sprite in tiles.sprites():
            if sprite.rect.colliderect(self.rect):
                # Handle horizontal collision (exactly like player)
                if self.rect.centerx < sprite.rect.centerx:
                    # Boss is to the left of tile, push left
                    self.rect.right = sprite.rect.left
                elif self.rect.centerx > sprite.rect.centerx:
                    # Boss is to the right of tile, push right
                    self.rect.left = sprite.rect.right
    
    def _update_attack(self):
        """Update attack system"""
        self.attack_timer += 1
        
        # Debug: Print attack state every 60 frames (1 second)
        if self.attack_timer % 60 == 0:
            print(f"BIG_WILLIG attack state: {self.attack_state}, timer: {self.attack_timer}")
        
        if self.attack_state == "idle":
            # Start attack after delay
            if self.attack_timer >= self.attack_delay:
                self.attack_state = "moving_left"
                self.attack_timer = 0
        
        elif self.attack_state == "moving_left":
            # Move left using physics (set direction, let world handle movement)
            self.direction.x = -self.move_speed
            if self.rect.x <= 50:  # Hit left side
                self.attack_state = "casting_left"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
        
        elif self.attack_state == "casting_left":
            # Cast for 0.5 seconds (30 frames)
            if self.attack_timer >= 30:
                self.attack_state = "shooting_left"
                self.attack_timer = 0
                self.fireball_count = 0
                self.fireball_timer = 0
        
        elif self.attack_state == "shooting_left":
            # Shoot three fireballs to the right with 1-second delay between each
            self.fireball_timer += 1
            
            if self.fireball_timer >= self.fireball_delay and self.fireball_count < 3:
                # Create fireball with downward angled trajectory (shooting right)
                from fireball import Fireball
                fireball = Fireball((self.rect.right, self.rect.centery), 1, 0.3)  # Moving right and down
                self.fireballs.add(fireball)
                self.fireball_count += 1
                self.fireball_timer = 0
            
            # Wait for all fireballs to disappear
            if self.fireball_count >= 3 and len(self.fireballs) == 0:
                self.attack_state = "returning"
                self.attack_timer = 0
        
        elif self.attack_state == "returning":
            # Return to original position using physics
            if self.rect.x < self.original_x:
                self.direction.x = self.move_speed
            else:
                self.rect.x = self.original_x
                self.direction.x = 0  # Stop moving
                self.attack_state = "moving_right"
                self.attack_timer = 0
        
        elif self.attack_state == "moving_right":
            # Move right using physics
            self.direction.x = self.move_speed
            if self.rect.x >= 750:  # Hit right side
                self.attack_state = "casting_right"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
        
        elif self.attack_state == "casting_right":
            # Cast for 0.5 seconds (30 frames)
            if self.attack_timer >= 30:
                self.attack_state = "shooting_right"
                self.attack_timer = 0
                self.fireball_count = 0
                self.fireball_timer = 0
        
        elif self.attack_state == "shooting_right":
            # Shoot three fireballs to the left with 1-second delay between each
            self.fireball_timer += 1
            
            if self.fireball_timer >= self.fireball_delay and self.fireball_count < 3:
                # Create fireball with downward angled trajectory (shooting left)
                from fireball import Fireball
                fireball = Fireball((self.rect.left, self.rect.centery), -1, 0.3)  # Moving left and down
                self.fireballs.add(fireball)
                self.fireball_count += 1
                self.fireball_timer = 0
            
            # Wait for all fireballs to disappear
            if self.fireball_count >= 3 and len(self.fireballs) == 0:
                self.attack_state = "next_attack"
                self.attack_timer = 0
        
        elif self.attack_state == "next_attack":
            # Move to center of arena
            center_x = 400  # Center of screen
            if self.rect.x < center_x:
                self.direction.x = self.move_speed
            elif self.rect.x > center_x:
                self.direction.x = -self.move_speed
            else:
                self.rect.x = center_x
                self.direction.x = 0  # Stop moving
                self.attack_state = "floating_up"
                self.attack_timer = 0
        
        elif self.attack_state == "floating_up":
            # Float up to top of screen
            self.direction.y = -2  # Float up
            if self.rect.y <= 50:  # Near top of screen
                self.attack_state = "float_casting"
                self.attack_timer = 0
                self.direction.y = 0  # Stop floating
        
        elif self.attack_state == "float_casting":
            # Cast for 0.5 seconds (30 frames)
            if self.attack_timer >= 30:
                self.attack_state = "float_rain"
                self.attack_timer = 0
                self.fireball_count = 0
                self.fireball_timer = 0
        
        elif self.attack_state == "float_rain":
            # Keep BIG_WILLIG at the top during rain
            self.rect.y = 50  # Stay at top
            self.direction.y = 0  # Stop vertical movement
            
            # Create fireball rain for 5 seconds (300 frames)
            self.fireball_timer += 1
            
            # Create scattered fireballs every 8 frames for more coverage
            if self.fireball_timer >= 8 and self.attack_timer < 300:
                from fireball import Fireball
                # Create scattered fireballs from top of screen
                for i in range(5):  # 5 fireballs per wave for better coverage
                    x_offset = (i - 2) * 80  # Spread them out more
                    fireball_x = self.rect.centerx + x_offset
                    fireball_y = 0  # Start from very top of screen
                    # Random direction for scattered effect
                    direction_x = 0.2 if i % 2 == 0 else -0.2
                    fireball = Fireball((fireball_x, fireball_y), direction_x, 0.5, "rain")  # Slow falling rain
                    self.fireballs.add(fireball)
                self.fireball_timer = 0
            
            # After 5 seconds, wait for all fireballs to fall before floating down
            if self.attack_timer >= 300:
                # Only float down when all rain fireballs are gone
                if len(self.fireballs) == 0:
                    print("BIG_WILLIG transitioning to floating_down state")
                    self.attack_state = "floating_down"
                    self.attack_timer = 0
        
        elif self.attack_state == "floating_down":
            # Float back down to original platform height
            self.rect.y += 2  # Float down directly
            if self.rect.y >= self.original_y:  # Back to original height
                self.rect.y = self.original_y
                self.direction.y = 0  # Stop floating
                # Wait a few frames to ensure boss has actually landed
                if self.attack_timer >= 5:  # Wait 5 frames after reaching height
                    print("BIG_WILLIG transitioning to vulnerable state")
                    self.attack_state = "vulnerable"
                    self.attack_timer = 0
                else:
                    self.attack_timer += 1
        
        elif self.attack_state == "vulnerable":
            # Vulnerable state - stand still for 3 seconds (180 frames)
            self.direction.x = 0  # Stop moving
            self.direction.y = 0  # Stop floating
            if self.attack_timer == 0:
                print("BIG_WILLIG is now vulnerable!")
            if self.attack_timer >= 180:  # 3 seconds
                # Restart the attack pattern
                print("BIG_WILLIG restarting attack pattern!")
                self.attack_state = "moving_left"
                self.attack_timer = 0
                self.fireball_count = 0
                self.fireball_timer = 0
