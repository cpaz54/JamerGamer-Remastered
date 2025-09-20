#HANDLES PAUSE MENU, OTHER MENUS, AND TEXT MENUS WHEN TEXT APPEARS FOR YOU TO INTERACT WITH
from death import *

def title_screen():
    running_title_screen = True
    screen.blit(title_screen_img,(0,0))
    while running_title_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running_title_screen = False
        pygame.display.update()

def pause_game():
    running_pause = True
    my_font = pygame.font.SysFont("Arial", 75, True)  # this needs to be after pygame.init()
    screen.blit(my_font.render('PAUSE', 1, BLACK), (WIDTH // 2-100, HEIGHT // 2-75))
    while running_pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    running_pause = False
        pygame.display.update()

def textbox(text, override_bottom = False):
    SCROLL_SPEED = 20

    #textbox displays at top if player is at bottom and vice versa
    if player.rect.y < HEIGHT//2 or not override_bottom:
        textbox_height_origin = HEIGHT - TILESIZE*5 #textbox appears at bottom of screen
    if player.rect.y >= HEIGHT//2 or override_bottom:
        textbox_height_origin = TILESIZE #textbox appears at top of screen
    if override_bottom:
        textbox_height_origin = HEIGHT - TILESIZE * 5  # textbox appears at bottom of screen
    textbox_width_origin = WIDTH - TILESIZE*16.5

    #initializes variables for while loop
    paragraph_count = 0
    new_line = True
    new_paragraph = True
    running_textbox = True #true when textbox is being blitted on
    scrolling_text = True #true when text is scrolling on textbox
    while running_textbox:
        clock.tick(FPS)  # this one line makes this while loop run at the FPS specified in the setup file (could probably just delete this line)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if scrolling_text: #if textbox is continued before scrolling text is finished, blits entire textbox on screen and stops scrolling text animation
                        scrolling_text = False
                        line_count = 0
                        for line in text[paragraph_count]:
                            my_font.render_to(screen, (int(textbox_width_origin + TILESIZE//1.667), int(textbox_height_origin + TILESIZE//1.667 + line_count * TILESIZE*1.2)), line, WHITE)
                            line_count += 1
                    else: #if text is not scrolling anymore, goes to next textbox and continues scrolling
                        scrolling_text = True
                        paragraph_count += 1
                        new_paragraph = True
                        if paragraph_count == len(text): #if the paragraph count is greater than the number of paragraphs, text loop ENDS
                            scrolling_text = False
                            running_textbox = False
                            player.e_pressed = False #no longer pressed down (e is what makes it pop up in the first place

        pygame.time.delay(SCROLL_SPEED) #amount of milliseconds between each character being displayed

        if scrolling_text:
            if new_line: #if new line, character count is set back to zero
                char_count = 0 #number of characters being shown
                new_line = False
            if new_paragraph: #if new paragraph, everything is set back to zero
                line_count = 0 #used to have multiple lines of text in textbox
                char_count = 0
                new_paragraph = False
            #blits rectangles for text blitting
            pygame.draw.rect(screen, (102,51,0), (textbox_width_origin, textbox_height_origin, TILESIZE*16, TILESIZE*4))
            pygame.draw.rect(screen, (137, 87, 46), (textbox_width_origin + TILESIZE//5, textbox_height_origin + TILESIZE//5, TILESIZE*16, TILESIZE*4))
            my_font = pygame.freetype.Font("prstartk.ttf", int(TILESIZE//1.667))  # this needs to be after pygame.init(), swmono, snapitc, romans

            line = text[paragraph_count][line_count][0:char_count] #line to be blitted, increases in one character every time while loop happens
            my_font.render_to(screen, (int(textbox_width_origin + TILESIZE//1.667), int(textbox_height_origin + TILESIZE//1.667 + line_count*TILESIZE*1.2)), line, WHITE) #line count affects line spacing
            if not player.mute and char_count % 3 == 0: #plays sound every 3 characters and if not muted
                pygame.mixer.Channel(1).play(pygame.mixer.Sound('Sounds/Sound Effects/text_beep.wav'))
            char_count += 1
            if char_count > len(text[paragraph_count][line_count]): #changes line if char count is above the amount of chars for that line
                new_line = True
                line_count += 1
            if line_count == len(text[paragraph_count]): #stops scrolling text once the max amount of lines are displayed for that paragraph
                scrolling_text = False

            if line_count > 0: #blits first line if second line is being drawn or greater
                my_font.render_to(screen, (int(textbox_width_origin + TILESIZE//1.667), int(textbox_height_origin + TILESIZE//1.667 + 0 * TILESIZE*1.2)),text[paragraph_count][0], WHITE) #prints first line
            if line_count > 1: #blits second line if third line is being drawn
                my_font.render_to(screen, (int(textbox_width_origin + TILESIZE//1.667), int(textbox_height_origin + TILESIZE//1.667 + 1 * TILESIZE*1.2)),text[paragraph_count][1], WHITE) #prints second line

            my_font.render_to(screen, (int(textbox_width_origin + TILESIZE*15.5), int(textbox_height_origin + TILESIZE*3.4)), 'e', WHITE) #renders "e" on bottom right, might change this later

        pygame.display.update() #updates display