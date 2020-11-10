
from pygame.locals import *
import pygame
import config
import random
import time
import math



battlemech_paths = {
	'Mech 01': 'img/battlemech/Mech 01.png',
	'Mech 02': 'img/battlemech/Mech 02.png',
	'Mech 03': 'img/battlemech/Mech 03.png'
}

enemy_paths = {
	'Mech 01': 'img/battlemech/Mech 01.png',
	'Mech 02': 'img/battlemech/Mech 02.png',
	'Mech 03': 'img/battlemech/Mech 03.png'
}

bullet_paths = {
	'Gun':    'img/weapons/Laser Red Gun.png',
	'Plasma': 'img/weapons/Laser Green Plasma.png',
	'Flame':  'img/weapons/Laser Purple Flame.png'
}

weapon_icon_paths = {
	'Gun':    'img/weapons/Laser Red Gun - Icon.png',
	'Plasma': 'img/weapons/Laser Green Plasma - Icon.png',
	'Flame':  'img/weapons/Laser Purple Flame - Icon.png'
}

wall_paths = {
	'floor 01': 'img/textures/floor 01.png',
	'floor 02': 'img/textures/floor 02.png',
	'wall 01':  'img/textures/wall 01.png',
	'door 01':  'img/textures/door 01.png'
}

box_paths = {
	'box 01': 'img/boxes/box 01.png'
}

