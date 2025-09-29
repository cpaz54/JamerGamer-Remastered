import pygame
from settings import tile_size, WIDTH, HEIGHT
from tile import Tile
from trap import Trap
from goal import Goal
from player import Player
from game import Game
from enemy import Enemy
from boss import Boss
from big_willig_boss import BigWilligBoss
from jester_boss import JesterBoss

class World:
	def __init__(self, screen):
		self.screen = screen
		self.game = Game(self.screen)
		self.world_data = self.game.get_current_stage_data()
		self._setup_world(self.world_data)
		self.world_shift = 0
		self.current_x = 0
		self.gravity = 0.7
		
		# Initialize health pickup system
		self.health_pickups = pygame.sprite.Group()
		self.health_pickup_timer = 0
		self.health_pickup_delay = 1800  # 30 seconds (60 FPS * 30)
		self.player_has_lost_life = False
		
		# Initialize music system
		self.current_music = None
		self.music_playing = False
		self.platforming_music_started = False
		self.boss_music_started = False
		self.dreadknight_phase2_music_started = False
		
		# Initialize boss system
		self.current_boss = None
		self.is_boss_stage = False

	# generates the world
	def _setup_world(self, layout):
		self.tiles = pygame.sprite.Group()
		self.traps = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.boss = pygame.sprite.GroupSingle()
		self.player = pygame.sprite.GroupSingle()
		self.goal = pygame.sprite.GroupSingle()
		
		# Check if this is boss stage (stage 4)
		self.is_boss_stage = (self.game.current_stage == 3)  # 0-indexed

		# Special handling for boss stage - spawn player and BIG_WILLIG boss
		if self.is_boss_stage:
			# Add invisible walls for boss stages to prevent player from going off-screen
			# Left wall (at x = -200, far off-screen) - full height
			for y in range(0, HEIGHT, tile_size):
				left_wall = Tile((-200, y), tile_size)
				left_wall.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)  # Transparent surface
				left_wall.image.fill((0, 0, 0, 0))  # Completely transparent
				self.tiles.add(left_wall)
			
			# Right wall (at x = 1200, far off-screen) - full height
			for y in range(0, HEIGHT, tile_size):
				right_wall = Tile((1200, y), tile_size)
				right_wall.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)  # Transparent surface
				right_wall.image.fill((0, 0, 0, 0))  # Completely transparent
				self.tiles.add(right_wall)
			
			player_sprite = Player((100, 150))  # Left side
			self.player.add(player_sprite)
			
			# Spawn BIG_WILLIG boss above elevated blocks (right side, 20% bigger, high up to fall)
			boss_sprite = BigWilligBoss((850, 100), 120)  # High up so he can fall down to platform
			self.boss.add(boss_sprite)
			
			# Initialize health pickup system
			self.health_pickups = pygame.sprite.Group()
			self.health_pickup_timer = 0
			self.health_pickup_delay = 1800  # 30 seconds (60 FPS * 30)
			self.player_has_lost_life = False
			
			# Boss transition system
			self.current_boss = "BIG_WILLIG"
			self.boss_defeated = False
			self.boss_transition_timer = 0
			self.boss_transition_delay = 180  # 3 seconds between bosses
			
		# Fade effect system for Laurtney to Cathedral transition
		self.fade_alpha = 0
		self.fade_timer = 0
		self.fade_duration = 180  # 3 seconds for fade in/out
		self.is_fading = False
		self.fade_direction = 1  # 1 for fade in, -1 for fade out
		self.cathedral_background = None
		self.burning_cathedral_background = None
		self.fade_triggered = False  # Flag to ensure fade only happens once
			
		# DreadKnight boss system
		self.dreadknight_timer = 0
		self.dreadknight_delay = 0
		self.boss_reward_rect = None  # For reward collision detection
			

		for row_index, row in enumerate(layout):
			for col_index, cell in enumerate(row):
				x, y = col_index * tile_size, row_index * tile_size
				if cell == "X":
					tile = Tile((x, y), tile_size)
					self.tiles.add(tile)
				elif cell == "t":
					tile = Trap((x + (tile_size // 4), y + (tile_size // 4)), tile_size // 2)
					self.traps.add(tile)
				elif cell == "P":
					# Only spawn player from layout if not boss stage (boss stage handled above)
					if not self.is_boss_stage:
						player_sprite = Player((x, y))
						self.player.add(player_sprite)
				elif cell == "G":
					goal_sprite = Goal((x, y), tile_size)
					self.goal.add(goal_sprite)
				elif cell == "E":
					enemy_sprite = Enemy((x, y), tile_size * 1.5)  # 3x bigger (1.5 * tile_size)
					self.enemies.add(enemy_sprite)

	# world scroll when the player is walking towards left/right
	def _scroll_x(self):
		# No scrolling in boss stage
		if self.is_boss_stage:
			self.world_shift = 0
			if self.player.sprite:
				self.player.sprite.speed = 3
			return
			
		player = self.player.sprite
		player_x = player.rect.centerx
		direction_x = player.direction.x

		if player_x < WIDTH // 3 and direction_x < 0:
			self.world_shift = 8
			player.speed = 0
		elif player_x > WIDTH - (WIDTH // 3) and direction_x > 0:
			self.world_shift = -8
			player.speed = 0
		else:
			self.world_shift = 0
			player.speed = 3

	# add gravity for player to fall
	def _apply_gravity(self, player):
		player.direction.y += self.gravity
		player.rect.y += player.direction.y
	
	def _apply_gravity_dual(self, laurtney_boss):
		"""Apply gravity to both Laurtney characters"""
		# Apply gravity to L character
		laurtney_boss.l_direction.y += self.gravity
		laurtney_boss.l_rect.y += laurtney_boss.l_direction.y
		
		# Apply gravity to C character
		laurtney_boss.c_direction.y += self.gravity
		laurtney_boss.c_rect.y += laurtney_boss.c_direction.y
		
		# Debug output every 60 frames (1 second)
		if hasattr(laurtney_boss, 'debug_timer'):
			laurtney_boss.debug_timer += 1
			if laurtney_boss.debug_timer % 60 == 0:
				print(f"WORLD gravity: L at ({laurtney_boss.l_rect.x}, {laurtney_boss.l_rect.y}), C at ({laurtney_boss.c_rect.x}, {laurtney_boss.c_rect.y})")

	# prevents player to pass through objects horizontally
	def _horizontal_movement_collision(self):
		player = self.player.sprite
		player.rect.x += player.direction.x * player.speed

		# Check collision with tiles
		for sprite in self.tiles.sprites():
			if sprite.rect.colliderect(player.rect):
				# checks if moving towards left
				if player.direction.x < 0:
					player.rect.left = sprite.rect.right
					player.on_left = True
					self.current_x = player.rect.left
				# checks if moving towards right
				elif player.direction.x > 0:
					player.rect.right = sprite.rect.left
					player.on_right = True
					self.current_x = player.rect.right
		
		# Enemies are no longer solid objects - player can pass through them
		
		if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
			player.on_left = False
		if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
			player.on_right = False

	# prevents player to pass through objects vertically
	def _vertical_movement_collision(self):
		player = self.player.sprite
		self._apply_gravity(player)

		# Check collision with tiles
		for sprite in self.tiles.sprites():
			if sprite.rect.colliderect(player.rect):
				# checks if moving towards bottom
				if player.direction.y > 0:
					player.rect.bottom = sprite.rect.top
					player.direction.y = 0
					player.on_ground = True
				# checks if moving towards up
				elif player.direction.y < 0:
					player.rect.top = sprite.rect.bottom
					player.direction.y = 0
					player.on_ceiling = True
		
		# Enemies are no longer solid objects - player can pass through them
		
		if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
			player.on_ground = False
		if player.on_ceiling and player.direction.y > 0:
			player.on_ceiling = False

	# add consequences when player run through traps
	def _handle_traps(self):
		player = self.player.sprite
		trap_contact = False

		for sprite in self.traps.sprites():
			if sprite.rect.colliderect(player.rect):
				trap_contact = True
				# Check if contact duration is sufficient for damage
				if player.start_trap_contact():
					if player.direction.x < 0 or player.direction.y > 0:
						player.rect.x += tile_size
					elif player.direction.x > 0 or player.direction.y > 0:
						player.rect.x -= tile_size
					player.take_damage()
					player.reset_contact_timers()  # Reset after taking damage
		
		# Reset trap contact timer if not in contact
		if not trap_contact:
			player.trap_contact_timer = 0

	# handle enemy collisions and sword hits
	def _handle_enemies(self):
		player = self.player.sprite
		enemy_contact = False

		# Check for enemy damage to player
		for enemy in self.enemies.sprites():
			if enemy.alive and enemy.rect.colliderect(player.rect):
				enemy_contact = True
				# Check if contact duration is sufficient for damage
				if player.start_enemy_contact():
					# Push player away and damage
					if player.direction.x < 0:
						player.rect.x += tile_size
					elif player.direction.x > 0:
						player.rect.x -= tile_size
					player.take_damage()
					player.reset_contact_timers()  # Reset after taking damage
		
		# Reset enemy contact timer if not in contact
		if not enemy_contact:
			player.enemy_contact_timer = 0

		# Check for sword hits on enemies (extended range)
		if player.sword_swinging:
			# Create extended attack area around player
			attack_range = 50  # Extended range in pixels
			attack_rect = pygame.Rect(
				player.rect.x - attack_range, 
				player.rect.y - attack_range,
				player.rect.width + (attack_range * 2),
				player.rect.height + (attack_range * 2)
			)
			
			for enemy in self.enemies.sprites():
				if enemy.alive and enemy.rect.colliderect(attack_rect):
					enemy.take_damage()

	# handle boss combat
	def _handle_boss_combat(self):
		if not self.is_boss_stage:
			return
			
		player = self.player.sprite

		# Check if player has walked halfway to trigger boss intro
		if self.boss.sprite and hasattr(self.boss.sprite, 'intro_state'):
			boss = self.boss.sprite
			if boss.intro_state == "waiting":
				# Trigger boss when player reaches halfway point
				halfway_point = WIDTH // 2
				if player.rect.centerx >= halfway_point:
					boss.trigger_intro()
					print("BIG_WILLIG boss triggered!")

		# Handle boss collisions and sword hits
		if self.boss.sprite:
			boss = self.boss.sprite
			# Check for sword hit with extended range
			if boss.alive and player.sword_swinging and player.can_damage_boss():
				# Create extended attack area around player
				attack_range = 50  # Extended range in pixels
				attack_rect = pygame.Rect(
					player.rect.x - attack_range, 
					player.rect.y - attack_range,
					player.rect.width + (attack_range * 2),
					player.rect.height + (attack_range * 2)
				)
				
				# For Laurtney boss, check collision with both characters separately
				if self.current_boss == "LAURTNEY":
					# Check collision with L character
					if boss.l_rect.colliderect(attack_rect):
						result = boss.take_damage("L")
						player.start_boss_damage_cooldown()
						print("LAURTNEY: L character hit!")
					# Check collision with C character
					elif boss.c_rect.colliderect(attack_rect):
						result = boss.take_damage("C")
						player.start_boss_damage_cooldown()
						print("LAURTNEY: C character hit!")
					else:
						result = None
					
					# Check if boss was defeated, started second phase, or started victory sequence
					if result == "defeated":
						self.boss_defeated = True
						self.boss_transition_timer = 0
						# Stop boss music when defeated
						if self.current_boss in ["BIG_WILLIG", "JESTER", "LAURTNEY"]:
							self._stop_music()
							self.boss_music_started = False
						print(f"{self.current_boss} defeated! Transitioning to next boss...")
					elif result == "phase2_started":
						print("DREAD_KNIGHT: Second phase started!")
					elif result == "victory_started":
						print("DREAD_KNIGHT: Victory sequence started!")
				else:
					# Other bosses use default collision
					if boss.rect.colliderect(attack_rect):
						result = boss.take_damage()
						player.start_boss_damage_cooldown()
						
						# Check if boss was defeated, started second phase, or started victory sequence
						if result == "defeated":
							self.boss_defeated = True
							self.boss_transition_timer = 0
							# Stop boss music when defeated
							if self.current_boss in ["BIG_WILLIG", "JESTER", "LAURTNEY"]:
								self._stop_music()
								self.boss_music_started = False
							print(f"{self.current_boss} defeated! Transitioning to next boss...")
						elif result == "phase2_started":
							print("DREAD_KNIGHT: Second phase started!")
						elif result == "victory_started":
							print("DREAD_KNIGHT: Victory sequence started!")
				
				# Boss damages player (with immunity) - but not during vulnerable, walking, or idle states, and not when player is attacking
					if (hasattr(boss, 'attack_state') and 
						boss.attack_state not in ["vulnerable", "idle", "walking_to_left_platform", "pausing_on_right_platform", "squat_pause"] and
						not player.sword_swinging):  # Don't damage player when they're attacking
						if player.take_damage():
							if player.direction.x < 0:
								player.rect.x += tile_size
							elif player.direction.x > 0:
								player.rect.x -= tile_size
							player.reset_contact_timers()
			
			# Handle Laurtney boss damage to player (only when attacking)
			if self.current_boss == "LAURTNEY" and boss.alive:
				# L character damages player only when throwing shurikens
				if (boss.l_attack_state == "throwing" and 
					boss.l_rect.colliderect(player.rect)):
					if player.take_damage():
						if player.direction.x < 0:
							player.rect.x += tile_size
						elif player.direction.x > 0:
							player.rect.x -= tile_size
						player.reset_contact_timers()
						print("LAURTNEY: L character damaged player while attacking!")
				
				# C character damages player only when punching
				if (hasattr(boss, 'c_attack_state') and boss.c_attack_state == "punching" and 
					boss.c_rect.colliderect(player.rect)):
					if player.take_damage():
						if player.direction.x < 0:
							player.rect.x += tile_size
						elif player.direction.x > 0:
							player.rect.x -= tile_size
						player.reset_contact_timers()
						print("LAURTNEY: C character damaged player while punching!")
				
				# Shurikens damage player (use smaller hitbox)
				for shuriken in boss.shurikens.sprites():
					if shuriken.hitbox.colliderect(player.rect):
						if player.take_damage():
							if player.direction.x < 0:
								player.rect.x += tile_size
							elif player.direction.x > 0:
								player.rect.x -= tile_size
							player.reset_contact_timers()
							print("LAURTNEY: Shuriken damaged player!")
						shuriken.kill()  # Remove shuriken after hitting player
			
			# Handle DreadKnight boss damage to player (only when attacking, not when pausing, and not when player is attacking)
			if self.current_boss == "DREAD_KNIGHT" and boss.alive:
				# Check for first phase attacks
				first_phase_attacking = (hasattr(boss, 'attack_state') and 
					boss.attack_state in ["charging_right", "charging_left", "charging_right_to_center", "slash_left", "slash_right"] and
					boss.attack_state not in ["delay", "final_pause"])
				
				# Check for second phase flame attacks (but NOT during flame rain)
				second_phase_attacking = (hasattr(boss, 'second_phase') and boss.second_phase and
					hasattr(boss, 'phase2_attack_state') and 
					boss.phase2_attack_state in ["flame_slash_left", "flame_slash_right"])
				
				# DreadKnight damages player during any attack, but NOT during pauses, flame rain, or when player is attacking
				if ((first_phase_attacking or second_phase_attacking) and
					not player.sword_swinging and  # Don't damage player when they're attacking
					boss.rect.colliderect(player.rect)):
					if player.take_damage():
						if player.direction.x < 0:
							player.rect.x += tile_size
						elif player.direction.x > 0:
							player.rect.x -= tile_size
						player.reset_contact_timers()
						print("DREAD_KNIGHT: Damaged player during attack!")
			
				# Handle flame rain damage
				if (self.current_boss == "DREAD_KNIGHT" and boss.alive and 
					hasattr(boss, 'second_phase') and boss.second_phase and
					hasattr(boss, 'phase2_attack_state') and boss.phase2_attack_state == "flame_rain"):
					for drop in boss.flame_rain_drops:
						drop_rect = pygame.Rect(drop['x'] + 15, drop['y'] + 15, 30, 30)  # Smaller hitbox (30x30 instead of 60x60)
						if drop_rect.colliderect(player.rect) and not player.sword_swinging:
							if player.take_damage():
								if player.direction.x < 0:
									player.rect.x += tile_size
								elif player.direction.x > 0:
									player.rect.x -= tile_size
								player.reset_contact_timers()
								print("DREAD_KNIGHT: Player hit by flame rain!")
								break  # Only one damage per frame
		
		# Handle reward collision (end game)
		if (self.current_boss == "DREAD_KNIGHT" and 
			hasattr(self, 'boss_reward_rect') and self.boss_reward_rect and
			hasattr(self.boss.sprite, 'victory_state') and self.boss.sprite.victory_state == "reward_showing"):
			# Check if player attacks the reward
			if player.sword_swinging and self.boss_reward_rect.colliderect(player.rect):
				print("DREAD_KNIGHT: Player collected reward! Game ending!")
				# Stop music when game ends
				self._stop_music()
				player.win = True
				self.game._game_win(player)
		
		# Handle boss fireball damage
		if self.boss.sprite and hasattr(self.boss.sprite, 'fireballs'):
			for fireball in self.boss.sprite.fireballs.sprites():
				if fireball.rect.colliderect(player.rect):
					# Fireball damages player
					if player.take_damage():
						# Push player away from fireball
						if fireball.direction_x > 0:  # Fireball moving right
							player.rect.x -= tile_size
						else:  # Fireball moving left
							player.rect.x += tile_size
						player.reset_contact_timers()
					# Remove fireball after hitting player
					fireball.kill()
		
		# Handle boss shock wave damage
		if self.boss.sprite and hasattr(self.boss.sprite, 'shock_waves'):
			for shock_wave in self.boss.sprite.shock_waves.sprites():
				if shock_wave.rect.colliderect(player.rect):
					# Shock wave damages player
					if player.take_damage():
						# Push player away from shock wave
						if shock_wave.direction > 0:  # Shock wave moving right
							player.rect.x -= tile_size
						else:  # Shock wave moving left
							player.rect.x += tile_size
						player.reset_contact_timers()
					shock_wave.kill()
		
		# Handle boss slash hit damage
		if self.boss.sprite and hasattr(self.boss.sprite, 'slash_hits'):
			for slash_hit in self.boss.sprite.slash_hits.sprites():
				if slash_hit.rect.colliderect(player.rect):
					# Slash hit damages player
					if player.take_damage():
						# Push player away from slash hit
						if slash_hit.direction == "right":  # Slash hit on right side
							player.rect.x -= tile_size
						else:  # Slash hit on left side
							player.rect.x += tile_size
						player.reset_contact_timers()
					slash_hit.kill()
		
		# Handle boss stone damage
		if self.boss.sprite and hasattr(self.boss.sprite, 'stones'):
			for stone in self.boss.sprite.stones.sprites():
				if stone.rect.colliderect(player.rect):
					# Stone damages player
					if player.take_damage():
						# Push player away from stone (stones move right)
						player.rect.x += tile_size
						player.reset_contact_timers()
					stone.kill()
		
		# Handle boss transitions
		if self.boss_defeated:
			self.boss_transition_timer += 1
			print(f"Boss transition timer: {self.boss_transition_timer}/{self.boss_transition_delay}")
			if self.boss_transition_timer >= self.boss_transition_delay:
				# Transition to next boss
				if self.current_boss == "BIG_WILLIG":
					# Spawn JESTER boss
					self.boss.empty()  # Remove old boss
					jester_sprite = JesterBoss((100, -100), 120)  # Start above screen, left side, 20% bigger
					self.boss.add(jester_sprite)
					self.current_boss = "JESTER"
					self.boss_defeated = False
					self.boss_transition_timer = 0
					# Move player to center of arena for jester fight
					print("DEBUG: Attempting to move player to center for jester fight")
					if hasattr(self, 'player') and self.player.sprite:
						print("DEBUG: Player exists, moving to center")
						self.player.sprite.rect.x = 400  # Center of arena
						self.player.sprite.rect.y = 400  # On top of ground (ground level for boss stage)
						print(f"JESTER transition - Player spawned at: ({self.player.sprite.rect.x}, {self.player.sprite.rect.y})")
					else:
						print("DEBUG: Player not found or doesn't exist")
					# Trigger JESTER intro immediately
					jester_sprite.trigger_intro()
					print("JESTER boss spawned and intro triggered - player moved to center!")
				elif self.current_boss == "JESTER":
					# Spawn LAURTNEY boss
					from laurtney_boss import LaurtneyBoss
					self.boss.empty()  # Remove old boss
					laurtney_sprite = LaurtneyBoss((100, -100), 120)  # Start above screen, 20% bigger
					self.boss.add(laurtney_sprite)
					self.current_boss = "LAURTNEY"
					self.boss_defeated = False
					self.boss_transition_timer = 0
					# Move player to center of arena for laurtney fight
					if hasattr(self, 'player') and self.player.sprite:
						self.player.sprite.rect.x = 400  # Center of arena
						self.player.sprite.rect.y = 400  # On top of ground
						print(f"LAURTNEY transition - Player spawned at: ({self.player.sprite.rect.x}, {self.player.sprite.rect.y})")
					# Trigger LAURTNEY intro immediately
					laurtney_sprite.trigger_intro()
					print("LAURTNEY boss spawned and intro triggered - player moved to center!")
				elif self.current_boss == "LAURTNEY":
					# Start fade to white transition to cathedral background (only once)
					if not self.fade_triggered and not self.is_fading:
						self.fade_triggered = True
						self.is_fading = True
						self.fade_timer = 0
						self.fade_direction = 1  # Fade in to white
						print("LAURTNEY defeated! Starting fade to white...")
				elif self.current_boss == "DREAD_KNIGHT":
					# DreadKnight defeated - could transition to next boss or end game
					print("DREAD_KNIGHT defeated! Game complete!")
				# Add more boss transitions here as needed


	def _play_music(self, music_file, loop=True):
		"""Play music file with optional looping"""
		try:
			pygame.mixer.music.load(f"assets/music/{music_file}")
			pygame.mixer.music.play(-1 if loop else 0)  # -1 for infinite loop, 0 for play once
			self.current_music = music_file
			self.music_playing = True
			print(f"Music: Playing {music_file}")
		except pygame.error as e:
			print(f"Failed to load music {music_file}: {e}")
	
	def _stop_music(self):
		"""Stop current music"""
		pygame.mixer.music.stop()
		self.music_playing = False
		self.current_music = None
		print("Music: Stopped")
	
	def _handle_music_system(self):
		"""Handle music transitions based on game state"""
		# Platforming stages (1-3) - play world.mp3
		if not self.is_boss_stage and not self.platforming_music_started:
			self._play_music("world.mp3", loop=True)
			self.platforming_music_started = True
			self.boss_music_started = False
			self.dreadknight_phase2_music_started = False
		
		# Boss stages - handle boss music
		elif self.is_boss_stage:
			# Stop platforming music when entering boss stage
			if self.platforming_music_started:
				self._stop_music()
				self.platforming_music_started = False
			
			# Handle boss music transitions - only start when title appears
			if (hasattr(self, 'current_boss') and self.current_boss and 
				hasattr(self, 'boss') and self.boss.sprite and 
				hasattr(self.boss.sprite, 'intro_state')):
				
				# Start music when title appears
				if (self.boss.sprite.intro_state == "title_show" and not self.boss_music_started):
					if self.current_boss == "BIG_WILLIG":
						self._play_music("ari_music.mp3", loop=True)
					elif self.current_boss == "JESTER":
						self._play_music("carson_music.mp3", loop=True)
					elif self.current_boss == "LAURTNEY":
						self._play_music("laurtney_music.mp3", loop=True)
					elif self.current_boss == "DREAD_KNIGHT":
						# Check if in second phase
						if (hasattr(self.boss.sprite, 'second_phase') and self.boss.sprite.second_phase):
							self._play_music("kev_phase_2.mp3", loop=True)
							self.dreadknight_phase2_music_started = True
						else:
							self._play_music("kev_phase_1.mp3", loop=True)
					self.boss_music_started = True
					print(f"Music: Started {self.current_boss} music when title appeared!")
			
			# Handle DreadKnight phase 2 transition
			if (self.current_boss == "DREAD_KNIGHT" and 
				hasattr(self.boss.sprite, 'second_phase') and self.boss.sprite.second_phase and
				not self.dreadknight_phase2_music_started):
				self._play_music("kev_phase_2.mp3", loop=True)
				self.dreadknight_phase2_music_started = True
				print("Music: Switched to DreadKnight phase 2 music")
	
	def _handle_health_pickups(self):
		"""Handle health pickup spawning and collection"""
		player = self.player.sprite
		
		# Check if player has lost a life (life < max_life)
		if player.life < 5:  # Assuming max life is 5
			self.player_has_lost_life = True
		
		# Spawn health pickup if conditions are met
		# Use faster frequency during DreadKnight second phase
		pickup_delay = self.health_pickup_delay
		if (self.current_boss == "DREAD_KNIGHT" and 
			hasattr(self, 'boss') and self.boss.sprite and hasattr(self.boss.sprite, 'second_phase') and self.boss.sprite.second_phase):
			pickup_delay = 900  # 15 seconds (60 FPS * 15) for second phase
			print(f"Health pickup: Using faster delay for DreadKnight second phase: {pickup_delay/60:.1f} seconds")
		
		if (self.player_has_lost_life and 
			len(self.health_pickups) == 0 and 
			self.health_pickup_timer >= pickup_delay):
			
			# Spawn health pickup on right side of arena
			from health_pickup import HealthPickup
			pickup_x = 700  # Right side of arena
			pickup_y = 400  # Ground level
			health_pickup = HealthPickup((pickup_x, pickup_y))
			self.health_pickups.add(health_pickup)
			self.health_pickup_timer = 0  # Reset timer
			print(f"Health pickup spawned! Timer: {self.health_pickup_timer}, Delay: {pickup_delay}, Boss: {self.current_boss}")
		
		# Check for pickup collection
		for pickup in self.health_pickups.sprites():
			if pickup.rect.colliderect(player.rect):
				# Player collects pickup
				player.life = min(player.life + 1, 5)  # Restore 1 life, max to 5
				pickup.collect()
				print("Health pickup collected! Player life:", player.life)
				# Reset conditions for next pickup
				self.player_has_lost_life = False
				self.health_pickup_timer = 0
	
	def _handle_fade_effect(self):
		"""Handle fade to white effect for Laurtney to Cathedral transition"""
		if hasattr(self, 'is_fading') and self.is_fading:
			self.fade_timer += 1
			
			# Calculate fade alpha based on direction and timer
			if self.fade_direction == 1:  # Fade in to white
				self.fade_alpha = min(255, (self.fade_timer / self.fade_duration) * 255)
			else:  # Fade out from white
				self.fade_alpha = max(0, 255 - ((self.fade_timer / self.fade_duration) * 255))
			
			# Check if fade in is complete
			if self.fade_direction == 1 and self.fade_alpha >= 255:
				# Load cathedral background
				if self.cathedral_background is None:
					try:
						cathedral_img = pygame.image.load("assets/terrain/cathedral.png").convert()
						self.cathedral_background = pygame.transform.scale(cathedral_img, (WIDTH, HEIGHT))
						print("Cathedral background loaded!")
					except pygame.error as e:
						print(f"Failed to load cathedral background: {e}")
						self.cathedral_background = pygame.Surface((WIDTH, HEIGHT))
						self.cathedral_background.fill((100, 100, 100))  # Gray fallback
				
				# Switch to fade out
				self.fade_direction = -1
				self.fade_timer = 0
				print("Fade in complete, switching to fade out...")
			
			# Check if fade out is complete
			elif self.fade_direction == -1 and self.fade_alpha <= 0:
				self.is_fading = False
				self.fade_alpha = 0
				print("Fade effect complete!")
				# Start DreadKnight boss after 2 seconds
				self.dreadknight_timer = 0
				self.dreadknight_delay = 120  # 2 seconds at 60 FPS
				print("DREAD_KNIGHT: Starting 2-second delay before boss spawn...")
	
	def _handle_dreadknight_spawn(self):
		"""Handle DreadKnight boss spawning after cathedral transition"""
		if hasattr(self, 'dreadknight_delay') and self.dreadknight_delay > 0:
			self.dreadknight_timer += 1
			
			if self.dreadknight_timer >= self.dreadknight_delay:
				# Spawn DreadKnight boss
				from dread_knight_boss import DreadKnightBoss
				self.boss.empty()  # Remove any existing boss
				dreadknight_sprite = DreadKnightBoss((50, -200), 200)  # Start above screen, left side
				self.boss.add(dreadknight_sprite)
				self.current_boss = "DREAD_KNIGHT"
				self.boss_defeated = False
				self.boss_transition_timer = 0
				
				# Move player to center of arena for dreadknight fight
				if hasattr(self, 'player') and self.player.sprite:
					self.player.sprite.rect.x = 400  # Center of arena
					self.player.sprite.rect.y = 400  # On top of ground
					# Reset player state for new boss fight
					self.player.sprite.game_over = False
					self.player.sprite.win = False
					print(f"DREAD_KNIGHT transition - Player spawned at: ({self.player.sprite.rect.x}, {self.player.sprite.rect.y})")
				
				# Trigger DreadKnight intro immediately
				dreadknight_sprite.trigger_intro()
				print("DREAD_KNIGHT boss spawned and intro triggered - player moved to center!")
				
				# Reset timer
				self.dreadknight_timer = 0
				self.dreadknight_delay = 0

	# updating the game world from all changes commited
	def update(self, player_event, skip_stage=False, sword_swing=False):
		# for tile
		if self.is_boss_stage:
			self.tiles.update(0)  # No world shift in boss stage
		else:
			self.tiles.update(self.world_shift)
		
		# Draw tiles only if not in cathedral (hide stone blocks in cathedral)
		if not (hasattr(self, 'cathedral_background') and self.cathedral_background is not None):
			self.tiles.draw(self.screen)

		# for trap
		self.traps.update(self.world_shift)
		self.traps.draw(self.screen)

		# for enemies
		self.enemies.update(self.world_shift, self.tiles)
		self.enemies.draw(self.screen)

		# for boss (boss stage only)
		if self.is_boss_stage:
			if self.boss.sprite:
				# Handle different boss types
				if self.current_boss == "BIG_WILLIG":
					# Apply gravity and horizontal movement to boss like player
					if self.boss.sprite.intro_state in ["falling", "fighting"]:
						# Only apply gravity if not in floating states
						if not (hasattr(self.boss.sprite, 'attack_state') and 
							   self.boss.sprite.attack_state in ["floating_up", "floating_down", "float_rain"]):
							self._apply_gravity(self.boss.sprite)
						# Apply horizontal movement
						self.boss.sprite.rect.x += self.boss.sprite.direction.x * self.boss.sprite.move_speed
						# Apply vertical movement for floating states
						if hasattr(self.boss.sprite, 'attack_state') and self.boss.sprite.attack_state in ["floating_up", "floating_down"]:
							self.boss.sprite.rect.y += self.boss.sprite.direction.y
					self.boss.sprite.update(0, self.tiles)  # No world shift in boss stage, pass tiles for collision
				
				elif self.current_boss == "JESTER":
					# JESTER boss update with physics (same as BIG_WILLIG)
					player_can_move = self.boss.sprite.update_intro()  # Returns True if player should be frozen
					if not player_can_move:
						# Restrict player movement during JESTER intro
						pass  # Player movement restriction handled in main update loop
					
					# Apply physics to JESTER boss like BIG_WILLIG
					if self.boss.sprite.intro_state in ["landed", "title_show", "title_hide", "fighting"]:
						# Apply gravity and collision (same as BIG_WILLIG)
						self._apply_gravity(self.boss.sprite)
						# Apply horizontal movement
						self.boss.sprite.rect.x += self.boss.sprite.direction.x * self.boss.sprite.move_speed
						# Handle collision with tiles
						self.boss.sprite._handle_vertical_collision(self.tiles)
						self.boss.sprite._handle_horizontal_collision(self.tiles)
					
					# Apply gravity and collision for jumping_down_to_center only
					if (hasattr(self.boss.sprite, 'attack_state') and 
						self.boss.sprite.attack_state == "jumping_down_to_center"):
						# Apply gravity and collision during movement states
						self._apply_gravity(self.boss.sprite)
						# Handle collision with tiles
						self.boss.sprite._handle_vertical_collision(self.tiles)
						self.boss.sprite._handle_horizontal_collision(self.tiles)
					
					self.boss.sprite.update(0, self.tiles)
				
				elif self.current_boss == "LAURTNEY":
					# LAURTNEY boss update with dual character support
					player_can_move = self.boss.sprite.update_intro()  # Returns True if player should be frozen
					if not player_can_move:
						# Restrict player movement during LAURTNEY intro
						pass  # Player movement restriction handled in main update loop
					
					# Apply physics to both LAURTNEY characters like BIG_WILLIG
					if self.boss.sprite.intro_state in ["landed", "title_show", "title_hide", "fighting", "falling"]:
						# Only apply world physics if not in attack patterns (attack patterns handle their own movement)
						if not hasattr(self.boss.sprite, 'attack_state') or self.boss.sprite.attack_state == "idle":
							# Apply gravity to both characters
							self._apply_gravity_dual(self.boss.sprite)
							# Handle collision with tiles for both characters
							self.boss.sprite._handle_vertical_collision_dual(self.tiles)
							# Handle horizontal collision for both characters
							self.boss.sprite._handle_horizontal_collision_dual(self.tiles)
					
					self.boss.sprite.update(0, self.tiles)
				
				elif self.current_boss == "DREAD_KNIGHT":
					# DREAD_KNIGHT boss update
					self.boss.sprite.update_intro()  # Update intro sequence
					
					# Check if DreadKnight has transformed and load burning cathedral
					if (hasattr(self.boss.sprite, 'second_phase') and self.boss.sprite.second_phase and 
						hasattr(self.boss.sprite, 'phase2_state') and self.boss.sprite.phase2_state == "transformed" and
						self.burning_cathedral_background is None):
						try:
							burning_cathedral_img = pygame.image.load("assets/terrain/burning_cathedral.png").convert()
							self.burning_cathedral_background = pygame.transform.scale(burning_cathedral_img, (WIDTH, HEIGHT))
							print("DREAD_KNIGHT: Burning cathedral background loaded!")
						except pygame.error as e:
							print(f"Failed to load burning cathedral background: {e}")
							self.burning_cathedral_background = pygame.Surface((WIDTH, HEIGHT))
							self.burning_cathedral_background.fill((255, 100, 0))  # Orange fallback
					
					self.boss.sprite.update(0, self.tiles)
				
				# Don't draw boss here - draw after player
			
		# Handle health pickup spawning and collection
		self._handle_health_pickups()
		
		# Handle music system
		self._handle_music_system()
		
		# Update health pickup timer
		self.health_pickup_timer += 1
			
		# Handle fade effect
		self._handle_fade_effect()
		
		# Handle DreadKnight boss spawning
		self._handle_dreadknight_spawn()

		# for goal
		self.goal.update(self.world_shift)
		self.goal.draw(self.screen)

		self._scroll_x()

		# for player
		# Check if boss intro is preventing player movement
		player_can_move = True
		if self.is_boss_stage and self.boss.sprite and hasattr(self.boss.sprite, 'intro_state'):
			# All bosses return False when player can move, True when player should be frozen
			player_can_move = not self.boss.sprite.update_intro()  # False = can move, True = frozen
		# If there's no boss sprite, always allow player movement
		
		if player_can_move:
			self._horizontal_movement_collision()
			self._vertical_movement_collision()
			self._handle_traps()
			self._handle_enemies()
		self._handle_boss_combat()
		self.player.update(player_event, sword_swing)
		self.game.show_life(self.player.sprite)
		
		# Show stage counter (boss health bar is drawn separately)
		if not self.is_boss_stage:
			self.game.show_stage()
		
		
		self.player.draw(self.screen)
		# Draw sword if swinging
		if hasattr(self.player.sprite, 'draw_sword'):
			self.player.sprite.draw_sword(self.screen)
		
		# Draw boss after player (boss stage only)
		if self.is_boss_stage:
			if self.boss.sprite:
				# Only draw boss and health bar if intro has started
				if hasattr(self.boss.sprite, 'intro_state') and self.boss.sprite.intro_state != "waiting":
					# Draw boss health bar and title
					if hasattr(self.boss.sprite, 'draw_health_bar'):
						self.boss.sprite.draw_health_bar(self.screen)
					if hasattr(self.boss.sprite, 'draw_title') and hasattr(self.boss.sprite, 'intro_state') and self.boss.sprite.intro_state == "title_show":
						self.boss.sprite.draw_title(self.screen)
					# Draw fireballs if they exist (BIG_WILLIG only)
					if hasattr(self.boss.sprite, 'fireballs'):
						self.boss.sprite.fireballs.draw(self.screen)
					# Draw shock waves if they exist (JESTER only)
					if hasattr(self.boss.sprite, 'shock_waves'):
						self.boss.sprite.shock_waves.draw(self.screen)
					# Draw slash hits if they exist (JESTER only)
					if hasattr(self.boss.sprite, 'slash_hits'):
						self.boss.sprite.slash_hits.draw(self.screen)
					# Draw stones if they exist (JESTER only)
					if hasattr(self.boss.sprite, 'stones'):
						self.boss.sprite.stones.draw(self.screen)
					
					# Draw boss - use custom draw method for LAURTNEY and DREAD_KNIGHT
					if self.current_boss == "LAURTNEY":
						self.boss.sprite.draw(self.screen)
					elif self.current_boss == "DREAD_KNIGHT":
						# Handle DreadKnight with potential shaking effect
						if (hasattr(self.boss.sprite, 'second_phase') and self.boss.sprite.second_phase and
							hasattr(self.boss.sprite, 'phase2_state') and self.boss.sprite.phase2_state == "shaking"):
							# Apply shaking offset
							shake_x, shake_y = self.boss.sprite.get_shake_offset()
							shake_rect = self.boss.sprite.rect.copy()
							shake_rect.x += shake_x
							shake_rect.y += shake_y
							self.screen.blit(self.boss.sprite.image, shake_rect)
						else:
							# Normal drawing - use individual sprite
							self.screen.blit(self.boss.sprite.image, self.boss.sprite.rect)
						
						# Draw flame rain if in second phase
						if (hasattr(self.boss.sprite, 'second_phase') and self.boss.sprite.second_phase and
							hasattr(self.boss.sprite, 'phase2_attack_state') and 
							self.boss.sprite.phase2_attack_state == "flame_rain"):
							self.boss.sprite.draw_flame_rain(self.screen)
						
						# Draw victory sequence
						if hasattr(self.boss.sprite, 'victory_state') and self.boss.sprite.victory_state != "idle":
							self.boss.sprite.draw_victory_message(self.screen)
							reward_rect = self.boss.sprite.draw_reward(self.screen)
							if reward_rect:
								self.boss_reward_rect = reward_rect  # Store for collision detection
					else:
						self.boss.draw(self.screen)
					
					# Draw health pickups during boss fights
					self.health_pickups.draw(self.screen)

		# Check win condition - boss stage or normal goal
		if self.is_boss_stage:
			# Check for player death first
			if self.player.sprite.life <= 0 or self.player.sprite.rect.y >= HEIGHT:
				self.game._game_lose(self.player.sprite)
			elif self.boss.sprite and not self.boss.sprite.alive and not self.player.sprite.win:
				# Boss defeated - player wins the game!
				self.player.sprite.win = True
				self.game._game_win(self.player.sprite)
		else:
			self.game.game_state(self.player.sprite, self.goal.sprite)
		
		# Check for stage skip - trigger win condition like reaching goal
		if skip_stage and not self.player.sprite.game_over:
			if self.is_boss_stage:
				# Special handling for DreadKnight second phase
				if self.current_boss == "DREAD_KNIGHT" and self.boss.sprite and self.boss.sprite.alive:
					if hasattr(self.boss.sprite, 'second_phase') and not self.boss.sprite.second_phase:
						# Trigger second phase instead of defeating
						result = self.boss.sprite.trigger_second_phase()
						if result == "phase2_started":
							print("F1 skip: DreadKnight second phase triggered!")
						else:
							print("F1 skip: DreadKnight second phase already active or failed to trigger")
					else:
						# Second phase already active or boss defeated, defeat normally
						self.boss.sprite.alive = False
						self.boss.sprite.kill()
						self.boss_defeated = True
						self.boss_transition_timer = 0
						# Stop music when boss is defeated
						self._stop_music()
						self.boss_music_started = False
						self.dreadknight_phase2_music_started = False
						print(f"F1 skip: {self.current_boss} defeated!")
				elif self.boss.sprite and self.boss.sprite.alive:
					# For other bosses, defeat current boss and transition to next
					self.boss.sprite.alive = False
					self.boss.sprite.kill()
					self.boss_defeated = True
					self.boss_transition_timer = 0
					# Stop music when boss is defeated
					self._stop_music()
					self.boss_music_started = False
					self.dreadknight_phase2_music_started = False
					print(f"F1 skip: {self.current_boss} defeated!")
					print(f"Boss defeated flag set: {self.boss_defeated}")
				else:
					print("F1 skip: No boss to defeat or boss already defeated")
			else:
				# For normal stages, trigger win condition like reaching the goal
				self.player.sprite.win = True
				self.game._game_win(self.player.sprite)
		
		# Check if we should restart the level or move to next stage
		if self.game.should_restart():
			if self.player.sprite.win and not self.game.is_final_stage():
				# Player won and there are more stages - move to next stage
				self.next_stage()
			else:
				# Player lost or completed final stage - restart current level
				self.restart_level()

	def restart_level(self):
		"""Restart the level by resetting the world"""
		self.game.reset_restart_timer()
		# Reset player state before setting up new world
		if hasattr(self, 'player') and self.player.sprite:
			self.player.sprite.game_over = False
			self.player.sprite.win = False
			# Reset damage immunity and boss damage cooldown for boss fight
			self.player.sprite.damage_immune = False
			self.player.sprite.damage_immunity_timer = 0
			self.player.sprite.boss_damage_cooldown = False
			self.player.sprite.boss_damage_timer = 0
		
		# Check if we're in the jester boss fight and restart with jester
		if hasattr(self, 'current_boss') and self.current_boss == "JESTER":
			# Restart with jester boss
			self._setup_world(self.world_data)
			# Remove any existing boss and spawn jester
			self.boss.empty()
			jester_sprite = JesterBoss((100, -100), 120)  # Start above screen, left side, 20% bigger
			self.boss.add(jester_sprite)
			self.current_boss = "JESTER"
			self.boss_defeated = False
			self.boss_transition_timer = 0
			# Spawn player in center of arena for jester fight
			player_sprite = Player((400, 400))  # Center of arena, on top of ground
			player_sprite.life = 5  # Full health on restart
			player_sprite.health = 100  # Full health bar
			self.player.add(player_sprite)
			print(f"JESTER restart - Player spawned at: ({player_sprite.rect.x}, {player_sprite.rect.y}) with full health!")
			# Trigger JESTER intro immediately
			jester_sprite.trigger_intro()
			# Reset music flags for restart
			self.boss_music_started = False
			self.dreadknight_phase2_music_started = False
			print("JESTER boss restarted after player death - player spawned in center!")
		elif hasattr(self, 'current_boss') and self.current_boss == "LAURTNEY":
			# Restart with laurtney boss
			from laurtney_boss import LaurtneyBoss
			self._setup_world(self.world_data)
			# Remove any existing boss and spawn laurtney
			self.boss.empty()
			laurtney_sprite = LaurtneyBoss((100, -100), 120)  # Start above screen, 20% bigger
			self.boss.add(laurtney_sprite)
			self.current_boss = "LAURTNEY"
			self.boss_defeated = False
			self.boss_transition_timer = 0
			# Spawn player in center of arena for laurtney fight
			player_sprite = Player((400, 400))  # Center of arena, on top of ground
			player_sprite.life = 5  # Full health on restart
			player_sprite.health = 100  # Full health bar
			self.player.add(player_sprite)
			print(f"LAURTNEY restart - Player spawned at: ({player_sprite.rect.x}, {player_sprite.rect.y}) with full health!")
			# Trigger LAURTNEY intro immediately
			laurtney_sprite.trigger_intro()
			# Reset music flags for restart
			self.boss_music_started = False
			self.dreadknight_phase2_music_started = False
			print("LAURTNEY boss restarted after player death - player spawned in center!")
		elif hasattr(self, 'current_boss') and self.current_boss == "DREAD_KNIGHT":
			# Check if we were in second phase before restart
			was_in_second_phase = False
			if hasattr(self, 'boss') and self.boss.sprite and hasattr(self.boss.sprite, 'second_phase'):
				was_in_second_phase = self.boss.sprite.second_phase
			
			# Restart with dreadknight boss - maintain cathedral background
			from dread_knight_boss import DreadKnightBoss
			self._setup_world(self.world_data)
			# Remove any existing boss and spawn dreadknight
			self.boss.empty()
			dreadknight_sprite = DreadKnightBoss((50, -200), 200)  # Start above screen, left side
			self.boss.add(dreadknight_sprite)
			self.current_boss = "DREAD_KNIGHT"
			self.boss_defeated = False
			self.boss_transition_timer = 0
			
			# Check if we should restart in second phase
			if was_in_second_phase:
				# Restart in second phase - set up boss properly for second phase transition
				dreadknight_sprite.health = 0  # Set health to 0 to trigger second phase
				dreadknight_sprite.rect.x = 400
				dreadknight_sprite.rect.y = 350
				dreadknight_sprite.alive = True  # Ensure boss is alive
				dreadknight_sprite.intro_state = "fighting"  # Set to fighting state
				print("DREAD_KNIGHT restart: Simulating first phase defeat to trigger second phase!")
			else:
				# Normal restart - trigger intro
				dreadknight_sprite.trigger_intro()
				print("DREAD_KNIGHT restart: Starting in first phase!")
			
			# Ensure cathedral background is maintained for DreadKnight fight
			if self.cathedral_background is None:
				try:
					cathedral_img = pygame.image.load("assets/terrain/cathedral.png").convert()
					self.cathedral_background = pygame.transform.scale(cathedral_img, (WIDTH, HEIGHT))
					print("DREAD_KNIGHT restart: Cathedral background loaded!")
				except pygame.error as e:
					print(f"Failed to load cathedral background: {e}")
					self.cathedral_background = pygame.Surface((WIDTH, HEIGHT))
					self.cathedral_background.fill((100, 100, 100))  # Gray fallback
			
			# Spawn player in center of arena for dreadknight fight
			player_sprite = Player((400, 400))  # Center of arena, on top of ground
			player_sprite.life = 5  # Full health on restart
			player_sprite.health = 100  # Full health bar
			self.player.add(player_sprite)
			print(f"DREAD_KNIGHT restart - Player spawned at: ({player_sprite.rect.x}, {player_sprite.rect.y}) with full health!")
			# Reset music flags for restart
			self.boss_music_started = False
			self.dreadknight_phase2_music_started = False
			print("DREAD_KNIGHT boss restarted after player death - player spawned in center!")
		else:
			# Normal restart (includes Big Willig and other bosses)
			self._setup_world(self.world_data)
			# Reset music flags for any boss restart
			self.boss_music_started = False
			self.dreadknight_phase2_music_started = False

	def next_stage(self):
		"""Move to the next stage"""
		if self.game.next_stage():
			self.world_data = self.game.get_current_stage_data()
			# Reset player state before setting up new world
			if hasattr(self, 'player') and self.player.sprite:
				self.player.sprite.game_over = False
				self.player.sprite.win = False
				# Reset damage immunity and boss damage cooldown
				self.player.sprite.damage_immune = False
				self.player.sprite.damage_immunity_timer = 0
				self.player.sprite.boss_damage_cooldown = False
				self.player.sprite.boss_damage_timer = 0
			self._setup_world(self.world_data)
			self.game.reset_restart_timer()
			return True
		return False

	def skip_to_next_stage(self):
		"""Skip to the next stage (cheat/debug feature)"""
		if not self.game.is_final_stage():
			self.next_stage()
		else:
			# If on final stage, restart the game from stage 1
			self.game.current_stage = 0
			self.world_data = self.game.get_current_stage_data()
			# Reset player state before setting up new world
			if hasattr(self, 'player') and self.player.sprite:
				self.player.sprite.game_over = False
				self.player.sprite.win = False
			self._setup_world(self.world_data)
			self.game.reset_restart_timer()