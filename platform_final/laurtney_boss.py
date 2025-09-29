import pygame
import math
from settings import WIDTH, HEIGHT

class LaurtneyBoss(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        
        print("LAURTNEY: Initializing LaurtneyBoss")
        
        # Dual boss properties - separate health for each character
        self.max_health = 8  # Each character has 8 health
        self.l_health = self.max_health  # L character health
        self.c_health = self.max_health  # C character health
        self.alive = True
        
        # Character positions - L on left platform, C on right platform
        # Start above screen for falling animation
        self.l_rect = pygame.Rect(50, -300, size, size)  # Left platform, start above screen
        self.c_rect = pygame.Rect(850, -300, size, size)  # Right platform, start above screen (slightly to the right)
        print(f"LAURTNEY: Initial positions - L at ({self.l_rect.x}, {self.l_rect.y}), C at ({self.c_rect.x}, {self.c_rect.y})")
        
        # Character directions and physics
        self.l_direction = pygame.math.Vector2(0, 0)
        self.c_direction = pygame.math.Vector2(0, 0)
        self.gravity = 0.7
        
        # Animation properties
        self.animation_index = 0
        self.animation_speed = 0.1
        self.facing_right = True
        
        # Load animations
        self._load_animations()
        
        # Set initial image
        self.image = self.l_stand_frames[0]
        self.mask = pygame.mask.from_surface(self.image)
        
        # Set initial animation frames
        self.l_current_frame = self.l_stand_frames[0]
        self.c_current_frame = self.c_stand_frames[0]
        
        # Intro sequence states
        self.intro_state = "waiting"  # waiting, health_bars, boss_appear, title_show, title_hide, falling, fighting
        self.intro_timer = 0
        self.title_duration = 300  # 5 seconds
        
        # Attack pattern states
        self.attack_state = "idle"  # idle, jumping_down_to_ground
        self.l_attack_state = "waiting"  # waiting, throwing, cooldown
        self.c_attack_state = "waiting"  # waiting, punching, returning, cooldown
        
        # Attack timers
        self.l_attack_timer = 0
        self.l_attack_delay = 60  # 1 second between attacks
        self.c_attack_timer = 0
        self.c_attack_delay = 90  # 1.5 seconds between attacks
        self.c_original_x = 0  # Store original position for return
        
        # Shuriken projectiles
        self.shurikens = pygame.sprite.Group()
        self.shuriken_timer = 0
        
        # Debug timer
        self.debug_timer = 0
        
        print("LAURTNEY: Successfully loaded all animations")
    
    def _load_animations(self):
        """Load all animation frames"""
        try:
            # Load L character stand animation (l_face_right.png)
            l_stand_img = pygame.image.load("assets/bosses/LAURTNEY/l_stand/l_face_right.png").convert_alpha()
            self.l_stand_frames = [l_stand_img]
            
            # Load C character stand animation (c_face_left.png)
            c_stand_img = pygame.image.load("assets/bosses/LAURTNEY/c_stand/c_face_left.png").convert_alpha()
            self.c_stand_frames = [c_stand_img]
            
            # Load L character attack animations
            l_throw1_img = pygame.image.load("assets/bosses/LAURTNEY/l_attack_right/l_throw_right.png").convert_alpha()
            l_throw2_img = pygame.image.load("assets/bosses/LAURTNEY/l_attack_right/l_throw_right2.png").convert_alpha()
            self.l_throw_frames = [l_throw1_img, l_throw2_img]
            
            # Load C character attack animations
            c_attack_img = pygame.image.load("assets/bosses/LAURTNEY/c_attack_left/c_attack_left.png").convert_alpha()
            self.c_attack_frames = [c_attack_img]
            
            # Load title image
            self.title_image = pygame.image.load("assets/bosses/LAURTNEY/laurtney_title.png").convert_alpha()
            # Scale title to be bigger
            self.title_image = pygame.transform.scale(self.title_image, (600, 300))
            
            print("LAURTNEY: Successfully loaded all animations")
        except Exception as e:
            print(f"LAURTNEY: Error loading animations: {e}")
            # Fallback images
            self.l_stand_frames = [pygame.Surface((size, size))]
            self.c_stand_frames = [pygame.Surface((size, size))]
            self.l_throw_frames = [pygame.Surface((size, size))]
            self.c_attack_frames = [pygame.Surface((size, size))]
            self.l_stand_frames[0].fill((100, 100, 100))  # Gray fallback
            self.c_stand_frames[0].fill((150, 150, 150))  # Light gray fallback
            self.l_throw_frames[0].fill((200, 100, 100))  # Red fallback
            self.c_attack_frames[0].fill((100, 200, 100))  # Green fallback
            self.title_image = pygame.Surface((600, 300))
            self.title_image.fill((200, 200, 200))  # Light gray fallback
    
    def trigger_intro(self):
        """Start the introduction sequence"""
        self.intro_state = "health_bars"
        self.intro_timer = 0
        print("LAURTNEY: Starting introduction sequence")
    
    def update_intro(self):
        """Update introduction sequence - returns True if player should be frozen"""
        if self.intro_state == "waiting":
            return False  # Player can move
        
        self.intro_timer += 1
        
        if self.intro_state == "health_bars":
            if self.intro_timer >= 60:  # 1 second
                self.intro_state = "boss_appear"
                self.intro_timer = 0
                print("LAURTNEY: Health bars appeared")
        
        elif self.intro_state == "boss_appear":
            if self.intro_timer >= 60:  # 1 second
                self.intro_state = "title_show"
                self.intro_timer = 0
                print("LAURTNEY: Bosses appeared")
        
        elif self.intro_state == "title_show":
            if self.intro_timer >= self.title_duration:  # 5 seconds
                self.intro_state = "title_hide"
                self.intro_timer = 0
                print("LAURTNEY: Title card hidden, starting fall")
            else:
                # Debug output every 60 frames (1 second)
                if self.intro_timer % 60 == 0:
                    print(f"LAURTNEY: Title showing - timer: {self.intro_timer}/{self.title_duration}")
        
        elif self.intro_state == "title_hide":
            if self.intro_timer >= 60:  # 1 second
                self.intro_state = "falling"
                self.intro_timer = 0
                print("LAURTNEY: Title card hidden, starting fall")
        
        elif self.intro_state == "falling":
            # Gravity is applied by world.py, just check for landing
            # Check if both characters have landed on platforms
            if self.l_rect.y >= 230 and self.c_rect.y >= 230:  # Platform height
                self.l_rect.y = 230
                self.c_rect.y = 230
                self.l_direction.y = 0
                self.c_direction.y = 0
                self.intro_state = "fighting"
                self.attack_state = "jumping_down_to_ground"
                self.intro_timer = 0
                print("LAURTNEY: Both characters landed, starting first attack pattern!")
            else:
                # Still falling, print debug info
                print(f"LAURTNEY falling: L at ({self.l_rect.x}, {self.l_rect.y}), C at ({self.c_rect.x}, {self.c_rect.y})")
        
        # Only freeze player during intro, not during fighting
        if self.intro_state == "fighting":
            return False  # Player can move during fighting
        return True  # Player is frozen during intro
    
    def update_attack_pattern(self):
        """Update attack patterns"""
        if self.attack_state == "jumping_down_to_ground":
            # Two-phase jump: up first, then down
            if not hasattr(self, 'jump_phase'):
                self.jump_phase = "up"
                self.jump_timer = 0
            
            self.jump_timer += 1
            
            if self.jump_phase == "up":
                # First phase: jump up and out
                self.l_direction.x = 1  # Move right slightly
                self.l_direction.y = -2  # Jump up
                self.c_direction.x = -1  # Move left slightly
                self.c_direction.y = -2  # Jump up
                
                # Apply movement
                self.l_rect.x += self.l_direction.x
                self.l_rect.y += self.l_direction.y
                self.c_rect.x += self.c_direction.x
                self.c_rect.y += self.c_direction.y
                
                # Switch to down phase after 30 frames (0.5 seconds)
                if self.jump_timer >= 30:
                    self.jump_phase = "down"
                    self.jump_timer = 0
                    print("LAURTNEY: Switching to down phase")
            
            elif self.jump_phase == "down":
                # Second phase: fall down
                self.l_direction.x = 1  # Continue moving right
                self.l_direction.y = 2  # Fall down
                self.c_direction.x = -1  # Continue moving left
                self.c_direction.y = 2  # Fall down
                
                # Apply movement
                self.l_rect.x += self.l_direction.x
                self.l_rect.y += self.l_direction.y
                self.c_rect.x += self.c_direction.x
                self.c_rect.y += self.c_direction.y
                
                # Check if they've reached ground level
                if self.l_rect.y >= 350 and self.c_rect.y >= 350:  # Ground level
                    self.l_rect.y = 350
                    self.c_rect.y = 350
                    self.l_direction.x = 0
                    self.l_direction.y = 0
                    self.c_direction.x = 0
                    self.c_direction.y = 0
                    self.attack_state = "idle"
                    # Clean up jump variables
                    if hasattr(self, 'jump_phase'):
                        delattr(self, 'jump_phase')
                    if hasattr(self, 'jump_timer'):
                        delattr(self, 'jump_timer')
                    print("LAURTNEY: Both characters landed on ground, starting attack loop!")
        
        elif self.attack_state == "idle":
            # Ensure both characters stay at ground level
            self.l_rect.y = 350
            self.c_rect.y = 350
            
            # Handle L character attack loop - only if L is alive
            if self.l_health > 0:
                self.l_attack_timer += 1
                
                if self.l_attack_state == "waiting":
                    # Wait 1 second before attacking
                    if self.l_attack_timer >= self.l_attack_delay:
                        self.l_attack_state = "throwing"
                        self.l_attack_timer = 0
                        self._animate_l_attack_right()
                        print("LAURTNEY: L character starting throw animation")
                
                elif self.l_attack_state == "throwing":
                    # First throw frame
                    if self.l_attack_timer == 30:  # 0.5 seconds
                        self._animate_l_throw_right()
                        print("LAURTNEY: L character throw frame 1")
                    # Create shuriken
                    elif self.l_attack_timer == 60:  # 1 second
                        self._create_shuriken()
                        self._animate_l_throw_right2()
                        print("LAURTNEY: L character throw frame 2 and shuriken created")
                    # Complete throw
                    elif self.l_attack_timer >= 90:  # 1.5 seconds
                        self.l_attack_state = "cooldown"
                        self.l_attack_timer = 0
                        self._animate_l_stand()
                        print("LAURTNEY: L character throw complete, starting cooldown")
                
                elif self.l_attack_state == "cooldown":
                    # Wait 1 second before next attack
                    if self.l_attack_timer >= 60:  # 1 second
                        self.l_attack_state = "waiting"
                        self.l_attack_timer = 0
                        print("LAURTNEY: L character cooldown complete, ready for next attack")
            
            # Handle C character attack loop - only if C is alive
            if self.c_health > 0:
                self.c_attack_timer += 1
                
                if self.c_attack_state == "waiting":
                    # Wait 1.5 seconds before attacking
                    if self.c_attack_timer >= self.c_attack_delay:
                        self.c_attack_state = "punching"
                        self.c_attack_timer = 0
                        self.c_original_x = self.c_rect.x  # Store original position
                        self._animate_c_attack_left()
                        print("LAURTNEY: C character starting punch attack")
                
                elif self.c_attack_state == "punching":
                    # Move left significantly during punch
                    if self.c_attack_timer < 15:  # First 0.25 seconds - move left
                        self.c_rect.x -= 6  # Move left (3x more)
                    elif self.c_attack_timer < 30:  # Next 0.25 seconds - move back
                        self.c_rect.x += 6  # Move back to original position (3x more)
                    elif self.c_attack_timer >= 30:  # After 0.5 seconds total
                        # Return to original position and switch to returning state
                        self.c_rect.x = self.c_original_x
                        self.c_attack_state = "returning"
                        self.c_attack_timer = 0
                        self._animate_c_stand()
                        print("LAURTNEY: C character punch complete, returning to position")
                
                elif self.c_attack_state == "returning":
                    # Stand for 1 second after punch
                    if self.c_attack_timer >= 60:  # 1 second standing
                        self.c_attack_state = "cooldown"
                        self.c_attack_timer = 0
                        print("LAURTNEY: C character standing complete, starting cooldown")
            
                elif self.c_attack_state == "cooldown":
                    # Wait 1.5 seconds before next attack
                    if self.c_attack_timer >= self.c_attack_delay:
                        self.c_attack_state = "waiting"
                        self.c_attack_timer = 0
                        print("LAURTNEY: C character cooldown complete, ready for next attack")
    
    def _create_shuriken(self):
        """Create a shuriken projectile"""
        from shuriken import Shuriken
        shuriken = Shuriken((self.l_rect.centerx, self.l_rect.centery - 20))
        self.shurikens.add(shuriken)
        print(f"LAURTNEY: L character threw shuriken {len(self.shurikens)} at position ({shuriken.rect.x}, {shuriken.rect.y})")
    
    def _animate_l_stand(self):
        """Animate L character standing"""
        self.l_current_frame = self.l_stand_frames[0]
    
    def _animate_c_stand(self):
        """Animate C character standing"""
        self.c_current_frame = self.c_stand_frames[0]
    
    def _animate_l_attack_right(self):
        """Animate L character attacking right"""
        self.l_current_frame = self.l_throw_frames[0]
    
    def _animate_l_throw_right(self):
        """Animate L character throwing right"""
        self.l_current_frame = self.l_throw_frames[0]
    
    def _animate_l_throw_right2(self):
        """Animate L character throwing right frame 2"""
        self.l_current_frame = self.l_throw_frames[1]
    
    def _animate_c_attack_left(self):
        """Animate C character attacking left"""
        self.c_current_frame = self.c_attack_frames[0]
    
    def update(self, x_shift, tiles=None):
        """Update boss"""
        # Update intro sequence
        self.update_intro()
        
        # Update attack patterns
        if self.intro_state == "fighting":
            self.update_attack_pattern()
        
        # Update shurikens
        self.shurikens.update()
        
        # Remove shurikens that are off screen
        for shuriken in self.shurikens.sprites():
            if shuriken.rect.x > WIDTH + 100:
                shuriken.kill()
    
    def draw(self, screen):
        """Draw both characters and title"""
        # Draw L character if alive
        if self.l_health > 0:
            screen.blit(self.l_current_frame, self.l_rect)
        
        # Draw C character if alive
        if self.c_health > 0:
            screen.blit(self.c_current_frame, self.c_rect)
        
        # Draw title if showing
        if self.intro_state == "title_show":
            self.draw_title(screen)
        
        # Draw shurikens
        self.shurikens.draw(screen)
        
        # Debug rectangles removed for clean gameplay
    
    def draw_title(self, screen):
        """Draw title card"""
        if self.title_image:
            title_rect = self.title_image.get_rect()
            title_rect.centerx = WIDTH // 2
            title_rect.centery = HEIGHT // 2 - 100
            screen.blit(self.title_image, title_rect)
    
    def draw_health_bar(self, screen):
        """Draw health bars for both characters"""
        if self.l_health > 0:
            # L character health bar
            health_width = 200
            health_height = 20
            health_x = WIDTH - 220
            health_y = 20
            
            # Background (red)
            pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_height))
            
            # Health (green)
            health_ratio = self.l_health / self.max_health
            health_fill = int(health_ratio * health_width)
            pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, health_fill, health_height))
            
            # Border
            pygame.draw.rect(screen, (255, 255, 255), (health_x, health_y, health_width, health_height), 2)
        
        if self.c_health > 0:
            # C character health bar (below L)
            health_width = 200
            health_height = 20
            health_x = WIDTH - 220
            health_y = 50  # Below L character health bar
            
            # Background (red)
            pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_height))
            
            # Health (green)
            health_ratio = self.c_health / self.max_health
            health_fill = int(health_ratio * health_width)
            pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, health_fill, health_height))
            
            # Border
            pygame.draw.rect(screen, (255, 255, 255), (health_x, health_y, health_width, health_height), 2)
    
    def take_damage(self, character="L"):
        """Take damage and return defeat status"""
        if character == "L":
            self.l_health -= 1
            print(f"LAURTNEY: L character health reduced to {self.l_health}/{self.max_health}")
            if self.l_health <= 0:
                print("LAURTNEY: L character defeated!")
                # Check if both characters are defeated
                if self.c_health <= 0:
                    print("LAURTNEY: Both characters defeated! Boss fight complete!")
                    self.alive = False
                    return "defeated"
                return "l_defeated"
        elif character == "C":
            self.c_health -= 1
            print(f"LAURTNEY: C character health reduced to {self.c_health}/{self.max_health}")
            if self.c_health <= 0:
                print("LAURTNEY: C character defeated!")
                # Check if both characters are defeated
                if self.l_health <= 0:
                    print("LAURTNEY: Both characters defeated! Boss fight complete!")
                    self.alive = False
                    return "defeated"
                return "c_defeated"
        else:
            # Default to L character if no character specified
            self.l_health -= 1
            print(f"LAURTNEY: L character health reduced to {self.l_health}/{self.max_health}")
            if self.l_health <= 0:
                print("LAURTNEY: L character defeated!")
                # Check if both characters are defeated
                if self.c_health <= 0:
                    print("LAURTNEY: Both characters defeated! Boss fight complete!")
                    self.alive = False
                    return "defeated"
                return "l_defeated"
        
        return "damaged"
    
    def _handle_vertical_collision_dual(self, tiles):
        """Handle vertical collision for both characters"""
        # Only apply collision detection when characters are actually moving
        # L character collision
        for tile in tiles:
            if self.l_rect.colliderect(tile.rect) and self.l_direction.y != 0:
                if self.l_direction.y > 0:  # Falling down
                    self.l_rect.bottom = tile.rect.top
                    self.l_direction.y = 0
                elif self.l_direction.y < 0:  # Moving up
                    self.l_rect.top = tile.rect.bottom
                    self.l_direction.y = 0
        
        # C character collision
        for tile in tiles:
            if self.c_rect.colliderect(tile.rect) and self.c_direction.y != 0:
                if self.c_direction.y > 0:  # Falling down
                    self.c_rect.bottom = tile.rect.top
                    self.c_direction.y = 0
                elif self.c_direction.y < 0:  # Moving up
                    self.c_rect.top = tile.rect.bottom
                    self.c_direction.y = 0
    
    def _handle_horizontal_collision_dual(self, tiles):
        """Handle horizontal collision for both characters"""
        # L character collision
        for tile in tiles:
            if self.l_rect.colliderect(tile.rect):
                if self.l_direction.x > 0:  # Moving right
                    self.l_rect.right = tile.rect.left
                elif self.l_direction.x < 0:  # Moving left
                    self.l_rect.left = tile.rect.right
        
        # C character collision
        for tile in tiles:
            if self.c_rect.colliderect(tile.rect):
                if self.c_direction.x > 0:  # Moving right
                    self.c_rect.right = tile.rect.left
                elif self.c_direction.x < 0:  # Moving left
                    self.c_rect.left = tile.rect.right
