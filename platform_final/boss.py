import pygame
import math

class Boss(pygame.sprite.Sprite):
	def __init__(self, pos, size):
		super().__init__()
		
		# Load boss image
		try:
			self.boss_img = pygame.image.load("assets/trap/boss.png").convert_alpha()
			self.image = pygame.transform.scale(self.boss_img, (size, size))
		except:
			# Create a fallback purple square
			self.image = pygame.Surface((size, size))
			self.image.fill((128, 0, 128))  # Purple
			print("Warning: Could not load boss.png, using fallback")
		
		self.rect = self.image.get_rect(center=pos)
		self.mask = pygame.mask.from_surface(self.image)
		
		# Boss properties
		self.max_health = 11  # Increased by 20% (9 * 1.2 = 10.8, rounded to 11)
		self.health = self.max_health
		self.alive = True
		
		# Position and movement
		self.start_pos = pos
		self.target_x = pos[0]
		self.target_y = pos[1]
		self.speed = 5.2  # Doubled from 2.6
		
		# Attack pattern system
		self.attack_patterns = ["v_pattern", "horizontal_sweep", "vertical_slam"]
		self.current_pattern = 0
		self.pattern_step = 0
		self.pattern_timer = 0
		self.pattern_delay = 120  # 2 seconds at 60 FPS
		
		# Minion spawning
		self.minions_spawned_at_6 = False
		self.minions_spawned_at_3 = False
		self.minion_mode = False
		
		# Stage boundaries
		self.stage_left = 150
		self.stage_right = 850
		self.stage_top = 50
		self.stage_bottom = 300

	def take_damage(self):
		"""Boss takes damage from sword"""
		if self.alive and not self.minion_mode:
			self.health -= 1
			print(f"Boss health: {self.health}")
			
			if self.health <= 0:
				self.alive = False
				self.kill()
			elif self.health == 7 and not self.minions_spawned_at_6:
				self.minions_spawned_at_6 = True
				self.minion_mode = True
				self.rect.center = (500, 100)  # Move out of reach (lowered position)
				return "spawn_minions"
			elif self.health == 4 and not self.minions_spawned_at_3:
				self.minions_spawned_at_3 = True
				self.minion_mode = True
				self.rect.center = (500, 100)  # Move out of reach (lowered position)
				return "spawn_minions"
		return None

	def resume_combat(self):
		"""Resume combat after minions are defeated"""
		self.minion_mode = False

	def _move_towards_target(self):
		"""Move boss towards target position"""
		dx = self.target_x - self.rect.centerx
		dy = self.target_y - self.rect.centery
		distance = math.sqrt(dx*dx + dy*dy)
		
		if distance > self.speed:
			# Normalize and move
			self.rect.centerx += int((dx / distance) * self.speed)
			self.rect.centery += int((dy / distance) * self.speed)
			return False
		else:
			# Reached target
			self.rect.centerx = self.target_x
			self.rect.centery = self.target_y
			return True

	def _execute_attack_pattern(self):
		"""Execute current attack pattern"""
		pattern = self.attack_patterns[self.current_pattern]
		
		if pattern == "v_pattern":
			self._v_pattern_attack()
		elif pattern == "horizontal_sweep":
			self._horizontal_sweep_attack()
		elif pattern == "vertical_slam":
			self._vertical_slam_attack()

	def _v_pattern_attack(self):
		"""V-shaped dive attack from upper left"""
		if self.pattern_step == 0:
			# Move to upper left
			self.target_x = self.stage_left
			self.target_y = self.stage_top
			if self._move_towards_target():
				self.pattern_step = 1
		elif self.pattern_step == 1:
			# Dive down to center
			self.target_x = (self.stage_left + self.stage_right) // 2
			self.target_y = self.stage_bottom
			if self._move_towards_target():
				self.pattern_step = 2
		elif self.pattern_step == 2:
			# Back up to upper right
			self.target_x = self.stage_right
			self.target_y = self.stage_top
			if self._move_towards_target():
				self._next_pattern()

	def _horizontal_sweep_attack(self):
		"""Horizontal sweep from left to right"""
		if self.pattern_step == 0:
			# Move to bottom center
			self.target_x = (self.stage_left + self.stage_right) // 2
			self.target_y = self.stage_bottom
			if self._move_towards_target():
				self.pattern_step = 1
		elif self.pattern_step == 1:
			# Sweep to right
			self.target_x = self.stage_right
			self.target_y = self.stage_bottom
			if self._move_towards_target():
				self.pattern_step = 2
		elif self.pattern_step == 2:
			# Sweep to left
			self.target_x = self.stage_left
			self.target_y = self.stage_bottom
			if self._move_towards_target():
				self._next_pattern()

	def _vertical_slam_attack(self):
		"""Vertical slam in center between platforms"""
		center_x = (self.stage_left + self.stage_right) // 2
		if self.pattern_step == 0:
			# Move to top center
			self.target_x = center_x
			self.target_y = self.stage_top
			if self._move_towards_target():
				self.pattern_step = 1
		elif self.pattern_step == 1:
			# Slam down
			self.target_x = center_x
			self.target_y = self.stage_bottom - 50
			if self._move_towards_target():
				self.pattern_step = 2
		elif self.pattern_step == 2:
			# Back up
			self.target_x = center_x
			self.target_y = self.stage_top
			if self._move_towards_target():
				self._next_pattern()

	def _next_pattern(self):
		"""Move to next attack pattern"""
		self.current_pattern = (self.current_pattern + 1) % len(self.attack_patterns)
		self.pattern_step = 0

	def move_to_safe_position(self):
		"""Move boss to safe position during minion phase"""
		self.target_x = (self.stage_left + self.stage_right) // 2
		self.target_y = self.stage_top - 50  # Above player reach
		self._move_towards_target()

	def update(self, x_shift):
		"""Update boss"""
		if not self.alive:
			return
		
		if self.minion_mode:
			# Move to safe position during minion phase
			self.move_to_safe_position()
		else:
			# Execute attack patterns
			self._execute_attack_pattern()
		
		# Apply world shift
		self.rect.x += x_shift
