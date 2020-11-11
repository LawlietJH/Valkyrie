
import config
import events
import data

import pygame

class Init:
	
	def __init__(self):
		
		# Config:
		self.config = config.InfinityConfig()
		self.scale = self.config.scale
		self.RESOLUTION = self.config.RESOLUTION
		self.screen = pygame.display.set_mode(self.RESOLUTION, pygame.DOUBLEBUF)#, pygame.FULLSCREEN)#, pygame.NOFRAME)
		
		# Pygame:
		self.music = pygame.mixer.music
		self.clock = pygame.time.Clock()
		
		# Objects:
		self.events = events.EventHandler()
		self.data = data.Data()
