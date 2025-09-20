'''TO DO: Clean up diagonal movement portion of code to be shorter in length'''
from images import *
from map_data import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #APPEARANCE
        self.image = player_imgs[0] #default image for player
        self.rect = self.image.get_rect() #figures out rectangle hitbox based on image
        self.rect.center = (TILESIZE*5, TILESIZE*5)
        self.hitbox = (self.rect.x + TILESIZE//4, self.rect.y + TILESIZE//2, TILESIZE//2, TILESIZE//2) #x pos, y pox, width, and height of rectangle (TEMPORARY DIMENSIONS RN)
        self._layer = 1 #the sprite's layer is defined here, and 1 is for top layer
        
        #MOVEMENT AND MOVEMENT ANIMATIONS
        self.player_speed = TILESIZE // 10 #use tilesize so speed is influenced by screen size (//10 for fast movement)
        self.directions = [False, True, False, False] #up, down, left, right (player facing down by default) [depends on the keys pressed - multiple ones can be true if diagonal]
        self.facing_directions = [False, True, False, False] #these are what the image is facing - only one can be true at a time {up, down, left, right}
        self.keys_directions = [False, False, False, False] #these keep track of what keys are being pressed (all are False if not pressing any direction)
        self.animation_count = 0 #used for walking
        self.animation_speed = 20 #sets how fast the walking animation goes (20 works well)
        self.diagonal_movement = False #false by default
        self.diagonal_coord_offset = int(math.sqrt(self.player_speed**2/2)) #used pythagorean theorem to have diagonal speed equal to player speed (so 3 here if speed is 5)
        self.previous_direction = 'right' #by default (may change later)
        self.ismoving = False #is True when pressing any of the direction keys, False if otherwise
        self.stunned = False #prevents player from moving when true
        self.jim_down = player_imgs[1:3]
        self.jim_up = player_imgs[3:5]
        self.jim_right = player_imgs[5:7]
        self.jim_left = player_imgs[7:9]
        
        #HEALTH
        self.health = 6 #start with 3 hearts
        self.invincible = False #only true for a period of time after getting hit by something
        self.invincible_animation_count = 0 #count used for animation for being invincible
        self.invincible_img_animation_speed = 20 #for how often player flickers when hit
        self.invincible_img_animation_count = 0
        self.invincible_time_length = 120
        self.noninvincible_img = self.image
        self.noninvincible_img_stationary = self.image
        self.alive = True #player is alive by default
        
        #COLLISIONS
        self.collision_with_jim_time = 0 #is used for timing the invincibility frames

        #BUTTONS PRESSED
        self.e_pressed = False #True for one frame when e button (interact) is pressed
        
        #OTHER ANIMATIONS
        self.original_frame = tree #used for saving previous image for item animation
        self.item_animation_count = 0 #used for using an item
        self.item_animation_speed = 12 #sets how fast the item use animation is - 12 is the best
        
        #INVENTORY/FLAGS
        self.mute = False
        self.shield_up = True
        self.key_amount = 0 #player has zero keys to default in the beginning of the game
        self.sword_get = False #starts out false until you get the sword
        self.bow_get = False
        self.money_displayed = 0 #starts at 0 (adds up every frame to reach self.money)
        self.money = 0
        self.unlocked_door = False
        self.item_used = False #when true, movement is stopped and the animation of using an item is done (see code below)
        self.sword_used = False #True when pressing attack button, is False when not on screen anymore, used to distinguish which item is being used
        self.current_room = 544533 #544533 is the default room, 1543533 is boss room
        self.change_room_teleport = False #for when rooms are changed when hiting a doorway (aka teleport)
        self.item_timer_length = 15
        self.item_timer_count = self.item_timer_length #gets set to 0 when arrow is used, and goes up every frame until it hits timer length, and then can shoot arrow again
        self.red_switch_on = True #red switch is on by default until player shoots a target to make it blue
        self.ghost_boss_dead = False

        #OTHER SPRITE LISTS (SHOULD BE IN GAME CLASS.. IF I HAD ONE. BUT THERE IS ONLY ONE PLAYER SO THIS WORKS)
        self.enemy_list = [] #for storing enemies - only one enemy_list, so it is kept in the player class (only one player)
        self.laser_list = []
        self.temp_wall_list = []
        self.tile_list = [] #all walls and chests, stored in player class because there is only ever one player
        self.stairs_list = []
        self.orb_list = []
        self.boss_list = []
        self.arrow_list = []
        self.doorway_list = []
        self.background_image_list = []
        self.switch_barrier_sprites = []
        self.animated_image_list = []
        self.pushable_block_sprites = []
        self.sign_list = []

        #SWORD VARIABLES
        self.sword_out = False #sword is out by default

    def movement(self):
        # MOVEMENT
        keys = pygame.key.get_pressed()

        #keeps track of what keys are pressed down and which ones aren't (implemented to have indication of
        if keys[pygame.K_UP]:
            self.keys_directions[0] = True
        else:
            self.keys_directions[0] = False
        if keys[pygame.K_DOWN]:
            self.keys_directions[1] = True
        else:
            self.keys_directions[1] = False
        if keys[pygame.K_LEFT]:
            self.keys_directions[2] = True
        else:
            self.keys_directions[2] = False
        if keys[pygame.K_RIGHT]:
            self.keys_directions[3] = True
        else:
            self.keys_directions[3] = False


        if not self.item_used and not self.stunned:  # player can only move if not stunned or using an item or if not colliding with an object
            if keys[pygame.K_DOWN] and not keys[pygame.K_UP] and not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                self.diagonal_movement = False  # sets to false when moving in one direction only
                self.rect.y += self.player_speed
                self.directions = [False, True, False, False]
                self.facing_directions = self.directions

                self.image, self.animation_count = animate(self.jim_down, self.animation_speed, self.animation_count)

            if keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                self.diagonal_movement = False
                self.rect.y -= self.player_speed
                self.directions = [True, False, False, False]
                self.facing_directions = self.directions

                self.image, self.animation_count = animate(self.jim_up, self.animation_speed, self.animation_count)

            if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT] and not keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
                self.diagonal_movement = False
                self.rect.x += self.player_speed
                self.directions = [False, False, False, True]
                self.facing_directions = self.directions

                self.image, self.animation_count = animate(self.jim_right, self.animation_speed, self.animation_count)

            if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                self.diagonal_movement = False
                self.rect.x -= self.player_speed
                self.directions = [False, False, True, False]
                self.facing_directions = self.directions

                self.image, self.animation_count = animate(self.jim_left, self.animation_speed, self.animation_count)

            # if diagonal movement is occurring:
            if (keys[pygame.K_RIGHT] and keys[pygame.K_UP]) or (keys[pygame.K_RIGHT] and keys[pygame.K_DOWN]) or (
                    keys[pygame.K_LEFT] and keys[pygame.K_UP]) or (keys[pygame.K_LEFT] and keys[pygame.K_DOWN]):
                if not self.diagonal_movement:  # finds original frame if more than one key is being pressed to move
                    if self.directions[0]:
                        self.previous_direction = 'up'
                    if self.directions[1]:
                        self.previous_direction = 'down'
                    if self.directions[2]:
                        self.previous_direction = 'left'
                    if self.directions[3]:
                        self.previous_direction = 'right'
                self.diagonal_movement = True  # sets to true once previous direction is saved

                # if moving up and right:
                if keys[pygame.K_RIGHT] and keys[pygame.K_UP] and not keys[pygame.K_LEFT] and not keys[pygame.K_DOWN]:
                    self.directions = [True, False, False, True]
                    self.rect.x += self.diagonal_coord_offset
                    self.rect.y -= self.diagonal_coord_offset

                    if self.previous_direction == 'right':
                        self.image, self.animation_count = animate(self.jim_right, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, False, True]
                    elif self.previous_direction == 'up':
                        self.image, self.animation_count = animate(self.jim_up, self.animation_speed, self.animation_count)
                        self.facing_directions = [True, False, False, False]
                    else:  # if previous frame is not up or right for some reason, defaults to right (same for other diagonal directions except with left instead of right, respectively
                        self.image, self.animation_count = animate(self.jim_right, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, False, True]

                # if moving down and left:
                if keys[pygame.K_LEFT] and keys[pygame.K_DOWN] and not keys[pygame.K_RIGHT] and not keys[pygame.K_UP]:
                    self.directions = [False, True, True, False]
                    self.rect.x -= self.diagonal_coord_offset
                    self.rect.y += self.diagonal_coord_offset

                    if self.previous_direction == 'left':
                        self.image, self.animation_count = animate(self.jim_left, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, True, False]
                    elif self.previous_direction == 'down':
                        self.image, self.animation_count = animate(self.jim_down, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, True, False, False]
                    else:
                        self.image, self.animation_count = animate(self.jim_left, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, True, False]

                # if moving up and left:
                if keys[pygame.K_LEFT] and keys[pygame.K_UP] and not keys[pygame.K_RIGHT] and not keys[pygame.K_DOWN]:
                    self.directions = [True, False, True, False]
                    self.rect.x -= self.diagonal_coord_offset
                    self.rect.y -= self.diagonal_coord_offset

                    if self.previous_direction == 'left':
                        self.image, self.animation_count = animate(self.jim_left, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, True, False]
                    elif self.previous_direction == 'up':
                        self.image, self.animation_count = animate(self.jim_up, self.animation_speed, self.animation_count)
                        self.facing_directions = [True, False, False, False]
                    else:
                        self.image, self.animation_count = animate(self.jim_left, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, True, False]

                # if moving down and right:
                if keys[pygame.K_RIGHT] and keys[pygame.K_DOWN] and not keys[pygame.K_LEFT] and not keys[pygame.K_UP]:
                    self.directions = [False, True, False, True]
                    self.rect.x += self.diagonal_coord_offset
                    self.rect.y += self.diagonal_coord_offset

                    if self.previous_direction == 'right':
                        self.image, self.animation_count = animate(self.jim_right, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, False, True]
                    elif self.previous_direction == 'down':
                        self.image, self.animation_count = animate(self.jim_down, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, True, False, False]
                    else:
                        self.image, self.animation_count = animate(self.jim_right, self.animation_speed, self.animation_count)
                        self.facing_directions = [False, False, False, True]

        if self.keys_directions[0] or self.keys_directions[1] or self.keys_directions[2] or self.keys_directions[3]: #checks if player is moving or not
            self.ismoving = True
        else:
            self.ismoving = False

        self.hitbox = (self.rect.x + TILESIZE // 4, self.rect.y + TILESIZE // 2, TILESIZE // 2,TILESIZE // 2)  # after movement, hitbox is updated - TEMPORARY SIZE OF HITBOX

        #ANIMATION FOR WHEN INVINCIBLE
        #separates moving and stationary invincible animation (restores to original image when not invincible anymore too)
        self.noninvincible_img = self.image
        #line below this is pretty buggy (might want to fix since animation with player and item use image with transparent image isn't good)
        if self.image != transparent and self.image != player_imgs[9] and self.image != player_imgs[10] and self.image != player_imgs[11] and self.image != player_imgs[12]:
            self.noninvincible_img_stationary = self.image
        if self.invincible and self.ismoving: #if invincible and moving
            self.image, self.invincible_img_animation_count = animate([self.noninvincible_img, transparent], self.invincible_img_animation_speed, self.invincible_img_animation_count)
        elif self.invincible and not self.ismoving:
            self.image, self.invincible_img_animation_count = animate([self.noninvincible_img_stationary, transparent], self.invincible_img_animation_speed, self.invincible_img_animation_count)
        if not self.invincible and self.image == transparent:
            self.image = self.noninvincible_img_stationary

    def use_item(self):
        # ITEM USED ANIMATION: if item used is true, then the action of attacking plays out and jim cannot move. if he does, the animation is interrupted
        if self.item_used:
            if self.item_animation_count == 0:
                self.original_frame = self.image
            self.shield_up = False

            # for changing player's image for animation (depends on direction player is facing)
            if self.facing_directions[0]:
                self.image = player_imgs[10]
            elif self.facing_directions[1]:
                self.image = player_imgs[9]
            elif self.facing_directions[2]:
                self.image = player_imgs[12]
            else:
                self.image = player_imgs[11]

            # updates counter for item animation
            self.item_animation_count += 1
            if self.item_animation_count > self.item_animation_speed:
                self.item_animation_count = 0
                self.image = self.original_frame
                self.item_used = False
                self.bow_used = False
                self.sword_used = False #sets these variables to False whenever action is done

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True

    def update_money_display(self):
        if player.money > player.money_displayed:
            player.money_displayed += 1
            if not self.mute:
                pygame.mixer.Channel(4).play(pygame.mixer.Sound('Sounds/Sound Effects/coin_get.wav'))

    def update_speed(self):
        #speed is set to normal at beginning of this, but if the player is touching any stair, it slows down (goes back to normal after not colliding with stair)
        self.player_speed = TILESIZE//12 #//10 for fast movement
        self.diagonal_coord_offset = TILESIZE//16  # pythagorean theorem to find the diagonal speed if the player speed is 3
        for stair in self.stairs_list:
            if collision_from_rects(self.hitbox, stair.hitbox):
                self.player_speed = TILESIZE//17 #makes it 2
                self.diagonal_coord_offset = int(math.sqrt(player.player_speed ** 2 / 2)) #pythagorean theorem to find the diagonal speed if the player speed is 3

    def update(self):
        self.movement()
        self.use_item()
        self.update_speed()
        self.update_money_display()

        #CHECKS IF DAMAGE CAN HAPPEN AGAIN TO PLAYER (INVINCIBILITY)
        if self.invincible:
            self.invincible_animation_count += 1
            if self.invincible_animation_count > self.invincible_time_length:
                self.invincible = False
                self.invincible_animation_count = 0


#ONCE CLASS IS ESTABLISHED - initializes player and adds player to the sprite group
player = Player()
player_sprites = pygame.sprite.LayeredUpdates() #creates the player sprite group and establishes layers
player_sprites.add(player)