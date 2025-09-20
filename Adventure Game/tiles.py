'''TO DO: MAKE WALL COLLISION CHECK BETTER AND MAKE WALL COLLISION CHECK BE REFERENCED FROM THE WALL CLASS INSTEAD OF TYPING IT ALL OUT AGAIN'''
from enemies import * #includes images, player, and functions

#TEMPORARY WALL LOADING TO TEST WALL CLASS

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, image, type): #takes in the xy location of where the wall needs to be and the image of the wall
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect() #figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE) #x pos, y pox, width, and height of rectangle (dimensions are of one tile)
        self.player_hitbox_before_collision = player.hitbox #saves the player hitbox rectangle initially (used later for collision with player)
        self.collision_on = True #off only if it is a switch barrier and the appropriate color is active
        self.type = type #full has nothing passing, half has arrows passing, switch is either red_switch or blue_switch, pushable is pushable block, enemy_gate destroyed if enemies dead
        self.animation_count_switch_barriers = 0 #for animating switch barriers
        self.animation_length_switch_barriers_closing = 32
        self.pushable_block_count = 0
        self.pushable_block_length = 2
        self.pushable_block_speed = TILESIZE//25
        self.num_of_collisions = 0 #for pushable blocks

    def check_arrow_collisions(self): #checks if arrow collides with wall
        for arrow in player.arrow_list: #removes arrow and enemy if both collide
            if collision_from_rects(self.hitbox, arrow.hitbox) and not self.type == 'half': #enemy disappears if it collides with the sword, then removes itself from enemy list and sprite group
                #pygame.mixer.Channel(2).play(pygame.mixer.Sound('Sounds/Sound Effects/arrow_break.wav'))  # plays sound of arrow firing
                #checks animation type (up, right, down, left)
                if arrow.image == arrow_imgs[0]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_up_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[1]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_right_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[2]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_down_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[3]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_left_destroyed_imgs, 12)) #arrow death animation
                player.arrow_list.remove(arrow)
                arrow_sprites.remove(arrow)
    
    def check_player_and_enemy_collisions(self):
        #CHECKING COLLISION WITH PLAYER USING HITBOXES OF BOTH
        if not collision_from_rects(player.hitbox,self.hitbox):
            self.player_hitbox_before_collision = player.hitbox #saves the player hitbox rectangle as long as the player does not collide with the wall
            #print('no collision')

        if collision_from_rects(player.hitbox,self.hitbox): #if hitboxes collide, the player rect is updated (player hitbox is then updated based on the player rect)
            #UPDATES player rect (images) based on what direction the player touches the wall
            #if player's position is detected on the bottom of the wall
            if self.player_hitbox_before_collision[1] >= self.hitbox[1]+self.hitbox[3]-player.player_speed:
                player.rect.y = self.rect.y + self.hitbox[3]//2
                #print(player.hitbox)
                #print(self.hitbox[0] + self.hitbox[2])
                #print('bottom')
            #if player is above the wall
            if self.player_hitbox_before_collision[1] <= self.hitbox[1]-self.player_hitbox_before_collision[3]+player.player_speed:
                player.rect.y = self.rect.y - self.hitbox[3]
                #print('top')
            #if player is to the right of the wall #exceptions based on colliding with multiple sprites - hardcoded based on player's speed (this took a while)
            if self.player_hitbox_before_collision[0] >= self.hitbox[0]+self.hitbox[2] and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 5 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 1 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 0 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] + 2 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 3 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 3 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 2 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 0 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 11 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 1:
                player.rect.x = self.rect.x + self.hitbox[2]*3//4 + 1 #player isn't moved far enough to the right (probably from rounding), so add 1 pixel to ensure no collision
                #print('right of wall')
                #print(self.player_hitbox_before_collision[1])
            #if player is to the left of the wall
            if self.player_hitbox_before_collision[0] <= self.hitbox[0]-self.player_hitbox_before_collision[2]:
                player.rect.x = self.rect.x - self.hitbox[2]*3//4
                #print('left of wall')
                #print(self.player_hitbox_before_collision)

        player.hitbox = (player.rect.x + TILESIZE//4, player.rect.y + TILESIZE//2, TILESIZE//2, TILESIZE//2) #updates hitbox since player.rect gets updated based on collision with wall

        #CHECK COLLISION WITH ENEMY AND WALL
        for enemy in player.enemy_list:
            if collision_from_rects(enemy.hitbox, self.hitbox):
                enemy.collide_with_wall = True
                if enemy.direction == 'up': #(if facing up)
                    enemy.rect.y = self.rect.y+TILESIZE
                elif enemy.direction == 'down':
                    enemy.rect.y = self.rect.y-TILESIZE
                elif enemy.direction == 'left':
                    enemy.rect.x = self.rect.x+TILESIZE
                elif enemy.direction == 'right':
                    enemy.rect.x = self.rect.x-TILESIZE
                enemy.hitbox = (enemy.rect.x, enemy.rect.y, TILESIZE, TILESIZE) #updates hitbox based on how enemy collided with wall

    #CHECKS IF SWITCH BARRIER NEEDS TO BE CHANGED REGARDING ITS IMAGE AND COLLISION
    def check_switch_barrier(self):
        #handles the image when the switch is going from closed to open
        if self.image == red_switch_barrier_imgs[0] and not player.red_switch_on:
            tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, red_switch_barrier_imgs[1:4], 24))
        if self.image == blue_switch_barrier_imgs[0] and player.red_switch_on:
            tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, blue_switch_barrier_imgs[1:4], 24))

        #handles the switch barrier collision settings and when the images when the switch is going from open to closed
        if self.type == 'red_switch' and player.red_switch_on and not self.image == red_switch_barrier_imgs[0]:
            if self.animation_count_switch_barriers < self.animation_length_switch_barriers_closing-1: #animates image if switched and not fully closed
                self.image, self.animation_count_switch_barriers = animate(red_switch_barrier_backwards_imgs, self.animation_length_switch_barriers_closing, self.animation_count_switch_barriers)
            self.collision_on = True
        elif self.type == 'red_switch' and not player.red_switch_on:
            self.image = red_switch_barrier_imgs[3]
            self.animation_count_switch_barriers = 0 #sets count back to zero
            self.collision_on = False
        elif self.type == 'blue_switch' and player.red_switch_on:
            self.image = blue_switch_barrier_imgs[3]
            self.animation_count_switch_barriers = 0 #sets count back to zero
            self.collision_on = False
        elif self.type == 'blue_switch' and not player.red_switch_on and not self.image == blue_switch_barrier_imgs[0]:
            if self.animation_count_switch_barriers < self.animation_length_switch_barriers_closing-1: #animates image if switched and not fully closed
                self.image, self.animation_count_switch_barriers = animate(blue_switch_barrier_backwards_imgs, self.animation_length_switch_barriers_closing, self.animation_count_switch_barriers)
            self.collision_on = True

    def check_if_pushed(self):
        #if the count of colliding with the wall exceeds a certain number, the block will get pushed one tile
        if collision_from_rects(self.hitbox, player.hitbox):
            self.pushable_block_count += 1
        else:
            self.pushable_block_count = 0

        #when the pushable count exceeds the threshold
        if self.pushable_block_count >= self.pushable_block_length:
            self.pushable_block_count = 0
            self.num_of_collisions = 0
            #direction the block is faced depends on the direction buttons the player is pressing, so need to fix the glitch that comes with this
            if player.directions[0] and not player.directions[1] and not player.directions[2] and not player.directions[3]: #facing up
                self.rect.y -= self.pushable_block_speed
            if player.directions[1] and not player.directions[0] and not player.directions[2] and not player.directions[3]: #facing down
                self.rect.y += self.pushable_block_speed
            if player.directions[2] and not player.directions[0] and not player.directions[1] and not player.directions[3]: #facing left
                self.rect.x -= self.pushable_block_speed
            if player.directions[3] and not player.directions[0] and not player.directions[1] and not player.directions[2]: #facing right
                self.rect.x += self.pushable_block_speed
            self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)  # updates hitbox based on new block position
            #checks if the block will collide with a block/any of these tiles when pushed:
            for wall in player.tile_list:
                if collision_from_rects(self.hitbox, wall.hitbox):
                    self.num_of_collisions += 1
            for switch_barrier in player.switch_barrier_sprites:
                if collision_from_rects(self.hitbox, switch_barrier.hitbox):
                    if player.red_switch_on and switch_barrier.type == 'red_switch':
                        self.num_of_collisions += 1
                    elif not player.red_switch_on and switch_barrier.type == 'blue_switch':
                        self.num_of_collisions += 1
            for pushable_block in player.pushable_block_sprites:
                if collision_from_rects(self.hitbox, pushable_block.hitbox):
                    self.num_of_collisions += 1
            for stair in player.stairs_list:
                if collision_from_rects(self.hitbox, stair.hitbox):
                    self.num_of_collisions += 1
            for enemy in player.enemy_list:
                if collision_from_rects(self.hitbox, enemy.hitbox):
                    self.num_of_collisions += 1
            #if the block runs into any of the above sprites, the block's position will be restored to what it was before being pushed
            if self.num_of_collisions >= 2: #2 because it counts itself
                if player.facing_directions[0]:
                    self.rect.y += self.pushable_block_speed
                if player.facing_directions[1]:
                    self.rect.y -= self.pushable_block_speed
                if player.facing_directions[2]:
                    self.rect.x += self.pushable_block_speed
                if player.facing_directions[3]:
                    self.rect.x -= self.pushable_block_speed
                self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)  # updates hitbox based on new block position

    def update(self):
        self.check_switch_barrier()
        if self.type == 'pushable':
            self.check_if_pushed()
        if self.collision_on: #collision only on if not an unactivated switch
            self.check_arrow_collisions()
            self.check_player_and_enemy_collisions()



