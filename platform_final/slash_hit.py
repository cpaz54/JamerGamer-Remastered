import pygame

class SlashHit(pygame.sprite.Sprite):
    def __init__(self, pos, image, direction):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.direction = direction  # "left" or "right"
        self.lifetime = 30  # 0.5 seconds
        self.timer = 0
        
    def update(self):
        """Update slash hit lifetime"""
        self.timer += 1
        
        # Remove if lifetime expired
        if self.timer >= self.lifetime:
            self.kill()