class Player(pygame.sprite.Sprite):
	
	def __init__(self, path, name, hp, sp, cpl_hp, cpl_sp, icpl_hp, icpl_sp, speed, money, weapons):
		
		super().__init__()
		
		self.path = path
		self.image_orig = load_image(battlemech_paths[self.path])
		self.image = self.image_orig
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
		self.name = name				# Player name
		
		self.hp_init = hp
		self.hp = hp					# Health points
		self.chp = hp					# Current health points
		self.hp_level = 0				# Health points level
		self.hppl = 80					# Health points per level
		self.cpl_hp = cpl_hp			# Cost per level HP
		self.icpl_hp = icpl_hp			# Increase Cost per level HP
		
		self.sp_init = sp
		self.sp = sp					# Shield points
		self.csp = sp					# Current shield points
		self.sp_level = 0				# Shield points level
		self.sppl = 100					# Shield points per level
		self.cpl_sp = cpl_sp			# Cost per level SP
		self.icpl_sp = icpl_sp			# Increase Cost per level SP
		
		self.money = money				# Player money
		self.weapons = weapons			# Player weapons
		self.actual_weapon = 'Gun'		# Actual weapon
		self.rect = self.image.get_rect(center=(150, 150))
		self.x = self.rect[0]			# Position X
		self.y = self.rect[1]			# Position Y
		
		self.speed = speed				# Player Speed
		self.dmg_hp = .2				# Damage to health points
		self.resistant_dmg_hp = .2		# Resistance to damage
		self.killed_time = 0
		self.last_hit_time = 0
		self.hp_time_recovery = .3
		self.sp_time_recovery = .15
		self.hp_recovery_time = time.perf_counter()
		self.sp_recovery_time = time.perf_counter()
		self.last_mouse_pos = None
		
		self.angle = 0
		self.colision = False
		self.dirs = ''
		self.scale = 1
	
	def update_speed(self, scale):
		self.scale = scale
		self.speed = self.speed*self.scale
	
	def update_pos(self, x, y):
		self.x = int(x*self.scale)
		self.y = int(y*self.scale)
	
	def load_player(self, data, all_weapons):
		
		for lvl in range(data['hp_level']): self.level_up_hp(False)
		for lvl in range(data['sp_level']): self.level_up_sp(False)
		
		self.money  = data['money']
		self.speed  = data['speed']
		self.dmg_hp = data['dmg_hp']
		self.resistant_dmg_hp = data['resistant_dmg_hp']
		self.hp_time_recovery = data['hp_time_recovery']
		self.sp_time_recovery = data['sp_time_recovery']
		
		for name, weapon in data['weapons'].items():
			
			if not name in self.weapons:
				if   name == 'Gun':    self.update_weapons(all_weapons[1])
				elif name == 'Plasma': self.update_weapons(all_weapons[2])
				elif name == 'Flame':  self.update_weapons(all_weapons[3])
			
			self.weapons[name].ammo  = data['weapons'][name]['ammo']
			self.weapons[name].tps   = data['weapons'][name]['tps']
			self.weapons[name].dofs  = data['weapons'][name]['dofs']
			self.weapons[name].speed = data['weapons'][name]['speed']
			self.weapons[name].accuracy = data['weapons'][name]['acc']
			self.weapons[name].ps    = data['weapons'][name]['ps']
			
			for lvl in range(data['weapons'][name]['lvl']): self.weapons[name].levelUp()
	
	def level_up_hp(self, money=True):
		
		if money: self.money -= self.cpl_hp
		
		self.cpl_hp += self.icpl_hp
		self.hp_level += 1
		aument = (self.hppl*self.hp_level)
		self.hp = self.hp_init + aument
		self.chp += self.hppl
	
	def level_up_sp(self, money=True):
		
		if money: self.money -= self.cpl_sp
		
		self.cpl_sp += self.icpl_sp
		self.sp_level += 1
		aument = (self.sppl*self.sp_level)
		self.sp = self.sp_init + aument
		self.csp += self.sppl
	
	@property
	def gun(self): return self.weapons[self.actual_weapon]
	
	def rotate(self, mouse_pos):
		run, rise = (mouse_pos[0]-self.x, mouse_pos[1]-self.y)
		self.angle = math.degrees(math.atan2(rise, run))
		self.image = pygame.transform.rotate(self.image_orig, -self.angle)
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
	
	def move(self, config, objs, enemies):
		
		# ~ print(self.speed, config.speed_delta, self.speed * config.speed_delta)
		
		self.mask = pygame.mask.from_surface(self.image)
		
		if not enemies and config.speed_up:
			if config.dir_l: self.x -= self.speed * config.speed_delta * 2
			if config.dir_r: self.x += self.speed * config.speed_delta * 2
			if config.dir_u: self.y -= self.speed * config.speed_delta * 2
			if config.dir_d: self.y += self.speed * config.speed_delta * 2
		else:
			if config.dir_l: self.x -= self.speed * config.speed_delta
			if config.dir_r: self.x += self.speed * config.speed_delta
			if config.dir_u: self.y -= self.speed * config.speed_delta
			if config.dir_d: self.y += self.speed * config.speed_delta
		
		for w in objs:
			
			if type(w).__name__ == 'Enemy' and w.chp == 0: continue
			if type(w).__name__ == 'Box'   and w.hp == 0:  continue
			
			m = pygame.mask.from_surface(w.image)
			offset = (int(self.x) - w.x, int(self.y) - w.y)
			result = m.overlap(self.mask, offset)
			
			if result:
				
				angle = math.degrees(math.atan2(offset[0], offset[1]))+90
				
				if not enemies and config.speed_up:
					if   135 < angle <= 225: self.x += self.speed*2 * config.speed_delta * 2
					if    45 < angle <= 135: self.y += self.speed*2 * config.speed_delta * 2
					if   -45 < angle <=  45: self.x -= self.speed*2 * config.speed_delta * 2
					if  angle <= -45 or angle > 225: self.y -= self.speed*2 * config.speed_delta * 2
				else:
					if   135 < angle <= 225: self.x += self.speed*2 * config.speed_delta
					if    45 < angle <= 135: self.y += self.speed*2 * config.speed_delta
					if   -45 < angle <=  45: self.x -= self.speed*2 * config.speed_delta
					if  angle <= -45 or angle > 225: self.y -= self.speed*2 * config.speed_delta
	
	def update(self, screen, config, col_objs, enemies):
		self.rotate(config.mouse_pos)
		self.move(config, col_objs, enemies)
		self.resize()
		self.select_weapon(config)
		self.rect = self.image.get_rect(center=(self.x, self.y))
		screen.blit(self.image, self.rect)
		
		if time.perf_counter() - self.last_hit_time > 10:
			if time.perf_counter() - self.hp_recovery_time > self.hp_time_recovery:
				if self.chp < self.hp:
					self.chp += 1
					self.hp_recovery_time = time.perf_counter()
			if time.perf_counter() - self.sp_recovery_time > self.sp_time_recovery:
				if self.csp < self.sp:
					self.csp += 1
					self.sp_recovery_time = time.perf_counter()
		
		if not self.chp == 0:
			mask = pygame.mask.from_surface(self.image)
			for enemy in enemies:
				for o in enemy.bullets:
					m = pygame.mask.from_surface(o.image)
					offset = (int(self.x) - int(o.x+(self.tx/2)), int(self.y) - int(o.y+(self.ty/2)))
					result = m.overlap(mask, offset)
					if result:
						str_ = o.gun.str
						if not self.chp == 0:
							self.damage_effect(str_, self.resistant_dmg_hp)
						o.hp -= 1000
						self.last_hit_time = time.perf_counter()
						break
	
	def damage_effect(self, str_, dmg_hp):
		dmg_sp = 1-dmg_hp
		if self.csp > 0:
			if self.csp - str_*dmg_sp >= 0:
				self.csp -= str_*dmg_sp
			else:
				temp = ((str_*dmg_sp)-self.csp)
				self.chp -= temp
				self.csp = 0
			if self.chp - str_*dmg_hp >= 0:
				self.chp -= str_*dmg_hp
			else:
				self.chp = 0
				self.killed_time = time.perf_counter()
		else:
			if self.chp - str_ >= 0:
				self.chp -= str_
			else:
				self.chp = 0
		self.chp = int(self.chp)
		self.csp = int(self.csp)
		if self.chp == 0:
			self.killed_time = time.perf_counter()
	
	@property
	def size(self): return '{}x{}'.format(self.tx, self.ty)
	
	def resize(self):
		self.tx = int(self.txo * self.scale)
		self.ty = int(self.tyo * self.scale)
		self.image = pygame.transform.scale(self.image, (self.tx, self.ty))
	
	def select_weapon(self, config): self.actual_weapon = config.weapons[config.selected_weapon]
	
	def update_weapons(self, weapons): self.weapons.update(weapons)

