#!/usr/bin/python
import pygame
import random

#define some colors
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super(Block, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 1
        if(self.rect.y > screen_height):
            self.rect.y = random.randrange(-100, -10)
            self.rect.x = random.randrange(screen_width)

pygame.init()
# screen_width = 700
# screen_height = 400
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode([screen_width, screen_height])

block_list = pygame.sprite.Group()
all_list = pygame.sprite.Group()

# Create the blocks
for i in range(50):
    block = Block(black, 20, 25)
    block.rect.x = random.randrange(screen_width)
    block.rect.y = random.randrange(screen_height)

    block_list.add(block)
    all_list.add(block)

# Create the player
player = Block(red, 20, 15)
all_list.add(player)

done = False
clock = pygame.time.Clock()
score = 0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(white)
    pos = pygame.mouse.get_pos()
    player.rect.x = pos[0]
    player.rect.y = pos[1]
    block_list.update()

    # This call automatically removes the blocks from the list
    blocks_hit_list = pygame.sprite.spritecollide(player, block_list, True)
    for block in blocks_hit_list:
        score+=1
        print(score)

    all_list.draw(screen)
    clock.tick(60)
    pygame.display.flip()

pygame.quit()





