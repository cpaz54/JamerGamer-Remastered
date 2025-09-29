import pygame, sys
from settings import *
from world import World

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")

class Platformer:
	def __init__(self, screen, width, height):
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.keys_pressed = {
			"left": False,
			"right": False,
			"jump": False,
			"sword": False
		}
		self.sword_just_pressed = False  # Track if sword was just pressed this frame
		self.skip_requested = False

		self.bg_img = pygame.image.load('assets/terrain/bg.png')
		self.bg_img = pygame.transform.scale(self.bg_img, (width, height))

	def _get_player_event(self):
		"""Determine player event based on current key states"""
		if self.keys_pressed["jump"]:
			return "space"
		elif self.keys_pressed["left"]:
			return "left"
		elif self.keys_pressed["right"]:
			return "right"
		else:
			return False

	def main(self):
		world = World(self.screen)
		while True:
			# Draw background (normal, cathedral, or burning cathedral)
			if hasattr(world, 'burning_cathedral_background') and world.burning_cathedral_background is not None:
				self.screen.blit(world.burning_cathedral_background, (0, 0))
			elif hasattr(world, 'cathedral_background') and world.cathedral_background is not None:
				self.screen.blit(world.cathedral_background, (0, 0))
			else:
				self.screen.blit(self.bg_img, (0, 0))

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_a:
						self.keys_pressed["left"] = True
					if event.key == pygame.K_d:
						self.keys_pressed["right"] = True
					if event.key == pygame.K_w or event.key == pygame.K_SPACE:
						self.keys_pressed["jump"] = True
					if event.key == pygame.K_j:  # J key for sword swing
						self.sword_just_pressed = True  # Only set on keydown
					if event.key == pygame.K_F1:  # Use F1 key for skip (safe key)
						print("F1 key pressed - skip requested!")  # Debug
						self.skip_requested = True
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_a:
						self.keys_pressed["left"] = False
					if event.key == pygame.K_d:
						self.keys_pressed["right"] = False
					if event.key == pygame.K_w or event.key == pygame.K_SPACE:
						self.keys_pressed["jump"] = False
					# No KEYUP handling needed for sword since we only care about keydown

			# Determine player event based on current key states
			player_event = self._get_player_event()
			world.update(player_event, self.skip_requested, self.sword_just_pressed)
			
			# Draw fade overlay if fading
			if hasattr(world, 'is_fading') and world.is_fading and world.fade_alpha > 0:
				fade_surface = pygame.Surface((WIDTH, HEIGHT))
				fade_surface.fill((255, 255, 255))  # White
				fade_surface.set_alpha(int(world.fade_alpha))
				self.screen.blit(fade_surface, (0, 0))
			
			# Draw white flash for DreadKnight transformation
			if (hasattr(world, 'boss') and world.boss.sprite and 
				hasattr(world.boss.sprite, 'second_phase') and world.boss.sprite.second_phase and
				hasattr(world.boss.sprite, 'phase2_state') and world.boss.sprite.phase2_state == "flash"):
				flash_surface = pygame.Surface((WIDTH, HEIGHT))
				flash_surface.fill((255, 255, 255))  # White flash
				flash_surface.set_alpha(255)  # Full opacity
				self.screen.blit(flash_surface, (0, 0))
			
			# Reset flags after processing
			if self.skip_requested:
				self.skip_requested = False
			if self.sword_just_pressed:
				self.sword_just_pressed = False
			pygame.display.update()
			self.clock.tick(60)


if __name__ == "__main__":
	play = Platformer(screen, WIDTH, HEIGHT)
	play.main()