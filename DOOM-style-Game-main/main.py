import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *


class Game:
    def __init__(self, screen=None):
        if screen is None:
            # Standalone mode - create our own display
            pg.init()
            pg.mouse.set_visible(False)
            self.screen = pg.display.set_mode(RES)
            pg.event.set_grab(True)
        else:
            # Integration mode - use provided screen
            self.screen = screen
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)
        
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        self.victory_achieved = False  # Flag to track when victory is achieved
        pg.time.set_timer(self.global_event, 40)
        self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return "exited"
            elif event.type == pg.KEYDOWN and event.unicode == "*":
                # Skip key - return to main game
                return "skipped"
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        while True:
            result = self.check_events()
            if result == "skipped":
                return "skipped"
            elif result == "exited":
                return "exited"
            
            # Check if victory has been achieved
            if self.victory_achieved:
                # Properly close pygame and return
                print("Victory achieved, exiting doom game...")
                pg.mixer.music.stop()
                pg.mixer.quit()
                return "victory"
            
            # Alternative victory check - if all enemies are dead
            if (hasattr(self, 'object_handler') and 
                hasattr(self.object_handler, 'npc_positions') and 
                len(self.object_handler.npc_positions) == 0 and
                hasattr(self.object_handler, 'wave_complete') and 
                self.object_handler.wave_complete):
                print("Alternative victory check - all enemies dead, exiting...")
                pg.mixer.music.stop()
                pg.mixer.quit()
                return "victory"
                
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
