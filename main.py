import pygame
import sys
import os
from settings import *
from helpers import draw_text_wrap, get_last_line_position, skip_to_next_state
from snake_game import Snake, Apple
from platformer import PlatPlayer, Platform, Hazard, PlatEnemy, Boss, RewardItem

# Adventure game integration
def run_adventure_game():
    """Wrapper function to run the adventure game and return completion status"""
    # Change to adventure game directory
    original_dir = os.getcwd()
    adventure_dir = os.path.join(original_dir, "Adventure Game")
    
    try:
        os.chdir(adventure_dir)
        
        # Import adventure game module
        sys.path.insert(0, adventure_dir)
        import adventure_module
        
        # Run the adventure game
        adventure_completed = adventure_module.run_adventure_game(screen)
        
        return adventure_completed
        
    except Exception as e:
        print(f"Error running adventure game: {e}")
        return False
    finally:
        # Restore original directory and path
        os.chdir(original_dir)
        if adventure_dir in sys.path:
            sys.path.remove(adventure_dir)

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

# ----- Cutscene 3 (after platformer) -----
cutscene3_text = (
    "Excellent work! You have conquered the platformer challenge and defeated the mighty boss! "
    "Now prepare yourself for the final test: an epic adventure through mysterious lands. "
    "Your skills will be tested in ways you've never experienced before!"
)
displayed_text3 = ""
text_index3 = 0
text_timer3 = 0
cursor_timer3 = 0

# ----- Cutscene 4 (after adventure game) -----
cutscene4_text = (
    "Incredible! You have completed the ultimate adventure and defeated the ghostly boss! "
    "Your journey through all the games is now complete. You have proven yourself to be "
    "a true master of all challenges. Congratulations, legendary adventurer!"
)
displayed_text4 = ""
text_index4 = 0
text_timer4 = 0
cursor_timer4 = 0

# ----- Puppet -----
try:
    puppet_open = pygame.image.load("Asset/puppet_open.png").convert_alpha()
    puppet_closed = pygame.image.load("Asset/puppet_closed.png").convert_alpha()
    puppet_open = pygame.transform.scale(puppet_open, (100, 100))
    puppet_closed = pygame.transform.scale(puppet_closed, (100, 100))
except pygame.error:
    # Create placeholder rectangles if images don't exist
    puppet_open = pygame.Surface((100, 100))
    puppet_open.fill(NEON_GREEN)
    puppet_closed = pygame.Surface((100, 100))
    puppet_closed.fill((0, 100, 0))

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
max_stages = 6  # 5 platforming stages + 1 boss stage
player = None

# ----- Adventure game variables -----
adventure_completed = False

