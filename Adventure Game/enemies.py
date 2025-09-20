from pause import *
'''spiders can't go in one tile gaps because of how they're movement is programmed - not a bug but just worth mentioning'''

class Spider(pygame.sprite.Sprite):
    def __init__(self, x, y, images):  # takes in the xy location of where the wall needs to be and the image of the wall
        pygame.sprite.Sprite.__init__(self)
        self.image = images[0]
        self.images = images #down by default
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)  # x pos, y pox, width, and height of rectangle [MIGHT WANT TO TWEAK THIS]
        self.direction = 'down' #up, down, left, right (facing down by default)
        self.direction_options = ['up', 'down', 'left', 'right', 'stop', 'stop']
        self.speed = int(TILESIZE/50)
        self.health = 1 #DO SOMETHING WITH THIS
        self.animation_count = 0 #for animation counting
        self.animation_speed = 30 #affects how fast the enemy walk animation is
        self.cycle_length = random.randint(int(TILESIZE*0.5),int(TILESIZE*1.5)) #how long until a new direction is chosen (speed times this value is how far the enemy will move)
        self.cycle_count = self.cycle_length+100 #for how long the enemy walks in a certain direction, is above length by default to choose a direction for the enemy right away
        self.collide_with_wall = False #turns true if enemy collides with wall

    def check_collisions(self):
        #if sword collides with enemy
        if collision_from_rects(self.hitbox, sword.hitbox): #enemy disappears if it collides with the sword, then removes itself from enemy list and sprite group
            tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y,death_animation_imgs, 24))
            player.enemy_list.remove(self)
            enemy_sprites.remove(self)
            if not player.mute:
                pygame.mixer.Channel(4).play(pygame.mixer.Sound('Sounds/Sound Effects/spider_death.wav'))
        #if arrow collides with enemy
        for arrow in player.arrow_list: #removes arrow and enemy if both collide
            if collision_from_rects(self.hitbox, arrow.hitbox): #enemy disappears if it collides with the sword, then removes itself from enemy list and sprite group
                tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y,death_animation_imgs, 24)) #enemy death animation
                #checks animation type (up, right, down, left)
                if arrow.image == arrow_imgs[0]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_up_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[1]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_right_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[2]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_down_destroyed_imgs, 12)) #arrow death animation
                if arrow.image == arrow_imgs[3]:
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_left_destroyed_imgs, 12)) #arrow death animation
                player.enemy_list.remove(self)
                enemy_sprites.remove(self)
                player.arrow_list.remove(arrow)
                arrow_sprites.remove(arrow)
                if not player.mute:
                    pygame.mixer.Channel(4).play(pygame.mixer.Sound('Sounds/Sound Effects/spider_death.wav'))

        #if player collides with enemy (player takes damage and knockback)
        if collision_from_rects(self.hitbox, player.hitbox) and not player.invincible:
            player.take_damage(1)
            original_player_rect = player.rect #stores original location of player for if he collides into
            if player.hitbox[0] < self.hitbox[0] and player.hitbox[1] < self.hitbox[1]:
                player.rect.x -= TILESIZE
                player.rect.y -= TILESIZE
            if player.hitbox[0] < self.hitbox[0] and player.hitbox[1] > self.hitbox[1]:
                player.rect.x -= TILESIZE
                player.rect.y += TILESIZE
            if player.hitbox[0] > self.hitbox[0] and player.hitbox[1] < self.hitbox[1]:
                player.rect.x += TILESIZE
                player.rect.y -= TILESIZE
            if player.hitbox[0] > self.hitbox[0] and player.hitbox[1] > self.hitbox[1]:
                player.rect.x += TILESIZE
                player.rect.y += TILESIZE

            for wall in player.tile_list: #checks every wall in wall list, and if player collided with wall, player takes no knockback
                if collision_from_rects(player.hitbox,wall.hitbox):
                    player.rect = original_player_rect

    def movement(self):
        # MOVEMENT
        self.cycle_count += 1
        if self.cycle_count > self.cycle_length:
            self.direction = self.direction_options[random.randrange(0, len(self.direction_options))]
            self.cycle_count = -1
            self.collide_with_wall = False  # turns true after some time to not stop movement

        if not self.collide_with_wall:
            if self.direction == 'up' and self.rect.y > 0:
                self.rect.y -= self.speed
                self.image, self.animation_count = animate(self.images[0:2], self.animation_speed, self.animation_count)
            elif self.direction == 'down' and self.rect.y < HEIGHT - TILESIZE:
                self.rect.y += self.speed
                self.image, self.animation_count = animate(self.images[2:4], self.animation_speed, self.animation_count)
            elif self.direction == 'left' and self.rect.x > 0:
                self.rect.x -= self.speed
                self.image, self.animation_count = animate(self.images[4:6], self.animation_speed, self.animation_count)
            elif self.direction == 'right' and self.rect.x < WIDTH - TILESIZE:
                self.rect.x += self.speed
                self.image, self.animation_count = animate(self.images[6:8], self.animation_speed, self.animation_count)

    def update(self):
        self.movement()
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE) #updates hitbox based on movement
        self.check_collisions() #checks collision with sword and player

