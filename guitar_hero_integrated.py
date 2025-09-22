# Guitar Hero - Integrated Version (Following Snake/Platformer Pattern)
import pygame
import time
import os

class GuitarHeroGame:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Initialize the original guitar hero variables (from guitarhero_elo.py)
        self.curTime = time.time()
        self.deltaTime = 0
        self.startTime = 0
        self.score = 0
        self.bps = 100.5  # Adjust this if needed for your song's tempo
        self.firstTime = True
        self.counters = []
        self.shine = [0, 0, 0, 0, 0]
        self.gameEnded = False
        self.restartTime = 0
        self.skipped = False
        
        # Load original assets from guitar-hero-source-code folder
        self.load_assets()
        
        # Fonts for drawing
        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 30)
        
        # Initialize counters with original data
        self.init_counters()
        
    def load_assets(self):
        """Load original images and music from guitar-hero-source-code folder"""
        guitar_hero_dir = os.path.join(os.path.dirname(__file__), 'guitar-hero', 'guitar-hero-source-code')
        
        # Load background image
        bg_path = os.path.join(guitar_hero_dir, 'images', 'background.png')
        if os.path.exists(bg_path):
            self.background_image = pygame.image.load(bg_path)
        else:
            # Fallback: create a black background
            self.background_image = pygame.Surface((800, 600))
            self.background_image.fill((0, 0, 0))
        
        # Load counter images (counter0.png, counter1.png, etc.)
        self.counter_images = []
        for i in range(5):
            counter_path = os.path.join(guitar_hero_dir, 'images', f'counter{i}.png')
            if os.path.exists(counter_path):
                self.counter_images.append(pygame.image.load(counter_path))
            else:
                # Fallback: create colored circles
                fallback = pygame.Surface((30, 30))
                colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
                fallback.fill(colors[i])
                self.counter_images.append(fallback)
        
        # Load shine effect image
        shine_path = os.path.join(guitar_hero_dir, 'images', 'shine.png')
        if os.path.exists(shine_path):
            self.shine_image = pygame.image.load(shine_path)
        else:
            # Fallback: create a white circle
            self.shine_image = pygame.Surface((50, 50))
            pygame.draw.circle(self.shine_image, (255, 255, 255), (25, 25), 25)
        
        # Load music
        music_path = os.path.join(guitar_hero_dir, 'music', 'elo.mp3')
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                self.music_available = True
            except:
                self.music_available = False
        else:
            self.music_available = False
        
    def init_counters(self):
        """Initialize counters using EXACT original counterPoints data from guitarhero_elo.py"""
        self.counters = []
        
        # EXACT counterPoints from guitarhero_elo.py - copied directly
        counterPoints = [
            (2, 5.3), (3, 5.6), (2, 6.0), (3, 6.4), (2, 6.8), (3, 7.2), (2, 7.6), (3, 8.0),
            (2, 8.4), (3, 8.9), (2, 9.3), (3, 9.7), (2, 10.2), (3, 10.6), (2, 11.0), (3, 11.4),
            (4, 11.8), (2, 12.3), (3, 12.7), (2, 13.1), (4, 13.5), (2, 14.0), (3, 14.4), (2, 14.8),
            (4, 15.3), (2, 15.7), (3, 16.1), (2, 16.5), (4, 16.9), (2, 17.3), (3, 17.7), (2, 18.1),
            (4, 18.6), (2, 19.0), (3, 19.4), (2, 19.8), (4, 20.2), (2, 20.7), (3, 21.1), (2, 21.5),
            (4, 22.0), (2, 22.4), (3, 22.8), (2, 23.2), (3, 23.7), (2, 24.1), (3, 24.5), (2, 24.9),
            (1, 25.3), (2, 25.7), (3, 26.2), (2, 26.6), (1, 27.0), (2, 27.4), (3, 27.9), (2, 28.3),
            (1, 28.7), (2, 29.1), (3, 29.5), (2, 29.9), (0, 30.4), (2, 30.8), (3, 31.2), (2, 31.6),
            (1, 32.1), (2, 32.5), (3, 32.9), (2, 33.3), (4, 33.8), (2, 34.2), (3, 34.6), (2, 35.0),
            (1, 35.4), (2, 35.8), (3, 36.3), (2, 36.7), (1, 37.1), (2, 37.5), (3, 37.9), (2, 38.4),
            (4, 38.8), (2, 39.2), (3, 39.6), (2, 40.0), (1, 40.5), (2, 40.9), (3, 41.3), (2, 41.7),
            (1, 42.1), (2, 42.6), (3, 43.0), (2, 43.4), (1, 43.8), (2, 44.3), (3, 44.7), (2, 45.1),
            (4, 45.5), (2, 46.0), (3, 46.4), (2, 46.8), (4, 47.2), (2, 47.6), (3, 48.1), (2, 48.5),
            (4, 48.9), (2, 49.3), (3, 49.7), (2, 50.2), (4, 50.6), (2, 51.0), (3, 51.4), (2, 51.8),
            (1, 52.3), (2, 52.7), (3, 53.1), (2, 53.5), (1, 54.0), (2, 54.4), (3, 54.8), (2, 55.2),
            (1, 55.7), (2, 56.1), (3, 56.5), (2, 56.9), (1, 57.3), (2, 57.8), (3, 58.2), (2, 58.6),
            (1, 59.0), (2, 59.4), (3, 59.8), (4, 60.2), (2, 60.7), (3, 61.1), (2, 61.5), (1, 61.9),
            (2, 62.4), (3, 62.8), (4, 63.2), (3, 63.6), (2, 64.0), (1, 64.4), (0, 64.9), (1, 65.3),
            (2, 65.5), (0, 66.1), (2, 66.1), (2, 66.3), (0, 66.3), (0, 66.6), (2, 66.6), (2, 66.8),
            (0, 66.8), (0, 67.0), (2, 67.0), (0, 67.2), (2, 67.2), (2, 67.4), (0, 67.4), (2, 67.7),
            (0, 67.7), (0, 67.9), (2, 67.9), (2, 68.1), (0, 68.1), (2, 68.3), (0, 68.3), (0, 68.5),
            (2, 68.5), (0, 68.7), (2, 68.7), (0, 68.9), (2, 69.0), (3, 69.2), (1, 69.2), (1, 69.4),
            (3, 69.4), (1, 69.6), (3, 69.6), (1, 69.8), (3, 69.8), (1, 70.0), (3, 70.0), (1, 70.2),
            (3, 70.2), (1, 70.4), (3, 70.4), (1, 70.6), (3, 70.6), (3, 70.8), (1, 70.8), (1, 71.0),
            (3, 71.0), (1, 71.2), (3, 71.2), (1, 71.4), (3, 71.4), (1, 71.6), (3, 71.6), (3, 71.9),
            (1, 71.9), (1, 72.1), (3, 72.1), (3, 72.3), (1, 72.3), (0, 72.5), (2, 72.5), (0, 72.7),
            (2, 72.7), (0, 73.0), (2, 73.0), (0, 73.2), (2, 73.2), (0, 73.4), (2, 73.4), (0, 73.6),
            (2, 73.6), (0, 73.8), (2, 73.8), (0, 74.0), (2, 74.0), (0, 74.2), (2, 74.2), (0, 74.4),
            (2, 74.4), (0, 74.6), (2, 74.6), (0, 74.8), (2, 74.8), (2, 75.0), (0, 75.0), (0, 75.2),
            (2, 75.2), (2, 75.4), (0, 75.4), (2, 75.6), (0, 75.7), (0, 75.9), (2, 75.9), (2, 76.1),
            (0, 76.1), (0, 76.3), (2, 76.3), (0, 76.5), (2, 76.5), (0, 76.7), (2, 76.7), (0, 76.9),
            (2, 76.9), (0, 77.1), (2, 77.1), (0, 77.3), (2, 77.4), (2, 77.6), (0, 77.6), (0, 77.8),
            (2, 77.8), (0, 78.0), (2, 78.0), (0, 78.2), (2, 78.2), (0, 78.4), (2, 78.4), (2, 78.6),
            (0, 78.8), (2, 78.8), (0, 79.0), (2, 79.0), (1, 79.6), (3, 79.7), (1, 79.9), (3, 79.9),
            (3, 80.1), (1, 80.1), (3, 80.3), (1, 80.3), (3, 80.5), (1, 80.5), (1, 80.7), (3, 80.7),
            (1, 80.9), (3, 80.9), (1, 81.2), (3, 81.2), (3, 81.4), (1, 81.4), (1, 81.6), (3, 81.6),
            (1, 81.8), (3, 81.8), (1, 82.0), (1, 82.2), (3, 82.2), (3, 82.4), (1, 82.4), (2, 82.7),
            (4, 82.7), (2, 82.9), (4, 82.9), (2, 83.1), (4, 83.1), (4, 83.3), (2, 83.3), (2, 83.5),
            (4, 83.5), (4, 83.7), (2, 83.7), (2, 83.9), (4, 83.9), (4, 84.1), (2, 84.1), (4, 84.3),
            (2, 84.3), (4, 84.5), (2, 84.5), (2, 84.7), (4, 84.7), (4, 84.9), (2, 85.0), (3, 85.2),
            (1, 85.2), (1, 85.4), (3, 85.4), (3, 85.6), (1, 85.6), (3, 85.8), (1, 85.8), (0, 86.0),
            (2, 86.0), (0, 86.2), (2, 86.2), (2, 86.4), (0, 86.4), (2, 86.6), (0, 86.6), (0, 86.8),
            (2, 86.9), (2, 87.1), (0, 87.1), (0, 87.3), (2, 87.3), (0, 87.5), (2, 87.5), (3, 87.7),
            (1, 87.7), (1, 87.9), (3, 87.9), (1, 88.1), (3, 88.1), (1, 88.3), (3, 88.3), (3, 88.5),
            (1, 88.5), (1, 88.8), (3, 88.8), (3, 89.0), (1, 89.0), (3, 89.1), (1, 89.1), (0, 89.4),
            (2, 89.4), (2, 89.6), (0, 89.6), (0, 89.8), (2, 89.8), (2, 90.0), (0, 90.0), (2, 90.2),
            (0, 90.2), (2, 90.5), (0, 90.5), (0, 90.6), (2, 90.6), (0, 90.9), (2, 90.9), (2, 91.1),
            (0, 91.1), (0, 91.8), (2, 92.3), (1, 92.7), (0, 93.6), (1, 93.9), (2, 94.4), (4, 95.2),
            (3, 95.5), (2, 96.1), (0, 97.8), (1, 98.1), (2, 98.6), (3, 99.0), (4, 99.5), (3, 99.8),
            (2, 100.1), (1, 100.6), (0, 101.1), (1, 101.5), (2, 101.9), (3, 102.3), (4, 102.7), (3, 103.1),
            (2, 103.6), (1, 104.0), (0, 104.5), (1, 105.8), (0, 106.2), (1, 107.9), (0, 109.7), (0, 111.2),
            (1, 111.6), (2, 112.1), (3, 112.5), (4, 112.9), (3, 113.8), (2, 114.2), (3, 114.7), (2, 115.1),
            (3, 115.5), (2, 115.9), (3, 116.4), (2, 116.8), (3, 117.2), (2, 117.6), (1, 118.0), (2, 118.5),
            (3, 118.9), (2, 119.3), (3, 119.7), (2, 120.1), (3, 120.6), (1, 121.0), (3, 121.4), (2, 121.8),
            (3, 122.2), (2, 122.6), (1, 123.0), (2, 123.5), (3, 123.9), (2, 124.3), (4, 124.7), (2, 125.2),
            (3, 125.6), (2, 126.0), (1, 126.4), (2, 126.8), (3, 127.3), (2, 127.7), (4, 128.1), (2, 128.5),
            (3, 129.0), (2, 129.4), (1, 129.8), (2, 130.2), (3, 130.7), (2, 131.1), (0, 131.4), (2, 131.9),
            (3, 132.3), (2, 132.7), (0, 133.2), (2, 133.6), (3, 134.0), (2, 134.4), (0, 134.8), (2, 135.3),
            (3, 135.7), (2, 136.1), (0, 136.5), (2, 137.0), (3, 137.8), (2, 138.6), (1, 139.5), (2, 140.3),
            (3, 141.2), (3, 141.6), (2, 142.0), (3, 142.4), (2, 142.9), (3, 143.3), (4, 143.7), (2, 144.1),
            (3, 144.5), (1, 144.9), (2, 145.4), (3, 145.8), (2, 146.2), (1, 146.7), (2, 147.1), (3, 147.5),
            (2, 147.9), (1, 148.3), (2, 148.8), (3, 149.2), (0, 149.6), (3, 150.5), (4, 150.8), (0, 153.0),
            (1, 153.3), (2, 154.6), (3, 155.0), (4, 155.4), (3, 155.9), (2, 156.3), (1, 156.7), (2, 157.1),
            (3, 157.5), (4, 158.0), (3, 158.4), (2, 160.1), (1, 161.0), (2, 161.8), (3, 162.2), (2, 162.6),
            (3, 163.1), (4, 163.5), (3, 163.9), (2, 164.3), (3, 164.8), (1, 165.2), (0, 165.2), (1, 165.6),
            (0, 165.6), (0, 166.0), (1, 166.0), (0, 166.5), (1, 166.5), (1, 166.9), (2, 166.9), (1, 167.3),
            (2, 167.3), (1, 167.8), (2, 167.8), (1, 168.1), (2, 168.1), (3, 168.6), (2, 168.6), (2, 169.0),
            (3, 169.0), (2, 169.4), (3, 169.4), (2, 169.8), (3, 169.8), (3, 170.3), (4, 170.3), (3, 170.7),
            (4, 170.7), (3, 171.1), (3, 171.5), (4, 171.5), (2, 171.9), (3, 171.9), (0, 175.5), (1, 175.5),
            (0, 180.4), (0, 180.6), (0, 180.8), (0, 181.0), (1, 181.3), (1, 181.5), (1, 181.7), (1, 181.9),
            (2, 182.1), (2, 182.3), (2, 182.5), (2, 182.7), (3, 183.1), (3, 183.3), (3, 183.5), (3, 183.8),
            (4, 184.0), (4, 184.2), (4, 184.4), (4, 184.6), (3, 184.8), (3, 185.0), (3, 185.2), (3, 185.5),
            (2, 185.7), (2, 185.9), (2, 186.1), (2, 186.3), (1, 186.5), (1, 186.7), (1, 186.9), (1, 187.2)
        ]
        
        # Create note objects using EXACT original logic
        for c in counterPoints:
            note = {
                'x': 300 + (c[0] * 50),  # EXACT original calculation
                'y': (c[1] - 9.9) * -50,  # EXACT original calculation
                'state': 1,  # EXACT original state
                'column': c[0]  # Store column for image selection
            }
            self.counters.append(note)
    
    def handle_event(self, event):
        """Handle keyboard events using EXACT original on_key_down logic"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # EXACT original logic from on_key_down function
                for c in self.counters:
                    if c['y'] > 490 and c['y'] < 525:  # EXACT original hit detection
                        if c['x'] == 300 and pygame.key.get_pressed()[pygame.K_z]: 
                            self.note_correct(0)
                        if c['x'] == 350 and pygame.key.get_pressed()[pygame.K_x]: 
                            self.note_correct(1)
                        if c['x'] == 400 and pygame.key.get_pressed()[pygame.K_c]: 
                            self.note_correct(2)
                        if c['x'] == 450 and pygame.key.get_pressed()[pygame.K_v]: 
                            self.note_correct(3)
                        if c['x'] == 500 and pygame.key.get_pressed()[pygame.K_b]: 
                            self.note_correct(4)
    
    def update(self):
        """Update game state using EXACT original update logic"""
        if self.skipped:
            return "skipped"
            
        # EXACT original update logic
        if self.gameEnded and self.curTime >= self.restartTime:
            self.restart_game()
            return "playing"
        
        if self.firstTime:
            # Play music if available
            if self.music_available:
                try:
                    pygame.mixer.music.play(-1)  # Loop the music
                except:
                    pass
            self.startTime = time.time()
            self.firstTime = False
            
        self.deltaTime = time.time() - self.curTime
        self.curTime = time.time()
        self.update_counters()
        
        # Check for completion
        if self.curTime - self.startTime > 190:
            if self.score >= 9000:
                return "completed"
        
        return "playing"
    
    def update_counters(self):
        """Update note positions using EXACT original updateCounters logic"""
        for c in self.counters:
            c['y'] += (self.bps / 2) * self.deltaTime  # EXACT original calculation
    
    def note_correct(self, column):
        """Handle correct note hit using EXACT original noteCorrect logic"""
        self.shine[column] = 10  # EXACT original logic
        self.score += 10  # EXACT original scoring
    
    def restart_game(self):
        """Restart the game using EXACT original restartGame logic"""
        self.score = 0
        self.firstTime = True
        self.gameEnded = False
        self.restartTime = 0
        self.shine = [0, 0, 0, 0, 0]
        
        # Stop and restart music
        if self.music_available:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(-1)
            except:
                pass
        
        # Recreate all counters
        self.init_counters()
        
        # Restart timing
        self.startTime = time.time()
        self.curTime = time.time()
        
        print("Game restarted! Try to get 9000 points!")
    
    def draw(self):
        """Draw the game using EXACT original draw logic"""
        # Use original drawBackground function
        self.draw_background()
        
        # Use original drawCounters function
        self.draw_counters()
        
        # Draw shine effects (EXACT original logic)
        for s in range(5):
            if self.shine[s] > 0:
                self.screen.blit(self.shine_image, (230 + (s * 50), 450))  # EXACT original positioning
                self.shine[s] -= 1
        
        # Draw score (EXACT original positioning)
        score_text = self.font.render(f"SCORE: {self.score}", True, (0, 0, 255))
        self.screen.blit(score_text, (self.width // 2 - 100, self.height - 50))
        
        # EXACT original end game logic
        if self.curTime - self.startTime > 190:
            if self.score >= 9000:
                # EXACT original success message
                congrats1 = self.font.render("WELL DONE! YOU ARE A", True, (255, 0, 0))
                congrats2 = self.font.render("TRUE TURN AND COUGHER", True, (255, 0, 0))
                
                self.screen.blit(congrats1, (self.width // 2 - 200, self.height // 2 - 40))
                self.screen.blit(congrats2, (self.width // 2 - 200, self.height // 2))
            else:
                # EXACT original failure message
                if not self.gameEnded:
                    self.gameEnded = True
                    self.restartTime = self.curTime + 3
                
                fail_text = self.font.render("Nice try, hit 9000 to move on", True, (255, 255, 0))
                score_text = self.small_font.render(f"Your score: {self.score}/9000", True, (255, 255, 0))
                time_left = max(0, self.restartTime - self.curTime)
                restart_text = self.small_font.render(f"Song will restart in {time_left:.0f} seconds...", True, (255, 255, 0))
                
                self.screen.blit(fail_text, (self.width // 2 - 200, self.height // 2 - 20))
                self.screen.blit(score_text, (self.width // 2 - 100, self.height // 2 + 20))
                self.screen.blit(restart_text, (self.width // 2 - 150, self.height // 2 + 50))
    
    def draw_background(self):
        """Draw background using EXACT original drawBackground logic"""
        # Get screen dimensions
        screen_width = self.width
        screen_height = self.height
        
        # Get background image dimensions
        bg_width, bg_height = self.background_image.get_size()
        
        # Calculate scaling to fill the screen while maintaining aspect ratio
        scale_x = screen_width / bg_width
        scale_y = screen_height / bg_height
        
        # Use the larger scale to ensure the image covers the entire screen
        scale = max(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(bg_width * scale)
        new_height = int(bg_height * scale)
        
        # Calculate offset to center the image
        offset_x = (screen_width - new_width) // 2
        offset_y = (screen_height - new_height) // 2
        
        # Scale the background image
        scaled_bg = pygame.transform.scale(self.background_image, (new_width, new_height))
        
        # Draw the scaled background
        self.screen.blit(scaled_bg, (offset_x, offset_y))
    
    def draw_counters(self):
        """Draw notes using EXACT original drawCounters logic with actual counter images"""
        for c in self.counters:
            if c['y'] < 520 and c['y'] > -20:  # EXACT original bounds
                # Use the actual counter image for this column
                counter_image = self.counter_images[c['column']]
                # Center the image on the note position
                image_rect = counter_image.get_rect(center=(int(c['x']), int(c['y'])))
                self.screen.blit(counter_image, image_rect)
    
    def skip(self):
        """Skip the game"""
        self.skipped = True
        # Stop music if playing
        if self.music_available:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        return "skipped"