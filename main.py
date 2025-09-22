import pygame
import sys
import os
from settings import *
from helpers import draw_text_wrap, get_last_line_position, skip_to_next_state
from snake_game import Snake, Apple
from platformer import PlatPlayer, Platform, Hazard, PlatEnemy, Boss, RewardItem
from doom_wrapper import run_doom_game
from guitar_hero_integrated import GuitarHeroGame

# Initialize pygame mixer for music
pygame.mixer.init()

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
    "But before you venture into the adventure realm, there's one more test of your skills. "
    "A musical challenge awaits - can you hit the right notes?"
)
displayed_text3 = ""
text_index3 = 0
text_timer3 = 0
cursor_timer3 = 0

# ----- Cutscene 3.5 (after Guitar Hero) -----
cutscene3_5_text = (
    "Incredible! You've proven yourself a true musical virtuoso! Your rhythm "
    "and timing are impeccable. Now you're ready for the ultimate adventure. "
    "Prepare yourself for exploration, puzzles, and danger in the adventure realm!"
)
displayed_text3_5 = ""
text_index3_5 = 0
text_timer3_5 = 0
cursor_timer3_5 = 0

# ----- Cutscene 4 (after adventure game) -----
cutscene4_text = (
    "Incredible! You have completed the ultimate adventure and defeated the ghostly boss! "
    "But your journey is not yet over. Prepare yourself for the final challenge: "
    "a battle against waves of demonic enemies in a classic first-person shooter!"
)
displayed_text4 = ""
text_index4 = 0
text_timer4 = 0
cursor_timer4 = 0

# ----- Cutscene 5 (after doom game) -----
cutscene5_text = (
    "VICTORY! You have conquered all the demonic waves and proven yourself a true warrior! "
    "Your journey through all the games is now complete. You have mastered every challenge: "
    "Snake, Platformer, Adventure, and Doom. You are a legendary gaming champion!"
)
displayed_text5 = ""
text_index5 = 0
text_timer5 = 0
cursor_timer5 = 0


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

# ----- Platformer Music Variables -----
current_music = None
shah_sound = None
shah_timer = 0
shah_interval = 8 * FPS  # 8 seconds in frames

# ----- Doom game variables -----
doom_game_running = False
doom_game_launched = False

# ----- Guitar Hero game variables -----
guitar_hero_game_running = False
guitar_hero_game_launched = False
guitar_hero_completed = False
guitar_hero_game = None

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

