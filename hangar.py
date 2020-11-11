
import config
import events
import save

from pygame.locals import *
import pygame
import random
import time
import os



def load_image(filename, transparent=True):
	
	global Error
	
	try: image = pygame.image.load(filename)
	except pygame.error as message: raise SystemError
	
	image = image.convert()
	
	if transparent:
		
		color = image.get_at((0,0))
		image.set_colorkey(color, RLEACCEL)
		
	return image



class Hangar:
	
	def __init__(self, screen, music, clock):
		
		self.h_config = config.HangarConfig()
		self.h_events = events.EventHandler()
		
		self.screen = screen
		self.music = music
		self.clock = clock
		
		self.bg_img = load_image('img/background/bg.png')
	
	def menu(self):
		
		while not self.h_config.exit:
			
			self.h_events.hangar_event_handler(self.h_config)
			self.draw_background()
			
			
			
			pygame.display.update()
			self.h_config.speed_delta = self.clock.tick(self.h_config.max_frames) / 10
	
	def draw_background(self):
		
		self.screen.blit(self.bg_img, (0,0))
		
		
