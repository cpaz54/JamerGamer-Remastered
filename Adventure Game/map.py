'''TO DO: PUT ENEMY_LIST AND ALL THIS MAP STUFF IN A CLASS TO PREVENT ENEMY_LIST FROM BEING A GLOBAL VARIABLE... OR NOT'''
import player
from tiles import *

#0 means no tiles, 1 means wall
#able to draw walls, animated images, disappearing images, spider enemies, temporary walls, background images, and stairs
def draw_map(map_grid, tile_img, animation_img, disappearing_img, red_imgs, shrub_img, background_img, stair_img):
    disappearing_image_list = []
    row_num = 0
    for row in map_grid:
        col_num = 0
        for tile in row:
            if tile == 200: #doorways in the 200s, img, room to teleport to, side of image
                player.doorway_list.append(Doorway(col_num*TILESIZE,row_num*TILESIZE, doorway_img, 1, 'top', TILESIZE*8, TILESIZE*8))
            if tile == 201:
                player.doorway_list.append(Doorway(col_num*TILESIZE,row_num*TILESIZE, floorboard_img, 543534, 'bottom', TILESIZE*9, TILESIZE*3))
            if tile == 202: #doorways in the 200s
                player.doorway_list.append(Doorway(col_num*TILESIZE,row_num*TILESIZE, mt_rock_entrance_img, 1544533, 'top', TILESIZE*8, TILESIZE*9))
            if tile == 203:
                player.doorway_list.append(Doorway(col_num*TILESIZE,row_num*TILESIZE, cave_floor_img, 543535, 'bottom', TILESIZE*13, TILESIZE*3))
            if tile == 204: #doorways in the 200s
                player.doorway_list.append(Doorway(col_num*TILESIZE,row_num*TILESIZE, black_square, 2, 'top', TILESIZE*8, TILESIZE*9))
            if tile == 205:
                player.doorway_list.append(Doorway(col_num*TILESIZE,row_num*TILESIZE, mt_rock_entrance_img_flipped, 1543533, 'bottom', TILESIZE*8, 0))
            if tile == 300: #stairs - 300s
                player.stairs_list.append(Stair(col_num * TILESIZE, row_num * TILESIZE, stair_img))
            if tile >= 350:
                if tile == 350: #chests/signs - 350s
                    player.tile_list.append(Chest(col_num * TILESIZE, row_num * TILESIZE, sword_imgs[1], [['You got a sword.', 'Press the A key to use.', 'This item can be used to'], ['harm enemies and cut down', 'bushes.']], col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 351:
                    player.tile_list.append(Chest(col_num * TILESIZE, row_num * TILESIZE, bow_img, [['You got the bow and arrow.', 'Press the Q key to use.', 'Arrows are unlimited, but'], ['only a certain amount of', 'arrows can be shot at a', 'time.']], col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 352:
                    player.tile_list.append(Chest(col_num * TILESIZE, row_num * TILESIZE, drops_imgs[0], [['1 measely gem?', "That's not very exciting."]], col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 353:
                    player.tile_list.append(Chest(col_num * TILESIZE, row_num * TILESIZE, drops_imgs[2], [['You got 100 gems.', "You're delighted!"]], col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 354:
                    player.tile_list.append(Chest(col_num * TILESIZE, row_num * TILESIZE, gold_key_img, [['You got a key.', "Use it to open a locked", 'door.']], col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 355:
                    player.tile_list.append(Sign(col_num * TILESIZE, row_num * TILESIZE, [["Welcome to a Zelda-like", "game. Maybe you will find", 'it enjoyable.'],["Do not fail, Jameson.", "We are watching.", ":)"]], sign_img))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 356:
                    player.tile_list.append(Chest(col_num * TILESIZE, row_num * TILESIZE, drops_imgs[1], [['You got 10 gems.', "Don't spend it all in one", 'place.']], col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 357:
                    player.tile_list.append(Sign(col_num * TILESIZE, row_num * TILESIZE, [["North: Fan Residence", "West: DiPalma Shores"]], sign_img))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
            if tile >= 400: #blitted images - 400s
                if tile == 400:
                    player.background_image_list.append(BackgroundImage(col_num*TILESIZE,row_num*TILESIZE, background_img))
                if tile == 401:
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 402:
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 403:
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, locked_door_opening_imgs[3]))
                if tile == 404:
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, flowers_img))
            if tile >= 500: #temporary walls - 500s
                if tile == 500:
                    player.temp_wall_list.append(TemporaryWall(col_num*TILESIZE,row_num*TILESIZE, shrub_img, 'shrub', col_num, row_num))
                if tile == 501:
                    player.temp_wall_list.append(TemporaryWall(col_num*TILESIZE,row_num*TILESIZE, locked_door_img, 'door', col_num, row_num))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, locked_door_opening_imgs[3]))
            if tile == 600: #enemies - 600s
                player.enemy_list.append(Spider(col_num*TILESIZE,row_num*TILESIZE, red_imgs))
            if tile == 601: #enemies - 600s
                player.boss_list.append(Boss(col_num * TILESIZE, row_num * TILESIZE, 0))
                for num in range(0,4):
                    player.orb_list.append(Orb(num * math.pi / 2))
            if tile == 602: #enemies - 600s
                player.enemy_list.append(Spider(col_num*TILESIZE,row_num*TILESIZE, red_imgs))
                player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
            if tile >= 700: #special tiles - 700s
                if tile == 700:
                    disappearing_image_list.append(DisappearingImage(col_num*TILESIZE,row_num*TILESIZE, disappearing_img, 24))
                if tile == 701:
                    player.tile_list.append(Target(col_num * TILESIZE, row_num * TILESIZE, col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'half'))
                if tile == 702:
                    player.switch_barrier_sprites.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'red_switch'))
                if tile == 703:
                    player.switch_barrier_sprites.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'blue_switch'))
                if tile == 704:
                    player.pushable_block_sprites.append(Wall(col_num * TILESIZE, row_num * TILESIZE, pushable_block_img, 'pushable'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 705:
                    player.tile_list.append(Target(col_num * TILESIZE, row_num * TILESIZE, col_num, row_num))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'half'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 706:
                    player.switch_barrier_sprites.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'red_switch'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 707:
                    player.switch_barrier_sprites.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'blue_switch'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 708:
                    player.tile_list.append(Trigger(col_num * TILESIZE, row_num * TILESIZE, 'boss_1'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 709:
                    player.temp_wall_list.append(TemporaryWall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'enemy_gate', col_num, row_num, False))
                    player.animated_image_list.append(AnimatedImage(col_num * TILESIZE, row_num * TILESIZE, water_top_imgs, 100))
                if tile == 710:
                    player.temp_wall_list.append(TemporaryWall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'enemy_gate', col_num, row_num, False))
                    player.animated_image_list.append(AnimatedImage(col_num * TILESIZE, row_num * TILESIZE, water_bottom_imgs, 100))
            if tile >= 800: #animated images - 800s
                if tile == 800:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, animation_img, 100))
                if tile == 801:
                    player.animated_image_list.append(AnimatedImage(col_num * TILESIZE, row_num * TILESIZE, NPC_imgs, 100))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                    player.tile_list.append(Sign(col_num * TILESIZE, row_num * TILESIZE, [["You talked to my brother?", 'Please clear out our', 'sex dungeon! Ghosts have'],["been terrorizing that", "place for way too long.", "Take my bow and arrow"], ["with you and be careful!"]], transparent))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 802:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, waterfall_imgs, 50))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 803:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_imgs, 100))
                if tile == 804:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_top_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 805:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_right_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 806:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_bottom_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 807:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_left_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 808:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_TR_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 809:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_BR_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 810:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_BL_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 811:
                    player.animated_image_list.append(AnimatedImage(col_num*TILESIZE,row_num*TILESIZE, water_TL_imgs, 100))
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,transparent, 'half'))
                if tile == 812:
                    player.animated_image_list.append(AnimatedImage(col_num * TILESIZE, row_num * TILESIZE, NPC2_imgs, 100))
                    player.tile_list.append(Sign(col_num * TILESIZE, row_num * TILESIZE, [["Hey Mister! My brother", 'needs your help to clear', 'out an old family sex dungeon.'],["Our house is to the north.", "...now where did I put", "the key..."]], transparent))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 813:
                    player.animated_image_list.append(AnimatedImage(col_num * TILESIZE, row_num * TILESIZE, NPC_imgs, 100))
                    player.tile_list.append(Sign(col_num * TILESIZE, row_num * TILESIZE, [["Thank you for clearing out", 'our family sex dungeon! Here is', 'some money to reward you.'], ['It may not look like a lot,', 'but it is all my brother', 'and I had saved up.']], transparent, 'npc1'))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
                if tile == 814:
                    player.animated_image_list.append(AnimatedImage(col_num * TILESIZE, row_num * TILESIZE, NPC2_imgs, 100))
                    player.tile_list.append(Sign(col_num * TILESIZE, row_num * TILESIZE, [["Wow thanks man. Now our", 'ancestors can rest in', 'peace.']], transparent, 'npc2'))
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, transparent, 'full'))
            if tile >= 900: #walls - 900s
                if tile == 900:
                    player.tile_list.append(Wall(col_num*TILESIZE,row_num*TILESIZE,tile_img, 'full'))
                if tile == 901:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, window_img, 'full'))
                if tile == 902:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, roof_img, 'full'))
                if tile == 903:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_indoor_top_img, 'full'))
                if tile == 904:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_indoor_bottom_img, 'full'))
                if tile == 905:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_indoor_left_img, 'full'))
                if tile == 906:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_indoor_right_img, 'full'))
                if tile == 907:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_corner_TR_img, 'full'))
                if tile == 908:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_corner_BR_img, 'full'))
                if tile == 909:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_corner_BL_img, 'full'))
                if tile == 910:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, wall_corner_TL_img, 'full'))
                if tile == 911:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, bed_imgs[0], 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 912:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, bed_imgs[1], 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 913:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, chest_img, 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 914:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, drawer_img, 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 915:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, candle_img, 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, floorboard_img))
                if tile == 916:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, mt_rock_img, 'full'))
                if tile == 917:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, mt_rock_entrance_img, 'full'))
                if tile == 918:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_top_img, 'full'))
                if tile == 919:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_bottom_img, 'full'))
                if tile == 920:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_right_img, 'full'))
                if tile == 921:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_left_img, 'full'))
                if tile == 922:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_TR_img, 'full'))
                if tile == 923:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_BR_img, 'full'))
                if tile == 924:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_BL_img, 'full'))
                if tile == 925:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_TL_img, 'full'))
                if tile == 926:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, opened_chest_img, 'full'))
                    player.background_image_list.append(BackgroundImage(col_num * TILESIZE, row_num * TILESIZE, cave_floor_img))
                if tile == 927:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_edge_TR_img, 'full'))
                if tile == 928:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_edge_BR_img, 'full'))
                if tile == 929:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_edge_BL_img, 'full'))
                if tile == 930:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, cave_wall_edge_TL_img, 'full'))
                if tile == 931:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, opened_chest_img, 'full'))
                if tile == 932:
                    player.tile_list.append(Wall(col_num * TILESIZE, row_num * TILESIZE, fence, 'full'))
            if tile == 100: #blank space
                pass
            col_num += 1
        row_num += 1
    for wall in player.tile_list:
        tile_sprites.add(wall)
    for animated_image in player.animated_image_list:
        animated_sprites.add(animated_image)
    for disappearing_image in disappearing_image_list:
        tile_sprites.add(disappearing_image)
    for enemy in player.enemy_list:
        enemy_sprites.add(enemy)
    for orb in player.orb_list:
        enemy_sprites.add(orb)
    for boss in player.boss_list:
        enemy_sprites.add(boss)
    for shrub in player.temp_wall_list:
        tile_sprites.add(shrub)
    for stair in player.stairs_list:
        tile_sprites.add(stair)
    for doorway in player.doorway_list:
        doorway_sprites.add(doorway)
    for switch_barrier in player.switch_barrier_sprites:
        switch_barrier_sprites.add(switch_barrier)
    for pushable_block in player.pushable_block_sprites:
        switch_barrier_sprites.add(pushable_block)
    for sign in player.sign_list:
        tile_sprites.add(sign)

