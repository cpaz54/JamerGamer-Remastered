'''Adventure game module for integration with main game'''
import pygame
import os

def run_adventure_game(screen):
    """Run the adventure game and return completion status"""
    # Change to adventure game directory
    adventure_dir = os.path.dirname(os.path.abspath(__file__))
    original_dir = os.getcwd()
    
    try:
        os.chdir(adventure_dir)
        
        # Import the main adventure game function
        from main import main
        
        # Run the adventure game main function with the provided screen
        # The main function will return True when both NPCs are talked to
        adventure_completed = main(screen)
        
        # Return the completion status
        return adventure_completed
        
    except Exception as e:
        print(f"Error running adventure game: {e}")
        return False
    finally:
        os.chdir(original_dir)
