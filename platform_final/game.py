import pygame
import time
from settings import HEIGHT, WIDTH, stages

pygame.font.init()

class Game:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.SysFont("impact", 70)
		self.message_color = pygame.Color("darkorange")
		self.restart_timer = None
		self.restart_delay = 3.0  # 3 seconds
		self.current_stage = 0
		self.total_stages = len(stages)

	# if player ran out of life or fell below the platform
	def _game_lose(self, player):
		player.game_over = True
		message = self.font.render('You Lose...', True, self.message_color)
		self.screen.blit(message,(WIDTH // 3 + 70, 70))
		
		# Start restart timer if not already started
		if self.restart_timer is None:
			self.restart_timer = time.time()

	# if player reach the goal
	def _game_win(self, player):
		player.game_over = True
		player.win = True
		
		# Check if this is the final stage
		if self.current_stage >= self.total_stages - 1:
			# Final boss victory message
			victory_message = self.font.render('BIG WILLIG DEFEATED!', True, self.message_color)
			win_message = self.font.render('You Win!!', True, self.message_color)
			self.screen.blit(victory_message, (WIDTH // 4, 50))
			self.screen.blit(win_message, (WIDTH // 3, 120))
		else:
			# Show stage completion message
			stage_message = self.font.render(f'Stage {self.current_stage + 1} Complete!', True, self.message_color)
			self.screen.blit(stage_message, (WIDTH // 4, 70))
			
			# Start timer for next stage
			if self.restart_timer is None:
				self.restart_timer = time.time()

	# checks if the game is over or not, and if win or lose
	def game_state(self, player, goal):
		if player.life <= 0 or player.rect.y >= HEIGHT:
			self._game_lose(player)
		elif player.rect.colliderect(goal.rect):
			self._game_win(player)
		else:
			None

	def show_life(self, player):
		life_size = 30
		img_path = "assets/life/life.png"
		life_image = pygame.image.load(img_path)
		life_image = pygame.transform.scale(life_image, (life_size, life_size))
		# life_rect = life_image.get_rect(topleft = pos)
		indent = 0
		for life in range(player.life):
			indent += life_size
			self.screen.blit(life_image, (indent, life_size))

	def show_stage(self):
		"""Show current stage number"""
		stage_font = pygame.font.SysFont("impact", 30)
		stage_text = stage_font.render(f'Stage {self.current_stage + 1}/{self.total_stages}', True, self.message_color)
		self.screen.blit(stage_text, (WIDTH - 150, 10))

	def show_boss_health(self, boss):
		"""Show boss health bar and name"""
		if not boss or not boss.alive:
			return
			
		# Boss health bar
		health_bar_width = 200
		health_bar_height = 20
		health_bar_x = WIDTH - health_bar_width - 10
		health_bar_y = 10
		
		# Background (red)
		pygame.draw.rect(self.screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
		
		# Health (green)
		health_percentage = boss.health / 11.0  # Boss has 11 max health
		current_health_width = int(health_bar_width * health_percentage)
		pygame.draw.rect(self.screen, (0, 255, 0), (health_bar_x, health_bar_y, current_health_width, health_bar_height))
		
		# Border
		pygame.draw.rect(self.screen, (255, 255, 255), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
		
		# Boss name
		name_font = pygame.font.SysFont("impact", 24)
		name_text = name_font.render("BIG WILLIG", True, (255, 0, 0))
		name_x = health_bar_x + (health_bar_width - name_text.get_width()) // 2
		name_y = health_bar_y + health_bar_height + 5
		self.screen.blit(name_text, (name_x, name_y))

	def should_restart(self):
		"""Check if it's time to restart the level"""
		if self.restart_timer is not None:
			elapsed_time = time.time() - self.restart_timer
			return elapsed_time >= self.restart_delay
		return False

	def reset_restart_timer(self):
		"""Reset the restart timer"""
		self.restart_timer = None

	def next_stage(self):
		"""Move to the next stage"""
		if self.current_stage < self.total_stages - 1:
			self.current_stage += 1
			return True
		return False

	def get_current_stage_data(self):
		"""Get the current stage data"""
		return stages[self.current_stage]

	def is_final_stage(self):
		"""Check if this is the final stage"""
		return self.current_stage >= self.total_stages - 1