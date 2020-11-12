
from roundrects import round_rect
import config
import events
import save

from pygame.locals import *
import pygame
import random
import save
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
		
		self.bg_img = load_image('img/background/bg2.png')
		
		self.default_player = {
			"hp": 200,
			"sp": 0,
			"hp_level": 0,
			"sp_level": 0,
			"money": 0,
			"weapons": {
				"Gun": {
					"lvl": 0,
					"str_": 10,
					"ammo": 5000,
					"dmg_hp": 0.2,
					"tps": 0.5,
					"dofs": 2,
					"speed": 5,
					"acc": 5,
					"ps": 10,
					"hp_abs": 0
				}
			},
			"speed": 2,
			"dmg_res": 0.5,
			"hp_time_recovery": 0.3,
			"sp_time_recovery": 0.15
		}
	
	def menu(self):
		
		while not self.h_config.exit:
			
			self.h_events.hangar_event_handler(self.h_config)
			
			self.draw_background()
			self.draw_boxes()
			
			pygame.display.update()
			self.h_config.speed_delta = self.clock.tick(self.h_config.max_frames) / 10
	
	def draw_background(self):
		
		self.screen.blit(self.bg_img, (-80,0))
	
	def draw_boxes(self):
		
		pinfo = save.load_data()
		if not pinfo: pinfo = self.default_player
		
		font_size = 14
		font = 'Inc-R '+str(font_size)
		
		colors = ['Blanco', 'VF']
		
		tx = 350
		ty = 80
		
		x = 10
		y = self.h_config.RESOLUTION[1] - ty - 10
		
		rect = [ x, y, tx, ty ]
		
		# ~ self.opq_rect(rect, self.h_config.COLOR['VS'], 200)
		# ~ pygame.draw.rect(self.screen, self.h_config.COLOR['VC'], rect, 2)
		
		# HP:
		round_rect(self.screen, rect,self.h_config.COLOR['Negro'], 10, 1, (*self.h_config.COLOR['Negro'], 200))
		
		rect_text = [ rect[0]+10, rect[1]+10 ]
		text = 'Acorazamiento (HP Nivel '+str(pinfo['hp_level'])+')'
		self.draw_text_with_depth(text, rect_text, font, colors[0], colors[1])
		
		rect_text = [ rect[0]+10, rect[1]+40 ]
		text = 'Protección: '+str(pinfo['hp'])
		self.draw_text_with_depth(text, rect_text, font, colors[0], colors[1])
		
		rect_text = [ rect[0]+10, rect[1]+55 ]
		text = 'Tras la mejora: '+str(pinfo['hp']+40)
		self.draw_text_with_depth(text, rect_text, font, colors[0], colors[1])
		rect_text = [ rect[0]+187, rect[1]+55 ]
		text = 'Aumentar la protección'
		self.draw_text_with_depth(text, rect_text, font, 'Verde Claro', 'Negro')
		
		# Weapons:
		x = self.h_config.RESOLUTION[0] - tx - 10
		y = self.h_config.RESOLUTION[1] - ty - 10
		
		objects_info = [
			{'name':'Gun',    'lvl':'0', 'str':'10', 'charger':'1000', 'ammo':'10000'},
			{'name':'Plasma', 'lvl':'0', 'str':'20', 'charger':'20',  'ammo':'200'},
			{'name':'Flame',  'lvl':'0', 'str':'30', 'charger':'10',  'ammo':'100'}
		]
		
		for i in range(len(objects_info)):
			
			rect = [ x, y, tx, ty ]
			round_rect(self.screen, rect,self.h_config.COLOR['Negro'], 10, 1, (*self.h_config.COLOR['Negro'], 200))
			
			rect_text = [ rect[0]+10, rect[1]+10 ]
			text = objects_info[i]['name']+' (Nivel '+objects_info[i]['lvl']+') - tecla ['+str(i+1)+']'
			self.draw_text_with_depth(text, rect_text, font, colors[0], colors[1])
			
			rect_text = [ rect[0]+10, rect[1]+25 ]
			text = 'Fuerza: '+objects_info[i]['str']
			self.draw_text_with_depth(text, rect_text, font, colors[0], colors[1])
			rect_text = [ rect[0]+216, rect[1]+25 ]
			text = 'Aumentar la fuerza'
			self.draw_text_with_depth(text, rect_text, font, 'Verde Claro', 'Negro')
			
			rect_text = [ rect[0]+10, rect[1]+40 ]
			text = 'Cargador: '+objects_info[i]['charger']
			self.draw_text_with_depth(text, rect_text, font, colors[0], colors[1])
			rect_text = [ rect[0]+210, rect[1]+40 ]
			text = 'Ampliar el cargador'
			self.draw_text_with_depth(text, rect_text, font, 'Verde Claro', 'Negro')
			
			rect_text = [ rect[0]+10, rect[1]+55 ]
			self.draw_text_with_depth('Municiones: '+objects_info[i]['ammo'], rect_text, font, colors[0], colors[1])
			rect_text = [ rect[0]+230, rect[1]+55 ]
			text = 'Comprar munición'
			self.draw_text_with_depth(text, rect_text, font, 'Verde Claro', 'Negro')
			
			y -= ty + 10
		
		font_size = 16
		font = 'Inc-R '+str(font_size)
		
		rect = [ x, y, tx, ty ]
		rect_text = [ rect[0]+10, rect[1]+70 ]
		self.draw_text_with_depth('Tus armas:', rect_text, font, 'Rojo', 'Naranja')
		
	
	def draw_text_with_depth(self, text, rect_text, font, color_front, color_back):
		self.draw_text(text, rect_text, font, color_back)
		self.draw_text(text, [rect_text[0]-1, rect_text[1]-1], font, color_front)
	
	def draw_text(self, text, pos, font, color):	# Dibuja Texto En Pantalla.
		font = self.h_config.FONT[font]
		color = self.h_config.COLOR[color]
		text = font.render(text, 1, color)			# Se Pasa El Texto Con La Fuente Especificada.
		self.screen.blit(text, pos)					# Se Dibuja En Pantalla El Texto en la Posición Indicada.
	
	# Rectángulo Opaco, sirve para crear rectangulos con transparencia.
	def opq_rect(self, surface, color=(0,0,0), alpha=128):
		img = pygame.Surface(surface[2:])
		img.set_alpha(alpha)
		img.fill(color)
		self.screen.blit(img, surface[:2])


if __name__ == '__main__':
	
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	
	RESOLUTION = (1280,  768)
	screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)#, pygame.FULLSCREEN)#, pygame.NOFRAME)
	music = pygame.mixer.music
	clock = pygame.time.Clock()
	
	hangar = Hangar(screen, music, clock)
	hangar.menu()
	
	pygame.quit()
