import pygame

class ShockWave(pygame.sprite.Sprite):
    def __init__(self, pos, image, direction):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.direction = direction  # -1 for left, 1 for right
        self.speed = 5  # Slower movement
        self.lifetime = 120  # 2 seconds
        self.timer = 0
        
    def update(self):
        """Update shock wave position and lifetime"""
        self.rect.x += self.direction * self.speed
        self.timer += 1
        
        # Remove if off screen or lifetime expired
        if self.rect.x < -200 or self.rect.x > 1000 or self.timer >= self.lifetime:
            self.kill()

