import pygame
from support import import_sprite

class Player(pygame.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()
		self._import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations["idle"][self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)
		self.mask = pygame.mask.from_surface(self.image)

		# player movement
		self.direction = pygame.math.Vector2(0, 0)
		self.speed = 5
		self.jump_move = -16

		# player status
		self.life = 5
		self.game_over = False
		self.win = False
		self.status = "idle"
		self.facing_right = True
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False
		
		# sword mechanics (now integrated into sprite animations)
		self.sword_swinging = False
		self.sword_swing_timer = 0
		self.sword_swing_duration = 20  # frames
		
		# damage immunity (for boss fight)
		self.damage_immune = False
		self.damage_immunity_timer = 0
		self.damage_immunity_duration = 120  # 2 seconds at 60 FPS
		
		# boss damage cooldown (prevent spam damage)
		self.boss_damage_cooldown = False
		self.boss_damage_timer = 0
		self.boss_damage_duration = 60  # 1 second at 60 FPS
		
		# contact timers for damage (require sustained contact)
		self.enemy_contact_timer = 0
		self.enemy_contact_duration = 10  # ~0.17 seconds at 60 FPS
		self.trap_contact_timer = 0
		self.trap_contact_duration = 10  # ~0.17 seconds at 60 FPS

	# gets all the image needed for animating specific player action
	def _import_character_assets(self):
		character_path = "assets/player/"
		self.animations = {
			"idle": [],
			"walk": [],
			"attack": [],
			"jump": [],
			"fall": [],
			"lose": [],
			"win": []
		}
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_sprite(full_path)

	# Sword animations are now integrated into the main sprite sheet
	# No separate sword loading needed

	# animates the player actions
	def _animate(self):
		animation = self.animations[self.status]

		# For idle animation, use only the first frame (no animation)
		if self.status == "idle":
			image = animation[0]  # Always use first frame for idle
		else:
			# loop over frame index for other animations
			self.frame_index += self.animation_speed
			if self.frame_index >= len(animation):
				self.frame_index = 0
			image = animation[int(self.frame_index)]
		
		# Scale sprites based on animation type
		if self.status == "attack":
			# For attack sprites, preserve original proportions to show sword reach
			# Don't force to standard size - let the sword extend naturally
			original_width, original_height = image.get_size()
			# Scale to standard height but preserve width ratio
			scale_factor = 50 / original_height
			new_width = int(original_width * scale_factor)
			image = pygame.transform.scale(image, (new_width, 50))
		else:
			# For other animations, use standard size
			image = pygame.transform.scale(image, (35, 50))
		
		# Handle sprite flipping based on facing direction
		if self.status == "jump" or self.status == "fall":
			# Jump and fall sprites in the folder are actually facing left
			# So we flip them when facing right, and use them as-is when facing left
			if self.facing_right:
				flipped_image = pygame.transform.flip(image, True, False)
				self.image = flipped_image
			else:
				self.image = image
		else:
			# For other animations, normal flipping logic
			if self.facing_right:
				self.image = image
			else:
				flipped_image = pygame.transform.flip(image, True, False)
				self.image = flipped_image

		# set the rect
		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.topleft)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)

	# checks if the player is moving towards left or right or not moving
	def _get_input(self, player_event):
		if player_event != False:
			if player_event == "right":
				self.direction.x = 1
				self.facing_right = True
			elif player_event == "left":
				self.direction.x = -1
				self.facing_right = False
		else:
			self.direction.x = 0

	def _jump(self):
		self.direction.y = self.jump_move

	def _sword_swing(self):
		"""Start sword swing animation"""
		if not self.sword_swinging:
			self.sword_swinging = True
			self.sword_swing_timer = 0

	# identifies player action
	def _get_status(self):
		if self.sword_swinging:
			self.status = "attack"
		elif self.direction.y < 0:
			self.status = "jump"
		elif self.direction.y > 1:
			self.status = "fall"
		elif self.direction.x != 0:
			self.status = "walk"
		else:
			self.status = "idle"

	# update the player's state
	def update(self, player_event, sword_swing=False):
		self._get_status()
		if self.life > 0 and not self.game_over:
			if player_event == "space" and self.on_ground:
				self._jump()
			else:
				self._get_input(player_event)
			
			# Handle sword swing
			if sword_swing:
				self._sword_swing()
		elif self.game_over and self.win:
			self.direction.x = 0
			self.status = "win"
		else:
			self.direction.x = 0
			self.status = "lose"
		self._animate()
		self._update_sword()
		self._update_damage_immunity()
		self._update_boss_damage_cooldown()
		self._update_contact_timers()

	def _update_sword(self):
		"""Update sword swing animation"""
		if self.sword_swinging:
			self.sword_swing_timer += 1
			if self.sword_swing_timer >= self.sword_swing_duration:
				self.sword_swinging = False
				self.sword_swing_timer = 0

	def _update_damage_immunity(self):
		"""Update damage immunity timer"""
		if self.damage_immune:
			self.damage_immunity_timer += 1
			if self.damage_immunity_timer >= self.damage_immunity_duration:
				self.damage_immune = False
				self.damage_immunity_timer = 0

	def take_damage(self):
		"""Take damage if not immune"""
		if not self.damage_immune:
			self.life -= 1
			self.damage_immune = True
			self.damage_immunity_timer = 0
			return True
		return False

	def _update_boss_damage_cooldown(self):
		"""Update boss damage cooldown timer"""
		if self.boss_damage_cooldown:
			self.boss_damage_timer += 1
			if self.boss_damage_timer >= self.boss_damage_duration:
				self.boss_damage_cooldown = False
				self.boss_damage_timer = 0
	
	def _update_contact_timers(self):
		"""Update contact timers - reset when not in contact"""
		# This will be called every frame, and the world will increment timers when in contact
		# If we're not in contact with enemies/traps, the timers will be reset in world.py
		pass

	def can_damage_boss(self):
		"""Check if player can damage boss (not on cooldown)"""
		return not self.boss_damage_cooldown

	def start_boss_damage_cooldown(self):
		"""Start boss damage cooldown"""
		self.boss_damage_cooldown = True
		self.boss_damage_timer = 0
	
	def start_enemy_contact(self):
		"""Start enemy contact timer"""
		self.enemy_contact_timer += 1
		return self.enemy_contact_timer >= self.enemy_contact_duration
	
	def start_trap_contact(self):
		"""Start trap contact timer"""
		self.trap_contact_timer += 1
		return self.trap_contact_timer >= self.trap_contact_duration
	
	def reset_contact_timers(self):
		"""Reset all contact timers"""
		self.enemy_contact_timer = 0
		self.trap_contact_timer = 0

	def draw_sword(self, screen):
		"""Sword is now integrated into the main sprite animations"""
		# No separate sword drawing needed - sword is part of the character sprite
		pass
