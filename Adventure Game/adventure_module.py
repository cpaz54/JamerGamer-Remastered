'''Adventure game module for integration with main game'''
import pygame
from map import * #includes all tile classes (also images and setup and player and tiles)

def run_adventure_game(screen):
    """Run the adventure game and return completion status"""
    global player
    
    # Initialize the adventure game
    title_screen() #runs title screen initial image before game
    if not player.mute:
        play_song('Sounds/Music/overworld_music_quieter.mp3') #initially plays song at beginning
    
    ###TEMPORARY CODE FOR DISPLAYING FPS
    frame_times = []
    start_t = pygame.time.get_ticks()
    
    fullscreen = False #used below for toggling fullscreen (not full screen by default)
    running = True
    
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
                        
                # Check for escape key to return to main game
                if event.key == pygame.K_ESCAPE:
                    return player.ghost_boss_dead
                    
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
        arrow_sprites.draw(screen)
        player_sprites.draw(screen)

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
        
        # Check if boss is defeated and return
        if player.ghost_boss_dead:
            return True

    return player.ghost_boss_dead
