import pygame
import sys
from settings import *
from player import Player
from game_platform import Platform, MovingPlatform
from enemy import Enemy

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("We Are Watching You... v2")
clock = pygame.time.Clock()
font = pygame.font.SysFont("courier", 48, bold=True)

# Groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
attacks = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Player
player = Player()
all_sprites.add(player)

# Platforms
ground = Platform(0, HEIGHT - 40, WIDTH, 40)
all_sprites.add(ground)
platforms.add(ground)

# Moving platform
moving_platform = MovingPlatform(200, 400, 150, 20, dx=2)
all_sprites.add(moving_platform)
platforms.add(moving_platform)

# Enemy
enemy = Enemy(400, HEIGHT - 80)
all_sprites.add(enemy)
enemies.add(enemy)

# Score
score = 0

# Game state
game_state = "menu"
strobe_timer = 0

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "game"

    if game_state == "menu":
        strobe_timer += 1
        show_text = (strobe_timer // 30) % 2 == 0
        screen.fill(BLACK)
        if show_text:
            text_surface = font.render("PRESS ENTER", True, NEON_GREEN)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surface, text_rect)

    elif game_state == "game":
        # Updates
        player.update(platforms, attacks)
        attacks.update()
        enemies.update()
        platforms.update()

        # Attack collisions
        for attack in attacks:
            hit_list = pygame.sprite.spritecollide(attack, enemies, False)
            for enemy in hit_list:
                enemy.take_damage()
                score += 100

        # Draw
        screen.fill(SKY_BLUE)
        all_sprites.draw(screen)
        attacks.draw(screen)

        # Display score
        score_surface = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surface, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
