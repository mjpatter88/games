#!/usr/bin/python
import pygame

# Define constants
MARGIN = 3
BLOCK_WIDTH = 32
CELL_DIM = BLOCK_WIDTH + 2 * MARGIN
WIDTH_IN_CELLS = 30
HEIGHT_IN_CELLS = 20
SCREEN_WIDTH = WIDTH_IN_CELLS * CELL_DIM
SCREEN_HEIGHT = HEIGHT_IN_CELLS * CELL_DIM
SPEED = 2 # Always make speed a factor of "CELL_DIM" so things stay aligned.

class Player(pygame.sprite.Sprite):

    # 0 - no movement
    # 1 - right
    # 2 - down
    # 3 - left
    # 4 - up
    cur_dir = 0
    next_dir = 0
    movement_clock = 0

    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = MARGIN + 10*CELL_DIM
        self.rect.y = MARGIN + 10*CELL_DIM

    def change_dir(self, new_dir):
        self.next_dir = new_dir

    def update(self):

        limit = CELL_DIM / SPEED

        if(self.movement_clock < limit):
            self.movement_clock += 1
        else:
            self.movement_clock = 1
            self.cur_dir = self.next_dir

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

    def __init__(self, x, y):
        super(TailPiece, self).__init__()
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def change_dir(self, new_dir):
        self.next_dir = new_dir

    def update(self):

        if self.cur_dir == 1:
            self.rect.x += SPEED
        elif self.cur_dir == 2:
            self.rect.y += SPEED
        elif self.cur_dir == 3:
            self.rect.x -= SPEED
        elif self.cur_dir == 4:
            self.rect.y -= SPEED

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
    running = True
    clock = pygame.time.Clock()
    sprite_list = pygame.sprite.Group()

    player = Player()
    sprite_list.add(player)

    tail = [] # A list of the tail sections. Start with 3.
    for x in xrange(3):
        new_section = TailPiece(player.rect.x - (x+1)*CELL_DIM, player.rect.y)
        tail.append(new_section)
        sprite_list.add(new_section)



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
