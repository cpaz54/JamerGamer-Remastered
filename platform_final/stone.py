import pygame

class Stone(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/bosses/JESTER/stone.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except:
            # Fallback if stone.png not found
            self.image = pygame.Surface((30, 30))
            self.image.fill((100, 100, 100))  # Gray stone
        
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = 6
        self.lifetime = 300  # 5 seconds
        self.timer = 0
        
    def update(self):
        """Update stone position and lifetime"""
        self.rect.x += self.speed  # Move right
        self.timer += 1
        
        # Remove if off screen or lifetime expired
        if self.rect.x > 1000 or self.timer >= self.lifetime:
            self.kill()