def reset_room():
    tile_sprites.empty()
    doorway_sprites.empty()
    enemy_sprites.empty()
    arrow_sprites.empty()
    chest_sprites.empty()
    switch_barrier_sprites.empty()
    animated_sprites.empty()
    player.background_image_list = []
    player.enemy_list = [] #resets the enemy list to zero when resetting rooms
    player.laser_list = []
    player.temp_wall_list = []
    player.tile_list = []
    player.stairs_list = []
    player.orb_list = []
    player.boss_list = []
    player.arrow_list = []
    player.doorway_list = []
    player.switch_barrier_sprites = []
    player.animated_image_list = []
    player.pushable_block_sprites = []
    player.sign_list = []

    if player.current_room == 2:
        play_song('Sounds/Music/village_theme_quieter.mp3') #plays in last room

#if a switch is supposed to be closed, prevents the animation from playing from open to closed when entering new room
def switch_barrier_animation_check():
    for switch_barrier in player.switch_barrier_sprites:
        if player.red_switch_on and switch_barrier.type == 'red_switch':
            switch_barrier.image = red_switch_barrier_imgs[0]

    for switch_barrier in player.switch_barrier_sprites:
        if not player.red_switch_on and switch_barrier.type == 'blue_switch':
            switch_barrier.image = blue_switch_barrier_imgs[0]

