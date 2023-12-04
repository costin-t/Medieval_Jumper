import pygame
from pygame import mixer
from pygame.locals import *
import os
from levelForWorld import *
import sys
from memory_profiler import profile

pygame.mixer.pre_init(44100, -16, 2 , 512)
screen_width = 800
screen_height = 600
mixer.init()
pygame.init()

#FPS
clock = pygame.time.Clock()
fps = 60

#definirea ecranului care ruleaza aplicatia
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption(' Medieval Jumper')

#define fonts
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
icon_image = pygame.image.load("Assets/knight.png")


pygame.display.set_icon(icon_image)

#Incarcarea imaginilor 
bird_img = pygame.image.load('Assets/bird.png')
bg_img = pygame.image.load('Assets/background.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
bg_menu = pygame.image.load('Assets/background_menu.png')
bg_menu = pygame.transform.scale(bg_menu, (screen_width, screen_height))

restart_img = pygame.image.load('Assets/restart.png')
restart_size = (90, 100)
restart_img = pygame.transform.scale(restart_img, restart_size)
start_img = pygame.image.load('Assets/start.png')
exit_img = pygame.image.load('Assets/exit.png')
help_img = pygame.image.load('Assets/help.png')


#Incarcare sunete
pygame.mixer.music.load('Assets/music.wav')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0 , 3000 )
coin_fx = pygame.mixer.Sound('Assets/coin_fx.wav')
coin_fx.set_volume(0.8)
jump_fx = pygame.mixer.Sound('Assets/jump.wav')
jump_fx.set_volume(0.3)
game_over_fx = pygame.mixer.Sound('Assets/game_over.wav')
game_over_fx.set_volume(0.4)
game_win_fx = pygame.mixer.Sound('Assets/game_win.wav')
game_win_fx.set_volume(0.4)
portal_fx = pygame.mixer.Sound('Assets/portal.wav')
portal_fx.set_volume(0.5)
menu_fx = pygame.mixer.Sound('Assets/menu.wav')
menu_fx.set_volume(0.5)


#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 9
score = 0
col_thresh = 20

#Gridul
#width = 16
#height = 12


#colors for the fond
white = (255, 255, 255)
win_restart_color = (138, 3, 3)

def draw_grid():
    for line in range(0,19):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line *tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height * tile_size))
###


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))




#function to reset level

