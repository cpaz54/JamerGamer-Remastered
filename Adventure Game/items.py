from player import *

class Sword(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sword_imgs[0] #sword is pointing up by default
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = -1000  # sword is stored off screen when not used (prevents visual bug)
        self.rect.y = -1000
        self.animation_count = -1 #starts one before 0 for indexing
        self.animation_speed = player.item_animation_speed
        self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE) #hitbox is initially the entire sword when offscreen

    def facing_up(self):
        self.image = sword_imgs[7:10][math.floor(self.animation_count / (self.animation_speed / len(sword_imgs[7:10])))]

        self.rect.x = player.rect.x
        self.rect.y = player.rect.y - TILESIZE + 8

        if self.image == sword_imgs[7]:
            self.rect.x = player.rect.x - TILESIZE // 2
            self.hitbox = (self.rect.x+TILESIZE//2, self.rect.y+TILESIZE//2, TILESIZE//2, TILESIZE//2)
        elif self.image == sword_imgs[8]:
            self.rect.x = player.rect.x
            self.hitbox = (self.rect.x-TILESIZE//4, self.rect.y, TILESIZE*1.5, TILESIZE//2)
        elif self.image == sword_imgs[9]:
            self.rect.x = player.rect.x + TILESIZE // 2
            self.hitbox = (self.rect.x, self.rect.y+TILESIZE//2, TILESIZE//2, TILESIZE//2)

    def facing_down(self):
        self.image = sword_imgs[3:6][math.floor(self.animation_count / (self.animation_speed / len(sword_imgs[3:6])))]

        self.rect.x = player.rect.x
        self.rect.y = player.rect.y + TILESIZE - 8

        if self.image == sword_imgs[3]:
            self.rect.x = player.rect.x + TILESIZE // 2
            self.hitbox = (self.rect.x, self.rect.y, TILESIZE//2, TILESIZE//2)
        elif self.image == sword_imgs[4]:
            self.rect.x = player.rect.x
            self.hitbox = (self.rect.x-TILESIZE//4, self.rect.y+TILESIZE//2, TILESIZE*1.5, TILESIZE//2)
        elif self.image == sword_imgs[5]:
            self.rect.x = player.rect.x - TILESIZE // 2
            self.hitbox = (self.rect.x+TILESIZE//2, self.rect.y, TILESIZE//2, TILESIZE//2)

    def facing_left(self):
        if math.floor(self.animation_count / (self.animation_speed / len(sword_imgs[5:8]))) == 0:
            self.image = sword_imgs[7]
        elif math.floor(self.animation_count / (self.animation_speed / len(sword_imgs[5:8]))) == 2:
            self.image = sword_imgs[5]
        else:
            self.image = sword_imgs[6]

        self.rect.x = player.rect.x - TILESIZE + 8
        self.rect.y = player.rect.y

        if self.image == sword_imgs[5]:
            self.rect.y = player.rect.y + TILESIZE // 2
            self.hitbox = (self.rect.x+TILESIZE//2, self.rect.y, TILESIZE//2, TILESIZE//2)
        elif self.image == sword_imgs[6]:
            self.rect.y = player.rect.y
            self.hitbox = (self.rect.x, self.rect.y-TILESIZE//4, TILESIZE//2, TILESIZE*1.5)
        elif self.image == sword_imgs[7]:
            self.rect.y = player.rect.y - TILESIZE // 2
            self.hitbox = (self.rect.x+TILESIZE//2, self.rect.y+TILESIZE//2, TILESIZE//2, TILESIZE//2)

    def facing_right(self):
        self.image = sword_imgs[1:4][math.floor(self.animation_count / (self.animation_speed / len(sword_imgs[1:4])))]

        self.rect.x = player.rect.x + TILESIZE - 8
        self.rect.y = player.rect.y

        if self.image == sword_imgs[1]:
            self.rect.y = player.rect.y - TILESIZE // 2
            self.hitbox = (self.rect.x, self.rect.y+TILESIZE//2, TILESIZE//2, TILESIZE//2)
        elif self.image == sword_imgs[2]:
            self.rect.y = player.rect.y
            self.hitbox = (self.rect.x+TILESIZE//2, self.rect.y-TILESIZE//4, TILESIZE//2, TILESIZE*1.5)
        elif self.image == sword_imgs[3]:
            self.rect.y = player.rect.y + TILESIZE // 2
            self.hitbox = (self.rect.x, self.rect.y, TILESIZE // 2, TILESIZE // 2)

    def update(self):
        # spawns sword in the player's hand
        if player.item_used and player.sword_get and player.sword_used: #only true when player is in animation for item use and the player has a sword in inventory
            self.animation_count += 1
            if self.animation_count >= self.animation_speed:
                self.animation_count = 0

            if player.facing_directions[3]:
                self.facing_right()
            elif player.facing_directions[2]:
                self.facing_left()
            elif player.facing_directions[1]:
                self.facing_down()
            elif player.facing_directions[0]:
                self.facing_up()
        else:
            self.rect.x = -1000
            self.rect.y = -1000
            self.hitbox = (self.rect.x, self.rect.y, TILESIZE, TILESIZE)

        if self.animation_count == 0 and not player.mute: #if sword is being spawned in, plays sounde effect
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('Sounds/Sound Effects/sword_swipe.wav'))  # plays sound of sword swinging

#ONCE CLASS IS ESTABLISHED - initializes sword and adds sword to the item sprite group
sword = Sword() #sets player layer to 1 (in front of sword layer)
item_sprites = pygame.sprite.LayeredUpdates() #makes sprite group and makes layers
item_sprites.add(sword)


class Arrow(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.speed = int(TILESIZE//6.25)
        if player.facing_directions[0]:
            self.image = arrow_imgs[0] #arrow points up
            self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
            self.rect.x = player.rect.x
            self.rect.y = player.rect.y - TILESIZE//4
        if player.facing_directions[3]:
            self.image = arrow_imgs[1] #arrow points right
            self.rect = self.image.get_rect()
            self.rect.x = player.rect.x + TILESIZE//2
            self.rect.y = player.rect.y
        if player.facing_directions[1]:
            self.image = arrow_imgs[2] #arrow points down
            self.rect = self.image.get_rect()
            self.rect.x = player.rect.x
            self.rect.y = player.rect.y + TILESIZE//2
        if player.facing_directions[2]:
            self.image = arrow_imgs[3] #arrow points left
            self.rect = self.image.get_rect()
            self.rect.x = player.rect.x - TILESIZE//2
            self.rect.y = player.rect.y

        self.hitbox = (-2000, -1000, TILESIZE, TILESIZE) #updated later in this class, off screen hitbox for a frame

    def update(self):
        #MOVEMENT and hitbox locations
        if self.image == arrow_imgs[0]: #goes up
            self.rect.y -= self.speed
            self.hitbox = (self.rect.x + TILESIZE//2, self.rect.y, TILESIZE//TILESIZE, TILESIZE//TILESIZE)  # initializes hitbox (changes in update function)
        elif self.image == arrow_imgs[1]: #goes right
            self.rect.x += self.speed
            self.hitbox = (self.rect.x + TILESIZE*0.9, self.rect.y + TILESIZE//2, TILESIZE//TILESIZE, TILESIZE//TILESIZE)
        elif self.image == arrow_imgs[2]: #goes down
            self.rect.y += self.speed
            self.hitbox = (self.rect.x + TILESIZE//2, self.rect.y + TILESIZE*0.9, TILESIZE//TILESIZE, TILESIZE//TILESIZE)
        elif self.image == arrow_imgs[3]: #goes left
            self.rect.x -= self.speed
            self.hitbox = (self.rect.x, self.rect.y + TILESIZE//2, TILESIZE//TILESIZE, TILESIZE//TILESIZE)

        #DESPAWN IF OFF SCREEN
        if self.rect.x > WIDTH or self.rect.x < -TILESIZE or self.rect.y > HEIGHT or self.rect.y < -TILESIZE:
            player.arrow_list.remove(self)
            arrow_sprites.remove(self)