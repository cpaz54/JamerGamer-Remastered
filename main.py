import pygame
import sys
from settings import *
from helpers import draw_text_wrap, get_last_line_position, skip_to_next_state
from snake_game import Snake, Apple
from platformer import Player as PlatPlayer, Platform, Hazard, Enemy as PlatEnemy, Boss, RewardItem

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Game Experience")
clock = pygame.time.Clock()

font = pygame.font.SysFont("courier", 32, bold=True)
small_font = pygame.font.SysFont("courier", 24)

# ----- Game flow variables -----
game_state = "menu"

# ----- Cutscene 1 -----
cutscene_text = (
    "Welcome to the game. Prepare yourself for a journey through four mini-games. "
    "Each game will challenge you in a unique way. Good luck and have fun!"
)
displayed_text = ""
text_index = 0
text_timer = 0
typing_speed = 5
cursor_timer = 0

# ----- Cutscene 2 -----
cutscene2_text = (
    "Great job finishing the Snake challenge! Now get ready for the next test: "
    "a classic platformer where timing and agility will be key. Stay sharp, "
    "and watch out for tricky jumps!"
)
displayed_text2 = ""
text_index2 = 0
text_timer2 = 0
cursor_timer2 = 0

# ----- Puppet -----
puppet_open = pygame.image.load("Asset/puppet_open.png").convert_alpha()
puppet_closed = pygame.image.load("Asset/puppet_closed.png").convert_alpha()
puppet_open = pygame.transform.scale(puppet_open, (100, 100))
puppet_closed = pygame.transform.scale(puppet_closed, (100, 100))
puppet_timer = 0
current_puppet = puppet_closed

# ----- Cutscene text layout -----
text_y_start = HEIGHT // 2
text_max_width = WIDTH - 40

# ----- Snake variables -----
snake = None
apple = None
snake_timer = 0
snake_speed = 10
snake_win = False
snake_flash_timer = 0

# ----- Platformer variables -----
platformer_initialized = False
player_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
hazards = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
reward_group = pygame.sprite.Group()
current_stage = 0
max_stages = 6

# ----- Platformer functions -----
def setup_stage(stage_num):
    platforms.empty()
    hazards.empty()
    enemies.empty()
    global player
    if stage_num < max_stages - 1:
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(150 + stage_num*50, HEIGHT-200, 200, 20, "Asset/wood_platform.png"))
        hazards.add(Hazard(400, HEIGHT-70, 50, 20, "Asset/spike.png"))
        enemies.add(PlatEnemy(350, HEIGHT-100, "Asset/enemy1.png"))
    else:
        boss_group.empty()
        boss = Boss(WIDTH//2 - 75, HEIGHT//2 - 75)
        boss_group.add(boss)
    player.rect.topleft = (50, HEIGHT-100)

def init_platformer():
    global player_group, player, platformer_initialized, current_stage
    player_group.empty()
    player = PlatPlayer(50, HEIGHT-100)
    player_group.add(player)
    current_stage = 0
    setup_stage(current_stage)
    platformer_initialized = True

# ----- Main loop -----
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Developer skip
            if event.unicode == "*":
                game_state = skip_to_next_state(game_state)
                if game_state == "cutscene":
                    displayed_text = ""
                    text_index = 0
                elif game_state == "cutscene2":
                    displayed_text2 = ""
                    text_index2 = 0
                elif game_state == "snake":
                    snake = Snake()
                    apple = Apple(snake)
                    snake_win = False
                elif game_state == "platformer":
                    platformer_initialized = False

            # State-specific Enter key
            elif game_state == "menu" and event.key == pygame.K_RETURN:
                game_state = "cutscene"
            elif game_state == "cutscene" and text_index >= len(cutscene_text) and event.key == pygame.K_RETURN:
                game_state = "snake"
                snake = Snake()
                apple = Apple(snake)
            elif game_state == "snake" and snake_win and event.key == pygame.K_RETURN:
                game_state = "cutscene2"
            elif game_state == "snake" and not snake.alive and event.key == pygame.K_RETURN:
                snake = Snake()
                apple = Apple(snake)
                snake_win = False
            elif game_state == "cutscene2" and text_index2 >= len(cutscene2_text) and event.key == pygame.K_RETURN:
                game_state = "platformer"

    # ----- MENU -----
    if game_state == "menu":
        strobe_timer = pygame.time.get_ticks() // 700
        screen.fill(BLACK)
        if strobe_timer % 2 == 0:
            text_surface = font.render("PRESS ENTER", True, NEON_GREEN)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_surface, text_rect)

    # ----- CUTSCENE 1 -----
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
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

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
        if not snake.alive:
            message_surface = font.render("Try again (Reach Size = 20 to continue)", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        if snake.size >= 20 and not snake_win:
            snake_win = True
            snake_flash_timer = 0
        if snake_win:
            snake_flash_timer += 1
            if snake_flash_timer % 30 < 15:
                message_surface = font.render("YOU WIN!", True, NEON_GREEN)
                screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # ----- CUTSCENE 2 -----
    elif game_state == "cutscene2":
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed
        screen.fill(BLACK)
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))
        text_timer2 += 1
        if text_timer2 % typing_speed == 0 and text_index2 < len(cutscene2_text):
            displayed_text2 += cutscene2_text[text_index2]
            text_index2 += 1
        draw_text_wrap(screen, displayed_text2, font, NEON_GREEN, 20, text_y_start, text_max_width)
        if text_index2 < len(cutscene2_text):
            cursor_timer2 += 1
            if cursor_timer2 % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text2, font, text_max_width, 20, text_y_start)
                cursor_surf = font.render("|", True, NEON_GREEN)
                screen.blit(cursor_surf, (cursor_x, cursor_y))
        else:
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # ----- PLATFORMER -----
    elif game_state == "platformer":
        if not platformer_initialized:
            init_platformer()
        keys = pygame.key.get_pressed()
        # Update player
        player.update(platforms, enemies, hazards)
        # Update enemies
        for enemy in enemies:
            enemy.update()
        # Update boss
        for boss in boss_group:
            boss.update(player_group, enemies)
        # Check reward pickup
        for reward in reward_group:
            if player.rect.colliderect(reward.rect):
                game_state = "cutscene3"
                reward_group.empty()
                platformer_initialized = False
        # Stage progression
        if player.rect.right > WIDTH and current_stage < max_stages - 1:
            current_stage += 1
            setup_stage(current_stage)
        # Draw all
        screen.fill(BLACK)
        platforms.draw(screen)
        hazards.draw(screen)
        enemies.draw(screen)
        boss_group.draw(screen)
        reward_group.draw(screen)
        player_group.draw(screen)
        # Boss health bar
        for boss in boss_group:
            pygame.draw.rect(screen, (255,0,0), (boss.rect.x, boss.rect.y - 10, boss.health * 10, 5))
        # Spawn reward if boss defeated
        if boss_group.sprites() == [] and current_stage == max_stages - 1 and reward_group.sprites() == []:
            reward_item = RewardItem(WIDTH//2, HEIGHT//2, "Asset/reward_item.png")
            reward_group.add(reward_item)

    pygame.display.flip()

pygame.quit()
sys.exit()
