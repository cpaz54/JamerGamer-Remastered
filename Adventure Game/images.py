from setup import * #imports everything from setup
from functions import *
import json

class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace('png', 'json')
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sprite_sheet, (0,0), (x, y, w, h))
        return sprite

    def parse_sprite(self, name):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h)
        return image

transparent = pygame.transform.scale(pygame.image.load('Tile_Sprites/transparent.png'), (TILESIZE, TILESIZE)).convert_alpha()

items_spritesheet = Spritesheet('Item_Sprites/Items.png')
sword_imgs = [pygame.transform.scale(items_spritesheet.parse_sprite('Items2.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(items_spritesheet.parse_sprite('Items0.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(items_spritesheet.parse_sprite('Items1.png'), (TILESIZE, TILESIZE))]
#starts pointing up and right and goes around clockwise every 45 degrees
sword_imgs = [sword_imgs[0], sword_imgs[1], sword_imgs[2],
              pygame.transform.flip(sword_imgs[1], False, True),
              pygame.transform.flip(sword_imgs[0], False, True),
              pygame.transform.flip(sword_imgs[1], True, True),
              pygame.transform.flip(sword_imgs[2], True, False),
              pygame.transform.flip(sword_imgs[1], True, False),
              sword_imgs[0], sword_imgs[1]]

arrow_imgs = [pygame.transform.scale(items_spritesheet.parse_sprite('Items3.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(items_spritesheet.parse_sprite('Items4.png'), (TILESIZE, TILESIZE))]
bow_img = pygame.transform.scale(items_spritesheet.parse_sprite('Items9.png'), (TILESIZE, TILESIZE))

#up, right, down, left
arrow_imgs = [arrow_imgs[0], arrow_imgs[1], pygame.transform.flip(arrow_imgs[0], False, True), pygame.transform.flip(arrow_imgs[1], True, False)]
arrow_up_destroyed_imgs = [pygame.transform.scale(items_spritesheet.parse_sprite('Items5.png'), (TILESIZE, TILESIZE)),
                           pygame.transform.scale(items_spritesheet.parse_sprite('Items6.png'), (TILESIZE, TILESIZE))]
arrow_down_destroyed_imgs  = [pygame.transform.flip(arrow_up_destroyed_imgs[0], False, True),
                              pygame.transform.flip(arrow_up_destroyed_imgs[1], False, True)]
arrow_right_destroyed_imgs = [pygame.transform.scale(items_spritesheet.parse_sprite('Items7.png'), (TILESIZE, TILESIZE)),
                           pygame.transform.scale(items_spritesheet.parse_sprite('Items8.png'), (TILESIZE, TILESIZE))]
arrow_left_destroyed_imgs  = [pygame.transform.flip(arrow_right_destroyed_imgs[0], True, False),
                              pygame.transform.flip(arrow_right_destroyed_imgs[1], True, False)]

player_spritesheet = Spritesheet('Player_Sprites/NPCSprites.png')
player_spritesheet_imgs = [pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites0.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites1.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites2.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites3.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites4.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites5.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites6.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites7.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites8.png'), (TILESIZE, TILESIZE)),
               pygame.transform.scale(player_spritesheet.parse_sprite('NPCSprites9.png'), (TILESIZE, TILESIZE))]
player_imgs = [player_spritesheet_imgs[0], player_spritesheet_imgs[1], pygame.transform.flip(player_spritesheet_imgs[1], True, False),
               player_spritesheet_imgs[2], pygame.transform.flip(player_spritesheet_imgs[2], True, False),
               player_spritesheet_imgs[3], player_spritesheet_imgs[4],
               pygame.transform.flip(player_spritesheet_imgs[3], True, False), pygame.transform.flip(player_spritesheet_imgs[4], True, False),
               player_spritesheet_imgs[5], player_spritesheet_imgs[6], player_spritesheet_imgs[7], pygame.transform.flip(player_spritesheet_imgs[7], True, False),
               player_spritesheet_imgs[9]]
damaged_player_imgs = [player_imgs[0],player_imgs[1],player_imgs[2],player_imgs[3],player_imgs[4],player_imgs[5],
                       player_imgs[6],player_imgs[0],player_imgs[0],player_imgs[0],player_imgs[0]]

NPC_imgs = [player_spritesheet_imgs[8], pygame.transform.flip(player_spritesheet_imgs[8], True, False)]

img =  pygame.transform.scale(pygame.image.load('Player_Sprites/NPC.png'), (TILESIZE, TILESIZE)).convert_alpha()
NPC2_imgs = [img, pygame.transform.flip(img, True, False)]

tile_spritesheet = Spritesheet('Tile_Sprites/TileSprites.png')
tile_imgs = []
for i in range(0,15): #goes from 0 to 14
    tile_imgs.append(pygame.transform.scale(tile_spritesheet.parse_sprite('TileSprites'+str(i)+'.png'), (TILESIZE, TILESIZE)))
for i in range(16,76): #goes from 16 to one below the second number
    tile_imgs.append(pygame.transform.scale(tile_spritesheet.parse_sprite('TileSprites'+str(i)+'.png'), (TILESIZE, TILESIZE)))

enemy_death_spritesheet = Spritesheet('Tile_Sprites/AnimationSprites.png')
death_animation_imgs = [pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites0.png'), (TILESIZE, TILESIZE)),
                    pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites1.png'), (TILESIZE, TILESIZE)),
                    pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites2.png'), (TILESIZE, TILESIZE)),
                    pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites3.png'), (TILESIZE, TILESIZE))]
laser_animation_imgs = [pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites4.png'), (TILESIZE, TILESIZE)),
                        pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites5.png'), (TILESIZE, TILESIZE)),
                        pygame.transform.scale(enemy_death_spritesheet.parse_sprite('AnimationSprites6.png'),(TILESIZE, TILESIZE))]

big_death_animation_imgs = []
for img in death_animation_imgs:
    big_death_animation_imgs.append(pygame.transform.scale(img, (TILESIZE*2, TILESIZE*2)))

#loading red enemy sprites
enemy_spritesheet = Spritesheet('Enemy_Sprites/EnemySprites.png')
red_imgs = [pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites0.png'), (TILESIZE, TILESIZE)),
                 pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites1.png'), (TILESIZE, TILESIZE)),
                 pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites2.png'), (TILESIZE, TILESIZE)),
                 pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites3.png'), (TILESIZE, TILESIZE))]
#up1, up2, down1, down2, left1, left2, right1, right2
red_imgs = [pygame.transform.flip(red_imgs[0], False, True), pygame.transform.flip(red_imgs[1], False, True),
            red_imgs[0], red_imgs[1],
            pygame.transform.flip(red_imgs[2], True, False), pygame.transform.flip(red_imgs[3], True, False),
            red_imgs[2], red_imgs[3]]

eye_orb_img = pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites7.png'), (TILESIZE, TILESIZE))
#first 2 laughing, next 2 charging up, and final 2 shooting:
ghost_imgs = [pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites5.png'), (TILESIZE*2, TILESIZE*2)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites6.png'), (TILESIZE*2, TILESIZE*2)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites11.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites12.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites13.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites14.png'), (TILESIZE, TILESIZE)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites17.png'), (TILESIZE*2, TILESIZE*2)),
              pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites18.png'), (TILESIZE*2, TILESIZE*2))]
eye_orb_closed_img = pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites8.png'), (TILESIZE, TILESIZE))
eye_orb_red_img = pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites9.png'), (TILESIZE, TILESIZE))
eye_orb_yellow_img = pygame.transform.scale(enemy_spritesheet.parse_sprite('EnemySprites10.png'), (TILESIZE, TILESIZE))


#loading tiles
#transparent = pygame.transform.scale(pygame.image.load('Tile_Sprites/transparent.png'), (TILESIZE, TILESIZE)).convert_alpha()
title_screen_img =  pygame.transform.scale(pygame.image.load('Menu_Images/title_screen_img.png'), (WIDTH, HEIGHT)).convert_alpha()
flowers_img =  pygame.transform.scale(pygame.image.load('Tile_Sprites/Misc.png'), (TILESIZE, TILESIZE)).convert_alpha()
fence = pygame.transform.scale(pygame.image.load('Tile_Sprites/fence.png'), (TILESIZE, TILESIZE)).convert_alpha()
bridge_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('Tile_Sprites/green_bridge.png'), (TILESIZE, TILESIZE)).convert_alpha(), 90)
tree = tile_imgs[4]
shrub_img = tile_imgs[6]
tall_grass = tile_imgs[7]
chest_img = tile_imgs[8]
opened_chest_img = tile_imgs[9]
sign_img = tile_imgs[10]
gravestone = pygame.transform.scale(pygame.image.load('Tile_Sprites/gravestone.png'), (TILESIZE, TILESIZE)).convert_alpha()
bed_imgs = [tile_imgs[11], tile_imgs[12]]
drawer_img = tile_imgs[13]
candle_img = tile_imgs[14]
stair_img = tile_imgs[15]
doorway_img = tile_imgs[16]
window_img = tile_imgs[17]
roof_img = tile_imgs[18]
mt_rock_img = tile_imgs[24]
mt_rock_entrance_img = tile_imgs[25]
mt_rock_entrance_img_flipped = pygame.transform.flip(mt_rock_entrance_img, False, True)
gold_key_img = pygame.transform.scale(pygame.image.load('Tile_Sprites/gold_key.png'), (int(TILESIZE*0.9), int(TILESIZE*0.9))).convert_alpha()

wall_indoor_top_img = tile_imgs[19]
wall_indoor_right_img = tile_imgs[21]
wall_indoor_bottom_img = pygame.transform.flip(wall_indoor_top_img, False, True)
wall_indoor_left_img = pygame.transform.flip(wall_indoor_right_img, True, False)
wall_corner_TR_img = tile_imgs[20]
wall_corner_BR_img = pygame.transform.flip(wall_corner_TR_img, False, True)
wall_corner_TL_img = pygame.transform.flip(wall_corner_TR_img, True, False)
wall_corner_BL_img = pygame.transform.flip(wall_corner_TR_img, True, True)
floorboard_img = tile_imgs[22]
wall_doorway_BL_img = pygame.transform.flip(tile_imgs[23], False, True)
wall_doorway_BR_img = pygame.transform.flip(tile_imgs[23], True, True)

cave_wall_top_img = tile_imgs[26]
cave_wall_bottom_img = pygame.transform.flip(cave_wall_top_img, False, True)
cave_wall_right_img = tile_imgs[27]
cave_wall_left_img = pygame.transform.flip(cave_wall_right_img, True, False)
cave_wall_TR_img = tile_imgs[28]
cave_wall_BR_img = pygame.transform.flip(cave_wall_TR_img, False, True)
cave_wall_TL_img= pygame.transform.flip(cave_wall_TR_img, True, False)
cave_wall_BL_img = pygame.transform.flip(cave_wall_TR_img, True, True)
cave_floor_img = tile_imgs[29]
cave_wall_edge_TR_img = tile_imgs[30]
cave_wall_edge_BR_img = pygame.transform.flip(cave_wall_edge_TR_img, False, True)
cave_wall_edge_TL_img= pygame.transform.flip(cave_wall_edge_TR_img, True, False)
cave_wall_edge_BL_img = pygame.transform.flip(cave_wall_edge_TR_img, True, True)

waterfall_imgs = [tile_imgs[31], tile_imgs[32]]
water_imgs = [tile_imgs[33], tile_imgs[34]]
water_top_imgs = [tile_imgs[35], tile_imgs[36]]
water_right_imgs = [tile_imgs[37], tile_imgs[38]]
water_bottom_imgs = [tile_imgs[39], tile_imgs[40]]
water_left_imgs = [tile_imgs[41], tile_imgs[42]]
water_TR_imgs = [tile_imgs[43], tile_imgs[44]]
water_BR_imgs = [tile_imgs[45], tile_imgs[46]]
water_BL_imgs = [tile_imgs[47], tile_imgs[48]]
water_TL_imgs = [tile_imgs[49], tile_imgs[50]]

locked_door_img = tile_imgs[51]
locked_door_opening_imgs = tile_imgs[52:56]

target_imgs = tile_imgs[56:58] #red then blue
drops_imgs = tile_imgs[58:62]

red_target_to_blue_imgs = [tile_imgs[62], tile_imgs[63], target_imgs[1]]
blue_target_to_red_imgs = [tile_imgs[64], tile_imgs[65], target_imgs[0]]

red_switch_barrier_imgs = [tile_imgs[66], tile_imgs[67], tile_imgs[68], tile_imgs[69]]
blue_switch_barrier_imgs = [tile_imgs[70], tile_imgs[71], tile_imgs[72], tile_imgs[73]]

red_switch_barrier_backwards_imgs = [tile_imgs[69], tile_imgs[68], tile_imgs[67], tile_imgs[66]]
blue_switch_barrier_backwards_imgs = [tile_imgs[73], tile_imgs[72], tile_imgs[71], tile_imgs[70]]

pushable_block_img = tile_imgs[74]

black_square = pygame.transform.scale(pygame.image.load('Tile_Sprites/black_square.png'), (TILESIZE, TILESIZE)).convert()