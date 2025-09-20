#TO DO: PLAYER MOVES BACK SLIGHTLY AFTER TOUCHING WALL (BUG BUT COULD BE FEATURE)
from items import * #includes images, player, and functions

#is here because needs to be before enemies file (used when enemy is killed)
class DisappearingImage(pygame.sprite.Sprite):
    def __init__(self, x, y, images, animation_length):
        pygame.sprite.Sprite.__init__(self)
        self.image = images[0] #starts with first image in the list
        self.images = images
        self.rect = self.image.get_rect()  # figures out rectangle hitbox based on image
        self.rect.x = x
        self.rect.y = y
        self.animation_count = 0 #starts at zero
        self.animation_length = animation_length #image disappears when it gets to this number (needs to be a multiple of list containing images)
        self.count = 0

    def update(self):
        self.image, self.animation_count = animate(self.images, self.animation_length, self.animation_count)
        if self.animation_count >= self.animation_length-1:
            tile_sprites.remove(self)