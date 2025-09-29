import pygame

class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos, direction_x, direction_y, fireball_type="side"):
        super().__init__()
        
        # Load fireball image based on type
        try:
            if fireball_type == "rain":
                self.image = pygame.image.load("assets/bosses/BIG_WILLIG/fire_ball_rain.png").convert_alpha()
                # Rain fireballs are larger
                self.image = pygame.transform.scale(self.image, (60, 60))
                self.speed = 3  # Slower falling speed
            else:  # side fireballs
                self.image = pygame.image.load("assets/bosses/BIG_WILLIG/fire_ball_side.png").convert_alpha()
                # Side fireballs are 20% bigger (40 * 1.2 = 48)
                self.image = pygame.transform.scale(self.image, (48, 48))
                self.speed = 8  # Faster horizontal speed
        except:
            # Create fallback fireball
            if fireball_type == "rain":
                self.image = pygame.Surface((60, 60))
                self.image.fill((255, 150, 0))  # Orange color for rain
                self.speed = 3
            else:
                self.image = pygame.Surface((48, 48))
                self.image.fill((255, 100, 0))  # Orange color for side
                self.speed = 8
            print("Warning: Could not load fireball image")
        
        self.rect = self.image.get_rect(center=pos)
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.fireball_type = fireball_type
        
    def update(self):
        """Update fireball position with angled trajectory"""
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        
        # Remove fireball if it goes off screen or hits ground
        if self.fireball_type == "rain":
            # Rain fireballs fall straight down and are removed when they hit the ground
            if self.rect.y > 600:  # Hit ground
                self.kill()
        else:
            # Side fireballs are removed when they go off screen or hit ground
            if self.rect.x > 1000 or self.rect.x < -100 or self.rect.y > 600:  # Off screen or hit ground
                self.kill()
