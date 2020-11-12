
import config
import init
import room
import save

import psutil
import pygame
import random
import time
import gc		# Garbage Collector
import os

class Infinity(init.Init):
	
	def __init__(self):
		
		init.Init.__init__(self)
		
		# General variables:
		self.rooms_limit = 25			# 15=16^2=225, 20=21^2=400, 25=26^2=625, 35=36^2=1225
		self.rooms = {(int(self.rooms_limit/2),int(self.rooms_limit/2)): room.Room((int(self.rooms_limit/2),int(self.rooms_limit/2)), self.RESOLUTION, 1, limit=self.rooms_limit)}
		self.room = self.rooms[(int(self.rooms_limit/2),int(self.rooms_limit/2))]
		self.actual_time = time.perf_counter()
		self.actual_frames = self.config.max_frames
		self.max_room = 1
		self.icon_weapons = [None, None, None]
		self.all_weapons = {
			1: {config.info.weapons[1]: self.data.gun},
			2: {config.info.weapons[2]: self.data.plasma},
			3: {config.info.weapons[3]: self.data.flame}
		}
		
		# Booleans:
		self.extra_room_open = False
		
		# Lists:
		self.player_absorptions = []
		self.drop_on_boxes = []
		self.damage_on_enemies = []
		self.damage_on_boxes = []
		self.damage_on_player = []
	
	def gamemode_infinity(self):
		
		for k, v in self.all_weapons.items():
			for k, w in v.items():
				w.update_speed(self.scale)
		
		self.data.player.update_speed(self.scale)
		self.data.player.update_weapons(self.all_weapons[1])
		
		data_loaded = save.load_data()
		if data_loaded:
			self.data.player.load_player(data_loaded, self.all_weapons)
		# ~ else:
			# ~ self.data.player.update_weapons(self.all_weapons[2])
			# ~ self.data.player.update_weapons(self.all_weapons[3])
		
		self.create_icons()
		
		self.data.player.update_pos(150, 150)
		
		while not self.config.pause:
			
			self.reset()
			self.mainloop()
			self.room.complete = True
			self.save_background_objs()
			
			if self.data.player.x < 0:
				self.data.player.update_pos(self.RESOLUTION[0]-100, int(self.RESOLUTION[1]/2))
				if self.room.room_L in self.rooms:
					self.room = self.rooms[self.room.room_L]
				else:
					if self.room.room_L:
						self.max_room+=1
						self.rooms[self.room.room_L] = room.Room(self.room.room_L, self.RESOLUTION, self.max_room, self.room.room, 'L', self.rooms_limit)
						self.room = self.rooms[self.room.room_L]
			
			elif self.data.player.x > self.RESOLUTION[0]:
				self.data.player.update_pos(100, int(self.RESOLUTION[1]/2))
				if self.room.room_R in self.rooms:
					self.room = self.rooms[self.room.room_R]
				else:
					if self.room.room_R:
						self.max_room+=1
						self.rooms[self.room.room_R] = room.Room(self.room.room_R, self.RESOLUTION, self.max_room, self.room.room, 'R', self.rooms_limit)
						self.room = self.rooms[self.room.room_R]
					
			elif self.data.player.y < 0:
				self.data.player.update_pos(int(self.RESOLUTION[0]/2), self.RESOLUTION[1]-100)
				if self.room.room_U in self.rooms:
					self.room = self.rooms[self.room.room_U]
				else:
					if self.room.room_U:
						self.max_room+=1
						self.rooms[self.room.room_U] = room.Room(self.room.room_U, self.RESOLUTION, self.max_room, self.room.room, 'U', self.rooms_limit)
						self.room = self.rooms[self.room.room_U]
			
			elif self.data.player.y > self.RESOLUTION[1]:
				self.data.player.update_pos(int(self.RESOLUTION[0]/2), 100)
				if self.room.room_D in self.rooms:
					self.room = self.rooms[self.room.room_D]
				else:
					if self.room.room_D:
						self.max_room+=1
						self.rooms[self.room.room_D] = room.Room(self.room.room_D, self.RESOLUTION, self.max_room, self.room.room, 'D', self.rooms_limit)
						self.room = self.rooms[self.room.room_D]
	
	def reset(self):
		self.config.frames = 0
		self.config.time_init = time.perf_counter()
		if not self.room.complete:
			self.create_random_box()
			self.create_enemies()
			self.create_background_objs()
		else:
			self.re_create_background_objs()
	
	def mainloop(self):
		self.config.pause = False
		while not self.config.pause:
			if self.data.player.x < 0 or self.data.player.x > self.RESOLUTION[0]\
			or self.data.player.y < 0 or self.data.player.y > self.RESOLUTION[1]: break
			self.key_events()
			self.config.frames += 1
			self.events.event_handler(self.config)
			self.draw_background()
			self.draw_boxes()
			self.draw_enemies()
			self.draw_player()
			self.create_bullets()
			self.draw_bullets()
			self.del_objs()
			self.draw_stats()
			self.frames_counter()
			pygame.display.update()						# Actualiza Los Datos En La Interfaz. update() o flip()
			self.config.speed_delta = self.clock.tick(self.config.max_frames) / 10
		
		save.save_data(self.data.player)
	
	def key_events(self):
		if self.config.level_up:
			self.data.player.money = self.data.player.gun.levelUp(self.data.player.money)
			self.config.level_up = False
		if self.config.level_up_hp:
			if self.data.player.money >= self.data.player.cpl_hp: self.data.player.level_up_hp()
			self.config.level_up_hp = False
		if self.config.level_up_sp:
			if self.data.player.money >= self.data.player.cpl_sp: self.data.player.level_up_sp()
			self.config.level_up_sp = False
		if self.config.shop_2 and not 'Plasma' in self.data.player.weapons:
			if self.data.player.money >= self.data.plasma_init_stats['cpw']:
				self.data.player.money -= self.data.plasma_init_stats['cpw']
				self.data.player.update_weapons(self.all_weapons[2])
				self.icon_weapons[1] = self.data.iconWeapon(self.screen, 'Plasma')
				self.config.unlocked_weapons[1] = 'Plasma'
			self.config.shop_2 = False
		if self.config.shop_3 and not 'Flame' in self.data.player.weapons:
			if self.data.player.money >= self.data.flame_init_stats['cpw']:
				self.data.player.money -= self.data.flame_init_stats['cpw']
				self.data.player.update_weapons(self.all_weapons[3])
				self.icon_weapons[2] = self.data.iconWeapon(self.screen, 'Flame')
				self.config.unlocked_weapons[2] = 'Flame'
			self.config.shop_3 = False
	
	def frames_counter(self, verb=False):
		
		font_size = int(16*self.scale)
		font = 'Inc-R '+str(font_size)
		pos_x = self.RESOLUTION[0] - 75*self.scale
		self.draw_text('FPS: '+str(self.actual_frames), (int(pos_x),   int(10*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text('FPS: '+str(self.actual_frames), (int(pos_x)-1, int(10*self.scale)-1), self.config.FONT[font], self.config.COLOR['Azul Claro'])
		
		if time.perf_counter() - self.config.time_init >= 1:
			if verb: print('\r Frames:', self.config.frames, end='')
			self.actual_frames = self.config.frames
			self.config.frames = 0
			self.config.time_init = time.perf_counter()
	
	def del_objs(self):
		
		for i in range(len(self.room.bullets)):
			if self.room.bullets[i].kill:
				b = self.room.bullets.pop(i)
				del b
				self.room.bullets.insert(i, None)
		while None in self.room.bullets: self.room.bullets.remove(None)
		
		for enemy in self.room.enemies:
			for i in range(len(enemy.bullets)):
				if enemy.bullets[i].kill:
					b = enemy.bullets.pop(i)
					del b
					enemy.bullets.insert(i, None)
			while None in enemy.bullets: enemy.bullets.remove(None)
		
		for i in range(len(self.room.boxes)):
			if self.room.boxes[i].kill:
				if time.perf_counter() - self.room.boxes[i].killed_time > 2:
					b = self.room.boxes.pop(i)
					del b
					self.room.boxes.insert(i, None)
		while None in self.room.boxes: self.room.boxes.remove(None)
		
		for i in range(len(self.room.enemies)):
			if self.room.enemies[i].kill:
				if time.perf_counter() - self.room.enemies[i].killed_time > 2:
					b = self.room.enemies.pop(i)
					del b
					self.room.enemies.insert(i, None)
		while None in self.room.enemies: self.room.enemies.remove(None)
		
		self.room.col_objs  = self.room.walls + self.room.boxes + self.room.enemies
	
	def add_drops(self, obj):
		for k, v in obj.drop.items():
			try:
				if k == 'money':  self.data.player.money += v
				elif k == 'ammo': self.data.player.weapons[obj.actual_weapon].ammo += v
				elif k == 'dmg res':
					if self.data.player.dmg_res <= .85:
						self.data.player.dmg_res += v
					else:
						self.data.player.weapons[obj.actual_weapon].speed += v*5
				elif k == 'tps':
					if self.data.player.weapons[obj.actual_weapon].tps > 0:
						self.data.player.weapons[obj.actual_weapon].tps -= v
					else:
						self.data.player.weapons[obj.actual_weapon].speed += v*5
				elif k == 'range': self.data.player.weapons[obj.actual_weapon].dofs += v
				elif k == 'speed': self.data.player.weapons[obj.actual_weapon].speed += v
				elif k == 'accuracy':
					if obj.actual_weapon == self.config.weapons[1] \
					and self.data.player.weapons[obj.actual_weapon].accuracy == 0:
						config.info.max_acc_1 = True
					elif obj.actual_weapon == self.config.weapons[2] \
					and self.data.player.weapons[obj.actual_weapon].accuracy == 0:
						config.info.max_acc_2 = True
					elif obj.actual_weapon == self.config.weapons[3] \
					and self.data.player.weapons[obj.actual_weapon].accuracy == 0:
						config.info.max_acc_3 = True
					
					if obj.actual_weapon == self.config.weapons[1] \
					and not config.info.max_acc_1:
						self.data.player.weapons[obj.actual_weapon].accuracy -= v
					elif obj.actual_weapon == self.config.weapons[2] \
					and not config.info.max_acc_2:
						self.data.player.weapons[obj.actual_weapon].accuracy -= v
					elif obj.actual_weapon == self.config.weapons[3] \
					and not config.info.max_acc_3:
						self.data.player.weapons[obj.actual_weapon].accuracy -= v
					else:
						self.data.player.weapons[obj.actual_weapon].speed += v/5
				elif k == 'piercing': self.data.player.weapons[obj.actual_weapon].ps += v
				elif k == 'speed mech':
					if self.data.player.speed < 4: self.data.player.speed += v
				elif k == 'hp abs':
					if obj.actual_weapon == self.config.weapons[1] \
					and self.data.player.weapons[obj.actual_weapon].hp_abs >= .01:
						config.info.max_hp_abs_1 = True
					elif obj.actual_weapon == self.config.weapons[2] \
					and self.data.player.weapons[obj.actual_weapon].hp_abs >= .03:
						config.info.max_hp_abs_2 = True
					elif obj.actual_weapon == self.config.weapons[3] \
					and self.data.player.weapons[obj.actual_weapon].hp_abs >= .05:
						config.info.max_hp_abs_3 = True
					
					if   obj.actual_weapon == self.config.weapons[1] \
					and not config.info.max_hp_abs_1: self.data.player.weapons[obj.actual_weapon].hp_abs += v
					elif obj.actual_weapon == self.config.weapons[2] \
					and not config.info.max_hp_abs_2: self.data.player.weapons[obj.actual_weapon].hp_abs += v
					elif obj.actual_weapon == self.config.weapons[3] \
					and not config.info.max_hp_abs_3: self.data.player.weapons[obj.actual_weapon].hp_abs += v
					else:
						if self.data.player.speed < 4: self.data.player.speed += v
				elif k == 'hp recovery':
					if self.data.player.hp_time_recovery > 0:
						self.data.player.hp_time_recovery -= v
					else:
						if self.data.player.sp_time_recovery > 0:
							self.data.player.sp_time_recovery -= (v-.005)
						else:
							self.data.player.weapons[obj.actual_weapon].speed += (v*2)
				elif k == 'sp recovery':
					if self.data.player.sp_time_recovery > 0:
						self.data.player.sp_time_recovery -= v
					else:
						if self.data.player.hp_time_recovery > 0:
							self.data.player.hp_time_recovery -= (v+.005)
						else:
							self.data.player.weapons[obj.actual_weapon].speed += (v*2.5)
			except KeyError: pass
	
	def del_bullets(self):
		for i in range(len(self.room.bullets)):
			if time.perf_counter() - self.room.bullets[i].time_init > self.room.bullets[i].gun.dofs:
				b = self.room.bullets.pop(i)
				del b
				self.room.bullets.insert(i, None)
		while None in self.room.bullets: self.room.bullets.remove(None)
		
		for enemy in self.room.enemies:
			for i in range(len(enemy.bullets)):
				if time.perf_counter() - enemy.bullets[i].time_init > enemy.bullets[i].gun.dofs:
					b = enemy.bullets.pop(i)
					del b
					enemy.bullets.insert(i, None)
			while None in enemy.bullets: enemy.bullets.remove(None)
	
	def create_icons(self):
		for name in self.data.player.weapons:
			if   name == self.config.weapons[1]: self.icon_weapons[0] = self.data.iconWeapon(self.screen, self.config.weapons[1])
			elif name == self.config.weapons[2]: self.icon_weapons[1] = self.data.iconWeapon(self.screen, self.config.weapons[2])
			elif name == self.config.weapons[3]: self.icon_weapons[2] = self.data.iconWeapon(self.screen, self.config.weapons[3])
	
	def create_bullets(self):
		if self.config.mbd['active'] and self.config.mbd['button'] == 1 and self.data.player.gun.ammo > 0:
			if time.perf_counter() - self.actual_time > self.data.player.gun.tps:
				accuracy  = self.data.player.angle+90
				accuracy += random.randint(int(-(self.data.player.gun.accuracy+.99)), int(self.data.player.gun.accuracy+.99))
				bullet = self.data.player.gun.bullet(self.screen, self.data.player.actual_weapon, self.data.player.x, self.data.player.y, accuracy, self.data.player.gun, self.scale)
				self.room.bullets.append(bullet)
				self.data.player.gun.ammo -= 1
				self.actual_time = time.perf_counter()
		
		for enemy in self.room.enemies:
			if enemy.chp > 0:
				accuracy  = enemy.angle+90
				accuracy += random.randint(-enemy.gun.accuracy, enemy.gun.accuracy)
				if enemy.bullets:
					if time.perf_counter() - enemy.bullets[-1].time_init > enemy.gun.tps:
						bullet = enemy.gun.bullet(self.screen, enemy.actual_weapon, enemy.x, enemy.y, accuracy, enemy.gun, self.scale)
						enemy.bullets.append(bullet)
						enemy.actual_time = time.perf_counter()
				else:
					if time.perf_counter() - enemy.actual_time > enemy.gun.tps:
						bullet = enemy.gun.bullet(self.screen, enemy.actual_weapon, enemy.x, enemy.y, accuracy, enemy.gun, self.scale)
						enemy.bullets.append(bullet)
						enemy.actual_time = time.perf_counter()
		self.del_bullets()
	
	def create_enemies(self):
		for i, (x, y) in enumerate(self.room.enemies_pos):
			pos_x = int( x * self.scale)
			pos_y = int( y * self.scale)
			if i == 2 and self.max_room > 25:
				self.room.enemies.append(self.data.enemy(pos_x, pos_y, **self.room.enemy_02_init_stats))
			elif i == 3 and self.max_room > 50:
				self.room.enemies.append(self.data.enemy(pos_x, pos_y, **self.room.enemy_03_init_stats))
			else:
				self.room.enemies.append(self.data.enemy(pos_x, pos_y, **self.room.enemy_01_init_stats))
	
	def create_random_box(self):
		for i in range(self.room.qty_boxes):
			self.room.boxes.append(self.data.box('box 01', (self.RESOLUTION[0], self.RESOLUTION[1]), self.room.level, self.data.player.weapons.keys()))
	
	def create_background_objs(self):
		
		self.select_background_colors()
		
		base = int(self.config.texture_size*self.scale)
		rx = int(self.RESOLUTION[0]/base)
		ry = int(self.RESOLUTION[1]/base)
		self.room.walls = []
		
		for y in range(ry):
			obj = []
			for x in range(rx):
				
				type_ = 'floor 01'
				
				if not 0 < y < ry-1 or x in [0, rx-1]:
					
					type_ = 'wall 01'
				
				if (x in [9, 10] and y in [0, 11]) or (y in [5, 6] and x in [0, 19]):
					
					if (self.room.wall_L and (x == 0 and y in [5,6])) \
					or (self.room.wall_R and (x == 19 and y in [5,6])) \
					or (self.room.wall_U and (x in [9, 10] and y == 0)) \
					or (self.room.wall_D and (x in [9, 10] and y == 11)):
						
						type_ = 'wall 01'
					
					else: type_ = 'door 01'
				
				texture = self.data.texture(self.screen, type_)
				
				if type_ in ['wall 01','door 01']:
					self.room.walls.append(texture)
				
				obj.append(texture)
				
			self.room.objs.append(obj)
		
		self.chk_opened_doors()
	
	def re_create_background_objs(self):
		
		for j, room_obj in enumerate(self.room.objs[:]):
			for i, name in enumerate(room_obj):
				
				obj = self.data.texture(self.screen, name)
				
				if name in ['wall 01', 'door 01']:
					self.room.walls.append(obj)
				
				self.room.objs[j][i] = obj
		
	def save_background_objs(self): # Garbage Collector
		
		self.room.col_objs = []
		self.room.walls = []
		
		for j, room_obj in enumerate(self.room.objs[:]):
			for i, obj in enumerate(room_obj):
				self.room.objs[j][i] = obj.name
		gc.collect()
		
	def chk_opened_doors(self):
		
		pos_x, pos_y = self.room.room
		candidats = []
		
		if self.rooms.get((pos_x,   pos_y+1)): self.room.opens.add('D')
		if self.rooms.get((pos_x+1, pos_y)):   self.room.opens.add('R')
		if self.rooms.get((pos_x,   pos_y-1)): self.room.opens.add('U')
		if self.rooms.get((pos_x-1, pos_y)):   self.room.opens.add('L')
		
		if not 'D' in self.room.opens and not self.room.wall_D: candidats.append('D')
		if not 'R' in self.room.opens and not self.room.wall_R: candidats.append('R')
		if not 'U' in self.room.opens and not self.room.wall_U: candidats.append('U')
		if not 'L' in self.room.opens and not self.room.wall_L: candidats.append('L')
		
		if candidats:
			r = random.randint(0, len(candidats)-1)
			c = candidats.pop(r)
			self.room.doors = c
			# ~ print(self.room.doors)
		else:
			# ~ print(2)
			self.extra_room_open = True
			self.room.doors = None
	
	def select_background_colors(self):
		base = int(self.config.texture_size*self.scale)
		rx = int(self.RESOLUTION[0]//base)
		ry = int(self.RESOLUTION[1]//base)
		self.room.colors = []
		for j in range(ry):
			color = []
			for i in range(rx):
				r = random.random()
				if   r > .50: cl = 'Negro'
				elif r > .25: cl = 'Gris O'
				elif r > .05: cl = 'Metal'
				elif r > .00: cl = 'Oxido'
				color.append(self.config.COLOR[cl])
			self.room.colors.append(color)
	
	def draw_stats(self):
		
		font_size = int(16*self.scale)
		font = 'Inc-R '+str(font_size)
		self.rect_opaco([int(5*self.scale),int(10*self.scale),int(500*self.scale),font_size*2+int(10*self.scale)], self.config.COLOR['Negro'], 150)
		
		chp = self.data.player.chp
		csp = self.data.player.csp
		hp = self.data.player.hp
		sp = self.data.player.sp
		ps = self.data.player.gun.ps
		money = self.data.player.money
		
		HPtxt = 'HP: '+str(int(chp)).ljust(6)+'/'+str(hp).ljust(6)
		SPtxt = 'SP: '+str(csp).ljust(6)+'/'+str(sp).ljust(6)
		Moneytxt = '$'+str(money)
		NLtxt = 'Next: $'+str(self.data.player.gun.cpl)
		NHPtxt = 'Next HP: $'+str(self.data.player.cpl_hp)
		NSPtxt = 'Next SP: $'+str(self.data.player.cpl_sp)
		
		self.draw_text(HPtxt,    (int(10*self.scale),   int(12*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text(HPtxt,    (int(10*self.scale)-1, int(12*self.scale)-1), self.config.FONT[font], self.config.COLOR['Rojo Claro'])
		self.draw_text(SPtxt,    (int(10*self.scale),   int(32*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text(SPtxt,    (int(10*self.scale)-1, int(32*self.scale)-1), self.config.FONT[font], self.config.COLOR['Azul Claro'])
		self.draw_text(Moneytxt, (int(180*self.scale),  int(12*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text(Moneytxt, (int(180*self.scale)-1,int(12*self.scale)-1), self.config.FONT[font], self.config.COLOR['Verde Claro'])
		self.draw_text(NLtxt,    (int(180*self.scale),  int(32*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text(NLtxt,    (int(180*self.scale)-1,int(32*self.scale)-1), self.config.FONT[font], self.config.COLOR['Verde Claro'])
		self.draw_text(NHPtxt,   (int(280*self.scale),  int(12*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text(NHPtxt,   (int(280*self.scale)-1,int(12*self.scale)-1), self.config.FONT[font], self.config.COLOR['Verde Claro'])
		self.draw_text(NSPtxt,   (int(280*self.scale),  int(32*self.scale)),   self.config.FONT[font], self.config.COLOR['Negro'])
		self.draw_text(NSPtxt,   (int(280*self.scale)-1,int(32*self.scale)-1), self.config.FONT[font], self.config.COLOR['Verde Claro'])
		
		self.draw_weapons()
	
	def draw_weapons(self):
		
		x = 5
		y = 65
		tam = 50
		
		for iw in self.icon_weapons:
			
			pos_x = int((x-1)*self.scale)
			pos_y = int((y-1)*self.scale)
			tam_x = int((tam+2)*self.scale)
			tam_y = int((tam+2)*self.scale)
			
			if not iw:
				self.rect_opaco([pos_x, pos_y, tam_x+int(8*self.scale), tam_y+int(16*self.scale)], self.config.COLOR['Negro'], 120)
				y += tam+int(20*self.scale)
				continue
			
			if iw.name == self.data.player.actual_weapon:
				self.rect_opaco([pos_x, pos_y, tam_x+int(10*self.scale), tam_y+int(16*self.scale)], self.config.COLOR['Negro'], 255)
			else:
				self.rect_opaco([pos_x, pos_y, tam_x+int(8*self.scale), tam_y+int(16*self.scale)], self.config.COLOR['Negro'], 120)
			
			iw.update(pos_x, pos_y, tam_x, tam_y, self.scale)
			
			font_size = int(18*self.scale)
			font = 'Wendy ' + str(font_size)
			weapon = self.data.player.weapons[iw.name]
			AMMOtxt = str(weapon.ammo)
			
			if self.scale > .75:
				self.draw_text(AMMOtxt, [int(tam_x/2)+10-int(len(AMMOtxt)*font_size/4), pos_y + int(tam_y/2) - int(font_size/2)], self.config.FONT[font], self.config.COLOR['Negro'])
			self.draw_text(AMMOtxt, [int(tam_x/2)+10-int(len(AMMOtxt)*font_size/4)-1, pos_y + int(tam_y/2) - int(font_size/2)-1], self.config.FONT[font], self.config.COLOR['Negro'])
			# ~ if self.scale > .75:
				# ~ self.draw_text(AMMOtxt, [int(tam_x/2)+10-int(len(AMMOtxt)*font_size/4)-2, pos_y + int(tam_y/2) - int(font_size/2)-2], self.config.FONT[font], self.config.COLOR['Gris'])
			self.draw_text(AMMOtxt, [int(tam_x/2)+10-int(len(AMMOtxt)*font_size/4)-3, pos_y + int(tam_y/2) - int(font_size/2)-3], self.config.FONT[font], self.config.COLOR['Blanco'])
			
			font_size = int(14*self.scale)
			font = 'Inc-R ' + str(font_size)
			DMGtxt = 'DMG:'+str(weapon.str).rjust(4)
			
			self.draw_text(DMGtxt,  [pos_x+int(2*self.scale),   pos_y+tam_y+int(1*self.scale)],   self.config.FONT[font], self.config.COLOR['Negro'])
			self.draw_text(DMGtxt,  [pos_x+int(2*self.scale)-1, pos_y+tam_y+int(1*self.scale)-1], self.config.FONT[font], self.config.COLOR['Azul Claro'])
			
			y += tam+int(20*self.scale)
	
	def draw_bullets(self):
		for b in self.room.bullets:
			t = time.perf_counter() - b.time_init
			effect = ['Plasma', 'Flame']
			if b.scale > .1 and b.name in effect and t > .5:		# Efecto desvanecer.
				b.scale -= .02
			b.update(self.config)
		for enemy in self.room.enemies:
			for b in enemy.bullets: b.update(self.config)
	
	def draw_boxes(self):
		for b in self.room.boxes:
			
			obj = b.update(self.screen, self.data.player, self.room.bullets, self.scale)
			
			if obj: self.damage_on_boxes.append(obj)
			self.draw_damage('boxes')
			
			if b.kill:
				if not b.loot_obtained:
					self.add_drops(b)		# Add Loot
					b.loot_obtained = True
				self.draw_drops(b)			# Draw Loot
			else:
				text = str(b.hp)
				font_size = int(14*self.scale)
				font = 'Wendy '+str(font_size)
				x = self.get_pos_text_center(b.x, len(text), font, font_size)
				pos = (x, int( b.y + (b.ty/2) ))
				self.draw_text(text,  pos,                 self.config.FONT[font], self.config.COLOR['Negro'])
				self.draw_text(text, (pos[0]-1, pos[1]-1), self.config.FONT[font], self.config.COLOR['Azul Claro'])
	
	def draw_background(self):
		
		x_pos = int(32*self.scale)
		y_pos = int(32*self.scale)
		base = int(64*self.scale)
		rx = int(self.RESOLUTION[0]//base)
		ry = int(self.RESOLUTION[1]//base)
		pos_x, pos_y = self.room.room
		
		if self.extra_room_open and self.room.doors:
			# ~ print(1)
			self.extra_room_open = False
			self.chk_opened_doors()
		
		if self.rooms.get((pos_x, pos_y+1)):
			x, y = 9, 11
			if 'door 01' in [self.room.objs[y][x].name, self.room.objs[y][x+1].name]:
				self.room.walls.remove(self.room.objs[y][x])
				self.room.walls.remove(self.room.objs[y][x+1])
				self.room.objs[y][x]   = self.data.texture(self.screen, 'floor 02')
				self.room.objs[y][x+1] = self.data.texture(self.screen, 'floor 02')
		
		if self.rooms.get((pos_x+1, pos_y)):
			x, y = 19, 5
			if 'door 01' in [self.room.objs[y][x].name, self.room.objs[y+1][x].name]:
				self.room.walls.remove(self.room.objs[y][x])
				self.room.walls.remove(self.room.objs[y+1][x])
				self.room.objs[y][x]   = self.data.texture(self.screen, 'floor 02')
				self.room.objs[y+1][x] = self.data.texture(self.screen, 'floor 02')
		
		if self.rooms.get((pos_x, pos_y-1)):
			x, y = 9, 0
			if 'door 01' in [self.room.objs[y][x].name, self.room.objs[y][x+1].name]:
				self.room.walls.remove(self.room.objs[y][x])
				self.room.walls.remove(self.room.objs[y][x+1])
				self.room.objs[y][x]   = self.data.texture(self.screen, 'floor 02')
				self.room.objs[y][x+1] = self.data.texture(self.screen, 'floor 02')
		
		if self.rooms.get((pos_x-1, pos_y)):
			x, y = 0, 5
			if 'door 01' in [self.room.objs[y][x].name, self.room.objs[y+1][x].name]:
				self.room.walls.remove(self.room.objs[y][x])
				self.room.walls.remove(self.room.objs[y+1][x])
				self.room.objs[y][x]   = self.data.texture(self.screen, 'floor 02')
				self.room.objs[y+1][x] = self.data.texture(self.screen, 'floor 02')
		
		for y in range(ry):
			for x in range(rx):
				pygame.draw.rect(self.screen, self.room.colors[y][x], (base*x,base*y,base,base))
				if not self.room.enemies:
					if self.room.objs[y][x].name == 'door 01':
						# ~ if ((x in    [0] and y in [5,6]) and self.rooms.get((pos_x-1, pos_y  )))\
						# ~ or ((x in   [19] and y in [5,6]) and self.rooms.get((pos_x+1, pos_y  )))\
						# ~ or ((x in [9,10] and y in   [0]) and self.rooms.get((pos_x,   pos_y-1)))\
						# ~ or ((x in [9,10] and y in  [11]) and self.rooms.get((pos_x,   pos_y+1))):
							# ~ self.room.walls.remove(self.room.objs[y][x])
							# ~ self.room.objs[y][x] = self.data.texture(self.screen, 'floor 02')
						
						if (x in [9,10] and y in  [11] and 'D' in self.room.doors)\
						or (x in   [19] and y in [5,6] and 'R' in self.room.doors)\
						or (x in [9,10] and y in   [0] and 'U' in self.room.doors)\
						or (x in    [0] and y in [5,6] and 'L' in self.room.doors):
							self.room.walls.remove(self.room.objs[y][x])
							self.room.objs[y][x] = self.data.texture(self.screen, 'floor 02')
				# ~ self.room.objs[y][x].screen = self.screen
				self.room.objs[y][x].update(x_pos+(base*x),y_pos+(base*y),self.scale)
				self.room.objs[y][x].colision(self.room.bullets)
		
		font_size = 24
		font = 'Retro '+str(font_size)
		
		if self.rooms.get((pos_x, pos_y-1)):
			txt = str(self.rooms[(pos_x, pos_y-1)].level)
			self.draw_text(txt, [int(self.RESOLUTION[0]/2-(len(txt)*(font_size/2)/2)), int(font_size/2)], self.config.FONT[font], self.config.COLOR['Oxido'])
		if self.rooms.get((pos_x+1, pos_y)):
			txt = str(self.rooms[(pos_x+1, pos_y)].level)
			self.draw_text(txt, [int(self.RESOLUTION[0]-40-(len(txt)*(font_size/2))), int(self.RESOLUTION[1]/2 - font_size/2)], self.config.FONT[font], self.config.COLOR['Oxido'])
		if self.rooms.get((pos_x, pos_y+1)):
			txt = str(self.rooms[(pos_x, pos_y+1)].level)
			self.draw_text(txt, [int(self.RESOLUTION[0]/2-(len(txt)*(font_size/2)/2)), int(self.RESOLUTION[1]-(font_size*1.5))], self.config.FONT[font], self.config.COLOR['Oxido'])
		if self.rooms.get((pos_x-1, pos_y)):
			txt = str(self.rooms[(pos_x-1, pos_y)].level)
			self.draw_text(txt, [int(len(txt)*(font_size/2))-5, int(self.RESOLUTION[1]/2 - font_size/2)], self.config.FONT[font], self.config.COLOR['Oxido'])
		
		font_size = 64
		font = 'Retro '+str(font_size)
		txt = str(self.room.level)
		self.draw_text(txt, [int(self.RESOLUTION[0]/2-(len(txt)*(font_size/2)/2)), int(self.RESOLUTION[1]/2 - font_size/2)], self.config.FONT[font], self.config.COLOR['Negro'])
	
	def draw_player(self):
		obj = self.data.player.update(self.screen, self.config, self.room.col_objs, self.room.enemies)
		for o in obj: self.damage_on_player.append(o)
		self.draw_damage('player')
		self.draw_absorption('player')
	
	def draw_enemies(self):
		for e in self.room.enemies:
			
			obj = e.update(self.screen, self.data.player, self.room.bullets)
			
			if obj: self.damage_on_enemies.append(obj)
			self.draw_damage('enemies')
			
			if e.kill:
				if not e.loot_obtained:
					self.add_drops(e)		# Add Loot
					e.loot_obtained = True
				self.draw_drops(e)			# Draw Loot
			else:
				font_size = int(14*self.scale)
				font = 'Inc-R '+str(font_size)
				
				text = 'HP: ' + str(e.chp).ljust(5) + '/'+ str(e.hp).ljust(5)
				x = self.get_pos_text_center(e.x, len(text), font, font_size)
				pos = (x, int( e.y + (e.ty/2) ))
				self.draw_text(text,  pos,                 self.config.FONT[font], self.config.COLOR['Negro'])
				self.draw_text(text, (pos[0]-1, pos[1]-1), self.config.FONT[font], self.config.COLOR['Rojo Claro'])
				
				text = 'SP: ' + str(e.csp).ljust(5) + '/'+ str(e.sp).ljust(5)
				x = self.get_pos_text_center(e.x, len(text), font, font_size)
				pos = (x, int( e.y + (e.ty/2) + 12 ))
				self.draw_text(text,  pos,                 self.config.FONT[font], self.config.COLOR['Negro'])
				self.draw_text(text, (pos[0]-1, pos[1]-1), self.config.FONT[font], self.config.COLOR['Azul Claro'])
	
	def get_speed_percent(self, weapon, value):
		if   weapon == self.config.weapons[1]: return 100 / self.data.gun_init_stats['speed']    * value
		elif weapon == self.config.weapons[2]: return 100 / self.data.plasma_init_stats['speed'] * value
		elif weapon == self.config.weapons[3]: return 100 / self.data.flame_init_stats['speed']  * value
	
	def draw_drops(self, obj):
		font_size = int(14*self.scale)
		font = 'Inc-R '+str(font_size)
		add = 0
		for k, v in obj.drop.items():
			try:
				if k == 'money':   text = '+$' + str(v)
				elif k == 'ammo':  text = obj.actual_weapon+' Ammo +'+str(v)
				elif k == 'dmg res':
					if self.data.player.dmg_res <= .85:
						text = 'Player DMG Resistance +'+str(v)
					else:
						percent = self.get_speed_percent(obj.actual_weapon, v*5)
						text = obj.actual_weapon+' Speed +'+str(percent)+'%'
						# ~ text = obj.actual_weapon+' Speed +'+str(v*10)
				elif k == 'tps':
					if self.data.player.weapons[obj.actual_weapon].tps > 0:
						text = obj.actual_weapon+' TPS Speed -'+str(v)
					else:
						percent = self.get_speed_percent(obj.actual_weapon, v)
						text = obj.actual_weapon+' Speed +'+str(percent)+'%'
						# ~ text = obj.actual_weapon+' Speed +'+str(v)
				elif k == 'range': text = obj.actual_weapon+' Range +'+str(v)
				elif k == 'speed':
					percent = self.get_speed_percent(obj.actual_weapon, v)
					text = obj.actual_weapon+' Speed +'+str(percent)+'%'
				elif k == 'accuracy':
					if obj.actual_weapon == self.config.weapons[1] \
					and not config.info.max_acc_1:
						percent = 100/self.data.gun_init_stats['acc']*v
						text = obj.actual_weapon+' Accuracy +'+str(percent)+'%'
					elif obj.actual_weapon == self.config.weapons[2] \
					and not config.info.max_acc_2:
						percent = 100/self.data.plasma_init_stats['acc']*v
						text = obj.actual_weapon+' Accuracy +'+str(percent)+'%'
					elif obj.actual_weapon == self.config.weapons[3] \
					and not config.info.max_acc_3:
						percent = 100/self.data.flame_init_stats['acc']*v
						text = obj.actual_weapon+' Accuracy +'+str(percent)+'%'
					else:
						percent = self.get_speed_percent(obj.actual_weapon, v/5)
						text = obj.actual_weapon+' Speed +'+str(percent)+'%'
						# ~ percent = 100/self.data.flame_init_stats['speed']*(v/5)
						# ~ text = obj.actual_weapon+' Speed +'+str(percent)+'%'
				elif k == 'piercing': text = obj.actual_weapon+' Piercing +'+str(v)
				elif k == 'speed mech':
					percent = 100/self.data.player_init_stats['speed']*v
					text = 'Speed Mech +'+str(percent)+'%'
				elif k == 'hp abs':
					if obj.actual_weapon == self.config.weapons[1] \
					and not config.info.max_hp_abs_1:
						text = obj.actual_weapon+' HP Absorption +'+str(v*100)+'%'
					elif obj.actual_weapon == self.config.weapons[2] \
					and not config.info.max_hp_abs_2:
						text = obj.actual_weapon+' HP Absorption +'+str(v*100)+'%'
					elif obj.actual_weapon == self.config.weapons[3] \
					and not config.info.max_hp_abs_3:
						text = obj.actual_weapon+' HP Absorption +'+str(v*100)+'%'
					else:
						if self.data.player.speed < 4:
							percent = 100/self.data.player_init_stats['speed']*v
							text = 'Speed Mech +'+str(percent)+'%'
				elif k == 'hp recovery': text = 'HP Recovery speed -'+str(v)
				elif k == 'sp recovery': text = 'SP Recovery speed -'+str(v)
				else: text = ''
			except KeyError: text = ''
			
			x = self.get_pos_text_center(obj.x, len(text), font, font_size)
			move = (time.perf_counter() - obj.killed_time) * 20
			pos = (x, int( obj.y + (obj.ty/2) - move - add - 75))
			self.draw_text(text,  pos,                 self.config.FONT[font], self.config.COLOR['Negro'])
			self.draw_text(text, (pos[0]-1, pos[1]-1), self.config.FONT[font], self.config.COLOR['Azul Claro'])
			add += 15
	
	def draw_absorption(self, type_):
		
		font_size = int(16*self.scale)
		font = 'Inc-R '+str(font_size)
		
		if type_ == 'player': absorptions = self.data.player.hp_absorb[:]
		
		for i, obj in enumerate(absorptions):
			
			text = '+'+str(round(obj['abs'], 2))
			
			current_time = time.perf_counter() - obj['hit']
			x = self.get_pos_text_center(obj['x'], len(text), font, font_size)
			move = (current_time) * 20
			pos = (x, int( obj['y'] + (obj['ty']/2) - move - 60))
			
			self.draw_text(text,  pos,                 self.config.FONT[font], self.config.COLOR['Negro'])
			self.draw_text(text, (pos[0]-1, pos[1]-1), self.config.FONT[font], self.config.COLOR['Verde Claro'])
			
			if type_ == 'player' and current_time > 1 and self.data.player.hp_absorb:
				self.data.player.hp_absorb.pop(i)
		
		# ~ if type_ == 'player':
			# ~ while None in self.data.player.hp_absorb: self.data.player.hp_absorb.remove(None)
	
	def draw_damage(self, type_):
		
		font_size = int(16*self.scale)
		font = 'Inc-R '+str(font_size)
		
		if type_ == 'enemies': damages = self.damage_on_enemies[:]
		elif type_ == 'boxes': damages = self.damage_on_boxes[:]
		elif type_ == 'player': damages = self.damage_on_player[:]
		
		for i, obj in enumerate(damages):
			
			text = '-'+str(obj['dmg'])
			
			current_time = time.perf_counter() - obj['hit']
			x = self.get_pos_text_center(obj['x'], len(text), font, font_size)
			move = (current_time) * 20
			pos = (x, int( obj['y'] + (obj['ty']/2) - move - 60))
			
			self.draw_text(text,  pos,                 self.config.FONT[font], self.config.COLOR['Negro'])
			self.draw_text(text, (pos[0]-1, pos[1]-1), self.config.FONT[font], self.config.COLOR['Rojo Claro'])
			
			if type_ == 'enemies' and current_time > 1: self.damage_on_enemies[i] = None
			elif type_ == 'boxes' and current_time > 1: self.damage_on_boxes[i] = None
			elif type_ == 'player' and current_time > 1: self.damage_on_player[i] = None
		
		if type_ == 'enemies':
			while None in self.damage_on_enemies: self.damage_on_enemies.remove(None)
		elif type_ == 'boxes':
			while None in self.damage_on_boxes: self.damage_on_boxes.remove(None)
		elif type_ == 'player':
			while None in self.damage_on_player: self.damage_on_player.remove(None)
	
	def get_pos_text_center(self, x, ltext, font, font_size):
		if font.startswith('Retro'): pixels = 3
		if font.startswith('Inc-R'): pixels = 4
		if font.startswith('Wendy'): pixels = 6
		x = x - int( ltext * (font_size/pixels) )
		return x
	
	def draw_text(self, text, pos, font, color):	# Dibuja Texto En Pantalla.
		text = font.render(text, 1, color)		# Se Pasa El Texto Con La Fuente Especificada.
		self.screen.blit(text, pos)					# Se Dibuja En Pantalla El Texto en la Posición Indicada.
	
	def rect_opaco(self, surface, color=(0,0,0), alpha=128): # Rectangulo Opaco, sirve para crear rectangulos transparentes.
		img = pygame.Surface(surface[2:])
		img.set_alpha(alpha)
		img.fill(color)
		self.screen.blit(img, surface[:2])



