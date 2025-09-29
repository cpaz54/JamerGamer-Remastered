import pygame

class BossMinion(pygame.sprite.Sprite):
	def __init__(self, pos, size):
		super().__init__()
		
		# Load minion image
		try:
			self.minion_img = pygame.image.load("assets/trap/boss_minion.png").convert_alpha()
			self.image = pygame.transform.scale(self.minion_img, (size, size))
		except:
			# Create a fallback red square
			self.image = pygame.Surface((size, size))
			self.image.fill((255, 0, 0))  # Red
			print("Warning: Could not load boss_minion.png, using fallback")
		
		self.rect = self.image.get_rect(topleft=pos)
		self.mask = pygame.mask.from_surface(self.image)
		
		# Minion properties
		self.health = 1
		self.alive = True
		
		# Simple movement towards player
		self.speed = 1.5
		self.direction_x = 1

	def take_damage(self):
		"""Minion takes damage from sword"""
		self.health -= 1
		if self.health <= 0:
			self.alive = False
			self.kill()

	def _move_towards_player(self, player_pos):
		"""Simple AI to move towards player"""
		if player_pos[0] > self.rect.centerx:
			self.rect.x += self.speed
		elif player_pos[0] < self.rect.centerx:
			self.rect.x -= self.speed

	def update(self, x_shift, player_pos=None):
		"""Update minion"""
		if not self.alive:
			return
		
		# Move towards player if position provided
		if player_pos:
			self._move_towards_player(player_pos)
		
		# Apply world shift
		self.rect.x += x_shift
