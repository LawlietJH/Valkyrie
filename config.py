
import pygame
import time

class Config:
	
	def __init__(self):
		
		self.quit = False
		self.pause = False
		self.dir_l = False
		self.dir_r = False
		self.dir_u = False
		self.dir_d = False
		
		self.mouse_pos = None
		self.mouse_pos_x = None
		self.mouse_pos_y = None
		self.bullets = []
		self.mbd = {				# Mouse Button Down
			'pos':None,
			'button':None,
			'active':None
		}
		
		self.speed_delta = 0
		self.time_init = time.perf_counter()
		self.max_frames = 60
		self.frames = 0
		self.texture_size = 64
		self.box_size = 50
		
		self.FONT = {
			'Inc-R 18': pygame.font.Font("font/Inconsolata-Regular.ttf", 18),
			'Inc-R 16': pygame.font.Font("font/Inconsolata-Regular.ttf", 16),
			'Inc-R 14': pygame.font.Font("font/Inconsolata-Regular.ttf", 14),
			'Inc-R 13': pygame.font.Font("font/Inconsolata-Regular.ttf", 13),
			'Inc-R 12': pygame.font.Font("font/Inconsolata-Regular.ttf", 12),
			'Inc-R 10': pygame.font.Font("font/Inconsolata-Regular.ttf", 10),
			'Retro 64': pygame.font.Font("font/Retro Gaming.ttf", 64),
			'Retro 32': pygame.font.Font("font/Retro Gaming.ttf", 32),
			'Retro 24': pygame.font.Font("font/Retro Gaming.ttf", 24),
			'Retro 18': pygame.font.Font("font/Retro Gaming.ttf", 18),
			'Retro 16': pygame.font.Font("font/Retro Gaming.ttf", 16),
			'Retro 14': pygame.font.Font("font/Retro Gaming.ttf", 14),
			'Retro 12': pygame.font.Font("font/Retro Gaming.ttf", 12),
			'Wendy 18': pygame.font.Font("font/Wendy.ttf", 18),
			'Wendy 16': pygame.font.Font("font/Wendy.ttf", 16),
			'Wendy 14': pygame.font.Font("font/Wendy.ttf", 14),
			'Wendy 13': pygame.font.Font("font/Wendy.ttf", 13),
			'Wendy 12': pygame.font.Font("font/Wendy.ttf", 12),
			'Wendy 10': pygame.font.Font("font/Wendy.ttf", 10)
		}	# Diccionario de Fuentes.
		
		self.COLOR = {
			'Blanco':   (255, 255, 255), 'Negro':       (  0,   0,   0),
			'Gris':     (189, 189, 189), 'Gris Claro':  (216, 216, 216),
			'Gris O':   (130, 130, 130), 'Plateado':    (227, 228, 229),
			'Oxido':    (205, 127,  50), 'Metal':       ( 83,  86,  84),
			'Verde':    (  4, 180,   4), 'Verde Claro': (  0, 255,   0),
			'VS':       ( 24,  25,  30), 'VN':          (  0,  50,  30),
			'VC':       (  0,  75,  30), 'VF':          (  0, 100,  30),
			'Azul':     ( 20,  80, 240), 'Azul Claro':  ( 40, 210, 250),
			'Amarillo': (255, 255,   0), 'Naranja':     (255, 120,   0),
			'Rojo':     (255,   0,   0), 'Rojo Claro':  (255,  50,  50),
			'Morado':   ( 76,  11,  95), 'Purpura':     ( 56,  11,  97)
		}	# Diccionario de Colores.
		
		self.weapons = {
			1: 'Gun',
			2: 'Plasma',
			3: 'Flame'
		}
		self.unlocked_weapons = [ 'Gun', None, None ]
		self.selected_weapon = 1
		self.speed_up = True
		self.level_up = False
		self.level_up_hp = False
		self.level_up_sp = False
		self.shop_2 = False
		self.shop_3 = False



class Info:
	
	weapons = {
		1: 'Gun',
		2: 'Plasma',
		3: 'Flame'
	}
	
	def drops_config(self, money, ammo):
		
		drops = {
			'money':       { 'probability': 95, 'drop': {'money': money}      },
			'ammo':        { 'probability': 10, 'drop': {'ammo': ammo}        },
			'dmg res':     { 'probability':  1, 'drop': {'dmg res': .01}      },
			'tps':         { 'probability':  1, 'drop': {'tps': .01}          },
			'range':       { 'probability':  1, 'drop': {'range': .01}        },
			'speed':       { 'probability':  1, 'drop': {'speed': .05}         },
			'accuracy':    { 'probability':  1, 'drop': {'accuracy':  1}      },
			'piercing':    { 'probability':  1, 'drop': {'piercing':  1}      },
			'speed mech':  { 'probability':  1, 'drop': {'speed mech': .02}   },
			'hp abs':      { 'probability':  1, 'drop': {'hp abs': .01}       },
			'hp recovery': { 'probability':  1, 'drop': {'hp recovery': .025} },
			'sp recovery': { 'probability':  1, 'drop': {'sp recovery': .02}  }
		}
		
		return drops
	
	def enemies_qty_max(self, level):
		if    level <  10: qty_max = 2
		elif  level <  20: qty_max = 3
		elif  level <  30: qty_max = 4
		elif  level <  50: qty_max = 5
		elif  level < 100: qty_max = 6
		else: qty_max = random.randint(7,10)
		return qty_max


info = Info()