# ----- Platformer functions -----
def setup_stage(stage_num):
    global player
    
    platforms.empty()
    hazards.empty()
    enemies.empty()
    boss_group.empty()
    reward_group.empty()

    if stage_num == 0:
        # Stage 1 - Stepped platforms with complete floor coverage
        # Ground floor - complete coverage
        platforms.add(Platform(0, HEIGHT-50, 200, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(250, HEIGHT-50, 200, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(500, HEIGHT-50, 200, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(700, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        
        # Second level platforms - reduced density
        platforms.add(Platform(150, HEIGHT-150, 120, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(450, HEIGHT-150, 120, 20, "Asset/wood_platform.png"))
        
        # Third level platforms - reduced density
        platforms.add(Platform(250, HEIGHT-250, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(550, HEIGHT-250, 100, 20, "Asset/wood_platform.png"))
        
        # Fourth level platforms - reduced density
        platforms.add(Platform(350, HEIGHT-350, 80, 20, "Asset/wood_platform.png"))
        
        # Ceiling platforms for verticality - reduced density
        platforms.add(Platform(100, 50, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(500, 50, 100, 20, "Asset/wood_platform.png"))
        
        hazards.add(Hazard(250, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(450, HEIGHT-30, 50, 20, "Asset/spike.png"))
        
        # Varied enemy patterns
        enemy1 = PlatEnemy(130, HEIGHT-180, "Asset/enemy1.png", patrol_range=100, aggro_range=90)
        enemy1.patrol_pattern = "back_forth"
        enemies.add(enemy1)
        enemy2 = PlatEnemy(380, HEIGHT-280, "Asset/enemy1.png", patrol_range=80, aggro_range=70)
        enemy2.patrol_pattern = "circle"
        enemies.add(enemy2)
        enemy3 = PlatEnemy(630, HEIGHT-180, "Asset/enemy1.png", patrol_range=90, aggro_range=85)
        enemy3.patrol_pattern = "stationary"
        enemies.add(enemy3)
        
    elif stage_num == 1:
        # Stage 2 - Vertical column layout with complete coverage
        # Ground floor - complete coverage
        platforms.add(Platform(0, HEIGHT-50, 150, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(200, HEIGHT-50, 150, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(400, HEIGHT-50, 150, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(600, HEIGHT-50, 200, 50, "Asset/ground_platform.png"))
        
        # Column 1 - Left side - reduced density
        platforms.add(Platform(50, HEIGHT-150, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(50, HEIGHT-250, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(50, 150, 50, 20, "Asset/wood_platform.png"))
        
        # Column 2 - Center left - reduced density
        platforms.add(Platform(250, HEIGHT-150, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(250, HEIGHT-350, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(250, 50, 50, 20, "Asset/wood_platform.png"))
        
        # Column 3 - Center right - reduced density
        platforms.add(Platform(450, HEIGHT-250, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(450, HEIGHT-350, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(450, 150, 50, 20, "Asset/wood_platform.png"))
        
        # Column 4 - Right side - reduced density
        platforms.add(Platform(650, HEIGHT-150, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(650, HEIGHT-250, 50, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(650, 50, 50, 20, "Asset/wood_platform.png"))
        
        # Connecting platforms - reduced density
        platforms.add(Platform(150, HEIGHT-200, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(350, HEIGHT-200, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(550, HEIGHT-200, 100, 20, "Asset/wood_platform.png"))
        
        hazards.add(Hazard(175, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(375, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(575, HEIGHT-30, 50, 20, "Asset/spike.png"))
        
        # Mixed enemy patterns
        enemy1 = PlatEnemy(75, HEIGHT-180, "Asset/enemy1.png", patrol_range=80, aggro_range=100)
        enemy1.patrol_pattern = "back_forth"
        enemies.add(enemy1)
        enemy2 = PlatEnemy(275, HEIGHT-280, "Asset/enemy1.png", patrol_range=80, aggro_range=80)
        enemy2.patrol_pattern = "stationary"
        enemies.add(enemy2)
        enemy3 = PlatEnemy(475, HEIGHT-180, "Asset/enemy1.png", patrol_range=80, aggro_range=90)
        enemy3.patrol_pattern = "circle"
        enemies.add(enemy3)
        enemy4 = PlatEnemy(675, HEIGHT-280, "Asset/enemy1.png", patrol_range=80, aggro_range=85)
        enemy4.patrol_pattern = "back_forth"
        enemies.add(enemy4)
        
    elif stage_num == 2:
        # Stage 3 - Zigzag pattern with complete coverage
        # Ground floor - complete coverage
        platforms.add(Platform(0, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(150, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(300, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(450, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(600, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(750, HEIGHT-50, 50, 50, "Asset/ground_platform.png"))
        
        # Zigzag pattern - alternating heights - reduced density
        platforms.add(Platform(0, HEIGHT-150, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(240, HEIGHT-250, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(480, HEIGHT-150, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(720, HEIGHT-250, 80, 20, "Asset/wood_platform.png"))
        
        # Third level - reduced density
        platforms.add(Platform(120, HEIGHT-350, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(360, HEIGHT-350, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(600, HEIGHT-350, 60, 20, "Asset/wood_platform.png"))
        
        # Ceiling platforms - reduced density
        platforms.add(Platform(75, 50, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(375, 50, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(675, 50, 100, 20, "Asset/wood_platform.png"))
        
        # High platforms for verticality - reduced density
        platforms.add(Platform(200, 100, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(500, 100, 60, 20, "Asset/wood_platform.png"))
        
        hazards.add(Hazard(125, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(275, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(425, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(575, HEIGHT-30, 50, 20, "Asset/spike.png"))
        
        # Vertical-focused enemies
        enemy1 = PlatEnemy(40, HEIGHT-180, "Asset/enemy1.png", patrol_range=100, aggro_range=85)
        enemy1.patrol_pattern = "back_forth"
        enemies.add(enemy1)
        enemy2 = PlatEnemy(160, HEIGHT-280, "Asset/enemy1.png", patrol_range=100, aggro_range=95)
        enemy2.patrol_pattern = "circle"
        enemies.add(enemy2)
        enemy3 = PlatEnemy(280, HEIGHT-180, "Asset/enemy1.png", patrol_range=100, aggro_range=75)
        enemy3.patrol_pattern = "stationary"
        enemies.add(enemy3)
        enemy4 = PlatEnemy(400, HEIGHT-280, "Asset/enemy1.png", patrol_range=100, aggro_range=90)
        enemy4.patrol_pattern = "back_forth"
        enemies.add(enemy4)
        
    elif stage_num == 3:
        # Stage 4 - Layered approach with complete coverage
        # Ground floor - complete coverage
        platforms.add(Platform(0, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(125, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(250, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(375, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(500, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(625, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(750, HEIGHT-50, 50, 50, "Asset/ground_platform.png"))
        
        # Layer 1 - Low platforms - reduced density
        platforms.add(Platform(62, HEIGHT-120, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(250, HEIGHT-120, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(437, HEIGHT-120, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(625, HEIGHT-120, 80, 20, "Asset/wood_platform.png"))
        
        # Layer 2 - Mid platforms - reduced density
        platforms.add(Platform(112, HEIGHT-200, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(300, HEIGHT-200, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(487, HEIGHT-200, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(675, HEIGHT-200, 60, 20, "Asset/wood_platform.png"))
        
        # Layer 3 - High platforms - reduced density
        platforms.add(Platform(62, HEIGHT-280, 40, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(250, HEIGHT-280, 40, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(437, HEIGHT-280, 40, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(625, HEIGHT-280, 40, 20, "Asset/wood_platform.png"))
        
        # Layer 4 - Very high platforms - reduced density
        platforms.add(Platform(112, HEIGHT-360, 30, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(300, HEIGHT-360, 30, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(487, HEIGHT-360, 30, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(675, HEIGHT-360, 30, 20, "Asset/wood_platform.png"))
        
        # Ceiling platforms - reduced density
        platforms.add(Platform(62, 50, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(250, 50, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(437, 50, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(625, 50, 100, 20, "Asset/wood_platform.png"))
        
        hazards.add(Hazard(112, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(237, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(362, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(487, HEIGHT-30, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(612, HEIGHT-30, 50, 20, "Asset/spike.png"))
        
        # Aggressive enemies with varied patterns
        enemy1 = PlatEnemy(40, HEIGHT-150, "Asset/enemy1.png", patrol_range=80, aggro_range=100)
        enemy1.patrol_pattern = "back_forth"
        enemies.add(enemy1)
        enemy2 = PlatEnemy(165, HEIGHT-230, "Asset/enemy1.png", patrol_range=80, aggro_range=90)
        enemy2.patrol_pattern = "circle"
        enemies.add(enemy2)
        enemy3 = PlatEnemy(290, HEIGHT-150, "Asset/enemy1.png", patrol_range=80, aggro_range=85)
        enemy3.patrol_pattern = "stationary"
        enemies.add(enemy3)
        enemy4 = PlatEnemy(415, HEIGHT-230, "Asset/enemy1.png", patrol_range=80, aggro_range=95)
        enemy4.patrol_pattern = "back_forth"
        enemies.add(enemy4)
        enemy5 = PlatEnemy(540, HEIGHT-150, "Asset/enemy1.png", patrol_range=80, aggro_range=90)
        enemy5.patrol_pattern = "circle"
        enemies.add(enemy5)
        
    elif stage_num == 4:
        # Stage 5 - Pyramid/stepped approach with complete coverage
        # Ground floor - complete coverage
        platforms.add(Platform(0, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(100, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(200, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(300, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(400, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(500, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(600, HEIGHT-50, 80, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(700, HEIGHT-50, 100, 50, "Asset/ground_platform.png"))
        
        # Step 1 - Low platforms - reduced density
        platforms.add(Platform(100, HEIGHT-120, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(300, HEIGHT-120, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(500, HEIGHT-120, 60, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(700, HEIGHT-120, 60, 20, "Asset/wood_platform.png"))
        
        # Step 2 - Mid platforms - reduced density
        platforms.add(Platform(150, HEIGHT-200, 40, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(350, HEIGHT-200, 40, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(550, HEIGHT-200, 40, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(750, HEIGHT-200, 50, 20, "Asset/wood_platform.png"))
        
        # Step 3 - High platforms - reduced density
        platforms.add(Platform(200, HEIGHT-280, 30, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(400, HEIGHT-280, 30, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(600, HEIGHT-280, 30, 20, "Asset/wood_platform.png"))
        
        # Step 4 - Very high platforms - reduced density
        platforms.add(Platform(250, HEIGHT-360, 20, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(450, HEIGHT-360, 20, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(650, HEIGHT-360, 20, 20, "Asset/wood_platform.png"))
        
        # Step 5 - Peak platforms - reduced density
        platforms.add(Platform(300, HEIGHT-440, 15, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(500, HEIGHT-440, 15, 20, "Asset/wood_platform.png"))
        
        # Ceiling platforms - reduced density
        platforms.add(Platform(50, 50, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(250, 50, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(450, 50, 80, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(650, 50, 80, 20, "Asset/wood_platform.png"))
        
        hazards.add(Hazard(90, HEIGHT-30, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(190, HEIGHT-30, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(290, HEIGHT-30, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(390, HEIGHT-30, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(490, HEIGHT-30, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(590, HEIGHT-30, 40, 20, "Asset/spike.png"))
        
        # Elite enemies with high aggro
        enemy1 = PlatEnemy(80, HEIGHT-150, "Asset/enemy1.png", patrol_range=80, aggro_range=120)
        enemy1.patrol_pattern = "back_forth"
        enemies.add(enemy1)
        enemy2 = PlatEnemy(180, HEIGHT-230, "Asset/enemy1.png", patrol_range=80, aggro_range=110)
        enemy2.patrol_pattern = "circle"
        enemies.add(enemy2)
        enemy3 = PlatEnemy(280, HEIGHT-150, "Asset/enemy1.png", patrol_range=80, aggro_range=100)
        enemy3.patrol_pattern = "stationary"
        enemies.add(enemy3)
        enemy4 = PlatEnemy(380, HEIGHT-230, "Asset/enemy1.png", patrol_range=80, aggro_range=115)
        enemy4.patrol_pattern = "back_forth"
        enemies.add(enemy4)
        enemy5 = PlatEnemy(480, HEIGHT-150, "Asset/enemy1.png", patrol_range=80, aggro_range=105)
        enemy5.patrol_pattern = "circle"
        enemies.add(enemy5)
        
    elif stage_num == 5:
        # Stage 6 - Boss stage
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        platforms.add(Platform(100, HEIGHT-200, 100, 20, "Asset/wood_platform.png"))
        platforms.add(Platform(600, HEIGHT-200, 100, 20, "Asset/wood_platform.png"))
        boss = Boss(WIDTH//2 - 75, HEIGHT//2 - 75)
        boss_group.add(boss)

    # Reset player position for each stage
    if player:
        player.rect.topleft = (50, HEIGHT-100)
        player.vel_y = 0
        player.on_ground = False

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
                elif game_state == "cutscene3":
                    displayed_text3 = ""
                    text_index3 = 0
                elif game_state == "cutscene4":
                    displayed_text4 = ""
                    text_index4 = 0
                elif game_state == "snake":
                    snake = Snake()
                    apple = Apple(snake)
                    snake_win = False
                elif game_state == "platformer":
                    platformer_initialized = False
                elif game_state == "adventure":
                    adventure_completed = False

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
            elif game_state == "cutscene3" and text_index3 >= len(cutscene3_text) and event.key == pygame.K_RETURN:
                game_state = "adventure"
                adventure_completed = False
            elif game_state == "adventure" and adventure_completed and event.key == pygame.K_RETURN:
                game_state = "cutscene4"
            elif game_state == "cutscene4" and text_index4 >= len(cutscene4_text) and event.key == pygame.K_RETURN:
                game_state = "menu"  # Return to menu or end game

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

        # Clear screen first to prevent trails
        screen.fill(BLACK)
        
        # Background
        try:
            bg = pygame.image.load("Asset/platformer_bg.png").convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))  # Scale to screen size
            screen.blit(bg, (0, 0))
        except pygame.error:
            screen.fill((50, 50, 100))  # Fallback background color

        # Player update and collision handling
        player.update(platforms, enemies, hazards)
        
        # Check if player died from hazards
        if pygame.sprite.spritecollide(player, hazards, False):
            # Reset player to start of current stage
            player.rect.topleft = (50, HEIGHT-100)
            player.vel_y = 0

        # Check if player died from enemies
        if pygame.sprite.spritecollide(player, enemies, False):
            # Reset player to start of current stage
            player.rect.topleft = (50, HEIGHT-100)
            player.vel_y = 0

        # Enemies update (pass player for aggro detection)
        enemies.update(player)
        
        # Boss update
        for boss in boss_group:
            boss.update(player_group, enemies)
            boss.minions.update(player)

        # Attack collisions
        for attack in player.attack_group:
            # Hit regular enemies
            hit_enemies = pygame.sprite.spritecollide(attack, enemies, True)
            if hit_enemies:
                attack.kill()
            
            # Hit boss minions
            for boss in boss_group:
                hit_minions = pygame.sprite.spritecollide(attack, boss.minions, True)
                if hit_minions:
                    attack.kill()
                
                # Hit boss
                if attack.rect.colliderect(boss.rect):
                    boss.health -= 1
                    attack.kill()
                    if boss.health <= 0:
                        boss.kill()

        # Stage progression - player reaches right edge
        if player.rect.right >= WIDTH - 10 and current_stage < max_stages - 1:
            current_stage += 1
            setup_stage(current_stage)
            print(f"Advanced to stage {current_stage + 1}")  # Debug print

        # Draw everything
        platforms.draw(screen)
        hazards.draw(screen)
        enemies.draw(screen)
        
        # Draw boss and minions
        for boss in boss_group:
            screen.blit(boss.image, boss.rect)
            boss.minions.draw(screen)
            
        reward_group.draw(screen)
        player_group.draw(screen)
        player.attack_group.draw(screen)

        # Boss health bar
        if current_stage == max_stages - 1:  # only in boss stage
            for boss in boss_group:
                if boss.health > 0:
                    bar_width = max(0, boss.health * 5)
                    pygame.draw.rect(screen, (255, 0, 0), (boss.rect.x, boss.rect.y - 15, bar_width, 10))
                    pygame.draw.rect(screen, (255, 255, 255), (boss.rect.x, boss.rect.y - 15, 150, 10), 2)

        # Reward on boss defeat
        if len(boss_group.sprites()) == 0 and current_stage == max_stages - 1 and len(reward_group.sprites()) == 0:
            reward_item = RewardItem(WIDTH - 100, HEIGHT - 100, "Asset/reward_item.png")
            reward_group.add(reward_item)

        # Reward pickup - check if player attacks it
        for reward in reward_group:
            # Check if any attack hits the reward
            for attack in player.attack_group:
                if attack.rect.colliderect(reward.rect):
                    game_state = "cutscene3"
                    reward_group.empty()
                    platformer_initialized = False
                    break

        # Stage indicator
        stage_text = small_font.render(f"Stage: {current_stage + 1}/{max_stages}", True, NEON_GREEN)
        screen.blit(stage_text, (10, 10))

    # ----- ADVENTURE GAME -----
    elif game_state == "adventure":
        # Run the adventure game
        adventure_completed = run_adventure_game()
        
        # After adventure game completes, show completion message
        screen.fill(BLACK)
        if adventure_completed:
            message_surface = font.render("ADVENTURE COMPLETED!", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))
        else:
            message_surface = font.render("Adventure game ended unexpectedly", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # ----- CUTSCENE 3 (after platformer) -----
    elif game_state == "cutscene3":
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed
        screen.fill(BLACK)
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))
        text_timer3 += 1
        if text_timer3 % typing_speed == 0 and text_index3 < len(cutscene3_text):
            displayed_text3 += cutscene3_text[text_index3]
            text_index3 += 1
        draw_text_wrap(screen, displayed_text3, font, NEON_GREEN, 20, text_y_start, text_max_width)
        if text_index3 < len(cutscene3_text):
            cursor_timer3 += 1
            if cursor_timer3 % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text3, font, text_max_width, 20, text_y_start)
                cursor_surf = font.render("|", True, NEON_GREEN)
                screen.blit(cursor_surf, (cursor_x, cursor_y))
        else:
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # ----- CUTSCENE 4 (after adventure game) -----
    elif game_state == "cutscene4":
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed
        screen.fill(BLACK)
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))
        text_timer4 += 1
        if text_timer4 % typing_speed == 0 and text_index4 < len(cutscene4_text):
            displayed_text4 += cutscene4_text[text_index4]
            text_index4 += 1
        draw_text_wrap(screen, displayed_text4, font, NEON_GREEN, 20, text_y_start, text_max_width)
        if text_index4 < len(cutscene4_text):
            cursor_timer4 += 1
            if cursor_timer4 % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text4, font, text_max_width, 20, text_y_start)
                cursor_surf = font.render("|", True, NEON_GREEN)
                screen.blit(cursor_surf, (cursor_x, cursor_y))
        else:
            prompt_surface = small_font.render("Press Enter to return to menu...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    pygame.display.flip()

pygame.quit()
sys.exit()