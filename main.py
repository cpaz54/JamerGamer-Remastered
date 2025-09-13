import pygame
import sys
from settings import *
from helpers import draw_text_wrap, get_last_line_position
from snake_game import Snake, Apple

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Game Experience")
clock = pygame.time.Clock()

font = pygame.font.SysFont("courier", 32, bold=True)
small_font = pygame.font.SysFont("courier", 24)

# Game flow variables
game_state = "menu"
cutscene_text = "Welcome to the game. Prepare yourself for a journey through four mini-games..."
displayed_text = ""
text_index = 0
text_timer = 0
typing_speed = 5
cursor_timer = 0

# Puppet
puppet_open = pygame.image.load("Asset/puppet_open.png").convert_alpha()
puppet_closed = pygame.image.load("Asset/puppet_closed.png").convert_alpha()
puppet_open = pygame.transform.scale(puppet_open, (100, 100))
puppet_closed = pygame.transform.scale(puppet_closed, (100, 100))
puppet_timer = 0
current_puppet = puppet_closed

# Cutscene text layout
text_y_start = HEIGHT // 2
text_max_width = WIDTH - 40

# Snake variables
snake = None
apple = None
snake_timer = 0
snake_speed = 10
snake_message = ""
snake_flash_timer = 0
snake_win = False

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
                game_state = "snake"
                snake = Snake()
                apple = Apple(snake)
            elif game_state == "snake" and snake_win and event.key == pygame.K_RETURN:
                game_state = "cutscene2"  # next cutscene
            elif game_state == "snake" and not snake.alive and event.key == pygame.K_RETURN:
                snake = Snake()
                apple = Apple(snake)
                snake_win = False

    # ----- MENU -----
    if game_state == "menu":
        strobe_timer = pygame.time.get_ticks() // 700
        screen.fill(BLACK)
        if strobe_timer % 2 == 0:
            text_surface = font.render("PRESS ENTER", True, NEON_GREEN)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surface, text_rect)

    # ----- CUTSCENE -----
    elif game_state == "cutscene":
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed

        screen.fill(BLACK)
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))

        text_timer += 1
        if text_timer % typing_speed == 0 and text_index < len(cutscene_text):
            displayed_text += cutscene_text[text_index]
            text_index += 1

        draw_text_wrap(screen, displayed_text, font, NEON_GREEN, 20, text_y_start, text_max_width)

        if text_index < len(cutscene_text):
            cursor_timer += 1
            if cursor_timer % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text, font, text_max_width, 20, text_y_start)
                cursor_surf = font.render("|", True, NEON_GREEN)
                screen.blit(cursor_surf, (cursor_x, cursor_y))
        else:
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH//2, HEIGHT - 20)))

    # ----- SNAKE -----
    elif game_state == "snake":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            snake.change_direction(0, -1)
        elif keys[pygame.K_DOWN]:
            snake.change_direction(0, 1)
        elif keys[pygame.K_LEFT]:
            snake.change_direction(-1, 0)
        elif keys[pygame.K_RIGHT]:
            snake.change_direction(1, 0)

        snake_timer += 1
        if snake_timer >= snake_speed:
            snake_timer = 0
            snake.update()
            if snake.alive and snake.body[0] == apple.position:
                snake.grow = True
                apple.position = apple.random_position(snake)

        screen.fill(BLACK)
        apple.draw(screen)
        snake.draw(screen)

        # Lose
        if not snake.alive:
            message_surface = font.render("Try again (Reach Size = 20 to continue)", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH//2, HEIGHT//2)))

        # Win
        if snake.size >= 20 and not snake_win:
            snake_win = True
            snake_flash_timer = 0

        if snake_win:
            snake_flash_timer += 1
            if snake_flash_timer % 30 < 15:
                message_surface = font.render("YOU WIN!", True, NEON_GREEN)
                screen.blit(message_surface, message_surface.get_rect(center=(WIDTH//2, HEIGHT//2)))
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH//2, HEIGHT - 20)))

    pygame.display.flip()

pygame.quit()
sys.exit()
