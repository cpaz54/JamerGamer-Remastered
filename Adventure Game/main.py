'''TO DO: Have screen shaking, add knockback from enemies and decrease health when touched, screen transitions, two different hitboxes for player'''
import pygame

'''BUGS: Player slows down when moving against wall but not facing it'''

from map import * #includes all tile classes (also images and setup and player and tiles)

title_screen() #runs title screen initial image before game
if not player.mute:
    play_song('Sounds/Music/overworld_music_quieter.mp3') #initially plays song at beginning
#Game Loop
def main(screen):
    ###TEMPORARY CODE FOR DISPLAYING FPS
    frame_times = []
    start_t = pygame.time.get_ticks()
    
    fullscreen = False #used below for toggling fullscreen (not full screen by default)
    running = True
    #screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # pycharm needs me to put this here for some reason (other interpreter doesn't need it)
    while running:
        #keeps loop running at the right speed
        clock.tick(FPS)

        player.e_pressed = False  # set to true if e is pressed, but if not, is false each frame (before events)
        #process input (events) [excludes arrow keys for movement which are in player class]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.VIDEORESIZE:
                if not fullscreen: #can only resize screen when not in full screen
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                
            if event.type == pygame.KEYDOWN: #happens if key is pressed down (only once, so can't hold down button)
                if event.key == pygame.K_a and player.sword_get and player.item_timer_count == player.item_timer_length: #only if a button is pressed, the player has the sword, and bow timer is updated
                    player.item_used = True
                    player.sword_used = True
                if event.key == pygame.K_f: #toggles full screen and not full screen (fullscreen variable declared above)
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                if event.key == pygame.K_p:
                    pause_game()
                if event.key == pygame.K_e:
                    player.e_pressed = True #for talking to people and opening chests
                if event.key == pygame.K_j:
                    player.jumping = True
                if event.key == pygame.K_c: #shows this image on the screen
                    player.image = player_imgs[13]

                # shoots arrow if key pressed, count charged up, and if the player has the bow
                if event.key == pygame.K_q and player.item_timer_count == player.item_timer_length and player.bow_get:
                    player.arrow_list.append(Arrow())
                    player.item_timer_count = 0 #makes it lower so there is a bummer with arrow shooting
                    if not player.mute:
                        pygame.mixer.Channel(1).play(pygame.mixer.Sound('Sounds/Sound Effects/arrow.wav'))  # plays sound of arrow firing
                    for arrow in player.arrow_list:
                        arrow_sprites.add(arrow)
                        player.item_used = True
        if player.item_timer_count < player.item_timer_length: #makes count equal to length eventually
            player.item_timer_count += 1
                
        # Update
        player_sprites.update()
        item_sprites.update()
        enemy_sprites.update()
        tile_sprites.update()
        animated_sprites.update()
        chest_sprites.update()
        doorway_sprites.update()
        arrow_sprites.update()
        switch_barrier_sprites.update()


        #TEMPORARY - checks if a room needs to be changed (happens every frame)
        change_rooms(overworld_dictionary)

        '''#TEMPORARY VISUALIZATION OF SCREEN
        for i in range(0,9):
            screen.blit(tree,(0,100*i))
        for i in range(0,16):
            screen.blit(tree,(100*i,0))
        #END OF TEMPORARY VISUALIZATION OF SCREEN'''

        #print(len(player.enemy_list))

        # Draw / render
        if player.current_room < 1000000: #outside
            screen.fill(GROUND_COLOR) #for some reason, this is the only place where screen cannot be filled (pass screen through function instead)
        if player.current_room > 1000000: #in cave
            screen.fill(CAVE_COLOR)
        for background_img in player.background_image_list:
            if not background_img.front:
                background_img.draw_img()
        animated_sprites.draw(screen)
        switch_barrier_sprites.draw(screen)
        for background_img in player.background_image_list:
            if background_img.front: #draws background image in front of animated sprites if front is specified as True
                background_img.draw_img()
        tile_sprites.draw(screen)
        doorway_sprites.draw(screen)
        chest_sprites.draw(screen)
        enemy_sprites.draw(screen)
        item_sprites.draw(screen)
        #for arrow in player.arrow_list:
            #pygame.draw.rect(screen, (255,0,0), arrow.hitbox)
        arrow_sprites.draw(screen)
        player_sprites.draw(screen)

        #TEMPORARY HITBOX DRAWING AND OTHER IMAGES
        #pygame.draw.rect(screen, (0,0,0), player.hitbox)
        #pygame.draw.rect(screen, (255,0,0), sword.hitbox)
        #screen.blit(target_imgs[0],(500,200))
        #screen.blit(target_imgs[1], (450, 200))
        #screen.blit(numbers_spritesheet_imgs[0], (50, 50))
        
        #TEMPORARY CODE FOR DISPLAYING FPS
        end_t = pygame.time.get_ticks()
        time_taken = end_t - start_t
        start_t = end_t
        frame_times.append(time_taken)
        frame_times = frame_times[-20:]
        fps = len(frame_times) / sum(frame_times)
        my_font = pygame.font.SysFont("default lol", 40) #this needs to be after pygame.init()
        screen.blit(my_font.render('FPS:' + str(round(fps*1000)), 3, BLACK), (0, 0))

        screen.blit(my_font.render('HEALTH: ' + str(player.health), 3, BLACK), (0, 30))
        screen.blit(my_font.render('MONEY: ' + str(player.money_displayed), 3, BLACK), (0, 60))
        screen.blit(my_font.render('KEYS: ' + str(player.key_amount), 3, BLACK), (0, 90))
        pygame.draw.rect(screen, (0, 0, 0), (WIDTH - TILESIZE * 3, 0, TILESIZE*2 + 25, TILESIZE-5))
        pygame.draw.rect(screen, (100, 255, 0), (WIDTH-TILESIZE*3+5,5,int(TILESIZE*3*player.item_timer_count/12-72),TILESIZE-15))
        
        pygame.display.update()

    pygame.quit()

main(screen)