#!/usr/bin/python
import pygame
import random
import sqlite3

# Define constants
MARGIN = 4
FOOD_MARGIN = 8
BLOCK_WIDTH = 32
CELL_DIM = BLOCK_WIDTH + 2 * MARGIN
WIDTH_IN_CELLS = 30
HEIGHT_IN_CELLS = 20
SCREEN_WIDTH = WIDTH_IN_CELLS * CELL_DIM
SCREEN_HEIGHT = HEIGHT_IN_CELLS * CELL_DIM
EASY_SPEED = 2 # Always make speed a factor of "CELL_DIM" so things stay aligned.
MED_SPEED = 4 
HARD_SPEED = 8
START_LEN = 10 # Inlucding the head tile even though it's not part of the tail.
DB_NAME = "snake.db"

class Game():
    def __init__(self):
        self.name = "Snakes on a Screen"
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(self.name)
        self.score = 0
        self.myFont = pygame.font.SysFont("monospace", 30)
        self.running = False
        self.sprite_list = pygame.sprite.Group()
        self.speed = HARD_SPEED
        self.bonus = 0 # Bonus points given based on how quickly fruit is captured
        # If it doesn't exist, create a high scores database
        self.dbConnection = sqlite3.connect(DB_NAME)
        self.dbCursor = self.dbConnection.cursor()
        self.dbCursor.execute('''CREATE TABLE IF NOT EXISTS high_scores
                     (score INTEGER, name TEXT, date TEXT)''')
        #TODO: Here look for a high score in the db, etc

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
        # TODO: implement a basic menu allowing the user to change speed
        # TODO: pause functionality?
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
        #TODO: make sure the fruit doesn't get added on the tail.

        # Create the label for the score and the bonus
        score_label = self.myFont.render("Score: ", 1, (255, 255, 255))
        bonus_label = self.myFont.render("Bonus: ", 1, (255, 255, 255))
        high_score_label = self.myFont.render("High Score: ", 1, (255, 255, 255))

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
            if self.bonus > 0:
                self.bonus = self.bonus - 1

            # Handle collisions with the snake
            tail_hits = pygame.sprite.spritecollide(player, tail[1:], False)
            # don't include the first piece of the tail the overlap isn't a real collision
            if tail_hits:
                self.running = False
                #TODO: call the end game menu, etc.

            # Handle collisions with the walls (warp or die?)
            #TODO: this

            # Handle collisions with the food
            point = pygame.sprite.collide_mask(player, food)
            # Create a sprite mask at load time to increase performance?
            if point:
                food.rect.x, food.rect.y = self.gen_rand_food_coords()
                #TODO: make sure the fruit doesn't get added on the tail.
                self.score = self.score + 10 + self.bonus + random.randint(0, 5)
                self.bonus = 5 * player.get_length() + self.bonus # Add in the remaining old bonus
                score_label = self.myFont.render(("Score: " + str(self.score)), 1, (255, 255, 255))
                player.extend_tail()

            # Draw the next frame
            bonus_label = self.myFont.render(("Bonus: " + str(self.bonus)), 1, (255, 255, 255))
            self.screen.fill((0, 0, 0))
            self.sprite_list.draw(self.screen)
            self.screen.blit(score_label, (10, 10))
            self.screen.blit(bonus_label, (SCREEN_WIDTH - 200, 10))
            self.screen.blit(high_score_label, (SCREEN_WIDTH/2 - 200, 10))
            pygame.display.flip()
            clock.tick(60)

        self.dbConnection.close()
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
        self.rect.x = MARGIN + 10*CELL_DIM # Set the starting position
        self.rect.y = MARGIN + 10*CELL_DIM
        self.movement_list = [0] * START_LEN # Holds the past moves so the tail can follow
        self.tail = []
        self.tail_index = 1
        self.cur_dir = 0
        self.next_dir = 0
        self.movement_clock = 0
        self.not_moved = True
        self.add_tail = False
        self.speed = game.speed
        self.length = START_LEN

    def create_initial_tail(self):
        # Add the beginning tail. Start with START_LEN
        for x in xrange(1, START_LEN):
            new_section = TailPiece(self.tail_index, self.rect.x - x*CELL_DIM, self.rect.y,
                                    self.movement_list, self.speed)
            self.tail.append(new_section)
            self.tail_index += 1
        return self.tail

    def extend_tail(self):
        '''
            This method really just sets a flag so the tail will be extended
            at the proper time.
        '''
        self.add_tail = True

    def add_tail_section(self):
        '''
        Create the new tail section.
        Give it the same movement as the old last tail section
        Base its location off the old last tail section position and direction
        Goal is so it is put in the same square that the old last one was when fruit was hit.
        '''
        self.add_tail = False
        self.length = self.length + 1
        cur_dir_to_x_factor = [0, -1, 0, 1, 0] # The new position is based on the direction,
        cur_dir_to_y_factor = [0, 0, -1, 0, 1] # so these make conversion easier
        old_last_tail = self.tail[self.tail_index - 2] # -2 since index starts at 1
        old_last_tail_move = old_last_tail.movement_list[old_last_tail.index] 
        new_x = old_last_tail.rect.x + (cur_dir_to_x_factor[old_last_tail_move] * CELL_DIM)
        new_y = old_last_tail.rect.y + (cur_dir_to_y_factor[old_last_tail_move] * CELL_DIM)
        new_section = TailPiece(self.tail_index, new_x, new_y, self.movement_list, self.speed)
        self.movement_list.insert(self.tail_index, old_last_tail_move)
        self.tail.append(new_section)
        self.tail_index += 1
        self.game.sprite_list.add(new_section)

    def change_dir(self, new_dir):
        self.next_dir = new_dir

    def get_length(self):
        return self.length

    def update(self):
        '''
        This function runs every frame. It updates the position, etc.
        '''
        limit = CELL_DIM / self.speed # synchronize turns, tail adds, etc. with the cell edges

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
            self.rect.x += self.speed
        elif self.cur_dir == 2:
            self.rect.y += self.speed
        elif self.cur_dir == 3:
            self.rect.x -= self.speed
        elif self.cur_dir == 4:
            self.rect.y -= self.speed

        # Update each of the tail sections
        for t in self.tail:
            t.update()


class TailPiece(pygame.sprite.Sprite):
    # 0 - no movement
    # 1 - right
    # 2 - down
    # 3 - left
    # 4 - up
    def __init__(self, index, x, y, moves, speed):
        super(TailPiece, self).__init__()
        self.image = pygame.image.load("images/square.png").convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movement_list = moves
        self.index = index
        self.cur_dir = 0 # See class comment for list of directions and integer mappings
        self.speed = speed

    def update(self):
        if self.movement_list[self.index] == 1:
            self.rect.x += self.speed
        elif self.movement_list[self.index] == 2:
            self.rect.y += self.speed
        elif self.movement_list[self.index] == 3:
            self.rect.x -= self.speed
        elif self.movement_list[self.index] == 4:
            self.rect.y -= self.speed


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




########################### Ideas/TODO #######################################
'''
1) High Score
2) Menus
3) Fruit not spawning on tail
4) Wall collisions
5) Change speed mid game?
6) Faster speeds?
7) walls or no fruit on top row?
8) Different levels (wall layouts)
      Could keep an array of legal fruit locations, then take a random index
'''
