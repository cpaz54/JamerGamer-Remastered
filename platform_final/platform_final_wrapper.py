import pygame
import sys
import os

# Ensure we're using the platform_final settings
# Remove any existing settings from sys.modules to force reload
if 'settings' in sys.modules:
    del sys.modules['settings']

# Force the platform_final directory to be first in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from main import Platformer

def run_platform_final_game(screen, width, height):
    """Wrapper function to run the platform_final game and return completion status"""
    try:
        # Use platform_final's own settings for proper visuals
        from settings import WIDTH as PF_WIDTH, HEIGHT as PF_HEIGHT
        
        # Create a completely separate window for platform_final
        platform_final_screen = pygame.display.set_mode((PF_WIDTH, PF_HEIGHT))
        pygame.display.set_caption("Platformer")
        
        # Create the platformer with its own screen
        platformer = Platformer(platform_final_screen, PF_WIDTH, PF_HEIGHT)
        
        # Create the world object
        from world import World
        world = World(platform_final_screen)
        
        # Run the game loop with completion detection
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    # Close the platform_final window properly
                    pygame.display.quit()
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        platformer.keys_pressed["left"] = True
                    if event.key == pygame.K_d:
                        platformer.keys_pressed["right"] = True
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        platformer.keys_pressed["jump"] = True
                    if event.key == pygame.K_j:  # J key for sword swing
                        platformer.sword_just_pressed = True
                    if event.key == pygame.K_F1:  # F1 key for stage skip
                        platformer.skip_requested = True
                    if event.unicode == "*":  # * key for entire game skip
                        print("Platformer game skipped via * key")
                        return True  # Return True to indicate completion/skip
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        platformer.keys_pressed["left"] = False
                    if event.key == pygame.K_d:
                        platformer.keys_pressed["right"] = False
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        platformer.keys_pressed["jump"] = False
            
            # Draw background first
            if hasattr(world, 'burning_cathedral_background') and world.burning_cathedral_background is not None:
                platform_final_screen.blit(world.burning_cathedral_background, (0, 0))
            elif hasattr(world, 'cathedral_background') and world.cathedral_background is not None:
                platform_final_screen.blit(world.cathedral_background, (0, 0))
            else:
                platform_final_screen.blit(platformer.bg_img, (0, 0))
            
            # Determine player event based on current key states
            player_event = platformer._get_player_event()
            
            # Check if the game has completed (player won) BEFORE updating world
            # This prevents the restart logic from interfering
            # Only trigger completion when Dread Knight is spawned AND defeated
            if (hasattr(world, 'player') and world.player.sprite and
                hasattr(world.player.sprite, 'win') and world.player.sprite.win and
                hasattr(world, 'current_boss') and world.current_boss == "DREAD_KNIGHT" and
                hasattr(world, 'boss') and world.boss.sprite and
                hasattr(world.boss.sprite, 'victory_state') and world.boss.sprite.victory_state == "reward_showing"):
                # Player defeated the Dread Knight and hit the reward - game complete!
                print("Platform_final completed! Dread Knight defeated and reward collected! Returning to main game...")
                return True
            
            # Update world with error handling for stage transitions
            try:
                world.update(player_event, platformer.skip_requested, platformer.sword_just_pressed)
            except Exception as e:
                print(f"Error during world update: {e}")
                # Continue running the game even if there's an error
                pass
            
            # Draw fade overlay if fading
            if hasattr(world, 'is_fading') and world.is_fading and world.fade_alpha > 0:
                fade_surface = pygame.Surface((PF_WIDTH, PF_HEIGHT))
                fade_surface.fill((255, 255, 255))  # White
                fade_surface.set_alpha(int(world.fade_alpha))
                platform_final_screen.blit(fade_surface, (0, 0))
            
            # Draw white flash for DreadKnight transformation
            if (hasattr(world, 'boss') and world.boss.sprite and 
                hasattr(world.boss.sprite, 'second_phase') and world.boss.sprite.second_phase and
                hasattr(world.boss.sprite, 'phase2_state') and world.boss.sprite.phase2_state == "flash"):
                flash_surface = pygame.Surface((PF_WIDTH, PF_HEIGHT))
                flash_surface.fill((255, 255, 255))  # White flash
                flash_surface.set_alpha(255)  # Full opacity
                platform_final_screen.blit(flash_surface, (0, 0))
            
            # Reset flags after processing
            if platformer.skip_requested:
                platformer.skip_requested = False
            if platformer.sword_just_pressed:
                platformer.sword_just_pressed = False
            
            pygame.display.flip()
            clock.tick(60)
        
        return False  # Game ended without completion
        
    except Exception as e:
        print(f"Error running platform_final game: {e}")
        return False
