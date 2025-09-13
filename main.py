import pygame
import sys
from settings import *
from helpers import draw_text_wrap, get_last_line_position

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Game Experience")
clock = pygame.time.Clock()

font = pygame.font.SysFont("courier", 32, bold=True)
small_font = pygame.font.SysFont("courier", 24)

# Load puppet images
puppet_open = pygame.image.load("Assets/puppet_open.png").convert_alpha()
puppet_closed = pygame.image.load("Assets/puppet_closed.png").convert_alpha()
puppet_open = pygame.transform.scale(puppet_open, (100, 100))
puppet_closed = pygame.transform.scale(puppet_closed, (100, 100))

# Game states
game_state = "menu"
cutscene_text = ("Welcome to the game. Prepare yourself for a journey through four mini-games. "
                 "Each game will challenge you in a unique way. Good luck and have fun!")
displayed_text = ""
text_index = 0
text_timer = 0
typing_speed = 5  # frames per letter
cursor_timer = 0

# Puppet animation
puppet_timer = 0
current_puppet = puppet_closed

# Cutscene text layout
text_y_start = HEIGHT // 2
text_max_width = WIDTH - 40  # 20 px padding each side

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "menu" and event.key == pygame.K_RETURN:
                game_state = "cutscene"
            elif game_state == "cutscene" and text_index >= len(cutscene_text) and event.key == pygame.K_RETURN:
                game_state = "snake"  # placeholder for Snake mini-game

    if game_state == "menu":
        # Slow strobe "Press Enter"
        strobe_timer = pygame.time.get_ticks() // 700
        screen.fill(BLACK)
        if strobe_timer % 2 == 0:
            text_surface = font.render("PRESS ENTER", True, NEON_GREEN)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surface, text_rect)

    elif game_state == "cutscene":
        # Animate puppet
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed

        screen.fill(BLACK)
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))

        # Typing effect
        text_timer += 1
        if text_timer % typing_speed == 0 and text_index < len(cutscene_text):
            displayed_text += cutscene_text[text_index]
            text_index += 1

        # Draw wrapped text
        draw_text_wrap(screen, displayed_text, font, NEON_GREEN, 20, text_y_start, text_max_width)

        # Blinking cursor
        if text_index < len(cutscene_text):
            cursor_timer += 1
            if cursor_timer % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text, font, text_max_width, 20, text_y_start)
                cursor_surf = font.render("|", True, NEON_GREEN)
                screen.blit(cursor_surf, (cursor_x, cursor_y))
        else:
            # Prompt to continue
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20))
            screen.blit(prompt_surface, prompt_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
