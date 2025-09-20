import pygame
import pygame.freetype
import math
import sys
import random

#establishing tile, width, and height sizes (width of 3200 and height of 1800 works best for my computer)
TILESIZE = 50 #50 recommended for here, 80 or higher for thonny if recording
WIDTH = TILESIZE * 17 #900 (850 makes screen side have an odd number)
HEIGHT = TILESIZE * 11 #600 (550 makes screen height have an odd number)
'''WIDTH = TILESIZE * 16 #so width of screen is 16 tiles long (set)
HEIGHT = WIDTH * 9 // 16 #aspect ratio of 16:9 (with this setup, height of screen is '''
FPS = 60 #60

#defining colors
GROUND_COLOR = (159, 221, 98)
CAVE_COLOR = (202, 131, 61) #CAVE_COLOR = (196, 107, 100) #19
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#initializing pygame and create window
pygame.mixer.pre_init(44100, -16, 1, 512) #no sound delay
pygame.init()
#pygame.mixer.init() #for sounds (do i need this?)

def play_song(file_path_and_name):
    # plays music for pygame:
    song = pygame.mixer.music.load(file_path_and_name) #must be .mp3
    pygame.mixer.music.play(-1)

#sets up font stuff (freetype)
pygame.freetype.init()

monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) #this is the display of the game, resizable makes the window be able to be resizable
pygame.display.set_caption("Adventure Game")
clock = pygame.time.Clock()

#CREATES SPRITE GROUP
all_sprites = pygame.sprite.Group()
tile_sprites = pygame.sprite.Group()
item_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
arrow_sprites = pygame.sprite.Group()
doorway_sprites = pygame.sprite.Group()
chest_sprites = pygame.sprite.Group()
switch_barrier_sprites = pygame.sprite.Group()
animated_sprites = pygame.sprite.Group()