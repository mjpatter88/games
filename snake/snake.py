#!/usr/bin/python
import pygame
import random

# Define constants
MARGIN = 3
FOOD_MARGIN = 8
BLOCK_WIDTH = 32
CELL_DIM = BLOCK_WIDTH + 2 * MARGIN
WIDTH_IN_CELLS = 30
HEIGHT_IN_CELLS = 20
SCREEN_WIDTH = WIDTH_IN_CELLS * CELL_DIM
SCREEN_HEIGHT = HEIGHT_IN_CELLS * CELL_DIM
SPEED = 2 # Always make speed a factor of "CELL_DIM" so things stay aligned.
START_LEN = 10 # Inlucding the head tile even though it's not part of the tail.

class Player(pygame.sprite.Sprite):

    # 0 - no movement
    # 1 - right
    # 2 - down
    # 3 - left
    # 4 - up
    cur_dir = 0
    next_dir = 0
    movement_clock = 0
    movement_list = [] # Holds the past moves so the tail can follow
    not_moved = True

    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = MARGIN + 10*CELL_DIM
        self.rect.y = MARGIN + 10*CELL_DIM
        self.movement_list = [0] * START_LEN

    def change_dir(self, new_dir):
        self.next_dir = new_dir

    def update(self):

        limit = CELL_DIM / SPEED

        if(self.movement_clock < limit):
            self.movement_clock += 1
        else:
            self.movement_clock = 1
            self.cur_dir = self.next_dir

            # Only do for the first move. Start moving right
            if self.not_moved and self.cur_dir != 0:
                for x in xrange(START_LEN):
                    self.movement_list.insert(0, 1)
                self.not_moved = False

            self.movement_list.insert(0, self.cur_dir)


        if self.cur_dir == 1:
            self.rect.x += SPEED
        elif self.cur_dir == 2:
            self.rect.y += SPEED
        elif self.cur_dir == 3:
            self.rect.x -= SPEED
        elif self.cur_dir == 4:
            self.rect.y -= SPEED


class TailPiece(pygame.sprite.Sprite):

    # 0 - no movement
    # 1 - right
    # 2 - down
    # 3 - left
    # 4 - up
    cur_dir = 0
    movement_list = None
    index = -1

    def __init__(self, index, x, y, moves):
        super(TailPiece, self).__init__()
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movement_list = moves
        self.index = index

    def update(self):

        if self.movement_list[self.index] == 1:
            self.rect.x += SPEED
        elif self.movement_list[self.index] == 2:
            self.rect.y += SPEED
        elif self.movement_list[self.index] == 3:
            self.rect.x -= SPEED
        elif self.movement_list[self.index] == 4:
            self.rect.y -= SPEED

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Food, self).__init__()
        self.image = pygame.image.load("images/food.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def rand_food_coords():
    x = random.randint(0, WIDTH_IN_CELLS)
    y = random.randint(0, HEIGHT_IN_CELLS)
    x_coord = FOOD_MARGIN + x*CELL_DIM
    y_coord = FOOD_MARGIN + y*CELL_DIM
    return x_coord, y_coord

def menu(screen):
    '''
    If needed, include the menu logic here. Once the user starts the game, call
    the function to change into the game state.
    '''
    snake(screen)

def snake(screen):
    '''
    The main game where the player moves around the snake.
    '''
    tail_index = 1
    running = True
    clock = pygame.time.Clock()
    sprite_list = pygame.sprite.Group()

    # Add the player
    player = Player()
    sprite_list.add(player)

    # Add the tail
    tail = [] # A list of the tail sections. Start with START_LEN.
    for x in xrange(1, START_LEN):
        new_section = TailPiece(tail_index, player.rect.x - x*CELL_DIM, player.rect.y,
                                player.movement_list)
        tail.append(new_section)
        sprite_list.add(new_section)
        tail_index += 1

    # Add the food
    food = Food(*rand_food_coords()) # * operator unpacks the tuple
    sprite_list.add(food)

    # Main game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.change_dir(3)
                elif event.key == pygame.K_RIGHT:
                    player.change_dir(1)
                elif event.key == pygame.K_DOWN:
                    player.change_dir(2)
                elif event.key == pygame.K_UP:
                    player.change_dir(4)


        player.update()
        for t in tail:
            t.update()

        # Handle collisions with the snake
        tail_hits = pygame.sprite.spritecollide(player, tail[1:], False)
        # don't include the first piece of the tail
        # the overlap isn't a real collision
        if tail_hits:
            running = False

        # Handle collisions with the walls
        

        # Handle collisions with the food
        point = pygame.sprite.collide_mask(player, food)
        # TODO: analyze the performance of this call
        # Create a sprite mask at load time to increase performance?
        
        if point:
            food.rect.x, food.rect.y = rand_food_coords()
            # print "Here"

        # Draw the next frame
        screen.fill((0, 0, 0))
        sprite_list.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption("Snakes on a Screen")
    menu(screen)

if __name__ == '__main__':
    main()
