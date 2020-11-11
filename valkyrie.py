

import infinity
import hangar
import init

import pygame
import os


class Game(init.Init):
	
	def __init__(self):
		
		init.Init.__init__(self)
		self.infinity = infinity.Infinity()
		self.hangar = hangar.Hangar(self.screen, self.music, self.clock)
	
	def main(self):
		
		self.hangar.menu()
		
		# ~ if self.hangar.h_config.start_infinity: self.infinity.gamemode_infinity()
		self.infinity.gamemode_infinity()


if __name__ == '__main__':
	
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	game = Game()
	game.main()
	pygame.quit()