#GHOST BOSS ENEMIES:
class Boss(pygame.sprite.Sprite): #lines in quotes were temporary and were taken out because big laser idea was scrapped
    def __init__(self, x, y, t):  # takes in the xy location of where the wall needs to be and the image of the wall
        pygame.sprite.Sprite.__init__(self)
        self.image = ghost_imgs[0] #by default
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.x_origin = self.rect.x
        self.y_origin = self.rect.y
        self.t = t
        self.animation_count = 0 #for animation counting
        self.animation_speed = 40 #affects how fast the enemy animation is, should be multiple of what list is
        self.transparent = True #if true, ghost is transparent, if not, not transparent (True by default)
        self.health = 3 #3 phases, 0 is when boss dies
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE*2, TILESIZE*2)
        self.laser_speed = 0.005 #1st phase number, the greter it is means more lasers
        self.is_moved = False #is true when first updated to signify when music starts

    def update(self):
        #PLAY BOSS MUSIC
        if not self.is_moved: #only true for first frame
            play_song('Sounds/Music/boss_battle_theme.mp3')  # plays boss music
        self.is_moved = True

        #these functions make the boss move in a figure 8 pattern
        self.rect.x = self.x_origin + math.sin(self.t)*TILESIZE*5
        self.rect.y = self.y_origin + math.cos(self.t) * math.sin(self.t) * TILESIZE//2
        if self.transparent: #only moves if the ghost is transparent
            self.t += 0.02
        if self.t >= math.pi * 2:  # prevents t variable from getting too big (2pi is the highest number needed)
            self.t = 0
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE*2, TILESIZE*2) #updates hitbox based on boss position
        #animation laughing ghost (only if transparent)
        if self.transparent:
            self.image, self.animation_count = animate(ghost_imgs[0:2], self.animation_speed, self.animation_count)

        #checks if image should be transparent
        if self.transparent: #transparent
            self.image.set_alpha(150)
        else: #makes image not transparent
            self.image.set_alpha(255)

        #checks if there are any orbs left (stops moving if no more orbs left):
        if len(player.orb_list) < 1:
            self.transparent = False
            self.image, self.animation_count = animate(ghost_imgs[6:8], self.animation_speed, self.animation_count)

        #checks arrow collision with boss:
        if not self.transparent:
            for arrow in player.arrow_list: #if arrow hits non transparent boss, the boss isn't transparent anymore and loses one health
                if collision_from_rects(self.hitbox, arrow.hitbox):  #if hit by arrow
                    tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_up_destroyed_imgs, 12))  # arrow death animation
                    player.arrow_list.remove(arrow)
                    arrow_sprites.remove(arrow)
                    if self.health == 3: #if finished with 1st phase:
                        self.laser_speed = 0.006
                        for num in range(0, 4):
                            player.orb_list.append(Orb(num * math.pi / 2))
                        for orb in player.orb_list:
                            enemy_sprites.add(orb)
                        if not player.mute:
                            pygame.mixer.Channel(3).play(pygame.mixer.Sound('Sounds/Sound Effects/laughing.wav'))
                    if self.health == 2: #if finished with 2nd phase:
                        self.laser_speed = 0.002
                        for num in range(0,8):
                            player.orb_list.append(Orb(num * math.pi / 4))
                        for orb in player.orb_list:
                            enemy_sprites.add(orb)
                        if not player.mute:
                            pygame.mixer.Channel(3).play(pygame.mixer.Sound('Sounds/Sound Effects/laughing.wav'))
                    self.transparent = True
                    self.health -= 1
                    if self.health == 0: #if boss is dead
                        pygame.mixer.Channel(3).play(pygame.mixer.Sound('Sounds/Sound Effects/eye_hurt.wav'))
                        pygame.mixer.music.stop() #stops music from playing
                        player.ghost_boss_dead = True
                        tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, big_death_animation_imgs, 24))  # orb death animation
                        player.boss_list.remove(self)
                        enemy_sprites.remove(self)

        #check if one eye is left (quicker shots with one eye left):
        if len(player.orb_list) == 1:
            self.laser_speed = 0.07

class EyeLaser(pygame.sprite.Sprite):
    def __init__(self, x, y):  # takes in the xy location of where the wall needs to be and the image of the wall
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILESIZE//8,TILESIZE//2))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE//8, TILESIZE//2)

    def remove(self):
        player.laser_list.remove(self)
        enemy_sprites.remove(self)

    def update(self):
        self.rect.y += TILESIZE//10
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE // 8, TILESIZE // 2) #updates hitbox
        if self.rect.y >= HEIGHT:
            self.remove()

        #if player collides with enemy (player takes damage and knockback)
        if collision_from_rects(self.hitbox, player.hitbox) and not player.invincible:
            player.take_damage(1)
            self.remove() #laser disappears if it hits player
            original_player_rect = player.rect #stores original location of player for if he collides into
            player.rect.y += TILESIZE #player always gets knocked back downward from laser

            for wall in player.tile_list: #checks every wall in wall list, and if player collided with wall, player takes no knockback
                if collision_from_rects(player.hitbox,wall.hitbox):
                    player.rect = original_player_rect

