import pygame
import math
from settings import WIDTH, HEIGHT

class DreadKnightBoss(pygame.sprite.Sprite):
    def __init__(self, pos, scale=200):
        super().__init__()
        self.scale = scale
        self.rect = pygame.Rect(pos[0], pos[1], 80, 120)  # Standard boss size
        self.alive = True
        self.health = 100
        self.max_health = 100
        
        # Animation system
        self.animation_speed = 0.1
        self.current_frame = 0
        self.facing_right = True
        
        # Intro sequence
        self.intro_state = "waiting"  # waiting, dropping, landed, title_show, title_hide, fighting
        self.intro_timer = 0
        self.title_duration = 540  # 9 seconds at 60 FPS
        
        # Title shake effect
        self.title_shake_offset = 0
        self.title_shake_timer = 0
        self.title_shake_duration = 180  # 3 seconds of shaking
        
        # Attack sequence
        self.attack_state = "idle"  # idle, charging_right, charging_left, delay, charging_right_to_center, slash_left, slash_right, final_pause
        self.attack_timer = 0
        self.charge_speed = 8  # Movement speed during charge
        self.delay_duration = 120  # 2 seconds at 60 FPS
        self.slash_duration = 60  # 1 second for each slash
        self.final_pause_duration = 120  # 2 seconds pause before repeating
        self.attack_started = False  # Flag to ensure attack only starts once
        
        # Second phase variables
        self.second_phase = False  # Flag to indicate second phase
        self.phase2_state = "idle"  # idle, shaking, rising, flash, transformed, dropping
        self.phase2_timer = 0
        self.shake_intensity = 0
        self.rise_speed = 1  # Speed of rising (slower)
        self.flash_duration = 30  # 0.5 seconds of white flash
        self.drop_speed = 4  # Speed of dropping back down
        self.health_refilled = False  # Flag to track if health has been refilled
        
        # Second phase attack variables
        self.phase2_attack_state = "idle"  # idle, flame_slash_left, flame_slash_right, flame_pause, flame_charge_left, flame_turn_right, flame_rain, flame_charge_center
        self.phase2_attack_timer = 0
        self.flame_slash_duration = 60  # 1 second for each flame slash
        self.flame_pause_duration = 120  # 2 seconds pause between attacks
        self.flame_charge_speed = 6  # Speed of charging
        self.flame_rain_duration = 180  # 3 seconds of rain
        self.flame_rain_timer = 0
        self.flame_rain_drops = []  # List of rain drop objects
        
        # Victory sequence variables
        self.victory_state = "idle"  # idle, shaking, disappearing, victory_message, reward_showing
        self.victory_timer = 0
        self.victory_shake_duration = 120  # 2 seconds of shaking
        self.victory_message_duration = 300  # 5 seconds of message
        self.victory_shake_intensity = 0
        
        # Load animations
        self._load_animations()
        
        # Set initial image
        self.image = self.stand_frames[0]
        self.mask = pygame.mask.from_surface(self.image)
        
        print("DREAD_KNIGHT: Initializing DreadKnightBoss")
    
    def _load_animations(self):
        """Load all animation frames"""
        try:
            # Stand animation (facing right)
            self.stand_frames = []
            stand_img = pygame.image.load("assets/bosses/DREAD_KNIGHT/stand/facing_right.png").convert_alpha()
            stand_img = pygame.transform.scale(stand_img, (80, 120))
            self.stand_frames.append(stand_img)
            
            # Charge animations
            self.charge_left_frames = []
            charge_left1 = pygame.image.load("assets/bosses/DREAD_KNIGHT/charge_left/charge_left.png").convert_alpha()
            charge_left1 = pygame.transform.scale(charge_left1, (80, 120))
            self.charge_left_frames.append(charge_left1)
            
            charge_left2 = pygame.image.load("assets/bosses/DREAD_KNIGHT/charge_left/char_left2.png").convert_alpha()
            charge_left2 = pygame.transform.scale(charge_left2, (80, 120))
            self.charge_left_frames.append(charge_left2)
            
            self.charge_right_frames = []
            charge_right1 = pygame.image.load("assets/bosses/DREAD_KNIGHT/charge_right/charging_right.png").convert_alpha()
            charge_right1 = pygame.transform.scale(charge_right1, (80, 120))
            self.charge_right_frames.append(charge_right1)
            
            charge_right2 = pygame.image.load("assets/bosses/DREAD_KNIGHT/charge_right/charging_right_2.png").convert_alpha()
            charge_right2 = pygame.transform.scale(charge_right2, (80, 120))
            self.charge_right_frames.append(charge_right2)
            
            # Sword animations - wider to accommodate extended sword
            self.sword_left_frames = []
            sword_left = pygame.image.load("assets/bosses/DREAD_KNIGHT/sword_left/sword_swing_left.png").convert_alpha()
            sword_left = pygame.transform.scale(sword_left, (140, 120))  # Wider for extended sword
            self.sword_left_frames.append(sword_left)
            
            self.sword_right_frames = []
            sword_right = pygame.image.load("assets/bosses/DREAD_KNIGHT/sword_right/sword_swing_right.png").convert_alpha()
            sword_right = pygame.transform.scale(sword_right, (140, 120))  # Wider for extended sword
            self.sword_right_frames.append(sword_right)
            
            # Flame animations
            self.flame_left_frames = []
            flame_left1 = pygame.image.load("assets/bosses/DREAD_KNIGHT/flame_left/flame_left_1.png").convert_alpha()
            flame_left1 = pygame.transform.scale(flame_left1, (180, 150))  # Even wider for extended hand with flames
            self.flame_left_frames.append(flame_left1)
            
            flame_left2 = pygame.image.load("assets/bosses/DREAD_KNIGHT/flame_left/flame_left_2.png").convert_alpha()
            flame_left2 = pygame.transform.scale(flame_left2, (160, 150))  # Even wider for charging left
            self.flame_left_frames.append(flame_left2)
            
            self.flame_right_frames = []
            flame_right1 = pygame.image.load("assets/bosses/DREAD_KNIGHT/flame_right/flame_right1.png").convert_alpha()
            flame_right1 = pygame.transform.scale(flame_right1, (80, 120))  # Normal size for flame_right1
            self.flame_right_frames.append(flame_right1)
            
            flame_right2 = pygame.image.load("assets/bosses/DREAD_KNIGHT/flame_right/flame_right_2.png").convert_alpha()
            flame_right2 = pygame.transform.scale(flame_right2, (180, 150))  # Even wider for extended hand with flames
            self.flame_right_frames.append(flame_right2)
            
            # Flame rain image
            self.flame_rain_img = pygame.image.load("assets/bosses/DREAD_KNIGHT/flame_rain.png").convert_alpha()
            self.flame_rain_img = pygame.transform.scale(self.flame_rain_img, (60, 60))  # Bigger rain drops
            
            # Reward image
            self.reward_img = pygame.image.load("assets/bosses/DREAD_KNIGHT/reward.png").convert_alpha()
            self.reward_img = pygame.transform.scale(self.reward_img, (80, 80))  # Reward size
            
            # Title image
            self.title_img = pygame.image.load("assets/bosses/DREAD_KNIGHT/kev_title.png").convert_alpha()
            self.title_img = pygame.transform.scale(self.title_img, (1080, 540))  # 10% smaller
            
            print("DREAD_KNIGHT: Successfully loaded all animations")
            
        except pygame.error as e:
            print(f"DREAD_KNIGHT: Error loading animations: {e}")
            # Create fallback images
            self.stand_frames = [pygame.Surface((80, 120))]
            self.charge_left_frames = [pygame.Surface((80, 120))]
            self.charge_right_frames = [pygame.Surface((80, 120))]
            self.sword_left_frames = [pygame.Surface((140, 120))]  # Wider for sword slashes
            self.sword_right_frames = [pygame.Surface((140, 120))]  # Wider for sword slashes
            self.flame_left_frames = [pygame.Surface((180, 150)), pygame.Surface((160, 150))]  # Extended hand and charging flame
            self.flame_right_frames = [pygame.Surface((180, 150))]  # Even wider for extended hand with flames
            self.flame_rain_img = pygame.Surface((60, 60))  # Bigger rain drops fallback
            self.reward_img = pygame.Surface((80, 80))  # Reward fallback
            self.title_img = pygame.Surface((360, 180))  # 10% smaller fallback
    
    def trigger_intro(self):
        """Start the introduction sequence"""
        self.intro_state = "dropping"
        self.intro_timer = 0
        print("DREAD_KNIGHT: Starting introduction sequence")
    
    def update_intro(self):
        """Update the introduction sequence"""
        if self.intro_state == "waiting":
            # Automatically start the intro sequence
            self.intro_state = "dropping"
            self.intro_timer = 0
            print("DREAD_KNIGHT: Auto-starting intro sequence from waiting state")
        
        elif self.intro_state == "dropping":
            self.intro_timer += 1
            # Drop down from above
            self.rect.y += 8  # Drop speed
            
            # Check if landed (at ground level)
            if self.rect.y >= 350:  # Ground level (same as player)
                self.rect.y = 350
                self.intro_state = "landed"
                self.intro_timer = 0
                print("DREAD_KNIGHT: Landed on ground level!")
        
        elif self.intro_state == "landed":
            self.intro_timer += 1
            # Wait 1 second (60 frames) before showing title
            if self.intro_timer >= 60:
                self.intro_state = "title_show"
                self.intro_timer = 0
                self.title_shake_timer = 0
                print("DREAD_KNIGHT: Title card shown!")
        
        elif self.intro_state == "title_show":
            self.intro_timer += 1
            self.title_shake_timer += 1
            
            # Handle title shake
            if self.title_shake_timer < self.title_shake_duration:
                # Shake effect
                self.title_shake_offset = math.sin(self.title_shake_timer * 0.3) * 5
            
            # Show title for 5 seconds
            if self.intro_timer >= self.title_duration:
                self.intro_state = "title_hide"
                self.intro_timer = 0
                print("DREAD_KNIGHT: Title card hidden!")
        
        elif self.intro_state == "title_hide":
            self.intro_timer += 1
            # Brief pause before fighting
            if self.intro_timer >= 30:  # 0.5 seconds
                self.intro_state = "fighting"
                self.intro_timer = 0
                print("DREAD_KNIGHT: Starting fight!")
        
        elif self.intro_state == "fighting":
            # Intro complete, start fighting
            if not self.attack_started and self.attack_state == "idle":
                self.attack_state = "charging_right"  # Start first attack
                self.attack_timer = 0
                self.attack_started = True
                print("DREAD_KNIGHT: Starting charging_right attack!")
        
        # Always allow player movement during intro sequence
        return False
    
    def update_attack(self):
        """Update attack sequence"""
        if self.attack_state == "charging_right":
            self.attack_timer += 1
            
            # Move right across screen
            self.rect.x += self.charge_speed
            
            # Check if hit right wall (screen width - boss width)
            if self.rect.x >= WIDTH - self.rect.width:
                self.rect.x = WIDTH - self.rect.width  # Clamp to wall
                self.attack_state = "delay"
                self.attack_timer = 0
                print("DREAD_KNIGHT: Hit right wall, starting 2-second delay!")
        
        elif self.attack_state == "delay":
            self.attack_timer += 1
            
            # Wait for delay duration
            if self.attack_timer >= self.delay_duration:
                self.attack_state = "charging_left"
                self.attack_timer = 0
                print("DREAD_KNIGHT: Starting charging_left attack!")
        
        elif self.attack_state == "charging_left":
            self.attack_timer += 1
            
            # Move left across screen
            self.rect.x -= self.charge_speed
            
            # Check if hit left wall
            if self.rect.x <= 0:
                self.rect.x = 0  # Clamp to wall
                self.attack_state = "charging_right_to_center"
                self.attack_timer = 0
                print("DREAD_KNIGHT: Hit left wall, charging back to center!")
        
        elif self.attack_state == "charging_right_to_center":
            self.attack_timer += 1
            
            # Center is the true middle of the screen (screen width is 1000)
            center_x = 500  # True center of the screen
            
            # Move right towards center, but don't overshoot
            if self.rect.x < center_x:
                # Move towards center
                self.rect.x += self.charge_speed
                # Don't go past center
                if self.rect.x > center_x:
                    self.rect.x = center_x
            
            # Check if reached center
            if self.rect.x >= center_x:
                self.rect.x = center_x  # Stop at center
                self.attack_state = "slash_left"
                self.attack_timer = 0
                print(f"DREAD_KNIGHT: Reached center at x={center_x}, starting left slash!")
        
        elif self.attack_state == "slash_left":
            self.attack_timer += 1
            
            # Slash left for 1 second
            if self.attack_timer >= self.slash_duration:
                self.attack_state = "slash_right"
                self.attack_timer = 0
                print("DREAD_KNIGHT: Left slash complete, starting right slash!")
        
        elif self.attack_state == "slash_right":
            self.attack_timer += 1
            
            # Slash right for 1 second
            if self.attack_timer >= self.slash_duration:
                self.attack_state = "final_pause"
                self.attack_timer = 0
                print("DREAD_KNIGHT: Right slash complete, starting final pause!")
        
        elif self.attack_state == "final_pause":
            self.attack_timer += 1
            
            # Pause for 2 seconds before repeating
            if self.attack_timer >= self.final_pause_duration:
                self.attack_state = "charging_right"
                self.attack_timer = 0
                print("DREAD_KNIGHT: Final pause complete, repeating attack cycle!")
    
    def update_phase2(self):
        """Update second phase sequence"""
        if self.phase2_state == "shaking":
            self.phase2_timer += 1
            self.shake_intensity += 0.2
            
            # Shake for 2 seconds (120 frames)
            if self.phase2_timer >= 120:
                self.phase2_state = "rising"
                self.phase2_timer = 0
                print("DREAD_KNIGHT: Shaking complete, starting to rise!")
        
        elif self.phase2_state == "rising":
            self.phase2_timer += 1
            
            # Center horizontally and rise slowly to center of screen (y=200)
            self.rect.x = 400  # Center of arena (WIDTH/2 - boss_width/2)
            if self.rect.y > 200:
                self.rect.y -= self.rise_speed
            else:
                self.rect.y = 200  # Center of screen
                self.phase2_state = "flash"
                self.phase2_timer = 0
                print("DREAD_KNIGHT: Reached center, starting flash!")
        
        elif self.phase2_state == "flash":
            self.phase2_timer += 1
            
            # Stay centered during flash
            self.rect.x = 400  # Center of arena
            # Flash for 0.5 seconds
            if self.phase2_timer >= self.flash_duration:
                self.phase2_state = "transformed"
                self.phase2_timer = 0
                # Refill health and mark as refilled
                self.health = 100
                self.health_refilled = True
                print("DREAD_KNIGHT: Flash complete, transformed! Health refilled!")
        
        elif self.phase2_state == "transformed":
            self.phase2_timer += 1
            
            # Stay centered during transformation
            self.rect.x = 400  # Center of arena
            # Brief pause before dropping
            if self.phase2_timer >= 30:  # 0.5 seconds
                self.phase2_state = "dropping"
                self.phase2_timer = 0
                print("DREAD_KNIGHT: Starting to drop back down!")
        
        elif self.phase2_state == "dropping":
            self.phase2_timer += 1
            
            # Drop back to ground level (y=350)
            if self.rect.y < 350:
                self.rect.y += self.drop_speed
            else:
                self.rect.y = 350  # Ground level
                self.phase2_state = "idle"
                self.phase2_timer = 0
                # Start flame attack pattern
                self.phase2_attack_state = "flame_slash_left"
                self.phase2_attack_timer = 0
                print("DREAD_KNIGHT: Landed! Starting flame attack pattern!")
    
    def update_flame_attacks(self):
        """Update second phase flame attacks"""
        if self.phase2_attack_state == "flame_slash_left":
            self.phase2_attack_timer += 1
            
            # Flame slash left for 1 second
            if self.phase2_attack_timer >= self.flame_slash_duration:
                self.phase2_attack_state = "flame_slash_right"
                self.phase2_attack_timer = 0
                print("DREAD_KNIGHT: Flame slash left complete, starting right!")
        
        elif self.phase2_attack_state == "flame_slash_right":
            self.phase2_attack_timer += 1
            
            # Flame slash right for 1 second
            if self.phase2_attack_timer >= self.flame_slash_duration:
                self.phase2_attack_state = "flame_pause"
                self.phase2_attack_timer = 0
                print("DREAD_KNIGHT: Flame slash right complete, pausing!")
        
        elif self.phase2_attack_state == "flame_pause":
            self.phase2_attack_timer += 1
            
            # Pause for 2 seconds before starting second attack
            if self.phase2_attack_timer >= self.flame_pause_duration:
                self.phase2_attack_state = "flame_charge_left"
                self.phase2_attack_timer = 0
                print("DREAD_KNIGHT: Starting flame charge left!")
        
        elif self.phase2_attack_state == "flame_charge_left":
            self.phase2_attack_timer += 1
            
            # Charge to left side of arena
            if self.rect.x > 100:  # Left side of arena
                self.rect.x -= self.flame_charge_speed
            else:
                self.rect.x = 100  # Left side
                self.phase2_attack_state = "flame_turn_right"
                self.phase2_attack_timer = 0
                print("DREAD_KNIGHT: Reached left side, turning right!")
        
        elif self.phase2_attack_state == "flame_turn_right":
            self.phase2_attack_timer += 1
            
            # Turn to face right for 1 second
            if self.phase2_attack_timer >= 60:  # 1 second
                self.phase2_attack_state = "flame_rain"
                self.phase2_attack_timer = 0
                self.flame_rain_timer = 0
                self.flame_rain_drops = []
                print("DREAD_KNIGHT: Starting flame rain!")
        
        elif self.phase2_attack_state == "flame_rain":
            self.phase2_attack_timer += 1
            self.flame_rain_timer += 1
            
            # Create rain drops every 10 frames (spaced pattern)
            if self.flame_rain_timer >= 10:
                self._create_flame_rain_drop()
                self.flame_rain_timer = 0
            
            # Update existing rain drops
            for drop in self.flame_rain_drops[:]:
                drop['y'] += 4  # Fall speed
                if drop['y'] > 400:  # Remove when they hit ground
                    self.flame_rain_drops.remove(drop)
            
            # Rain for 3 seconds
            if self.phase2_attack_timer >= self.flame_rain_duration:
                self.phase2_attack_state = "flame_charge_center"
                self.phase2_attack_timer = 0
                self.flame_rain_drops = []
                print("DREAD_KNIGHT: Rain complete, charging back to center!")
        
        elif self.phase2_attack_state == "flame_charge_center":
            self.phase2_attack_timer += 1
            
            # Charge back to center
            if self.rect.x < 400:  # Center of arena
                self.rect.x += self.flame_charge_speed
            else:
                self.rect.x = 400  # Center
                self.phase2_attack_state = "flame_slash_left"
                self.phase2_attack_timer = 0
                print("DREAD_KNIGHT: Back to center, repeating attack cycle!")
    
    def update_victory_sequence(self):
        """Update victory sequence"""
        if self.victory_state == "shaking":
            self.victory_timer += 1
            self.victory_shake_intensity += 0.3
            
            # Clear flame rain when victory starts
            self.flame_rain_drops = []
            
            # Shake for 2 seconds
            if self.victory_timer >= self.victory_shake_duration:
                self.victory_state = "disappearing"
                self.victory_timer = 0
                print("DREAD_KNIGHT: Shaking complete, disappearing!")
        
        elif self.victory_state == "disappearing":
            self.victory_timer += 1
            
            # Disappear for 1 second
            if self.victory_timer >= 60:  # 1 second
                self.victory_state = "victory_message"
                self.victory_timer = 0
                print("DREAD_KNIGHT: Disappeared, showing victory message!")
        
        elif self.victory_state == "victory_message":
            self.victory_timer += 1
            
            # Show message for 5 seconds
            if self.victory_timer >= self.victory_message_duration:
                self.victory_state = "reward_showing"
                self.victory_timer = 0
                print("DREAD_KNIGHT: Victory message complete, showing reward!")
    
    def _create_flame_rain_drop(self):
        """Create a flame rain drop at a random x position"""
        import random
        x = random.randint(200, 800)  # Random x position across arena
        y = 50  # Start above screen
        self.flame_rain_drops.append({'x': x, 'y': y})
    
    def update(self, x_shift, tiles):
        """Update boss state"""
        if not self.alive:
            return
        
        # Update intro sequence
        self.update_intro()
        
        # Update victory sequence if active
        if self.victory_state != "idle":
            self.update_victory_sequence()
        # Update second phase if active
        elif self.second_phase:
            self.update_phase2()
            # Update flame attacks if in second phase and landed
            if self.phase2_state == "idle" and self.health_refilled:
                self.update_flame_attacks()
        # Update attack sequence if fighting and not in second phase
        elif self.intro_state == "fighting":
            self.update_attack()
        
        # Update animation
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.stand_frames):
            self.current_frame = 0
        
        # Set current image based on victory sequence, attack state, or second phase
        if self.victory_state != "idle":
            if self.victory_state == "shaking":
                # Use flame form with shake effect
                self.image = self.flame_left_frames[1]  # flame_left_2.png
            elif self.victory_state in ["disappearing", "victory_message", "reward_showing"]:
                # Invisible during disappearing and message phases
                self.image = pygame.Surface((1, 1))  # Tiny invisible image
        elif self.second_phase:
            if self.phase2_state in ["shaking", "rising", "flash"]:
                # Use normal standing during transformation
                self.image = self.stand_frames[int(self.current_frame)]
            elif self.phase2_state in ["transformed", "dropping"]:
                # Use flame_left_2.png after transformation
                self.image = self.flame_left_frames[1]  # flame_left_2.png
            elif self.phase2_state == "idle" and self.health_refilled:
                # Use flame attack animations during second phase attacks
                if self.phase2_attack_state == "flame_slash_left":
                    self.image = self.flame_left_frames[0]  # flame_left_1.png
                elif self.phase2_attack_state == "flame_slash_right":
                    self.image = self.flame_right_frames[1]  # flame_right_2.png
                elif self.phase2_attack_state in ["flame_pause", "flame_charge_left"]:
                    self.image = self.flame_left_frames[1]  # flame_left_2.png
                elif self.phase2_attack_state == "flame_turn_right":
                    self.image = self.flame_right_frames[0]  # flame_right1.png
                elif self.phase2_attack_state in ["flame_rain", "flame_charge_center"]:
                    self.image = self.flame_right_frames[0]  # flame_right1.png
                else:
                    self.image = self.flame_left_frames[1]  # flame_left_2.png (default)
        elif self.attack_state == "charging_right":
            # Alternate between charging_right.png and charging_right_2.png
            frame_index = int(self.attack_timer / 10) % 2  # Switch every 10 frames
            self.image = self.charge_right_frames[frame_index]
        elif self.attack_state == "charging_left":
            # Alternate between char_left2.png and charge_left.png
            frame_index = int(self.attack_timer / 10) % 2  # Switch every 10 frames
            self.image = self.charge_left_frames[frame_index]
        elif self.attack_state == "charging_right_to_center":
            # Alternate between charging_right.png and charging_right_2.png
            frame_index = int(self.attack_timer / 10) % 2  # Switch every 10 frames
            self.image = self.charge_right_frames[frame_index]
        elif self.attack_state == "slash_left":
            # Use sword_swing_left.png during left slash
            self.image = self.sword_left_frames[0]  # sword_swing_left.png
        elif self.attack_state == "slash_right":
            # Use sword_swing_right.png during right slash
            self.image = self.sword_right_frames[0]  # sword_swing_right.png
        elif self.attack_state == "delay" or self.attack_state == "final_pause":
            # Use char_left2.png during delays
            self.image = self.charge_left_frames[1]  # char_left2.png is index 1
        else:
            # Default to standing
            self.image = self.stand_frames[int(self.current_frame)]
        self.mask = pygame.mask.from_surface(self.image)
    
    def get_shake_offset(self):
        """Get shake offset for second phase shaking"""
        if self.second_phase and self.phase2_state == "shaking":
            import math
            # Create shaking effect
            shake_x = math.sin(self.phase2_timer * 0.3) * self.shake_intensity
            shake_y = math.cos(self.phase2_timer * 0.2) * (self.shake_intensity * 0.5)
            return (shake_x, shake_y)
        return (0, 0)
    
    def draw_flame_rain(self, screen):
        """Draw flame rain drops"""
        for drop in self.flame_rain_drops:
            screen.blit(self.flame_rain_img, (drop['x'], drop['y']))
    
    def draw_victory_message(self, screen):
        """Draw victory message"""
        if self.victory_state == "victory_message":
            font = pygame.font.Font(None, 74)
            text = font.render("YOU WIN! COLLECT YOUR REWARD", True, (255, 255, 255))  # White text
            text_rect = text.get_rect(center=(500, 200))  # Center of screen
            screen.blit(text, text_rect)
    
    def draw_reward(self, screen):
        """Draw reward image"""
        if self.victory_state == "reward_showing":
            # Draw reward at center of screen
            reward_rect = self.reward_img.get_rect(center=(500, 300))
            screen.blit(self.reward_img, reward_rect)
            return reward_rect  # Return rect for collision detection
        return None
    
    def take_damage(self):
        """Take damage and return status"""
        if not self.alive:
            return None
        
        # In second phase, can't take damage until health is refilled
        if self.second_phase and not self.health_refilled:
            print("DREAD_KNIGHT: Cannot take damage until health refills!")
            return "immune"
        
        self.health -= 10
        print(f"DREAD_KNIGHT: Health reduced to {self.health}")
        
        if self.health <= 0:
            if not self.second_phase:
                # Start second phase instead of dying
                self.second_phase = True
                self.phase2_state = "shaking"
                self.phase2_timer = 0
                self.shake_intensity = 0
                print("DREAD_KNIGHT: Starting second phase - shaking!")
                return "phase2_started"
            else:
                # Only start victory sequence if we're in second phase AND have been transformed
                if self.phase2_state == "idle" and self.health_refilled:
                    # Start victory sequence in second phase
                    self.victory_state = "shaking"
                    self.victory_timer = 0
                    self.victory_shake_intensity = 0
                    print("DREAD_KNIGHT: Starting victory sequence!")
                    return "victory_started"
                else:
                    # Still in transformation phase, just die normally
                    self.alive = False
                    print("DREAD_KNIGHT: Defeated during transformation!")
                    return "defeated"
        
        return "damaged"
    
    def trigger_second_phase(self):
        """Trigger second phase directly (for F1 skip)"""
        if not self.second_phase:
            self.second_phase = True
            self.phase2_state = "shaking"
            self.phase2_timer = 0
            self.shake_intensity = 0
            self.health = 0  # Set health to 0 to trigger transformation
            print("DREAD_KNIGHT: F1 skip - triggering second phase!")
            return "phase2_started"
        return None
    
    def draw_health_bar(self, screen):
        """Draw health bar"""
        if self.intro_state in ["title_show", "title_hide", "fighting"]:
            # Health bar background
            health_bg_rect = pygame.Rect(WIDTH - 220, 20, 200, 20)
            pygame.draw.rect(screen, (255, 0, 0), health_bg_rect)
            
            # Health bar fill
            health_width = int((self.health / self.max_health) * 200)
            health_rect = pygame.Rect(WIDTH - 220, 20, health_width, 20)
            pygame.draw.rect(screen, (0, 255, 0), health_rect)
            
            # Health bar border
            pygame.draw.rect(screen, (255, 255, 255), health_bg_rect, 2)
    
    def draw_title(self, screen):
        """Draw title card with shake effect"""
        if self.intro_state == "title_show":
            # Calculate title position (center of screen with shake)
            title_x = (WIDTH - self.title_img.get_width()) // 2 + self.title_shake_offset
            title_y = (HEIGHT - self.title_img.get_height()) // 2
            
            screen.blit(self.title_img, (title_x, title_y))