# ----- Doom game variables -----

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
        # Ground floor - complete coverage across entire width
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        
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
        
        # Spikes positioned on top of ground platform
        hazards.add(Hazard(250, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(450, HEIGHT-70, 50, 20, "Asset/spike.png"))
        
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
        # Ground floor - complete coverage across entire width
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        
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
        
        # Spikes positioned on top of ground platform
        hazards.add(Hazard(175, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(375, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(575, HEIGHT-70, 50, 20, "Asset/spike.png"))
        
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
        # Ground floor - complete coverage across entire width
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        
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
        
        # Spikes positioned on top of ground platform
        hazards.add(Hazard(125, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(275, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(425, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(575, HEIGHT-70, 50, 20, "Asset/spike.png"))
        
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
        # Ground floor - complete coverage across entire width
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        
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
        
        # Spikes positioned on top of ground platform
        hazards.add(Hazard(112, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(237, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(362, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(487, HEIGHT-70, 50, 20, "Asset/spike.png"))
        hazards.add(Hazard(612, HEIGHT-70, 50, 20, "Asset/spike.png"))
        
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
        # Ground floor - complete coverage across entire width
        platforms.add(Platform(0, HEIGHT-50, WIDTH, 50, "Asset/ground_platform.png"))
        
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
        
        # Spikes positioned on top of ground platform
        hazards.add(Hazard(90, HEIGHT-70, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(190, HEIGHT-70, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(290, HEIGHT-70, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(390, HEIGHT-70, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(490, HEIGHT-70, 40, 20, "Asset/spike.png"))
        hazards.add(Hazard(590, HEIGHT-70, 40, 20, "Asset/spike.png"))
        
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

def load_platformer_music():
    """Load platformer music files"""
    global shah_sound
    try:
        shah_sound = pygame.mixer.Sound("Asset/shah.mp3")
    except pygame.error:
        print("Warning: Could not load shah.mp3")
        shah_sound = None

def stop_all_music():
    """Stop all music and sound effects"""
    global current_music
    pygame.mixer.music.stop()
    pygame.mixer.stop()  # Stop all sound effects too
    current_music = None

def play_platformer_music(stage_num):
    """Play appropriate music for the current stage"""
    global current_music
    
    # Stop current music
    if current_music:
        pygame.mixer.music.stop()
        current_music = None
    
    try:
        if stage_num < 5:  # Stages 0-4 (before boss)
            pygame.mixer.music.load("Asset/ambient.mp3")
            pygame.mixer.music.play(-1)  # Loop indefinitely
            current_music = "ambient"
        elif stage_num == 5:  # Boss stage
            pygame.mixer.music.load("Asset/boss_music.mp3")
            pygame.mixer.music.play(-1)  # Loop indefinitely
            current_music = "boss"
    except pygame.error:
        print(f"Warning: Could not load music for stage {stage_num}")

def init_platformer():
    global player_group, player, platformer_initialized, current_stage, shah_timer
    player_group.empty()
    player = PlatPlayer(50, HEIGHT-100)
    player_group.add(player)
    current_stage = 0
    setup_stage(current_stage)
    platformer_initialized = True
    shah_timer = 0  # Reset shah timer
    play_platformer_music(current_stage)  # Start music for stage 0

# ----- Main loop -----
# Load platformer music at startup
load_platformer_music()

running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Handle Guitar Hero game events
            if game_state == "guitar_hero" and guitar_hero_game is not None:
                guitar_hero_game.handle_event(event)
            
            # Developer skip
            if event.unicode == "*":
                # Special handling for doom game skip
                if game_state == "doom":
                    # Create skip signal file for doom game
                    skip_file = "doom_skip_signal.txt"
                    with open(skip_file, "w") as f:
                        f.write("skip")
                    print("Skip signal sent to doom game")
                elif game_state == "guitar_hero":
                    # Skip the Guitar Hero game
                    if guitar_hero_game is not None:
                        guitar_hero_game.skip()
                    stop_all_music()  # Stop guitar hero music
                    print("Guitar Hero game skipped")
                else:
                    # Normal skip for other states
                    stop_all_music()  # Stop any current music
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
                    elif game_state == "cutscene3_5":
                        displayed_text3_5 = ""
                        text_index3_5 = 0
                    elif game_state == "cutscene4":
                        displayed_text4 = ""
                        text_index4 = 0
                    elif game_state == "cutscene5":
                        displayed_text5 = ""
                        text_index5 = 0
            
            # Handle other key events
            if event.key == pygame.K_RETURN:
                if game_state == "menu":
                    game_state = "cutscene"
                elif game_state == "cutscene" and text_index >= len(cutscene_text):
                    game_state = "snake"
                    snake = Snake()
                    apple = Apple(snake)
                    snake_win = False
                elif game_state == "snake" and snake is not None and not snake.alive:
                    snake = Snake()
                    apple = Apple(snake)
                    snake_win = False
                elif game_state == "snake" and snake is not None and snake.size >= 20 and snake_win:
                    game_state = "cutscene2"
                    stop_all_music()  # Stop snake game music
                elif game_state == "cutscene2" and text_index2 >= len(cutscene2_text):
                    game_state = "platformer"
                elif game_state == "cutscene3" and text_index3 >= len(cutscene3_text):
                    game_state = "guitar_hero"
                    guitar_hero_game_running = False
                    guitar_hero_game_launched = False
                elif game_state == "guitar_hero" and guitar_hero_completed:
                    game_state = "cutscene3_5"
                    stop_all_music()  # Stop guitar hero music
                elif game_state == "cutscene3_5" and text_index3_5 >= len(cutscene3_5_text):
                    game_state = "adventure"
                    adventure_completed = False
                elif game_state == "adventure" and adventure_completed:
                    game_state = "cutscene4"
                    stop_all_music()  # Stop adventure game music
                elif game_state == "cutscene4" and text_index4 >= len(cutscene4_text):
                    game_state = "doom"
                    doom_game_running = False
                    doom_game_launched = False
                elif game_state == "cutscene5" and text_index5 >= len(cutscene5_text):
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
        # Initialize snake and apple if they don't exist
        if snake is None:
            snake = Snake()
            apple = Apple(snake)
            snake_win = False
        
        keys = pygame.key.get_pressed()
        if snake is not None:
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
            if snake is not None:
                snake.update()
                if snake.alive and apple is not None and snake.body[0] == apple.position:
                    snake.grow = True
                    apple.position = apple.random_position(snake)

        screen.fill(BLACK)
        if apple is not None:
            apple.draw(screen)
        if snake is not None:
            snake.draw(screen)
        if snake is not None and not snake.alive:
            message_surface = font.render("Try again (Reach Size = 20 to continue)", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        if snake is not None and snake.size >= 20 and not snake_win:
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
        
        # Shah sound effect during boss stage (every 8 seconds)
        if current_stage == max_stages - 1:  # Boss stage
            shah_timer += 1
            if shah_timer >= shah_interval:
                if shah_sound:
                    shah_sound.play()
                shah_timer = 0

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
            # Only change music when transitioning to boss stage (stage 5)
            if current_stage == 5:
                play_platformer_music(current_stage)  # Switch to boss music
            shah_timer = 0  # Reset shah timer for new stage
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
                    stop_all_music()  # Stop platformer music
                    break

        # Stage indicator
        stage_text = small_font.render(f"Stage: {current_stage + 1}/{max_stages}", True, NEON_GREEN)
        screen.blit(stage_text, (10, 10))

    # ----- GUITAR HERO GAME -----
    elif game_state == "guitar_hero":
        if not guitar_hero_game_launched:
            # Initialize the Guitar Hero game only once
            guitar_hero_game_launched = True
            guitar_hero_game_running = True
            guitar_hero_game = GuitarHeroGame(screen)
        
        if guitar_hero_game is not None:
            # Update the game
            result = guitar_hero_game.update()
            
            if result == "skipped":
                # Skip directly to next cutscene
                game_state = "cutscene3_5"
                displayed_text3_5 = ""
                text_index3_5 = 0
                stop_all_music()  # Stop guitar hero music
                guitar_hero_game_running = False
                guitar_hero_game = None
                # Continue to next frame to avoid staying in guitar_hero state
                continue
            elif result == "completed":
                # Guitar Hero completed normally (target score reached)
                guitar_hero_completed = True
                guitar_hero_game_running = False
                guitar_hero_game = None
                screen.fill(BLACK)
                message_surface = font.render("GUITAR HERO COMPLETED!", True, NEON_GREEN)
                screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
                screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))
            else:
                # Game is still playing, draw it
                guitar_hero_game.draw()
        else:
            # Guitar Hero game already completed, just show the completion screen or wait for input
            if guitar_hero_completed:
                screen.fill(BLACK)
                message_surface = font.render("GUITAR HERO COMPLETED!", True, NEON_GREEN)
                screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
                screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))
            else:
                # Show loading or waiting screen
                screen.fill(BLACK)
                message_surface = font.render("GUITAR HERO", True, NEON_GREEN)
                screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                prompt_surface = small_font.render("Press * to skip", True, NEON_GREEN)
                screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # ----- ADVENTURE GAME -----
    elif game_state == "adventure":
        # Run the adventure game
        adventure_result = run_adventure_game()
        
        # Handle different return values
        if adventure_result == "skipped":
            # Skip directly to next cutscene
            game_state = "cutscene4"
            displayed_text4 = ""
            text_index4 = 0
            stop_all_music()  # Stop adventure game music
        elif adventure_result:
            # Adventure completed normally
            adventure_completed = True
            screen.fill(BLACK)
            message_surface = font.render("ADVENTURE COMPLETED!", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))
        else:
            # Adventure ended unexpectedly
            screen.fill(BLACK)
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

    # ----- CUTSCENE 3.5 (after Guitar Hero) -----
    elif game_state == "cutscene3_5":
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed
        screen.fill(BLACK)
        
        # Draw puppet
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 2 - 50))
        
        # Typewriter effect for cutscene3_5
        text_timer3_5 += 1
        if text_timer3_5 % typing_speed == 0 and text_index3_5 < len(cutscene3_5_text):
            displayed_text3_5 += cutscene3_5_text[text_index3_5]
            text_index3_5 += 1
        
        # Draw text
        draw_text_wrap(screen, displayed_text3_5, font, NEON_GREEN, 20, text_y_start, text_max_width)
        
        # Draw cursor
        if text_index3_5 < len(cutscene3_5_text):
            cursor_timer3_5 += 1
            if cursor_timer3_5 % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text3_5, font, text_max_width, 20, text_y_start)
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
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    # ----- DOOM GAME -----
    elif game_state == "doom":
        if not doom_game_launched:
            # Launch the doom game only once
            doom_game_launched = True
            doom_game_running = True
            doom_result = run_doom_game(screen)
            
            # Handle different return values
            if doom_result == "skipped":
                # Skip directly to next cutscene
                game_state = "cutscene5"
                displayed_text5 = ""
                text_index5 = 0
                stop_all_music()  # Stop doom game music
                doom_game_running = False
                # Continue to next frame to avoid staying in doom state
                continue
            elif doom_result:
                # Doom completed normally - go directly to cutscene5
                game_state = "cutscene5"
                displayed_text5 = ""
                text_index5 = 0
                stop_all_music()  # Stop doom game music
                doom_game_running = False
                # Continue to next frame to avoid staying in doom state
                continue
            else:
                # Doom ended unexpectedly
                doom_game_running = False
                screen.fill(BLACK)
                message_surface = font.render("Doom game ended unexpectedly", True, NEON_GREEN)
                screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
                screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))
        else:
            # Doom game already launched, show loading or waiting screen
            screen.fill(BLACK)
            message_surface = font.render("DOOM GAME", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            prompt_surface = small_font.render("Press * to skip", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))


    # ----- CUTSCENE 5 (after doom game) -----
    elif game_state == "cutscene5":
        puppet_timer += 1
        if puppet_timer % 10 == 0:
            current_puppet = puppet_open if current_puppet == puppet_closed else puppet_closed
        screen.fill(BLACK)
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))
        text_timer5 += 1
        if text_timer5 % typing_speed == 0 and text_index5 < len(cutscene5_text):
            displayed_text5 += cutscene5_text[text_index5]
            text_index5 += 1
        draw_text_wrap(screen, displayed_text5, font, NEON_GREEN, 20, text_y_start, text_max_width)
        if text_index5 < len(cutscene5_text):
            cursor_timer5 += 1
            if cursor_timer5 % 30 < 15:
                cursor_x, cursor_y = get_last_line_position(displayed_text5, font, text_max_width, 20, text_y_start)
                cursor_surf = font.render("|", True, NEON_GREEN)
                screen.blit(cursor_surf, (cursor_x, cursor_y))
        else:
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))


    pygame.display.flip()

pygame.quit()
sys.exit()