class Orb(pygame.sprite.Sprite):
    def __init__(self, t):  # takes in the xy location of where the wall needs to be and the image of the wall
        pygame.sprite.Sprite.__init__(self)
        self.image = eye_orb_img
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = 0 #is 0 but gets updated immediately to follow ghost boss
        self.rect.y = 0
        self.x_origin = self.rect.x
        self.y_origin = self.rect.y
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)
        self.t = t
        self.blink = False
        self.blink_length = 10 #for how long the eye stays blinked
        self.blink_timer = 0 #for count variable
        self.health = 3 #for arrow hitting: 3 is white, 2 is yellow, 1 is red, and 0 is dead (white by default)

    def update(self):
        #UPDATES POSITION TO CENTER AROUND GHOST
        for boss in player.boss_list: #makes position origin equal to boss position so it follows the boss
            self.x_origin = boss.rect.x + TILESIZE//2
            self.y_origin = boss.rect.y + TILESIZE//2

        #ORB PATTERN AROUND BOSS DEPENDS ON HEALTH OF BOSS:
        for boss in player.boss_list: #phase 3 is elliptical movement
            if boss.health == 3:
                #makes orbs move in an elliptical pattern (parametric equations):
                self.rect.x = self.x_origin + math.cos(self.t) * TILESIZE * 3
                self.rect.y = self.y_origin + 0.3 * math.sin(self.t) * TILESIZE * 3
                self.t += 0.02
            elif boss.health == 2:
                #slightly faster than previous phase:
                self.rect.x = self.x_origin + math.cos(self.t) * TILESIZE * 3
                self.rect.y = self.y_origin + 0.3 * math.sin(self.t) * TILESIZE * 3
                self.t += 0.04
            elif boss.health == 1: #final and 3rd phase
                #makes orbs move in a different pattern:
                self.rect.x = self.x_origin + (math.cos(3*self.t) + math.cos(3*self.t)/2 + math.sin(1*self.t)/3) * (TILESIZE)
                self.rect.y = self.y_origin + (math.sin(3*self.t) + math.sin(3*self.t)/2 + math.cos(1*self.t)/3) * (TILESIZE)
                self.t += 0.02

        if self.t >= math.pi * 2:  # prevents t variable from getting too big (2pi is the highest number needed)
            self.t = 0
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE) #updates after moving

        for arrow in player.arrow_list:
            if collision_from_rects(arrow.hitbox, self.hitbox):
                self.health -= 1
                tile_sprites.add(DisappearingImage(arrow.rect.x, arrow.rect.y, arrow_up_destroyed_imgs, 12)) #arrow death animation
                player.arrow_list.remove(arrow)
                arrow_sprites.remove(arrow)
                if self.health == 2:
                    self.image = eye_orb_yellow_img
                    if not player.mute:
                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('Sounds/Sound Effects/eye_injure.wav'))
                elif self.health == 1:
                    self.image = eye_orb_red_img
                    if not player.mute:
                        pygame.mixer.Channel(2).play(pygame.mixer.Sound('Sounds/Sound Effects/eye_injure.wav'))
                elif self.health < 1:
                    if not player.mute:
                        pygame.mixer.Channel(3).play(pygame.mixer.Sound('Sounds/Sound Effects/eye_hurt.wav'))
                    tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y, death_animation_imgs, 24)) #orb death animation
                    player.orb_list.remove(self)
                    enemy_sprites.remove(self)

        #checks if orb blinks (random)
        if not self.blink and random.random() < 0.0045: #if random chance and not already blinking, make image blink
            self.image = eye_orb_closed_img
            self.blink = True
        if self.blink: #if blinking, runs timer. if the timer runs out, the eye no longer blinks
            self.blink_timer += 1
            if self.blink_timer >= self.blink_length: #unblinks
                self.blink = False
                self.blink_timer = 0
                if self.health == 3:
                    self.image = eye_orb_img
                elif self.health == 2:
                    self.image = eye_orb_yellow_img
                else:
                    self.image = eye_orb_red_img

        #checks if orb should shoot laser:
        for boss in player.boss_list:
            if random.random() < boss.laser_speed:
                if not player.mute:
                    pygame.mixer.Channel(6).play(pygame.mixer.Sound('Sounds/Sound Effects/laser.wav'))
                player.laser_list.append(EyeLaser(self.rect.x+TILESIZE//2, self.rect.y+TILESIZE//2))
                tile_sprites.add(DisappearingImage(self.rect.x, self.rect.y+TILESIZE, laser_animation_imgs, 12)) #laser shoot animation
                for laser in player.laser_list:
                    enemy_sprites.add(laser)