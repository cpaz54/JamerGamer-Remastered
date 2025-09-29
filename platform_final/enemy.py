import pygame
from support import import_sprite

class Enemy(pygame.sprite.Sprite):
	def __init__(self, pos, size):
		super().__init__()
		
		# Load single enemy image
		try:
			self.enemy_img = pygame.image.load("assets/trap/enemy_1.png").convert_alpha()
			self.image = pygame.transform.scale(self.enemy_img, (size, size))
		except:
			# Create a simple colored rectangle if image not found
			self.image = pygame.Surface((size, size))
			self.image.fill((255, 0, 0))  # Red square as fallback
			print("Warning: Could not load enemy_1.png, using fallback")
		
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect(topleft = pos)
		
		# Enemy properties
		self.health = 1
		self.alive = True
		
		# Patrol movement
		self.patrol_speed = 1
		self.patrol_direction = 1  # 1 for right, -1 for left
		self.patrol_distance = 60  # How far to patrol (reduced to prevent getting stuck)
		self.start_x = pos[0]  # Starting position for patrol
		self.move_timer = 0

	# adds animation to the enemy (static image for now)
	def _animate(self):
		if not self.alive:
			return
		# For now, enemies are static - no animation needed
		pass

	# handle patrol movement
	def _patrol(self, tiles_group=None):
		if not self.alive:
			return
			
		# Store original position
		old_x = self.rect.x
		
		# Move in patrol direction
		self.rect.x += self.patrol_direction * self.patrol_speed
		
		# Check for collision with tiles if tiles_group is provided
		if tiles_group:
			collision = False
			for tile in tiles_group:
				if self.rect.colliderect(tile.rect):
					collision = True
					break
			
			# If collision detected, reverse direction and restore position
			if collision:
				self.rect.x = old_x
				self.patrol_direction *= -1
				return
		
		# Check if we've gone too far from start position
		distance_from_start = abs(self.rect.x - self.start_x)
		if distance_from_start >= self.patrol_distance:
			# Reverse direction
			self.patrol_direction *= -1
		
		# Debug output every 60 frames (1 second)
		self.move_timer += 1
		if self.move_timer % 60 == 0:
			print(f"Enemy at ({self.rect.x}, {self.rect.y}) - direction: {self.patrol_direction}, distance: {distance_from_start}")

	# take damage from sword
	def take_damage(self):
		self.health -= 1
		if self.health <= 0:
			self.alive = False
			self.kill()  # Remove from sprite group

	# update object position due to world scroll
	def update(self, x_shift, tiles_group=None):
		if self.alive:
			self._animate()
			self._patrol(tiles_group)  # Add patrol movement with collision detection
			self.rect.x += x_shift
