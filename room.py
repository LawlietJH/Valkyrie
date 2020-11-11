
import config
import data

import random

class Room:
	
	def __init__(self, room, resolution, level, ro=None, rod=None, limit=500):
		
		self.room = room
		self.enemies = []
		self.colors = []
		self.objs = []
		self.walls = []
		self.bullets = []
		self.boxes = []
		self.col_objs = []
		
		self.room_D = (self.room[0], self.room[1]+1) if self.room[1] <= limit-1 else None
		self.room_R = (self.room[0]+1, self.room[1]) if self.room[0] <= limit-1 else None
		self.room_U = (self.room[0], self.room[1]-1) if self.room[1] > 0 else None
		self.room_L = (self.room[0]-1, self.room[1]) if self.room[0] > 0 else None
		
		self.wall_D = True if self.room[1] == limit-1 else False
		self.wall_R = True if self.room[0] == limit-1 else False
		self.wall_U = True if self.room[1] == 0     else False
		self.wall_L = True if self.room[0] == 0     else False
		
		self.walls_DRUL = [self.wall_L,self.wall_R,self.wall_U,self.wall_D]
		
		self.ro  = ro					# Room Orogin (Number)
		self.rod = rod					# Room Origin Direction: 'L', 'R', 'U', 'D'
		self.level = level				# Room level
		self.complete = False
		self.resolution = resolution
		
		qty_enemies = random.randint(2, config.info.enemies_qty_max(self.level))
		self.enemies_pos = [ random.choice(self.choice()) for _ in range(qty_enemies) ]
		self.qty_boxes = random.randint(1,3)
		
		self.opens = set()
		self.doors = ''
		
		self.set_enemies()
	
	def set_enemies(self):
		
		gun_init_stats = {
			'name':  config.info.weapons[1],
			'lvl':    0,
			'str_':   10 * ( 1 + int( self.level/5 ) ),					# Cambia cada 5 niveles.
			# ~ 'str_':   2 * self.level,									# Cambia cada nivel.
			'ammo':   None,
			'cpw':    None,
			'cpl':    None,
			'cpa':    None,
			'istr':   None,
			'icost':  None,
			'dmg_hp': 0,
			'tps':    2 - self.level/100 if self.level/100 <= 1.5 else 1.5,
			'dofs':   2 + self.level/100,
			'speed':  4,
			'acc':    6 - int(self.level/15) if int(self.level/15) <= 6 else 6,
			'ps':     10,
			'hp_abs': None
		}
		
		plasma_init_stats = {
			'name':  config.info.weapons[2],
			'lvl':    0,
			'str_':   48 * ( 1 + int( self.level/6 ) ),					# Cambia cada 10 niveles.
			# ~ 'str_':   8 * self.level,									# Cambia cada nivel.
			'ammo':   None,
			'cpw':    None,
			'cpl':    None,
			'cpa':    None,
			'istr':   None,
			'icost':  None,
			'dmg_hp': .1,
			'tps':    1 - self.level/100 if self.level/100 <= .5 else .5,
			'dofs':   2 + self.level/100,
			'speed':  2,
			'acc':    10 - int(self.level/10) if int(self.level/10) <= 10 else 10,
			'ps':     20,
			'hp_abs': None
		}
		
		flame_init_stats = {
			'name':  config.info.weapons[3],
			'lvl':    0,
			'str_':   112 * ( 1 + int( self.level/7 ) ),				# Cambia cada 10 niveles.
			# ~ 'str_':   16 * self.level,									# Cambia cada nivel.
			'ammo':   None,
			'cpw':    None,
			'cpl':    None,
			'cpa':    None,
			'istr':   None,
			'icost':  None,
			'dmg_hp': .2,
			'tps':    2 - self.level/100 if self.level/100 <= 1.5 else 1.5,
			'dofs':   1 + self.level/60,
			'speed':  5,
			'acc':    3 - int(self.level/30) if int(self.level/30) <= 3 else 3,
			'ps':     30,
			'hp_abs': None
		}
		
		self.enemy_01_init_stats = {
			'path':    'Mech 01',
			'name':    'Enemy 01',
			'hp':      125 * ( 1 + int( self.level/5 ) ),
			'sp':      100 * ( 1 + int( self.level/2 ) ),
			'room_level': self.level,
			'weapon':  config.info.weapons[1],
			'weapons': {config.info.weapons[1]: data.Weapon(data.Bullet, **gun_init_stats)}
		}
		
		self.enemy_02_init_stats = {
			'path':    'Mech 02',
			'name':    'Enemy 02',
			'hp':      250 * ( 1 + int( self.level/5 ) ),
			'sp':      200 * ( 1 + int( self.level/2 ) ),
			'room_level': self.level,
			'weapon':  config.info.weapons[2],
			'weapons': {config.info.weapons[2]: data.Weapon(data.Bullet, **plasma_init_stats)}
		}
		
		self.enemy_03_init_stats = {
			'path':    'Mech 03',
			'name':    'Enemy 03',
			'hp':      500 * ( 1 + int( self.level/5 ) ),
			'sp':      400 * ( 1 + int( self.level/2 ) ),
			'room_level': self.level,
			'weapon':  config.info.weapons[3],
			'weapons': {config.info.weapons[3]: data.Weapon(data.Bullet, **flame_init_stats)}
		}
	
	def choice(self):
		choice = []
		if self.rod == 'R':
			choice = [
				(random.randint(100, self.resolution[0]-100), random.randint(100, self.resolution[1]/2-100)),
				(random.randint(300, self.resolution[0]-100), random.randint(self.resolution[1]/2-100, self.resolution[1]/2+100)),
				(random.randint(100, self.resolution[0]-100), random.randint(self.resolution[1]/2+100, self.resolution[1]-100))
			]
		
		elif self.rod == 'L':
			choice = [
				(random.randint(100, self.resolution[0]-100), random.randint(100, self.resolution[1]/2-100)),
				(random.randint(100, self.resolution[0]-300), random.randint(self.resolution[1]/2-100, self.resolution[1]/2+100)),
				(random.randint(100, self.resolution[0]-100), random.randint(self.resolution[1]/2+100, self.resolution[1]-100))
			]
		
		elif self.rod == 'D':
			choice = [
				(random.randint(100, self.resolution[0]/2-100),                      random.randint(100, self.resolution[1]-100)),
				(random.randint(self.resolution[0]/2-100, self.resolution[0]/2+100), random.randint(300, self.resolution[1]-100)),
				(random.randint(self.resolution[0]/2+100, self.resolution[0]-100),   random.randint(100, self.resolution[1]-100))
			]
		
		elif self.rod == 'U':
			choice = [
				(random.randint(100, self.resolution[0]/2-100),                      random.randint(100, self.resolution[1]-100)),
				(random.randint(self.resolution[0]/2-100, self.resolution[0]/2+100), random.randint(100, self.resolution[1]-300)),
				(random.randint(self.resolution[0]/2+100, self.resolution[0]-100),   random.randint(100, self.resolution[1]-100))
			]
		else:
			choice = [
				(random.randint(600, self.resolution[0]-100), random.randint(100, self.resolution[1]-100)),
				(random.randint(100, self.resolution[0]-100), random.randint(600, self.resolution[1]-100))
			]
		return choice