def reset_level(level):
    player.reset(100, screen_height - 130)
    bad_mushroom_group.empty()
    lava_group.empty()
    spike_group.empty()
    coin_group.empty()
    exit_group.empty()
    platform_group.empty()
    world_data = (f'level{level}_data')
    world = World(eval(world_data))
    score_coin = Coin(tile_size // 4, tile_size // 4)
    coin_group.add(score_coin)

    return world

class Button():
    def __init__ (self, x, y, image):
        self.image = image  
        self.rect = self.image.get_rect()
        self.rect.x = x - 90 
        self.rect.y = y - 90
        self.clicked = False
        screen.blit(self.image, self.rect)
    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked condition
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                if game_over_fx.get_num_channels() > 0:
                    game_over_fx.stop()
                pygame.mixer.music.unpause()
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action

def help():
    # Load background image
    background_image = pygame.image.load('Assets/help_bg.png')
    
    # Define the instructions text and font
    font = pygame.font.SysFont('Arial Black', 19)
    text = [
        '  Escape  The  Forest',
        ''
        '   Use the arrow keys to move;',
        ' '
        '     Collect coins to earn points;',
        ' '
        "      Avoid enemies like mushroom's, spike's and lava;",
        ' '
        '         Enter to the portal to the next level;',
        ' '
    ]

    # Render the instructions text onto the surface
    text_surface_list = []
    for line in text:
        text_surface = font.render(line, True, (0, 0, 0))
        text_surface_list.append(text_surface)
    
    # Create an "Exit" button
    button_image = pygame.image.load('Assets/exit_help.png')
    button_size = (100, 50)
    exit_button_image = pygame.transform.scale(button_image, button_size)
    exit_button = Button(700, 500, exit_button_image)
    
    # Display the instructions surface in a Pygame window
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.rect.collidepoint(event.pos):
                    return True	
                
        # Blit background image
        screen.blit(background_image, (30, 95))
        
        # Blit text onto surface
        y_offset = 100
        for text_surface in text_surface_list:
            screen.blit(text_surface, (100, y_offset))
            y_offset += 45
        
        # Draw exit button
        exit_button.draw()
        
        pygame.display.update()

#player class
class Player():
    
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 5
        
        if game_over == 0:
            #get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                
                jump_fx.play()
                
                self.vel_y = -15
                self.jumped = True
                #####
              
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            # jump only once 
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
            
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
              
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.couter = 0
                self.index = 0
                
                if self.direction == 1:
                    self.image = self.stationery_right
                if self.direction == -1:
                    self.image = self.stationery_left
            

            #handle  animation imagines( iterete thro index and call from the list that number)
            if self.counter > walk_cooldown:
                self.counter = 0  
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            #add gravity 
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy +=self.vel_y

            #cHECK FOR COLLION
            self.in_air = True
            for tile in world.tile_list:

            # check for colision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

            #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground - jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    #check if above the ground -falling
                    elif self.vel_y > 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0 
                        self.in_air = False

            #check for collision with enemies
            if pygame.sprite.spritecollide(self, bad_mushroom_group, False):
                game_over = -1
                game_over_fx.play()

            #check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()
            
            if pygame.sprite.spritecollide(self, spike_group, False ):
                game_over = -1
                game_over_fx.play()
            
             #check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1


            #check for colision with platform
            for platform in platform_group:
                 # check for collision at x point
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                     dx = 1
                # check for collision at x point
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = -1
                  
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top ) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #move sideways with platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy
        
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('Game Over', font, win_restart_color, ( screen_height // 2) - 50 , screen_height // 4)
         
    
        #draw player to screen
        screen.blit(self.image, self.rect)
        #Draw the rectangle around the player
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        

        return game_over

  

    def reset (self, x, y):

        #lista pentru animatia 
        jump_img = pygame.image.load("Assets/Jump.png")
        self.jump_img_right = pygame.transform.scale(jump_img, (50, 75))
        self.jump_img_left = pygame.transform.flip(self.jump_img_right, True , False)
        fall_img = pygame.image.load("Assets/Fall.png")
        self.fall_img = pygame.transform.scale(fall_img, (45, 50))
       
        self.images_right = []
        self.images_left = []
        self.index = 0
        # counter pentru animatie
        self.counter = 0
        
        for num in range(2, 12):      
            img_right = pygame.image.load(f"Assets/run{num}.png")
            img_right = pygame.transform.scale(img_right, (45, 70))
            #Rastoarna imaginea pentru a realiza animatia
            img_left = pygame.transform.flip(img_right, True , False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        

        stationery_right = pygame.image.load("Assets/run1.png")
        self.stationery_right = pygame.transform.scale(stationery_right, (45, 70))
        stationert_left =  pygame.transform.flip(stationery_right, True , False)
        self.stationery_left = pygame.transform.scale(stationert_left, (45, 70))
       
        dead_image = pygame.image.load("Assets/death.png")
        self.dead_image = pygame.transform.scale(dead_image, (45, 50))

        # player drawing on the screen and variable for moving
        # first image of the player standing
        self.image = self.stationery_right 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        #velocity for jumping
        self.vel_y = 0
        #jump only once
        self.jumped = False
        #direction that is facing for animation
        self.direction = 0
        self.in_air = True

#world data that supply levels
class World():
    
    
    def __init__(self, data): 
       
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load("Assets/dirt.png")
        wood_img = pygame.image.load("Assets/wood.png")
        Tree_head = pygame.image.load("Assets/Tree2.png")
        log= pygame.image.load('Assets/Tree_front.png')
        pavel_img = pygame.image.load('Assets/pavel.png')
        

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size 
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                
                if tile == 2:
                    img = pygame.transform.scale(wood_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size 
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 3:

                    img = pygame.transform.scale(Tree_head, (tile_size, tile_size *2))
                    img_rect = img.get_rect() 
                    img_rect.x = col_count * tile_size 
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 4:
                    img = pygame.transform.scale(log, (tile_size, tile_size *2))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size 
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                
                if tile == 5:
                    blob = Enemy(col_count * tile_size, row_count * tile_size )
                    bad_mushroom_group.add(blob)
                    
                if tile == 6:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)

                #up platform
                if tile == 7:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)

                if tile == 8:
                    lava = Lava(col_count * tile_size, row_count * tile_size )
                    lava_group.add(lava)

                if tile == 9:
                    spike = Spike(col_count * tile_size, row_count * tile_size )
                    spike_group.add(spike)

                if tile == 10:
                    coin = Coin(col_count * tile_size + 10, row_count * tile_size + 10)
                    coin_group.add(coin)

                if tile == 11: 
                    exit = Exit(col_count * tile_size, row_count * tile_size)
                    exit_group.add(exit)

                if tile == 12:
                    img = pygame.transform.scale(pavel_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size 
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)


                col_count += 1
            row_count += 1
            #row count and col count ma ajuta sa decinda unde pe ecran se va afisa pamantul


    #atribuie pentru 0 nimic si pentru 1 pamant
    def draw(self):
        for tile in self.tile_list:
            #it tuble the 0 is image and 1 is the rectangle
            screen.blit(tile[0], tile[1])
            #rect around the dirt
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2, 3)
    



class Enemy(pygame.sprite.Sprite):
    
    def __init__(self,x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images_right = []
        self.images_left = []
        for num in range(1, 9):
            img = pygame.image.load(f"Assets/mushroom_Run{num}.png")
            img = pygame.transform.scale(img, (30, 50))
            self.images_right.append(img)
            img_left = pygame.transform.flip(img, True , False)
            self.images_left.append(img_left)
        
        self.index = 0
        self.image = self.images_left[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0
        self.move_direction = 1
        self.move_counter = 0
        
    def update(self):
        
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_left):
                self.index = 0
                
            self.image = self.images_left[self.index]
            if self.move_direction == 1:
                self.image = self.images_right[self.index]
            else:
                self.image = self.images_left[self.index]

        self.rect.x += self.move_direction
        self.move_counter += 1

        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
        


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size //2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y
    
    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/spike.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size - 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/lavaf.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 9):
            img = pygame.image.load(f"Assets/coin{num}.png")
            img = pygame.transform.scale(img, (tile_size //2 , tile_size //2 ))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0

    def update(self):
        idle_rotation = 10
        self.counter += 1
        if self.counter > idle_rotation:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/portal.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#instances
player = Player ( 100, screen_height - 130)
bad_mushroom_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#create coin for showing the score
score_coin = Coin(tile_size // 4, tile_size // 4)
coin_group.add(score_coin)

exit_button = pygame.sprite.Group()

world_data = (f'level{level}_data')
world = World(eval(world_data))

#create buttons
restart_button = Button((screen_width // 2) + 50, (screen_height// 2) + 50,  restart_img)
start_button = Button((screen_width // 2) - 50, (screen_height// 2) - 50, start_img)
exit_button = Button((screen_width //2) - 50, (screen_height // 2) + 250, exit_img)
help_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, help_img)


run = True
while run:
    
        clock.tick(fps)
        #pune pe ecran imaginea
        screen.blit(bg_img, (0,0))
        screen.blit(bird_img, (150,150))

         
        if main_menu == True:
            screen.blit(bg_menu, (0, 0))
            draw_text('MEDIEVAL JUMPER', font, white, ( screen_height // 4), screen_height // 8)
            if exit_button.draw():
                run = False
            if start_button.draw():
                main_menu = False
                menu_fx.play()
            if help_button.draw():
                menu_fx.play()
                help()
                
        else:
            world.draw()
            if game_over == 0:
                bad_mushroom_group.update()
                coin_group.update()
                platform_group.update()
                draw_text(' Level ' + str(level), font_score, white, tile_size + 50, 10)
                #score
                if pygame.sprite.spritecollide(player, coin_group, True):
                    score += 1
                    coin_fx.play()
                draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

            bad_mushroom_group.draw(screen)
            platform_group.draw(screen)
            lava_group.draw(screen)
            spike_group.draw(screen)
            exit_group.draw(screen)
            coin_group.draw(screen)
            ###
            #draw_grid()
            ###
            
            game_over = player.update(game_over)

            if game_over == -1:
               
                if restart_button.draw():
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
            
            # if player has completed the level
            if game_over == 1:
                #reset game and go to next leve
                level += 1
                if level <= max_levels:
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    portal_fx.play()
                else:
                    game_win_fx.play()
                    draw_text('You Win!', font, win_restart_color, (screen_width // 2) - 140, screen_height //4)
                    #player win
                 
                    if restart_button.draw():
                        level = 0
                        world_data = []
                        world = reset_level(level)
                        game_over = 0
                        score = 0
                        
        
        # game loop with run=true
                                         
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
       

        
        pygame.display.update()

pygame.quit()

