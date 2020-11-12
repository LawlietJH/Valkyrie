
# By: LawlietJH
# Python 3

import infinity
import hangar
import init

import pygame
import gc
import os


__project__ = 'Valkyrie'
__author__ = 'LawlietJH'
__version__ = '1.0.1'

__license__ = 'MIT'
__status__ = 'Development'
__framework__ = 'pygame'
__date__ = '2020/11/06'
__description__ = 'Juego 2D con pygame inspirado en los juegos clasicos de destruir naves.'


class Game(init.Init):
	
	def __init__(self):
		
		init.Init.__init__(self)
		
		self.infinity = infinity.Infinity()
		self.hangar = hangar.Hangar(self.screen, self.music, self.clock)
		
		# ~ pid = os.getpid()
		# ~ py = psutil.Process(pid)
		# ~ memoryUse = py.memory_info()[0]/(2**20)  # memory use in MB
		# ~ print('memory use:', memoryUse)
		
		# ~ print(psutil.cpu_percent())
		# ~ print(psutil.virtual_memory())
		# ~ print(dict(psutil.virtual_memory()._asdict()))
	
	def main(self):
		
		# ~ self.hangar.menu()
		
		# ~ if self.hangar.h_config.start_infinity: self.infinity.gamemode_infinity()
		self.infinity.gamemode_infinity()


if __name__ == '__main__':
	
	gc.enable()
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	game = Game()
	game.main()
	pygame.quit()
