import pygame
from settings import WIDTH, HEIGHT

class Shuriken(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Load and scale shuriken image
        self.image = pygame.image.load("assets/bosses/LAURTNEY/shurikin.png").convert_alpha()
        # Scale to 3x larger, then 50% bigger (90x90)
        self.image = pygame.transform.scale(self.image, (90, 90))
        
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        
        # Movement
        self.speed = 6
        
        # Create smaller hitbox for collision
        self.hitbox = pygame.Rect(self.rect.x + 15, self.rect.y + 15, 60, 60)
    
    def update(self):
        """Update shuriken position"""
        # Move right
        self.rect.x += self.speed
        
        # Update hitbox position
        self.hitbox.x = self.rect.x + 15
        self.hitbox.y = self.rect.y + 15
        
        # Remove if off screen
        if self.rect.x > WIDTH + 100:
            self.kill()
