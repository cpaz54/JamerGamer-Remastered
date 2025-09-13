import pygame
import random
from settings import *

CELL_SIZE = 20
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

class Snake:
    def __init__(self):
        self.body = [(COLS//2, ROWS//2)]
        self.direction = (1, 0)  # moving right initially
        self.grow = False
        self.alive = True
        self.size = 1

    def update(self):
        if not self.alive:
            return
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % COLS, (head_y + dy) % ROWS)

        if new_head in self.body:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if self.grow:
            self.grow = False
            self.size += 1
        else:
            self.body.pop()

    def change_direction(self, dx, dy):
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)

    def draw(self, surface):
        for segment in self.body:
            rect = pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, GREEN, rect)

class Apple:
    def __init__(self, snake):
        self.position = self.random_position(snake)

    def random_position(self, snake):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in snake.body:
                return pos

    def draw(self, surface):
        rect = pygame.Rect(self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, (255,0,0), rect)
