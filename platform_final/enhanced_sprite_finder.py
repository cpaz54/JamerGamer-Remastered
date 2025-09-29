import pygame
import sys
import os

def find_sprite_coordinates_with_names():
    """
    Enhanced sprite coordinate finder that allows naming sprites.
    This will help extract boss sprites with meaningful names.
    """
    
    pygame.init()
    
    # Get the sprite sheet path from user
    print("Boss Sprite Extractor")
    print("====================")
    print("Available boss folders:")
    
    bosses_dir = "assets/bosses"
    if os.path.exists(bosses_dir):
        boss_folders = [f for f in os.listdir(bosses_dir) if os.path.isdir(os.path.join(bosses_dir, f))]
        for i, folder in enumerate(boss_folders, 1):
            print(f"{i}. {folder}")
        
        # Let user choose boss folder
        try:
            choice = int(input("\nEnter the number of the boss folder: ")) - 1
            if 0 <= choice < len(boss_folders):
                selected_boss = boss_folders[choice]
                boss_path = os.path.join(bosses_dir, selected_boss)
                print(f"\nSelected: {selected_boss}")
            else:
                print("Invalid choice!")
                return
        except ValueError:
            print("Invalid input!")
            return
    else:
        print("Bosses folder not found!")
        return
    
    # Find sprite sheet in the boss folder
    print(f"\nLooking for image files in: {boss_path}")
    all_files = os.listdir(boss_path)
    print(f"All files in folder: {all_files}")
    
    sprite_files = [f for f in all_files if f.endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Image files found: {sprite_files}")
    
    if not sprite_files:
        print(f"No image files found in {boss_path}")
        print("Available files:")
        for f in all_files:
            print(f"  {f}")
        return
    
    if len(sprite_files) == 1:
        sprite_sheet_path = os.path.join(boss_path, sprite_files[0])
    else:
        print("\nMultiple sprite files found:")
        for i, file in enumerate(sprite_files, 1):
            print(f"{i}. {file}")
        try:
            choice = int(input("Enter the number of the sprite file: ")) - 1
            if 0 <= choice < len(sprite_files):
                sprite_sheet_path = os.path.join(boss_path, sprite_files[choice])
            else:
                print("Invalid choice!")
                return
        except ValueError:
            print("Invalid input!")
            return
    
    print(f"\nUsing sprite sheet: {sprite_sheet_path}")
    
    if not os.path.exists(sprite_sheet_path):
        print(f"Error: Sprite sheet '{sprite_sheet_path}' not found!")
        return
    
    # Load the sprite sheet
    try:
        # Set a dummy display mode first for image loading
        pygame.display.set_mode((1, 1))
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        sheet_width, sheet_height = sprite_sheet.get_size()
        print(f"Loaded sprite sheet: {sheet_width}x{sheet_height}")
    except pygame.error as e:
        print(f"Error loading sprite sheet: {e}")
        return
    
    # Limit window size to prevent issues
    max_width, max_height = 1200, 800
    if sheet_width > max_width or sheet_height > max_height:
        scale_factor = min(max_width / sheet_width, max_height / sheet_height)
        display_width = int(sheet_width * scale_factor)
        display_height = int(sheet_height * scale_factor)
        print(f"Scaling down to {display_width}x{display_height} for display")
    else:
        display_width, display_height = sheet_width, sheet_height
        scale_factor = 1.0
    
    # Create a window to display the sprite sheet
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption(f"Sprite Coordinate Finder - {selected_boss}")
    
    # Scale the sprite sheet for display if needed
    if scale_factor != 1.0:
        display_sprite_sheet = pygame.transform.scale(sprite_sheet, (display_width, display_height))
    else:
        display_sprite_sheet = sprite_sheet
    
    clock = pygame.time.Clock()
    running = True
    
    # Track current sprite and corners
    current_sprite_name = ""
    sprite_corners = {}
    current_corners = []
    
    print("\nInstructions:")
    print("- Type a name for each sprite (e.g., 'idle', 'attack_left', 'attack_right', 'hurt')")
    print("- Click the 4 corners of each sprite in order: top-left, top-right, bottom-left, bottom-right")
    print("- Press SPACE to save current sprite and move to next")
    print("- Press ENTER to finish and extract all sprites")
    print("- Press ESC to exit")
    print("- Press R to reset current sprite")
    print()
    
    # Get first sprite name
    current_sprite_name = input("Enter name for first sprite: ").strip()
    if not current_sprite_name:
        current_sprite_name = "sprite_1"
    print(f"Current sprite: {current_sprite_name}")
    print("Click the 4 corners...")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Move to next sprite
                    if len(current_corners) == 4:
                        sprite_corners[current_sprite_name] = current_corners.copy()
                        print(f"✅ {current_sprite_name} completed: {current_corners}")
                        current_corners = []
                        
                        # Get next sprite name
                        current_sprite_name = input("\nEnter name for next sprite (or press ENTER to finish): ").strip()
                        if not current_sprite_name:
                            print("\n🎉 All sprites completed!")
                            print("\nFinal coordinates:")
                            for sprite_name, corners in sprite_corners.items():
                                tl, tr, bl, br = corners
                                x, y = tl
                                width = tr[0] - tl[0]
                                height = bl[1] - tl[1]
                                print(f"{sprite_name}: x={x}, y={y}, width={width}, height={height}")
                            
                            # Extract sprites
                            extract_sprites_to_folder(sprite_sheet, sprite_corners, boss_path)
                            running = False
                        else:
                            print(f"Current sprite: {current_sprite_name}")
                            print("Click the 4 corners...")
                    else:
                        print(f"⚠️ Need 4 corners for {current_sprite_name}, got {len(current_corners)}")
                elif event.key == pygame.K_RETURN:
                    # Finish and extract
                    if len(current_corners) == 4:
                        sprite_corners[current_sprite_name] = current_corners.copy()
                        print(f"✅ {current_sprite_name} completed: {current_corners}")
                    
                    print("\n🎉 All sprites completed!")
                    print("\nFinal coordinates:")
                    for sprite_name, corners in sprite_corners.items():
                        tl, tr, bl, br = corners
                        x, y = tl
                        width = tr[0] - tl[0]
                        height = bl[1] - tl[1]
                        print(f"{sprite_name}: x={x}, y={y}, width={width}, height={height}")
                    
                    # Extract sprites
                    extract_sprites_to_folder(sprite_sheet, sprite_corners, boss_path)
                    running = False
                elif event.key == pygame.K_r:
                    # Reset current sprite
                    current_corners = []
                    print(f"Reset {current_sprite_name}. Click the 4 corners...")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Convert display coordinates to original sprite coordinates
                    display_x, display_y = pygame.mouse.get_pos()
                    x = int(display_x / scale_factor)
                    y = int(display_y / scale_factor)
                    current_corners.append((x, y))
                    corner_names = ["top-left", "top-right", "bottom-left", "bottom-right"]
                    if len(current_corners) <= 4:
                        print(f"Corner {len(current_corners)} ({corner_names[len(current_corners)-1]}): x={x}, y={y}")
                    if len(current_corners) == 4:
                        print(f"✅ {current_sprite_name} corners complete! Press SPACE for next sprite or ENTER to finish.")
        
        # Draw the sprite sheet
        screen.blit(display_sprite_sheet, (0, 0))
        
        # Draw a crosshair at mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 0, 0), (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
        pygame.draw.line(screen, (255, 0, 0), (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)
        
        # Draw current sprite corners (convert to display coordinates)
        for i, (x, y) in enumerate(current_corners):
            color = (0, 255, 0) if i < 4 else (255, 0, 0)
            display_x = int(x * scale_factor)
            display_y = int(y * scale_factor)
            pygame.draw.circle(screen, color, (display_x, display_y), 5)
            pygame.draw.circle(screen, (255, 255, 255), (display_x, display_y), 3)
        
        # Draw completed sprite rectangles (convert to display coordinates)
        for sprite_name, corners in sprite_corners.items():
            if len(corners) == 4:
                tl, tr, bl, br = corners
                x, y = tl
                width = tr[0] - tl[0]
                height = bl[1] - tl[1]
                # Convert to display coordinates
                display_x = int(x * scale_factor)
                display_y = int(y * scale_factor)
                display_width = int(width * scale_factor)
                display_height = int(height * scale_factor)
                pygame.draw.rect(screen, (0, 255, 0), (display_x, display_y, display_width, display_height), 2)
                # Draw sprite label
                font = pygame.font.Font(None, 24)
                text = font.render(sprite_name, True, (0, 255, 0))
                screen.blit(text, (display_x, display_y - 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    try:
        pygame.quit()
    except:
        pass

def extract_sprites_to_folder(sprite_sheet, sprite_corners, output_folder):
    """Extract sprites to the boss folder with their names"""
    
    print(f"\nExtracting sprites to {output_folder}...")
    
    for sprite_name, corners in sprite_corners.items():
        if len(corners) == 4:
            tl, tr, bl, br = corners
            x, y = tl
            width = tr[0] - tl[0]
            height = bl[1] - tl[1]
            
            # Extract sprite
            sprite_rect = pygame.Rect(x, y, width, height)
            sprite = sprite_sheet.subsurface(sprite_rect)
            
            # Save with the sprite name
            output_path = os.path.join(output_folder, f"{sprite_name}.png")
            pygame.image.save(sprite, output_path)
            print(f"Extracted {sprite_name} → {output_path}")
    
    print(f"✅ Successfully extracted {len(sprite_corners)} sprites!")

if __name__ == "__main__":
    find_sprite_coordinates_with_names()
