import pygame

class HealthPickup(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Load heart image
        try:
            self.image = pygame.image.load("assets/life/life.png").convert_alpha()
            # Scale heart to appropriate size
            self.image = pygame.transform.scale(self.image, (30, 30))
        except:
            # Create fallback heart
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 0, 0))  # Red color
            print("Warning: Could not load heart image")
        
        self.rect = self.image.get_rect(center=pos)
        self.collected = False
        
    def update(self):
        """Update health pickup"""
        # Health pickup doesn't need animation, just collision detection
        pass
    
    def collect(self):
        """Mark pickup as collected"""
        self.collected = True
        self.kill()