class Enemy(pygame.sprite.Sprite):
	
	def __init__(self, posx, posy, path, name, hp, sp, room_level, weapon, weapons):
		
		super().__init__()
		
		self.path = path
		self.image_orig = load_image(enemy_paths[self.path])
		self.image = self.image_orig
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
		self.name = name			# Enemy name
		
		self.rect = self.image.get_rect(center=(posx, posy))
		self.x = self.rect[0]		# Position X
		self.y = self.rect[1]		# Position Y
		
		self.hp = hp				# Health points
		self.chp = hp				# Current health points
		
		self.sp = sp				# Shield points
		self.csp = sp				# Current shield points
		
		self.rp = 50				# Resistance Points
		
		# ~ self.money = random.randint(1,20)*10	# Enemy money
		self.weapons = weapons		# Enemy weapons
		self.actual_weapon = weapon	# Actual weapon
		
		self.room_level = room_level
		self.speed = 2				# Enemy Speed
		self.angle = 0
		self.colision = False
		self.dirs = ''
		self.scale = 1
		self.killed_time = 0
		self.actual_time = time.perf_counter()
		
		self.bullets = []
		self.drop = {}
		
		self.set_drops()
	
	def set_drops(self):
		
		if self.room_level > 20:
			money_min = self.room_level-20
			money_max = self.room_level
		else:
			money_min = 1
			money_max = 20
		
		money_max += 10 if self.name == 'Enemy 01' and random.random() <= .5 else 0
		money_max += 20 if self.name == 'Enemy 02' and random.random() <= .5 else 0
		money_max += 30 if self.name == 'Enemy 03' and random.random() <= .5 else 0
		money_val = random.randint(money_min, money_max)*10
		
		ammo = {'Gun':100, 'Plasma':50, 'Flame':25}
		
		drops = config.info.drops_config(money_val, ammo[self.actual_weapon])
		
		if random.random() < drops['money']['probability']      /100: self.drop.update(drops['money']['drop'])
		if random.random() < drops['ammo']['probability']       /100: self.drop.update(drops['ammo']['drop'])
		if random.random() < drops['tps']['probability']        /100: self.drop.update(drops['tps']['drop'])
		if random.random() < drops['range']['probability']      /100: self.drop.update(drops['range']['drop'])
		if random.random() < drops['speed']['probability']      /100: self.drop.update(drops['speed']['drop'])
		if random.random() < drops['accuracy']['probability']   /100: self.drop.update(drops['accuracy']['drop'])
		if random.random() < drops['piercing']['probability']   /100: self.drop.update(drops['piercing']['drop'])
		if random.random() < drops['speed mech']['probability'] /100: self.drop.update(drops['speed mech']['drop'])
		if random.random() < drops['hp recovery']['probability']/100: self.drop.update(drops['hp recovery']['drop'])
		if random.random() < drops['sp recovery']['probability']/100: self.drop.update(drops['sp recovery']['drop'])
	
	@property
	def gun(self): return self.weapons[self.actual_weapon]
	
	def update_speed(self, scale):
		self.scale = scale
		self.speed = self.speed*self.scale
	
	def update_pos(self, x, y):
		self.x = int(x*self.scale)
		self.y = int(y*self.scale)
	
	def update(self, screen, player, col_objs):
		# ~ self.move(config, col_objs)
		player_pos = (player.x, player.y)
		if not self.chp == 0: self.rotate(player_pos)
		self.resize()
		self.rect = self.image.get_rect(center=(self.x, self.y))
		screen.blit(self.image, self.rect)
		
		if not self.chp == 0:
			mask = pygame.mask.from_surface(self.image)
			for o in col_objs:
				m = pygame.mask.from_surface(o.image)
				offset = (self.x - int(o.x+(self.tx/2)), self.y - int(o.y+(self.ty/2)))
				result = m.overlap(mask, offset)
				if result:
					str_ = o.gun.str
					if not self.chp == 0:
						self.damage_effect(str_, player.dmg_hp)
					o.hp -= self.rp
					return
	
	def damage_effect(self, str_, dmg_hp):
		dmg_sp = 1-dmg_hp
		if self.csp > 0:
			if self.csp - str_*dmg_sp >= 0:
				self.csp -= str_*dmg_sp
			else:
				temp = ((str_*dmg_sp)-self.csp)
				self.chp -= temp
				self.csp = 0
			if self.chp - str_*dmg_hp >= 0:
				self.chp -= str_*dmg_hp
			else:
				self.chp = 0
				self.killed_time = time.perf_counter()
		else:
			if self.chp - str_ >= 0:
				self.chp -= str_
			else:
				self.chp = 0
		self.chp = int(self.chp)
		self.csp = int(self.csp)
		if self.chp == 0:
			self.killed_time = time.perf_counter()
	
	def resize(self):
		self.tx = int(self.txo * self.scale)
		self.ty = int(self.tyo * self.scale)
		self.image = pygame.transform.scale(self.image, (self.tx, self.ty))
	
	def rotate(self, player_pos):
		run, rise = (player_pos[0]-self.x, player_pos[1]-self.y)
		self.angle = math.degrees(math.atan2(rise, run))
		self.image = pygame.transform.rotate(self.image_orig, -self.angle)
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
	
	@property
	def kill(self):
		if self.chp <= 0: return True
		else: return False