#need to remove all tile and enemy sprites and reload new map
def change_rooms(map_dictionary):
    if player.rect.x > WIDTH - TILESIZE//2: #going right a room
        reset_room()
        player.current_room += 1
        draw_map(map_dictionary[player.current_room], tree, tile_imgs[0:4], death_animation_imgs,red_imgs,shrub_img,tall_grass,stair_img)
        player.rect.x = 0
        switch_barrier_animation_check()

    elif player.rect.x < -TILESIZE//2: #going left a room
        reset_room()
        player.current_room -= 1
        draw_map(map_dictionary[player.current_room], tree, tile_imgs[0:4], death_animation_imgs,red_imgs,shrub_img,tall_grass,stair_img)
        player.rect.x = WIDTH-TILESIZE
        switch_barrier_animation_check()

    elif player.rect.y < -TILESIZE//2: #going up a room
        reset_room()
        player.current_room -= 1000
        draw_map(map_dictionary[player.current_room], tree, tile_imgs[0:4], death_animation_imgs,red_imgs,shrub_img,tall_grass,stair_img)
        player.rect.y = HEIGHT-TILESIZE
        switch_barrier_animation_check()

    elif player.rect.y > HEIGHT - TILESIZE//2: #going down a room
        reset_room()
        player.current_room += 1000
        draw_map(map_dictionary[player.current_room], tree, tile_imgs[0:4], death_animation_imgs,red_imgs,shrub_img,tall_grass,stair_img)
        player.rect.y = 0
        switch_barrier_animation_check()

    if player.change_room_teleport: #if player's room is set to something that is not an overworld value
        player.change_room_teleport = False
        reset_room()
        draw_map(map_dictionary[player.current_room], tree, tile_imgs[0:4], death_animation_imgs, red_imgs, shrub_img,tall_grass, stair_img)
        switch_barrier_animation_check()


#draws first room you spawn in
draw_map(overworld_dictionary[player.current_room], tree, tile_imgs[0:4], death_animation_imgs, red_imgs, shrub_img, tall_grass,stair_img)