from sprite_object import *
from npc import *
from random import choices, randrange
import time
import math


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        # Wave system variables
        self.center_triggered = False
        self.current_wave = 0
        self.wave_delay = 0
        self.wave_delay_time = 5000  # 5 seconds in milliseconds
        self.center_area = (7.5, 14.5)  # Center of the room coordinates
        self.center_radius = 2.0  # Radius around center to trigger
        
        # Wave definitions - exact specifications
        self.waves = [
            # Wave 1: 8 soldiers
            {'type': 'soldiers', 'count': 8},
            # Wave 2: 4 soldiers + 2 cacodemons
            {'type': 'mixed', 'soldiers': 4, 'caco_demons': 2},
            # Wave 3: 1 cyber demon
            {'type': 'cyber_demon', 'count': 1},
            # Wave 4: 1 cyber demon + 4 soldiers + 2 cacodemons
            {'type': 'final', 'cyber_demon': 1, 'soldiers': 4, 'caco_demons': 2}
        ]
        self.wave_repeat_count = 0
        self.wave_complete = False
        
        # Start with Wave 1 immediately
        self.spawn_next_wave()
        self.enemies = 0

        # sprite map
        add_sprite(AnimatedSprite(game))
        add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

        # npc map
        # add_npc(SoldierNPC(game, pos=(11.0, 19.0)))
        # add_npc(SoldierNPC(game, pos=(11.5, 4.5)))
        # add_npc(SoldierNPC(game, pos=(13.5, 6.5)))
        # add_npc(SoldierNPC(game, pos=(2.0, 20.0)))
        # add_npc(SoldierNPC(game, pos=(4.0, 29.0)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 14.5)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 16.5)))
        # add_npc(CyberDemonNPC(game, pos=(14.5, 25.5)))

    def check_center_trigger(self):
        # Center trigger no longer needed - waves start immediately
        pass
    
    def start_wave_system(self):
        # Wave system already started in __init__
        pass
    
    def spawn_next_wave(self):
        if self.current_wave >= len(self.waves):
            self.wave_complete = True
            return
            
        wave = self.waves[self.current_wave]
        print(f"Spawning Wave {self.current_wave + 1}: {wave}")  # Debug info
        
        if wave['type'] == 'soldiers':
            for i in range(wave['count']):
                pos = self.get_spawn_position()
                self.add_npc(SoldierNPC(self.game, pos=pos))
        
        elif wave['type'] == 'mixed':
            for i in range(wave['soldiers']):
                pos = self.get_spawn_position()
                self.add_npc(SoldierNPC(self.game, pos=pos))
            for i in range(wave['caco_demons']):
                pos = self.get_spawn_position()
                self.add_npc(CacoDemonNPC(self.game, pos=pos))
        
        elif wave['type'] == 'cyber_demon':
            for i in range(wave['count']):
                pos = self.get_spawn_position()
                self.add_npc(CyberDemonNPC(self.game, pos=pos))
        
        elif wave['type'] == 'final':
            for i in range(wave['cyber_demon']):
                pos = self.get_spawn_position()
                self.add_npc(CyberDemonNPC(self.game, pos=pos))
            for i in range(wave['soldiers']):
                pos = self.get_spawn_position()
                self.add_npc(SoldierNPC(self.game, pos=pos))
            for i in range(wave['caco_demons']):
                pos = self.get_spawn_position()
                self.add_npc(CacoDemonNPC(self.game, pos=pos))
    
    def get_spawn_position(self):
        # Spawn enemies in a larger area with better distribution
        center_x, center_y = self.center_area
        spawn_radius = 5.0  # Increased spawn radius
        min_distance = 1.5  # Minimum distance from center
        
        # Try to find a valid spawn position around the center
        max_attempts = 100
        for attempt in range(max_attempts):
            # Random angle and distance from center
            angle = randrange(0, 360) * 3.14159 / 180  # Convert to radians
            # Ensure minimum distance to spread enemies out
            distance = randrange(int(min_distance * 2), int(spawn_radius * 2)) / 2.0
            
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            
            # Check if position is valid (not in walls) and not too close to existing NPCs
            map_x, map_y = int(x), int(y)
            if (map_x, map_y) not in self.game.map.world_map:
                # Check distance from existing NPCs to avoid clustering
                too_close = False
                for existing_npc in self.npc_list:
                    if existing_npc.alive:
                        dist = ((x - existing_npc.x) ** 2 + (y - existing_npc.y) ** 2) ** 0.5
                        if dist < 1.0:  # Minimum 1 unit between NPCs
                            too_close = True
                            break
                
                if not too_close:
                    return (x, y)
        
        # Fallback - try positions in a grid pattern around center
        for radius in range(1, 6):
            for angle_step in range(0, 360, 30):  # 12 positions around circle
                angle = angle_step * 3.14159 / 180
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                map_x, map_y = int(x), int(y)
                if (map_x, map_y) not in self.game.map.world_map:
                    return (x, y)
        
        # Final fallback
        return (center_x, center_y)
    
    def check_wave_progression(self):
        # Check if all enemies in current wave are dead
        alive_enemies = [npc for npc in self.npc_list if npc.alive]
        
        # Debug: Print detailed enemy status (reduced frequency)
        if hasattr(self, 'progression_debug_counter'):
            self.progression_debug_counter += 1
        else:
            self.progression_debug_counter = 0
            
        if self.progression_debug_counter % 600 == 0:  # Every 10 seconds
            print(f"Wave Status - Wave: {self.current_wave + 1}, Alive: {len(alive_enemies)}, Delay: {self.wave_delay:.0f}ms")
        
        if len(alive_enemies) == 0 and self.wave_delay <= 0 and not self.wave_complete:
            # Move to next wave immediately (no repeats since we spawn all at once)
            print(f"Wave {self.current_wave + 1} completed. Moving to wave {self.current_wave + 2}")  # Debug
            self.current_wave += 1
            if self.current_wave < len(self.waves):
                self.wave_delay = self.wave_delay_time
                print(f"Setting wave delay: {self.wave_delay_time}ms")  # Debug
            else:
                # All waves completed
                self.wave_complete = True
                print("All waves completed!")  # Debug
    
    def update_wave_delay(self):
        if self.wave_delay > 0:
            self.wave_delay -= self.game.delta_time * 16.67  # Convert to milliseconds
            # Only print delay every 60 frames (about once per second)
            if hasattr(self, 'delay_debug_counter'):
                self.delay_debug_counter += 1
            else:
                self.delay_debug_counter = 0
                
            if self.delay_debug_counter % 60 == 0:
                print(f"Wave delay: {self.wave_delay:.0f}ms")  # Debug
                
            if self.wave_delay <= 0:
                print("Wave delay finished, spawning next wave")  # Debug
                if not self.wave_complete:
                    self.spawn_next_wave()
                else:
                    # All waves complete - show win screen
                    print("All waves complete, showing win screen")  # Debug
                    self.check_win()

    def check_win(self):
        if not len(self.npc_positions):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.check_center_trigger()
        self.update_wave_delay()
        self.check_wave_progression()
        
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        alive_count = len([npc for npc in self.npc_list if npc.alive])
        
        # Debug info every 60 frames (about once per second)
        if hasattr(self, 'debug_counter'):
            self.debug_counter += 1
        else:
            self.debug_counter = 0
            
        if self.debug_counter % 60 == 0:  # Every 60 frames
            print(f"Debug - Wave: {self.current_wave + 1}, Alive: {alive_count}, Delay: {self.wave_delay:.0f}ms, Complete: {self.wave_complete}")
        
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        
        if self.wave_complete and len(self.npc_positions) == 0:
            self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)