class AnimatedImage(pygame.sprite.Sprite):
    def __init__(self, x, y, images, animation_length):
        pygame.sprite.Sprite.__init__(self)
        self.image = images[0]
        self.images = images
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.animation_count = 0
        self.animation_length = animation_length #needs to be a multiple of the length of the image list

    def update(self):
        self.image, self.animation_count = animate(self.images, self.animation_length, self.animation_count)

class TemporaryWall(pygame.sprite.Sprite):
    def __init__(self, x, y, image, type, col_num, row_num, full_wall = True):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)
        self.type = type #shrub is destroyed by sword, cracked_wall destroyed by bomb, door destroyed by key consumption, enemy_gate is destroyed by no more enemies
        self.col_num = col_num
        self.row_num = row_num
        self.full_wall = full_wall

    def check_arrow_collisions(self): #checks if arrow collides with wall
        for arrow in player.arrow_list: #removes arrow and enemy if both collide
            if collision_from_rects(self.hitbox, arrow.hitbox) and self.full_wall: #enemy disappears if it collides with the sword, then removes itself from enemy list and sprite group
                #checks animation type (up, right, down, left)
                if arrow.image == arrow_imgs[0]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_up_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[1]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_right_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[2]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_down_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[3]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_left_destroyed_imgs, 12)) #arrow death animation
                player.arrow_list.remove(arrow)
                arrow_sprites.remove(arrow)

    def update(self):
        self.check_arrow_collisions()
        #CHECKS COLLISION WITH SWORD AND IS TYPE SHRUB
        if collision_from_rects(self.hitbox, sword.hitbox) and self.type == 'shrub':  # enemy disappears if it collides with the sword, then removes itself from temporary list and sprite group
            tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, death_animation_imgs, 24))
            player.temp_wall_list.remove(self)
            tile_sprites.remove(self)

        #CHECKS COLLISION WITH PLAYER AND IS TYPE DOOR AND PLAYER HAS A KEY
        if collision_from_rects(self.hitbox, player.hitbox) and self.type == 'door' and player.key_amount > 0:  # door disappears if it collides with player and player has key
            player.key_amount -= 1
            if not player.mute:
                pygame.mixer.Channel(5).play(pygame.mixer.Sound('Sounds/Sound Effects/slam_wood.wav'))

            #for when room is left, this door will not load anymore (changes map data):
            overworld_dictionary[player.current_room][self.row_num][self.col_num] = 403

            tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, locked_door_opening_imgs, 24))
            player.temp_wall_list.remove(self)
            tile_sprites.remove(self)

        #CHECKS IF TYPE IS ENEMY_GATE AND ALL ENEMIES ARE DEAD
        if self.type == 'enemy_gate' and len(player.enemy_list) == 0 and player.ghost_boss_dead:
            tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, death_animation_imgs, 24))
            player.background_image_list.append(BackgroundImage(self.rect.x, self.rect.y, bridge_img, True))
            player.temp_wall_list.remove(self)
            tile_sprites.remove(self)

        #CHECKING COLLISION WITH PLAYER USING HITBOXES OF BOTH
        if not collision_from_rects(player.hitbox,self.hitbox):
            self.player_hitbox_before_collision = player.hitbox #saves the player hitbox rectangle as long as the player does not collide with the wall
            #print('no collision')

        if collision_from_rects(player.hitbox,self.hitbox): #if hitboxes collide, the player rect is updated (player hitbox is then updated based on the player rect)
            #UPDATES player rect (images) based on what direction the player touches the wall
            #if player's position is detected on the bottom of the wall
            if self.player_hitbox_before_collision[1] >= self.hitbox[1]+self.hitbox[3]-player.player_speed:
                player.rect.y = self.rect.y + self.hitbox[3]//2
                #print(player.hitbox)
                #print(self.hitbox[0] + self.hitbox[2])
                #print('bottom')
            #if player is above the wall
            if self.player_hitbox_before_collision[1] <= self.hitbox[1]-self.player_hitbox_before_collision[3]+player.player_speed:
                player.rect.y = self.rect.y - self.hitbox[3]
                #print('top')
            #if player is to the right of the wall #exceptions based on colliding with multiple sprites - hardcoded based on player's speed (this took a while)
            if self.player_hitbox_before_collision[0] >= self.hitbox[0]+self.hitbox[2] and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 5 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 1 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 0 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] + 2 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] + self.hitbox[3] - 3 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 3 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 2 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 0 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 11 and \
               self.player_hitbox_before_collision[1] != self.hitbox[1] - player.hitbox[3] + 1:
                player.rect.x = self.rect.x + self.hitbox[2]*3//4 + 1 #player isn't moved far enough to the right (probably from rounding), so add 1 pixel to ensure no collision
                #print('right of wall')
                #print(self.player_hitbox_before_collision[1])
            #if player is to the left of the wall
            if self.player_hitbox_before_collision[0] <= self.hitbox[0]-self.player_hitbox_before_collision[2]:
                player.rect.x = self.rect.x - self.hitbox[2]*3//4
                #print('left of wall')
                #print(self.player_hitbox_before_collision)

        player.hitbox = (player.rect.x + TILESIZE//4, player.rect.y + TILESIZE//2, TILESIZE//2, TILESIZE//2) #updates hitbox since player.rect gets updated based on collision with wall

        #CHECK COLLISION WITH ENEMY AND WALL
        for enemy in player.enemy_list:
            if collision_from_rects(enemy.hitbox, self.hitbox):
                enemy.collide_with_wall = True
                if enemy.direction == 'up': #(if facing up)
                    enemy.rect.y = self.rect.y+TILESIZE
                elif enemy.direction == 'down':
                    enemy.rect.y = self.rect.y-TILESIZE
                elif enemy.direction == 'left':
                    enemy.rect.x = self.rect.x+TILESIZE
                elif enemy.direction == 'right':
                    enemy.rect.x = self.rect.x-TILESIZE
                enemy.hitbox = (enemy.rect.x, enemy.rect.y, TILESIZE, TILESIZE) #updates hitbox based on how enemy collided with wall

class BackgroundImage(pygame.sprite.Sprite):
    def __init__(self, x, y, image, front = False):
        self.image = image
        self.rectx = x
        self.recty = y
        self.front = front

    def draw_img(self):
        screen.blit(self.image, (self.rectx, self.recty))

class Stair(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)

class Doorway(pygame.sprite.Sprite):
    def __init__(self, x, y, image, room, side_of_tile, x_teleport, y_teleport):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        if side_of_tile == 'top':
            self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE//2) #hitbox is shorter than
        elif side_of_tile == 'bottom':
            self.hitbox = (self.rect.x, self.rect.y+15*TILESIZE//16, TILESIZE, TILESIZE // 2)
        self.room = room #room number, see map file for types of rooms
        self.x_teleport = x_teleport
        self.y_teleport = y_teleport

    def update(self):
        if collision_from_rects(player.hitbox, self.hitbox):
            player.current_room = self.room #usually in the single digits for rooms in houses, is set to larger number when back in overworld again
            player.change_room_teleport = True
            player.rect.x = self.x_teleport
            player.rect.y = self.y_teleport

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, text, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y + TILESIZE, TILESIZE, TILESIZE // 2)  # area where player needs to be to read sign
        self.text = text

    def update(self):
        if collision_from_rects(player.hitbox, self.hitbox) and player.facing_directions[0] and player.e_pressed:
            textbox(self.text)

class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y, item, text, col_num, row_num):
        pygame.sprite.Sprite.__init__(self)
        self.image = chest_img
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.opened = False #chest not opened by default
        self.item = item
        self.hitbox = (self.rect.x, self.rect.y + TILESIZE, TILESIZE, TILESIZE//2) #area where player needs to be to open chest
        self.player_img_before_opening = player_imgs[0] #placeholder, is used so that player image is updated to it's original img after opening chest
        self.frame_waited = False #to make the animation of player holding up item and chest opening happen before textbox appears
        self.textbox_appeared = False
        self.text = text #what is being said
        self.col_num = col_num
        self.row_num = row_num

    def update(self):
        #displays textbox after player animation and chest opening happens:
        if self.frame_waited and not self.textbox_appeared: #frame waited and textbox has not already appeared
            screen.blit(self.item, (player.rect.x, player.rect.y - TILESIZE))
            self.textbox_appeared = True
            textbox(self.text)
            player.image = self.player_img_before_opening #returns players image back to what it was

            #for when room is left, this chest will not load anymore (changes map data):
            overworld_dictionary[player.current_room][self.row_num][self.col_num] = 931
        #opens chest if player is in front of chest, facing up, chest is not already opened, and interact key is pressed
        if collision_from_rects(player.hitbox, self.hitbox) and player.facing_directions[0] and not self.opened and player.e_pressed:
            if not player.mute:
                pygame.mixer.Channel(5).play(pygame.mixer.Sound('Sounds/Sound Effects/pickup.wav'))
            self.player_img_before_opening = player.image  # saves player image for after item holding up is complete
            self.image = opened_chest_img
            player.image = player_imgs[13]
            self.opened = True #makes it so dialog can't happen again or animation
            self.frame_waited = True

            #inventory additions:
            if self.item == sword_imgs[1]:
                player.sword_get = True
            elif self.item == bow_img:
                player.bow_get = True
            elif self.item == drops_imgs[0]:
                player.money += 1
            elif self.item == drops_imgs[1]:
                player.money += 10
            elif self.item == drops_imgs[2]:
                player.money += 100
            elif self.item == gold_key_img:
                player.key_amount += 1

class Target(pygame.sprite.Sprite):
    def __init__(self, x, y, col_num, row_num):
        pygame.sprite.Sprite.__init__(self)
        self.image = target_imgs[0]
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE) #area where arrow needs to hit the target
        self.col_num = col_num
        self.row_num = row_num

    def update(self):
        for arrow in player.arrow_list:  # removes arrow if both collide
            if collision_from_rects(self.hitbox,arrow.hitbox):
                if not player.mute:
                    pygame.mixer.Channel(5).play(pygame.mixer.Sound('Sounds/Sound Effects/switch_flipped.wav'))
                # checks animation type (up, right, down, left)
                if arrow.image == arrow_imgs[0]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_up_destroyed_imgs, 12))  # arrow death animation
                if arrow.image == arrow_imgs[1]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_right_destroyed_imgs, 12))  # arrow death animation
                if arrow.image == arrow_imgs[2]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_down_destroyed_imgs, 12))  # arrow death animation
                if arrow.image == arrow_imgs[3]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_left_destroyed_imgs, 12))  # arrow death animation
                player.arrow_list.remove(arrow)
                arrow_sprites.remove(arrow)

                #changes world state from red to blue or blue to red depending on what exists now
                if player.red_switch_on:
                    player.red_switch_on = False #blue
                    tile_sprites.add(DisappearingImage(self.hitbox[0], self.hitbox[1], red_target_to_blue_imgs, 15))
                else:
                    player.red_switch_on = True
                    tile_sprites.add(DisappearingImage(self.hitbox[0], self.hitbox[1], blue_target_to_red_imgs, 15))

        #changes image depending on what world setting is set to (red or blue)
        if player.red_switch_on:
            self.image = target_imgs[0]
        else:
            self.image = target_imgs[1]

class Trigger(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = transparent
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)  # area where player needs to be to trigger the trigger
        self.type = type
        self.triggered = False #is set to True when it is triggered so it doesn't keep getting triggered

    def update(self):
        if collision_from_rects(self.hitbox, player.hitbox) and not self.triggered:
            self.triggered = True
            if self.type == 'boss_1' and not player.ghost_boss_dead:
                pygame.mixer.music.stop()
                textbox([['So you are trying to clear', 'this tomb? Silly boy. No', 'one has been able to'], ['defeat me since my death', '100 years ago!']], True)
                player.boss_list.append(Boss(TILESIZE * 15 // 2, 1.5 * TILESIZE, 0))
                for num in range(0, 4):
                    player.orb_list.append(Orb(num * math.pi / 2))
                for boss in player.boss_list:
                    enemy_sprites.add(boss)
                for orb in player.orb_list:
                    enemy_sprites.add(orb)