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

class Game():
    def __init__(self):
        self.name = "Snakes on a Screen"
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(self.name)
        self.score = 0
        self.scoreFont = pygame.font.SysFont("monospace", 30)
        self.running = False
        self.sprite_list = pygame.sprite.Group()

    def gen_rand_food_coords(self):
        x = random.randint(0, WIDTH_IN_CELLS - 1)
        y = random.randint(0, HEIGHT_IN_CELLS - 1)
        x_coord = FOOD_MARGIN + x*CELL_DIM
        y_coord = FOOD_MARGIN + y*CELL_DIM
        return x_coord, y_coord

    def menu(self):
        '''
        If needed, include the menu logic here. Once the user starts the game, call
        the function to change into the game state.
        '''
        self.game_loop()

    def game_loop(self):
        '''
        The main game where the player moves around the snake.
        '''
        self.running = True
        clock = pygame.time.Clock()

        # Add the player and the tail
        player = Player(self)
        self.sprite_list.add(player)
        tail = player.create_initial_tail()
        for piece in tail:
            self.sprite_list.add(piece)


        # Add the food
        food = Food(*self.gen_rand_food_coords()) # * operator unpacks the tuple
        self.sprite_list.add(food)

        # Create the label for the score
        score_label = self.scoreFont.render("Score: ", 1, (255, 255, 255))

        # Main game loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

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

            # Handle collisions with the snake
            tail_hits = pygame.sprite.spritecollide(player, tail[1:], False)
            # don't include the first piece of the tail
            # the overlap isn't a real collision
            if tail_hits:
                self.running = False

            # Handle collisions with the walls (warp or die?)
            

            # Handle collisions with the food
            point = pygame.sprite.collide_mask(player, food)
            # TODO: analyze the performance of this call
            # Create a sprite mask at load time to increase performance?
            if point:
                food.rect.x, food.rect.y = self.gen_rand_food_coords()
                self.score = self.score + 10
                score_label = self.scoreFont.render(("Score: " + str(self.score)), 1, (255, 255, 255))
                player.extend_tail()

            # Draw the next frame
            self.screen.fill((0, 0, 0))
            self.sprite_list.draw(self.screen)
            self.screen.blit(score_label, (10, 10))
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


class Player(pygame.sprite.Sprite):
    # 0 - no movement
    # 1 - right
    # 2 - down
    # 3 - left
    # 4 - up

    def __init__(self, game):
        super(Player, self).__init__()
        self.game = game
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = MARGIN + 10*CELL_DIM
        self.rect.y = MARGIN + 10*CELL_DIM
        self.movement_list = [0] * START_LEN # Holds the past moves so the tail can follow
        self.tail = []
        self.tail_index = 1
        self.cur_dir = 0
        self.next_dir = 0
        self.movement_clock = 0
        self.not_moved = True
        self.add_tail = False

    def create_initial_tail(self):
        # Add the beginning tail. Start with START_LEN
        for x in xrange(1, START_LEN):
            new_section = TailPiece(self.tail_index, self.rect.x - x*CELL_DIM, self.rect.y,
                                    self.movement_list)
            self.tail.append(new_section)
            self.tail_index += 1
        return self.tail

    def extend_tail(self):
        '''
            This method really just sets a flag so the tail will be extended
            at the proper time.
        '''
        print "Tail add"
        self.add_tail = True

    def add_tail_section(self):
        print "Tail added"
        self.add_tail = False
        # Create the new tail section.
        # Give it the same movement as the old last tail section
        # Base its location off the old last tail section position and direction
        # Goal is so it is put in the same square that the old last one was when fruit was hit.
        cur_dir_to_x_factor = [0, -1, 0, 1, 0] # The new position is based on the direction,
        cur_dir_to_y_factor = [0, 0, -1, 0, 1] # so these make conversion easier
        old_last_tail = self.tail[self.tail_index - 2] # -2 since index starts at 1
        old_last_tail_move = old_last_tail.movement_list[old_last_tail.index] 
        new_x = old_last_tail.rect.x + (cur_dir_to_x_factor[old_last_tail_move] * CELL_DIM)
        new_y = old_last_tail.rect.y + (cur_dir_to_y_factor[old_last_tail_move] * CELL_DIM)
        new_section = TailPiece(self.tail_index, new_x, new_y, self.movement_list)
        self.movement_list.insert(self.tail_index, old_last_tail_move)
        self.tail.append(new_section)
        self.tail_index += 1
        self.game.sprite_list.add(new_section)

    def change_dir(self, new_dir):
        self.next_dir = new_dir

    def update(self):
        '''
        This function runs every frame. It updates the position, etc.
        '''
        limit = CELL_DIM / SPEED # synchronize turns, tail adds, etc. with the cell edges

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

            # This has to take place after the initial movement list is created
            # Otherwise the tail will always be one move behind
            self.movement_list.insert(0, self.cur_dir)

            if self.add_tail:
                self.add_tail_section()

        if self.cur_dir == 1:
            self.rect.x += SPEED
        elif self.cur_dir == 2:
            self.rect.y += SPEED
        elif self.cur_dir == 3:
            self.rect.x -= SPEED
        elif self.cur_dir == 4:
            self.rect.y -= SPEED

        # Update each of the tail sections
        for t in self.tail:
            t.update()


class TailPiece(pygame.sprite.Sprite):
    # 0 - no movement
    # 1 - right
    # 2 - down
    # 3 - left
    # 4 - up
    def __init__(self, index, x, y, moves):
        super(TailPiece, self).__init__()
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movement_list = moves
        self.index = index
        self.cur_dir = 0 # See class comment for list of directions and integer mappings

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


def main():
    game = Game()
    game.menu()

if __name__ == '__main__':
    main()