class Weapon:
	
	def __init__(self, bullet, name, lvl, str_, ammo, cpw, cpl, cpa, istr, icost, tps, dofs, speed, acc, ps):
		self.bullet = bullet	# Bullet Class
		self.name = name		# Weapon name
		self.lvl = lvl			# Weapon level
		self.str = str_			# Weapon strenght
		self.ammo = ammo		# Ammunition quantity
		self.cpw = cpw			# Cost per weapon
		self.cpl = cpl			# Cost increase per level
		self.cpa = cpa			# Cost per ammunition
		self.istr  = istr		# Increase strength per level
		self.icost = icost		# Increase cost per level
		self.tps = tps			# Time per shot
		self.dofs = dofs		# Duration of the shot
		self.speed = speed		# Shot speed
		self.accuracy = acc		# Shot Accuracy
		self.ps = ps			# Piercing Strike
	
	def update_speed(self, scale):
		self.speed = self.speed*scale
	
	def levelUp(self, money=None):
		if money:
			if money >= self.cpl:
				money -= self.cpl
				self.lvl += 1
				self.str += self.istr
				self.cpl += self.icost
			return money
		else:
			self.lvl += 1
			self.str += self.istr
			self.cpl += self.icost
	
	def addAmmo(self, qty):
		
		if money >= self.cpl:
			
			money -= self.cpa
			self.ammo += qty
		
		return money
	
	def __str__(self):
		stats  = '\n  {}:{}'.format(self.name, 'Next'.rjust(20) )
		stats += '\n    Lvl = {}'.format(str(self.lvl).ljust(12))
		stats += '{}'.format(self.lvl + 1)
		stats += '\n    Str = {}'.format(str(self.str).ljust(12))
		stats += '{}'.format(self.str + self.istr)
		return stats

