#!/usr/bin/python
import pygame
import random

class RedBlock(pygame.sprite.Sprite):
	"""This class represents a sprite to draw on the screen"""
	def __init__(self):
		super(RedBlock, self).__init__()
		self.image = pygame.Surface((132, 132))
		self.image.fill((255, 0, 0))
		self.rect = self.image.get_rect()

class RoadBlock(pygame.sprite.Sprite):
	"""This class represents a road sprite"""
	def __init__(self):
		super(RoadBlock, self).__init__()
		self.image = pygame.image.load("images/test.png").convert()
		self.image.set_colorkey((0, 0, 0))
		self.rect = self.image.get_rect()
		
class RoadBlock2(pygame.sprite.Sprite):
	"""This class represents a second road sprite"""
	def __init__(self):
		super(RoadBlock2, self).__init__()
		self.image = pygame.image.load("images/test2.png").convert()
		self.image.set_colorkey((0, 0, 0))
		self.rect = self.image.get_rect()

pygame.init()

screen_width = 700
screen_height = 400
screen = pygame.display.set_mode([screen_width, screen_height])

spriteList = pygame.sprite.Group() # I guess you need to do this to draw?

block = RedBlock()
block.rect.x = 50
block.rect.y = 100
spriteList.add(block)

block2 = RoadBlock()
block2.rect.x = 200
block2.rect.y = 300


block3 = RoadBlock2()
block3.rect.x = 133
block3.rect.y = 266

spriteList.add(block3)
spriteList.add(block2)

clock = pygame.time.Clock()
done = False

while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True

	screen.fill((255, 255, 255))
	spriteList.draw(screen)

	pygame.display.flip()

	clock.tick(60)

pygame.quit()
