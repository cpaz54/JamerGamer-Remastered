import pygame
import sys
import os
from settings import *
from helpers import draw_text_wrap, get_last_line_position, skip_to_next_state
from snake_game import Snake, Apple
# Import platform_final components
import sys
import os
platform_final_path = os.path.join(os.getcwd(), "platform_final")
sys.path.insert(0, platform_final_path)
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

# Platform_final game integration
def run_platform_final_game():
    """Wrapper function to run the platform_final game and return completion status"""
    # Change to platform_final directory
    original_dir = os.getcwd()
    platform_final_dir = os.path.join(original_dir, "platform_final")
    
    try:
        os.chdir(platform_final_dir)
        
        # Import platform_final wrapper module
        sys.path.insert(0, platform_final_dir)
        import platform_final_wrapper
        
        # Run the platform_final game
        platform_final_completed = platform_final_wrapper.run_platform_final_game(screen, WIDTH, HEIGHT)
        
        return platform_final_completed
        
    except Exception as e:
        print(f"Error running platform_final game: {e}")
        return False
    finally:
        # Restore original directory and path
        os.chdir(original_dir)
        if platform_final_dir in sys.path:
            sys.path.remove(platform_final_dir)

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
    "Jameson. Let's play a game. A test of your skills, a test of your luck, a test of your patience. "
    "Let's start with something simple..."
)
displayed_text = ""
text_index = 0
text_timer = 0
typing_speed = 5
cursor_timer = 0

# ----- Cutscene 2 -----
cutscene2_text = (
    "Very good. You pick up fast. Now, let's try something a little more challenging..."
    "Use WASD and the space bar to move. Press J to attack. "
    "These will be your only instructions."
)
displayed_text2 = ""
text_index2 = 0
text_timer2 = 0
cursor_timer2 = 0

# ----- Cutscene 3 (after platformer) -----
cutscene3_text = (
    "It seems you've bested us all in battle. But some challenges still await. "
    "This one is a bit more... musical."
    "Press Z X C V B to select notes, press SPACE to play them."
)
displayed_text3 = ""
text_index3 = 0
text_timer3 = 0
cursor_timer3 = 0

# ----- Cutscene 3.5 (after Guitar Hero) -----
cutscene3_5_text = (
    "Your rhythm, your sense of showmanship...remarkable. "
    "Now for something more old school... "
    "Use the arrow keys to move and E to interact."
)
displayed_text3_5 = ""
text_index3_5 = 0
text_timer3_5 = 0
cursor_timer3_5 = 0

# ----- Cutscene 4 (after adventure game) -----
cutscene4_text = (
    "Well, well, well. You've made it this far. "
    "It seems nothing can stop you now. "
    "I hope you have a mouse nearby..."
)
displayed_text4 = ""
text_index4 = 0
text_timer4 = 0
cursor_timer4 = 0

# ----- Cutscene 5 (after doom game) -----
cutscene5_text = (
    "Very good, Jameson, very good! "
    "It seems you've mastered all our tests...for now. "
    "Be a good boy and go out back behind the house...the door is unlocked."
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

# ----- Platform_final variables -----
platform_final_completed = False

# ----- Doom game variables -----
doom_game_running = False
doom_game_launched = False

# ----- Guitar Hero game variables -----
guitar_hero_game_running = False
guitar_hero_game_launched = False
guitar_hero_completed = False
guitar_hero_game = None

# ----- Adventure game variables -----
adventure_completed = False

# ----- Doom game variables -----

# ----- Platform_final functions -----

def stop_all_music():
    """Stop all music and sound effects"""
    pygame.mixer.music.stop()
    pygame.mixer.stop()  # Stop all sound effects too

# ----- Main loop -----

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
                elif game_state == "platform_final":
                    # Skip the platform_final game
                    game_state = "cutscene3"
                    platform_final_completed = True
                    stop_all_music()  # Stop platform_final music
                    
                    # Restore main game window dimensions for cutscenes
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.display.set_caption("we are watching")
                    
                    print("Platform_final game skipped")
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
                    game_state = "platform_final"
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

    # ----- PLATFORM_FINAL GAME -----
    elif game_state == "platform_final":
        # Run the platform_final game
        platform_final_result = run_platform_final_game()
        
        # Handle different return values
        if platform_final_result:
            # Platform_final completed normally - transition immediately to next cutscene
            game_state = "cutscene3"
            stop_all_music()  # Stop platform_final music
            
            # Restore main game window dimensions for cutscenes
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Multi-Game Experience")
            
            print("Platform_final completed! Transitioning to cutscene3")
        else:
            # Platform_final ended unexpectedly
            screen.fill(BLACK)
            message_surface = font.render("Platform_final game ended unexpectedly", True, NEON_GREEN)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            prompt_surface = small_font.render("Press Enter to continue...", True, NEON_GREEN)
            screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

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
            # Adventure completed normally - transition to next cutscene
            game_state = "cutscene4"
            displayed_text4 = ""
            text_index4 = 0
            stop_all_music()  # Stop adventure game music
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
        screen.blit(current_puppet, (WIDTH // 2 - 50, HEIGHT // 4 - 50))
        
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