class Bullet(pygame.sprite.Sprite):
	
	def __init__(self, screen, name, x, y, angle, gun, scale):
		
		super().__init__()
		
		self.screen = screen
		self.name = name
		self.width = 16
		self.height = 4
		self.image_orig = load_image(bullet_paths[self.name])
		self.image = self.image_orig
		self.image.fill((255,255,255))
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.course = 0
		self.shoot = False
		self.angle = angle
		self.scale = scale
		self.hp = gun.ps
		self.gun = gun
		self.time_init = time.perf_counter()
	
	def update(self, config):
		self.image = load_image(bullet_paths[self.name])
		self.resize()
		self.image = pygame.transform.rotate(self.image, -self.angle+90)
		self.rect = self.image.get_rect()
		rads = math.radians(self.angle)
		self.x += self.gun.speed * config.speed_delta * math.sin(rads)
		self.y -= self.gun.speed * config.speed_delta * math.cos(rads)
		self.screen.blit(self.image, (self.x, self.y))
	
	def resize(self):
		self.tx = int(self.txo * self.scale)
		self.ty = int(self.tyo * self.scale)
		self.image = pygame.transform.scale(self.image, (self.tx, self.ty))
	
	@property
	def kill(self):
		if self.hp <= 0: return True
		else: return False


class Box(pygame.sprite.Sprite):
	
	def __init__(self, name, dims, room_level, weapons):
		
		super().__init__()
		
		self.name = name
		self.image_orig = load_image(box_paths[self.name])
		self.image = self.image_orig
		self.angle = random.randint(10,350)
		self.image = pygame.transform.rotate(self.image, -self.angle)
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
		self.x = random.randint(100,dims[0]-100)
		self.y = random.randint(100,dims[1]-100)
		self.room_level = room_level
		self.hp = self.room_level*10					# Health Points
		self.rp = 50									# Resistance Points
		self.killed_time = 0
		
		self.drop = {}
		# ~ self.actual_weapon = random.choice(['Gun', 'Plasma', 'Flame'])
		self.actual_weapon = random.choice(list(weapons))
		self.drop_update()
	
	def drop_update(self):
		
		if self.room_level > 20:
			money_min = self.room_level - 20
			money_max = self.room_level + 20
		else:
			money_min = 1
			money_max = 20
		
		money_val = random.randint(money_min, money_max)*10
		
		ammo = {'Gun':50, 'Plasma':10, 'Flame':5}
		
		drops = config.info.drops_config(money_val, ammo[self.actual_weapon])
		
		if random.random() < drops['money']['probability']      /100: self.drop.update(drops['money']['drop'])
		if random.random() < drops['ammo']['probability']       /100: self.drop.update(drops['ammo']['drop'])
		if random.random() < drops['tps']['probability']        /100: self.drop.update(drops['tps']['drop'])
		if random.random() < drops['range']['probability']      /100: self.drop.update(drops['range']['drop'])
		if random.random() < drops['speed']['probability']      /100: self.drop.update(drops['speed']['drop'])
		if random.random() < drops['accuracy']['probability']   /100: self.drop.update(drops['accuracy']['drop'])
		if random.random() < drops['piercing']['probability']   /100: self.drop.update(drops['piercing']['drop'])
		if random.random() < drops['speed mech']['probability'] /100: self.drop.update(drops['speed mech']['drop'])
		if random.random() < drops['hp recovery']['probability']/100: self.drop.update(drops['hp recovery']['drop'])
		if random.random() < drops['sp recovery']['probability']/100: self.drop.update(drops['sp recovery']['drop'])
	
	def update_hp(self, hp): self.hp = hp
	
	def update(self, screen, player, objs, percent=1):
		self.resize(percent)
		self.rect = self.image.get_rect(center=(self.x, self.y))
		screen.blit(self.image, self.rect)
		
		if not self.hp == 0:
			mask = pygame.mask.from_surface(self.image)
			for o in objs:
				m = pygame.mask.from_surface(o.image)
				offset = (self.x - int(o.x+(self.tx/2)), self.y - int(o.y+(self.ty/2)))
				result = m.overlap(mask, offset)
				if result:
					if not self.hp == 0:
						self.hp -= o.gun.str
						if self.hp < 0: self.hp = 0
						if self.hp == 0:
							self.killed_time = time.perf_counter()
					o.hp -= self.rp
					return
	
	@property
	def size(self): return '{}x{}'.format(self.tx, self.ty)
	
	def resize(self, percent):
		self.tx = int(self.txo * percent)
		self.ty = int(self.tyo * percent)
		self.image = pygame.transform.scale(self.image, (self.tx, self.ty))
	
	@property
	def kill(self):
		if self.hp <= 0: return True
		else: return False

