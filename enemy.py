import pygame
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.health = 3
        self.direction = 1
        self.speed = 2

    def update(self):
        # Basic patrol
        self.rect.x += self.direction * self.speed
        if self.rect.left < 100 or self.rect.right > 700:
            self.direction *= -1

        # TODO: later add chasing player

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
