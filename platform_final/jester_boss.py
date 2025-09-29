import pygame
from settings import WIDTH, HEIGHT
from shock_wave import ShockWave
from slash_hit import SlashHit
from stone import Stone

class JesterBoss(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.rect = pygame.Rect(pos[0], pos[1], size, size)
        
        # Boss properties
        self.max_health = 10
        self.health = self.max_health
        self.alive = True
        
        # Introduction sequence
        self.intro_state = "waiting"  # waiting, dropping, landed, title_show, title_hide, fighting
        self.intro_timer = 0
        self.title_timer = 0
        self.title_duration = 300  # 5 seconds
        
        # Animation properties
        self.facing_right_frames = []
        self.squat_frames = []
        self.jump_frames = []
        self.slash_left_frames = []
        self.slash_right_frames = []
        self.attack_left_frames = []
        self.attack_right_frames = []
        self.walk_left_frames = []
        self.bowl_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.025  # 50% slower than BIG_WILLIG
        
        # Physics properties (same as player)
        self.direction = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.on_ceiling = False
        
        # Attack system
        self.attack_state = "idle"  # idle, preparing_jump, jumping_down_from_left, landing, shock_wave, standing_slash_left, standing_slash_right, jumping_up_to_right, pausing_on_right_platform, jumping_down_from_right, walking_left, pausing, bowling, jumping_up_to_left
        self.attack_timer = 0
        self.attack_delay = 120  # Half as fast (60 * 2)
        self.move_speed = 1  # Reduced by 50% from 2  # Normal movement speed
        self.original_x = self.rect.x
        self.original_y = self.rect.y
        
        # Shock wave system
        self.shock_waves = pygame.sprite.Group()
        self.shock_wave_timer = 0
        self.shock_wave_duration = 120  # 2 seconds
        
        # Slash hit effects
        self.slash_hits = pygame.sprite.Group()
        self.slash_hit_timer = 0
        self.slash_hit_duration = 20  # 0.33 seconds (quicker)
        
        # Bowling system
        self.stones = pygame.sprite.Group()
        self.bowling_timer = 0
        self.bowling_duration = 180  # 3 seconds
        self.stone_count = 0
        self.max_stones = 20
        self.stone_delay = 15  # 0.25 seconds (15 frames at 60fps)
        self.last_stone_time = 0
        
        # Load animation frames
        self._load_facing_right_frames()
        self._load_squat_frames()
        self._load_jump_frames()
        self._load_slash_frames()
        self._load_attack_frames()
        self._load_walk_left_frames()
        self._load_bowl_frames()
        self._load_title_image()
        
        # Set initial image
        self.image = self.facing_right_frames[0] if self.facing_right_frames else self._create_fallback_image(size)
        
        # Title image
        self.title_image = None
        self._load_title_image()
        
        # Health bar
        self.health_bar_rect = pygame.Rect(WIDTH - 250, 30, 200, 20)
        self.health_bar_bg_color = (50, 0, 0)
        self.health_bar_color = (200, 0, 0)
    
    def _load_facing_right_frames(self):
        """Load facing_right animation frames"""
        try:
            facing_right_img = pygame.image.load("assets/bosses/JESTER/stand/facing_right.png").convert_alpha()
            
            # Scale frame to boss size (slightly bigger)
            boss_size = 120  # 20% bigger than original 100
            facing_right_img = pygame.transform.scale(facing_right_img, (boss_size, boss_size))
            
            self.facing_right_frames = [facing_right_img]
        except:
            print("Warning: Could not load JESTER facing_right frames")
            self.facing_right_frames = []
    
    def _load_squat_frames(self):
        """Load squat animation frames"""
        try:
            squat_img = pygame.image.load("assets/bosses/JESTER/jump/squat.png").convert_alpha()
            
            # Scale frame to boss size (slightly bigger)
            boss_size = 120  # 20% bigger than original 100
            squat_img = pygame.transform.scale(squat_img, (boss_size, boss_size))
            
            self.squat_frames = [squat_img]
        except:
            print("Warning: Could not load JESTER squat frames")
            self.squat_frames = []
    
    def _load_jump_frames(self):
        """Load jump animation frames"""
        try:
            jump_img = pygame.image.load("assets/bosses/JESTER/jump/jump.png").convert_alpha()
            
            # Scale frame to boss size (slightly bigger)
            boss_size = 120  # 20% bigger than original 100
            jump_img = pygame.transform.scale(jump_img, (boss_size, boss_size))
            
            self.jump_frames = [jump_img]
        except:
            print("Warning: Could not load JESTER jump frames")
            self.jump_frames = []
    
    def _load_slash_frames(self):
        """Load shock wave slash frames"""
        try:
            # Load slash left
            slash_left_img = pygame.image.load("assets/bosses/JESTER/attack_left/slash_left.png").convert_alpha()
            slash_left_img = pygame.transform.scale(slash_left_img, (120, 60))  # Wider for shock wave
            self.slash_left_frames = [slash_left_img]
            
            # Load slash right
            slash_right_img = pygame.image.load("assets/bosses/JESTER/attack_right/slash_right.png").convert_alpha()
            slash_right_img = pygame.transform.scale(slash_right_img, (120, 60))  # Wider for shock wave
            self.slash_right_frames = [slash_right_img]
        except:
            print("Warning: Could not load JESTER slash frames")
            self.slash_left_frames = []
            self.slash_right_frames = []
    
    def _load_attack_frames(self):
        """Load standing attack frames"""
        try:
            # Load attack left
            attack_left_img = pygame.image.load("assets/bosses/JESTER/attack_left/attack_left.png").convert_alpha()
            attack_left_img = pygame.transform.scale(attack_left_img, (120, 120))
            self.attack_left_frames = [attack_left_img]
            
            # Load attack right
            attack_right_img = pygame.image.load("assets/bosses/JESTER/attack_right/attack_right.png").convert_alpha()
            attack_right_img = pygame.transform.scale(attack_right_img, (120, 120))
            self.attack_right_frames = [attack_right_img]
        except:
            print("Warning: Could not load JESTER attack frames")
            self.attack_left_frames = []
            self.attack_right_frames = []
    
    def _load_walk_left_frames(self):
        """Load walk left animation frames"""
        try:
            walk_left_img = pygame.image.load("assets/bosses/JESTER/walk_left/walk_left.png").convert_alpha()
            walk_left_img = pygame.transform.scale(walk_left_img, (120, 120))
            self.walk_left_frames = [walk_left_img]
        except:
            print("Warning: Could not load JESTER walk_left frames")
            self.walk_left_frames = []
    
    def _load_bowl_frames(self):
        """Load bowl animation frames"""
        try:
            bowl_img = pygame.image.load("assets/bosses/JESTER/bowl/squat.png").convert_alpha()
            bowl_img = pygame.transform.scale(bowl_img, (120, 120))
            self.bowl_frames = [bowl_img]
        except:
            print("Warning: Could not load JESTER bowl frames")
            self.bowl_frames = []
    
    def _load_title_image(self):
        """Load boss title image"""
        try:
            self.title_image = pygame.image.load("assets/bosses/JESTER/carson_title.png").convert_alpha()
            # Scale title to same size as BIG_WILLIG (1200x600)
            self.title_image = pygame.transform.scale(self.title_image, (1200, 600))
        except:
            print("Warning: Could not load JESTER title image")
            self.title_image = None
    
    def _create_fallback_image(self, size):
        """Create fallback image if sprites fail to load"""
        image = pygame.Surface((size, size))
        image.fill((255, 0, 255))  # Magenta color
        return image
    
    def trigger_intro(self):
        """Trigger the JESTER introduction sequence"""
        self.intro_state = "dropping"
        print("JESTER boss triggered!")
    
    def update_intro(self):
        """Update the introduction sequence"""
        self.intro_timer += 1
        
        # Debug output every 60 frames (1 second)
        if self.intro_timer % 60 == 0:
            print(f"JESTER intro state: {self.intro_state}, timer: {self.intro_timer}, pos: ({self.rect.x}, {self.rect.y})")
        
        if self.intro_state == "waiting":
            pass  # Do nothing until triggered
        
        elif self.intro_state == "dropping":
            # Drop from top of screen with slight left movement
            self.rect.y += 5  # Drop down
            self.rect.x -= 1  # Move slightly left to hit platform
            if self.rect.y >= 200:  # Land on upper platform (row 4 * 50px)
                self.rect.y = 200
                self.rect.x = 50  # Position on upper platform
                self.intro_state = "landed"
                self.intro_timer = 0
                print("JESTER landed on platform!")
        
        elif self.intro_state == "landed":
            # Wait a moment after landing
            if self.intro_timer >= 30:  # 0.5 seconds
                self.intro_state = "title_show"
                self.title_timer = 0
        
        elif self.intro_state == "title_show":
            # Show title for 5 seconds
            self.title_timer += 1
            if self.title_timer == 1:
                print("JESTER title showing!")
            if self.title_timer >= self.title_duration:
                self.intro_state = "title_hide"
                self.intro_timer = 0
                print("JESTER title hiding!")
        
        elif self.intro_state == "title_hide":
            # Hide title and start fighting
            if self.intro_timer >= 30:  # 0.5 seconds
                self.intro_state = "fighting"
                self.intro_timer = 0
        
        elif self.intro_state == "fighting":
            # Update attack patterns
            self._update_attack()
        
        # Animate based on state
        if self.intro_state in ["dropping", "landed", "title_show", "title_hide"]:
            self._animate_facing_right()
        elif self.intro_state == "fighting":
            if self.attack_state in ["idle", "preparing_jump"]:
                self._animate_squat()
            elif self.attack_state == "jumping":
                self._animate_jump()
            elif self.attack_state in ["landing", "shock_wave"]:
                self._animate_squat()
            elif self.attack_state == "jumping_down_to_center":
                self._animate_jump()
            elif self.attack_state == "jumping_to_right_platform":
                print("JESTER: Animating jump to right platform")
                self._animate_jump()
            elif self.attack_state == "pausing_on_right_platform":
                self._animate_facing_right()  # Stand still during pause
            elif self.attack_state == "jumping_from_right_to_center":
                print("JESTER: Animating jump from right to center")
                self._animate_jump()
            elif self.attack_state == "swing_left":
                self._animate_attack_left()
            elif self.attack_state == "swing_right":
                self._animate_attack_right()
            elif self.attack_state == "walking_to_left_platform":
                self._animate_walk_left()  # Use walk_left animation
            elif self.attack_state == "squat_pause":
                self._animate_squat()  # Use squat animation
            elif self.attack_state == "throwing_stones":
                self._animate_squat()  # Stay in squat while throwing
        
        # Player cannot move during intro until title disappears
        return self.intro_state in ["waiting", "dropping", "landed", "title_show", "title_hide"]
    
    def _animate_facing_right(self):
        """Animate the facing_right frames"""
        if not self.facing_right_frames:
            return
        
        self.image = self.facing_right_frames[0]  # facing_right.png
    
    def _animate_squat(self):
        """Animate between facing_right and squat frames"""
        if not self.facing_right_frames or not self.squat_frames:
            return
        
        # Alternate between facing_right and squat (slower animation)
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 2:  # 2 frames to alternate
            self.animation_timer = 0
        
        if int(self.animation_timer) == 0:
            self.image = self.facing_right_frames[0]  # facing_right.png
        else:
            self.image = self.squat_frames[0]  # squat.png
    
    def _animate_jump(self):
        """Animate the jump frame"""
        if not self.jump_frames:
            print("JESTER: No jump frames available!")
            return
        
        self.image = self.jump_frames[0]  # jump.png
    
    def _animate_attack_left(self):
        """Animate the attack left frame"""
        if not self.attack_left_frames:
            return
        
        self.image = self.attack_left_frames[0]  # attack_left.png
    
    def _animate_attack_right(self):
        """Animate the attack right frame"""
        if not self.attack_right_frames:
            return
        
        self.image = self.attack_right_frames[0]  # attack_right.png
    
    def _animate_walk_left(self):
        """Animate the walk left frame"""
        if not self.walk_left_frames:
            return
        
        self.image = self.walk_left_frames[0]  # walk_left.png
    
    def _animate_bowl(self):
        """Animate the bowl frame"""
        if not self.bowl_frames:
            return
        
        self.image = self.bowl_frames[0]  # bowl/squat.png
    
    def is_intro_complete(self):
        """Check if the introduction is complete"""
        return self.intro_state == "fighting"
    
    def take_damage(self):
        """Boss takes damage from sword"""
        if self.alive and self.is_intro_complete():
            self.health -= 1
            print(f"JESTER health: {self.health}")
            
            if self.health <= 0:
                self.alive = False
                self.kill()
                return "defeated"
        return None
    
    def _update_attack(self):
        """Update attack patterns"""
        self.attack_timer += 1
        
        # Debug output every 30 frames (0.5 seconds)
        if self.attack_timer % 30 == 0:
            print(f"JESTER attack state: {self.attack_state}, timer: {self.attack_timer}, pos: ({self.rect.x}, {self.rect.y})")
        
        if self.attack_state == "idle":
            # Stay at current position (either platform or center)
            self.direction.x = 0  # Stop moving
            self.direction.y = 0  # Stop falling
            # If at center, wait for shockwaves to finish then do swing attacks
            if self.rect.x >= 400:
                self.rect.x = 400  # Force to center
                self.rect.y = 350  # Force to ground level
                # Wait for shockwaves to finish (check if shockwaves group is empty)
                if len(self.shock_waves) == 0 and self.attack_timer >= 60:  # Wait 1 second after landing
                    # Start swing attacks
                    self.attack_state = "swing_left"
                    self.attack_timer = 0
                    print("JESTER: Shockwaves complete, starting swing attacks")
            # Start attack sequence from left platform
            elif self.intro_state == "fighting" and self.attack_timer >= self.attack_delay and self.rect.x <= 100:
                self.attack_state = "jumping_down_to_center"
                self.attack_timer = 0
                print("JESTER: Starting - jumping down to center")
        
        elif self.attack_state == "jumping_down_to_center":
            # Jump arc from left platform to center of screen
            # Create proper arc trajectory
            if self.attack_timer < 45:  # First 0.75 seconds - jump up and right
                self.direction.x = self.move_speed * 4  # Move right much faster
                self.direction.y = -4  # Move up high (negative y = up)
            elif self.attack_timer < 90:  # Next 0.75 seconds - continue right and start down
                self.direction.x = self.move_speed * 4  # Continue right much faster
                self.direction.y = 0  # Level out
            else:  # Final phase - arc down to center
                self.direction.x = self.move_speed * 4  # Continue right much faster
                self.direction.y = 3  # Move down fast
            
            # Check if we've reached center area and ground level
            if self.rect.x >= 400 and self.rect.y >= 330:  # Center area and near ground level
                # Force to exact center position and stop all movement
                self.rect.x = 400  # Exact center of screen
                self.rect.y = 350  # Ground level
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop falling
                # Create shockwave when landing
                self._create_shock_waves()
                print("JESTER: Landed at center - creating shockwaves")
                # Stop and stay at center
                self.attack_state = "idle"
                self.attack_timer = 0
                print("JESTER: Landing complete")
        
        elif self.attack_state == "jumping_to_right_platform":
            # Jump arc from center to right platform - use same arc as left-to-center
            # Create proper arc trajectory (mirror of center-to-left)
            if self.attack_timer < 45:  # First 0.75 seconds - jump up and right
                self.direction.x = self.move_speed * 4  # Move right much faster
                self.direction.y = -4  # Move up high (negative y = up)
            elif self.attack_timer < 90:  # Next 0.75 seconds - continue right and start down
                self.direction.x = self.move_speed * 4  # Continue right much faster
                self.direction.y = 0  # Level out
            else:  # Final phase - arc down to right platform
                self.direction.x = self.move_speed * 4  # Continue right much faster
                self.direction.y = 3  # Move down fast
            
            # Debug output
            if self.attack_timer % 30 == 0:
                print(f"JESTER jumping to right: pos=({self.rect.x}, {self.rect.y}), timer={self.attack_timer}, direction=({self.direction.x}, {self.direction.y})")
            
            # Check if we've reached right platform area and platform level
            if self.rect.x >= 750 and self.rect.y >= 200:  # Right platform area and near platform level
                # Force to exact right platform position and stop all movement
                self.rect.x = 800  # Right platform position
                self.rect.y = 230  # Right platform level
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop falling
                self.attack_state = "pausing_on_right_platform"
                self.attack_timer = 0
                print("JESTER: Reached right platform, pausing")
            # Safety check - if we've been jumping too long, force to platform
            elif self.attack_timer >= 180:  # 3 seconds max
                self.attack_state = "pausing_on_right_platform"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop moving
                self.rect.x = 800  # Right platform position
                self.rect.y = 230  # Right platform level
                print("JESTER: Safety timeout - forced to right platform")
        
        elif self.attack_state == "pausing_on_right_platform":
            # Pause on right platform for 3 seconds
            self.direction.x = 0  # Stop moving
            self.rect.y = 230  # Right platform level
            if self.attack_timer >= 180:  # 3 seconds
                self.attack_state = "jumping_from_right_to_center"
                self.attack_timer = 0
                print("JESTER: Pause complete, jumping from right to center")
        
        elif self.attack_state == "jumping_from_right_to_center":
            # Jump arc from right platform to center of screen
            # Create proper arc trajectory (mirror of left jump)
            if self.attack_timer < 45:  # First 0.75 seconds - jump up and left
                self.direction.x = -self.move_speed * 4  # Move left much faster
                self.direction.y = -4  # Move up high (negative y = up)
            elif self.attack_timer < 90:  # Next 0.75 seconds - continue left and start down
                self.direction.x = -self.move_speed * 4  # Continue left much faster
                self.direction.y = 0  # Level out
            else:  # Final phase - arc down to center
                self.direction.x = -self.move_speed * 4  # Continue left much faster
                self.direction.y = 3  # Move down fast
            
            # Debug output
            if self.attack_timer % 30 == 0:
                print(f"JESTER jumping from right: pos=({self.rect.x}, {self.rect.y}), timer={self.attack_timer}")
            
            # Check if we've reached center area and ground level
            if self.rect.x <= 400 and self.rect.y >= 330:  # Center area and near ground level
                # Force to exact center position and stop all movement
                self.rect.x = 400  # Exact center of screen
                self.rect.y = 350  # Ground level
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop falling
                # Create shockwave when landing
                self._create_shock_waves()
                print("JESTER: Landed at center from right - creating shockwaves")
                # Stop and stay at center
                self.attack_state = "idle"
                self.attack_timer = 0
                print("JESTER: Landing complete")
            # Safety check - if we've been jumping too long, force to center
            elif self.attack_timer >= 180:  # 3 seconds max
                self.rect.x = 400  # Exact center of screen
                self.rect.y = 350  # Ground level
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop falling
                self._create_shock_waves()
                print("JESTER: Safety timeout - forced to center from right")
                self.attack_state = "idle"
                self.attack_timer = 0
        
        elif self.attack_state == "swing_left":
            # Swing left attack
            self.direction.x = 0  # Stop moving
            self.rect.y = 350  # Ground level
            # Create slash effect at the start of the swing
            if self.attack_timer == 1:
                self._create_slash_hit("left")
                print("JESTER: Creating left slash effect")
            # Wait for slash effect to disappear before moving to next swing
            if len(self.slash_hits) == 0 and self.attack_timer >= 30:  # Wait for slash to disappear
                self.attack_state = "swing_right"
                self.attack_timer = 0
                print("JESTER: Left swing complete, starting right swing")
        
        elif self.attack_state == "swing_right":
            # Swing right attack
            self.direction.x = 0  # Stop moving
            self.rect.y = 350  # Ground level
            # Create slash effect at the start of the swing
            if self.attack_timer == 1:
                self._create_slash_hit("right")
                print("JESTER: Creating right slash effect")
            # Wait for slash effect to disappear before moving to next action
            if len(self.slash_hits) == 0 and self.attack_timer >= 30:  # Wait for slash to disappear
                # After both swings, walk left to left platform edge
                self.attack_state = "walking_to_left_platform"
                self.attack_timer = 0
                print("JESTER: Right swing complete, walking left to platform")
        
        elif self.attack_state == "walking_to_left_platform":
            # Walk left to left platform edge
            self.direction.x = -self.move_speed  # Move left
            self.rect.y = 350  # Stay at bottom level height
            # Check if we've reached the left platform edge (around x=100)
            if self.rect.x <= 100:
                self.attack_state = "squat_pause"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
                self.rect.x = 100  # Left platform edge
                print("JESTER: Reached left platform edge, starting squat pause")
        
        elif self.attack_state == "squat_pause":
            # Pause for 5 seconds with squat animation
            self.direction.x = 0  # Stop moving
            self.rect.y = 350  # Bottom level height
            if self.attack_timer >= 300:  # 5 seconds
                self.attack_state = "throwing_stones"
                self.attack_timer = 0
                self.stone_count = 0  # Reset stone counter
                print("JESTER: Squat pause complete, starting stone throwing")
        
        elif self.attack_state == "throwing_stones":
            # Throw 20 stones every 0.5 seconds
            self.direction.x = 0  # Stop moving
            self.rect.y = 350  # Bottom level height
            # Throw a stone every 30 frames (0.5 seconds)
            if self.attack_timer % 30 == 0 and self.stone_count < 20:
                self._create_stone()
                self.stone_count += 1
                print(f"JESTER: Throwing stone {self.stone_count}/20")
            # After all stones are thrown, wait for them to disappear
            elif self.stone_count >= 20 and len(self.stones) == 0:
                # All stones have disappeared, restart the cycle from left platform
                self.attack_state = "idle"
                self.attack_timer = 0
                self.rect.x = 50  # Left platform position
                self.rect.y = 230  # Left platform level
                print("JESTER: All stones disappeared, restarting attack cycle from left platform")
        
        elif self.attack_state == "landing":
            # Land and create shock waves
            if self.attack_timer >= 30:  # 0.5 seconds
                self.attack_state = "shock_wave"
                self.attack_timer = 0
                self._create_shock_waves()
        
        elif self.attack_state == "shock_wave":
            # Shock waves active
            # Ensure we stay on ground level
            if self.rect.y != 400:  # If not on ground level, correct it
                self.rect.y = 400  # Top of bottom row
            if self.attack_timer >= 60:  # 1 second
                # First shockwave - go to left/right attacks
                self.attack_state = "standing_slash_left"
                self.attack_timer = 0
        
        elif self.attack_state == "standing_slash_left":
            # Standing slash left
            # Ensure we stay on ground level
            if self.rect.y != 400:  # If not on ground level, correct it
                self.rect.y = 400  # Top of bottom row
            if self.attack_timer >= 30:  # 0.5 seconds
                self._create_slash_hit("left")
            if self.attack_timer >= 60:  # 1 second
                self.attack_state = "standing_slash_right"
                self.attack_timer = 0
        
        elif self.attack_state == "standing_slash_right":
            # Standing slash right
            # Ensure we stay on ground level
            if self.rect.y != 400:  # If not on ground level, correct it
                self.rect.y = 400  # Top of bottom row
            if self.attack_timer >= 30:  # 0.5 seconds
                self._create_slash_hit("right")
            if self.attack_timer >= 60:  # 1 second
                self.attack_state = "jumping_up_to_right"
                self.attack_timer = 0
                # Start physics-based movement to right platform
                self.direction.x = self.move_speed  # Move right
                self.direction.y = -2  # Move up
        
        elif self.attack_state == "jumping_up_to_right":
            # Jump up to right platform
            self.direction.x = self.move_speed  # Move right
            self.direction.y = -2  # Move up
            # Check if we've reached the right platform area
            if self.rect.x >= 750 and self.rect.y <= 350:  # On or near right platform
                self.attack_state = "pausing_on_right_platform"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop moving
        
        elif self.attack_state == "pausing_on_right_platform":
            # Pause for 2 seconds on right platform
            self.direction.x = 0  # Stop moving
            # Maintain right platform level during pause
            if self.rect.y != 350:  # If not on right platform level, correct it
                self.rect.y = 350  # Right platform level
            if self.attack_timer >= 120:  # Pause for 2 seconds (120 frames at 60fps)
                self.attack_state = "jumping_down_from_right"
                self.attack_timer = 0
                # Start physics-based movement down from right
                self.direction.x = -self.move_speed  # Move left
                self.direction.y = 2  # Move down
        
        elif self.attack_state == "jumping_down_from_right":
            # Jump down from right platform to ground level
            self.direction.x = -self.move_speed  # Move left
            self.direction.y = 2  # Move down
            # Check if we've reached ground level
            if self.rect.y >= 400:  # Ground level (top of bottom row)
                self.attack_state = "walking_left"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop falling
        
        elif self.attack_state == "walking_left":
            # Walk to left side of arena using physics
            self.direction.x = -self.move_speed  # Normal speed
            # Ensure we're on top of bottom row during walking
            if self.rect.y != 400:  # If not on top of bottom row, correct it
                self.rect.y = 400  # Top of bottom row
            # Walk for a specific amount of time instead of detecting position
            if self.attack_timer >= 120:  # Walk for 2 seconds (120 frames at 60fps)
                self.attack_state = "pausing"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
        
        elif self.attack_state == "pausing":
            # Pause for 3 seconds before bowling
            self.direction.x = 0  # Stop moving
            # Ensure we're on top of bottom row during pausing
            if self.rect.y != 400:  # If not on top of bottom row, correct it
                self.rect.y = 400  # Top of bottom row
            if self.attack_timer >= 180:  # Pause for 3 seconds (180 frames at 60fps)
                self.attack_state = "bowling"
                self.attack_timer = 0
                self.bowling_timer = 0
                self.stone_count = 0
        
        elif self.attack_state == "bowling":
            # Bowling attack - squat for 3 seconds, then bowl 20 stones
            self.direction.x = 0  # Stop moving during bowling
            self._handle_bowling()
        
        elif self.attack_state == "jumping_up_to_left":
            # Jump back up to left platform after bowling
            self.direction.x = -self.move_speed  # Move left
            self.direction.y = -2  # Move up
            # Check if we've reached the left platform area
            if self.rect.x <= 100 and self.rect.y <= 350:  # On or near left platform
                self.attack_state = "idle"
                self.attack_timer = 0
                self.direction.x = 0  # Stop moving
                self.direction.y = 0  # Stop moving
    
    def _start_jump_to_center(self):
        """Start the jump to center movement"""
        # Calculate center position (middle of screen)
        center_x = WIDTH // 2 - self.rect.width // 2
        self.target_x = center_x
        self.jump_start_x = self.rect.x
        self.jump_start_y = self.rect.y
        self.jump_progress = 0.0
        self.jump_height = 100  # Height of the arc
    
    def _continue_jump(self):
        """Continue the jump movement in an arc"""
        self.jump_progress += 0.005  # 50% slower jumping speed (was 0.01)
        
        if self.jump_progress >= 1.0:
            # Jump complete, land at center
            self.rect.x = self.target_x
            self.attack_state = "landing"
            self.attack_timer = 0
        else:
            # Calculate arc position
            # Linear interpolation for x
            current_x = self.jump_start_x + (self.target_x - self.jump_start_x) * self.jump_progress
            # Parabolic arc for y
            arc_height = self.jump_height * (1 - (2 * self.jump_progress - 1) ** 2)
            current_y = self.jump_start_y - arc_height
            
            self.rect.x = int(current_x)
            self.rect.y = int(current_y)
    
    def _create_shock_waves(self):
        """Create shock waves to left and right"""
        print(f"JESTER: Creating shockwaves at position ({self.rect.x}, {self.rect.y})")
        
        # Create left shock wave - position it slightly lower
        if self.slash_left_frames:
            left_shock = ShockWave((self.rect.x - 80, self.rect.centery - 30), self.slash_left_frames[0], -1)
            self.shock_waves.add(left_shock)
            print(f"JESTER: Created LEFT shockwave at ({self.rect.x - 80}, {self.rect.centery - 30})")
        else:
            print("JESTER: No left slash frames available")
        
        # Create right shock wave - position it slightly lower
        if self.slash_right_frames:
            right_shock = ShockWave((self.rect.right + 20, self.rect.centery - 30), self.slash_right_frames[0], 1)
            self.shock_waves.add(right_shock)
            print(f"JESTER: Created RIGHT shockwave at ({self.rect.right + 20}, {self.rect.centery - 30})")
        else:
            print("JESTER: No right slash frames available")
    
    def _create_slash_hit(self, direction):
        """Create slash hit effect beside boss"""
        if direction == "left" and self.slash_left_frames:
            # Create slash hit to the left of boss
            slash_hit = SlashHit((self.rect.x - 60, self.rect.centery - 30), self.slash_left_frames[0], "left")
            self.slash_hits.add(slash_hit)
        elif direction == "right" and self.slash_right_frames:
            # Create slash hit to the right of boss
            slash_hit = SlashHit((self.rect.right, self.rect.centery - 30), self.slash_right_frames[0], "right")
            self.slash_hits.add(slash_hit)
    
    
    
    def _handle_bowling(self):
        """Handle the bowling attack"""
        # Keep on top of bottom row during bowling
        if self.rect.y != 350:  # If not on top of bottom row, correct it
            self.rect.y = 350  # On top of bottom row
        
        self.bowling_timer += 1
        
        # Squat for 3 seconds (180 frames)
        if self.bowling_timer < 180:
            # Still squatting, do nothing
            pass
        else:
            # Start bowling stones
            if self.stone_count < self.max_stones:
                # Create stone with 0.25 second delay between throws
                if self.bowling_timer - self.last_stone_time >= self.stone_delay:
                    self._create_stone()
                    self.stone_count += 1
                    self.last_stone_time = self.bowling_timer
            else:
                # All stones bowled, jump up to left platform
                self.attack_state = "jumping_up_to_left"
                self.attack_timer = 0
    
    def _create_stone(self):
        """Create a stone projectile"""
        # Create stone at slash height (same as shockwaves)
        stone = Stone((self.rect.centerx, self.rect.centery - 30))
        self.stones.add(stone)
    
    def _start_jump_to_left(self):
        """Start the jump to left side movement"""
        # Calculate left side position (ground level, not platform)
        left_x = 50  # Left side position
        self.target_x = left_x
        self.jump_start_x = self.rect.x
        self.jump_start_y = self.rect.y
        self.jump_progress = 0.0
        self.jump_height = 0  # No arc, just move horizontally
    
    def _continue_jump_to_left(self):
        """Continue the jump to left platform movement"""
        self.jump_progress += 0.01  # Half the jumping speed
        
        if self.jump_progress >= 1.0:
            # Jump complete, land at left platform
            self.rect.x = self.target_x
            self.attack_state = "idle"
            self.attack_timer = 0
        else:
            # Calculate arc position
            # Linear interpolation for x
            current_x = self.jump_start_x + (self.target_x - self.jump_start_x) * self.jump_progress
            # Parabolic arc for y
            arc_height = self.jump_height * (1 - (2 * self.jump_progress - 1) ** 2)
            current_y = self.jump_start_y - arc_height
            
            self.rect.x = int(current_x)
            self.rect.y = int(current_y)
    
    
    def draw_health_bar(self, screen):
        """Draw the boss health bar"""
        if self.intro_state in ["health_bar", "boss_appear", "title_show", "title_hide", "dropping", "landed", "fighting"]:
            # Draw health bar background
            pygame.draw.rect(screen, self.health_bar_bg_color, self.health_bar_rect)
            
            # Draw health bar
            health_width = int((self.health / self.max_health) * self.health_bar_rect.width)
            health_rect = pygame.Rect(self.health_bar_rect.x, self.health_bar_rect.y, health_width, self.health_bar_rect.height)
            pygame.draw.rect(screen, self.health_bar_color, health_rect)
    
    def draw_title(self, screen):
        """Draw the boss title during intro"""
        if self.intro_state == "title_show" and self.title_image:
            # Center the title on screen but raise it up to not cover boss
            title_rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            screen.blit(self.title_image, title_rect)
    
    def _handle_vertical_collision(self, tiles):
        """Handle vertical collision with tiles (same as BIG_WILLIG)"""
        for sprite in tiles.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0:  # Falling down
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0:  # Moving up
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0
                    self.on_ceiling = True
        
        if self.on_ground and self.direction.y < 0 or self.direction.y > 1:
            self.on_ground = False
        if self.on_ceiling and self.direction.y > 0:
            self.on_ceiling = False
    
    def _handle_horizontal_collision(self, tiles):
        """Handle horizontal collision with tiles (same as BIG_WILLIG)"""
        for sprite in tiles.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.rect.centerx < sprite.rect.centerx:
                    # Boss is to the left of tile, push left
                    self.rect.right = sprite.rect.left
                elif self.rect.centerx > sprite.rect.centerx:
                    # Boss is to the right of tile, push right
                    self.rect.left = sprite.rect.right

    def update(self, x_shift, tiles=None):
        """Update boss"""
        self.update_intro()
        
        # Update shock waves, slash hits, and stones
        self.shock_waves.update()
        self.slash_hits.update()
        self.stones.update()
        
        # Apply movement for jumping and walking states
        if self.attack_state in ["jumping_down_to_center", "jumping_to_right_platform", "jumping_from_right_to_center", "walking_to_left_platform"]:
            # Apply horizontal movement
            self.rect.x += self.direction.x * self.move_speed
            # Apply vertical movement
            self.rect.y += self.direction.y
            # Debug output
            if self.attack_timer % 30 == 0:
                print(f"JESTER: Applied movement - pos=({self.rect.x}, {self.rect.y}), direction=({self.direction.x}, {self.direction.y})")
        
        # Apply x_shift (for world movement)
        self.rect.x += x_shift