class Texture(pygame.sprite.Sprite):
	
	def __init__(self, screen, name):
		
		super().__init__()
		
		self.screen = screen
		self.name = name
		self.image = load_image(wall_paths[self.name])
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
		self.x = 0
		self.y = 0
	
	def resize(self, escale):
		self.tx = int(self.txo * escale)
		self.ty = int(self.tyo * escale)
		self.image = pygame.transform.scale(self.image, (self.tx, self.ty))
	
	def update(self, x, y, scale=1):
		if not scale == 1: self.resize(scale)
		self.x = x
		self.y = y
		self.rect = self.image.get_rect(center=(self.x, self.y))
		self.screen.blit(self.image, self.rect)
	
	def colision(self, objs):
		if self.name in ['wall 01']:
			mask = pygame.mask.from_surface(self.image)
			for o in objs:
				m = pygame.mask.from_surface(o.image)
				offset = (self.x - int(o.x+(self.tx/2)), self.y - int(o.y+(self.ty/2)))
				result = m.overlap(mask, offset)
				if result:
					o.hp -= 200
					return

class IconWeapon(pygame.sprite.Sprite):
	
	def __init__(self, screen, name):
		
		super().__init__()
		
		self.screen = screen
		self.name = name
		self.image = load_image(weapon_icon_paths[self.name])
		self.tx = self.image.get_width()
		self.ty = self.image.get_height()
		self.txo = self.tx
		self.tyo = self.ty
		self.x = 0
		self.y = 0
	
	def resize(self, escale):
		self.tx = int(self.txo * escale)
		self.ty = int(self.tyo * escale)
		self.image = pygame.transform.scale(self.image, (self.tx, self.ty))
	
	def update(self, pos_x, pos_y, tam_x, tam_y, scale=1):
		if not scale == 1: self.resize(scale)
		self.x = pos_x
		self.y = pos_y
		center = ( pos_x + int(tam_x/2), pos_y + int(tam_y/2))
		self.rect = self.image.get_rect(center=center)
		self.screen.blit(self.image, self.rect)



class Data:
	
	def __init__(self):
		
		self.gun_init_stats = {
			'name':  'Gun',
			'lvl':   0,
			'str_':  10,			#10
			'ammo':  1000,
			'cpw':   0,
			'cpl':   100,
			'cpa':   10,
			'istr':  10,
			'icost': 100,
			'tps':   .5,			# .5
			'dofs':  2,				#  2
			'speed': 5,				#  5
			'acc':   5,				#  5
			'ps':    10
		}
		
		self.plasma_init_stats = {
			'name': 'Plasma',
			'lvl':   0,
			'str_':  100,
			'ammo':  10,
			'cpw':   10000,
			'cpl':   5000,
			'cpa':   100,
			'istr':  50,
			'icost': 2500,
			'tps':   1,
			'dofs':  1,
			'speed': 3,
			'acc':   1,
			'ps':    20
		}
		
		self.flame_init_stats = {
			'name': 'Flame',
			'lvl':   0,
			'str_':  200,
			'ammo':  5,
			'cpw':   20000,
			'cpl':   10000,
			'cpa':   200,
			'istr':  100,
			'icost': 5000,
			'tps':   2,
			'dofs':  1,
			'speed': 5,
			'acc':   0,
			'ps':    30
		}
		
		self.gun    = Weapon(Bullet, **self.gun_init_stats)
		self.plasma = Weapon(Bullet, **self.plasma_init_stats)
		self.flame  = Weapon(Bullet, **self.flame_init_stats)
		
		self.player_init_stats = {
			'path':    'Mech 03',
			'name':    'Player',
			'hp':      200,
			'sp':      0,
			'cpl_hp':  100,
			'cpl_sp':  100,
			'icpl_hp': 100,
			'icpl_sp': 100,
			'speed':   2,		#2
			'money':   0,
			'weapons': {}
		}
		
		self.player = Player(**self.player_init_stats)
		self.iconWeapon = IconWeapon
		self.texture = Texture
		self.enemy = Enemy
		self.box = Box



def load_image(filename, transparent=True):
	
	global Error
	
	try: image = pygame.image.load(filename)
	except pygame.error as message: raise SystemError
	
	image = image.convert()
	
	if transparent:
		
		color = image.get_at((0,0))
		image.set_colorkey(color, RLEACCEL)
		
	return image


