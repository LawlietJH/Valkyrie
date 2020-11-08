
import pygame

class EventHandler():
	
	def event_handler(self, config):
		
		for event in pygame.event.get():
		
			if event.type == pygame.QUIT: config.quit = True
			
			elif event.type == pygame.KEYDOWN:
				
				if event.key == pygame.K_ESCAPE: config.pause = True
				
				if   event.key == pygame.K_a: config.dir_l = True
				elif event.key == pygame.K_d: config.dir_r = True
				elif event.key == pygame.K_w: config.dir_u = True
				elif event.key == pygame.K_s: config.dir_d = True
				
				if   event.key == pygame.K_1: config.selected_weapon = 1 if 1 <= config.unlocked_weapons else config.selected_weapon
				elif event.key == pygame.K_2: config.selected_weapon = 2 if 2 <= config.unlocked_weapons else config.selected_weapon
				elif event.key == pygame.K_3: config.selected_weapon = 3 if 3 <= config.unlocked_weapons else config.selected_weapon
				
				elif event.key == pygame.K_j: config.level_up_hp = True
				elif event.key == pygame.K_k: config.level_up_sp = True
				elif event.key == pygame.K_l: config.level_up = True
				
			elif event.type == pygame.KEYUP:
				
				if   event.key == pygame.K_a: config.dir_l = False
				elif event.key == pygame.K_d: config.dir_r = False
				elif event.key == pygame.K_w: config.dir_u = False
				elif event.key == pygame.K_s: config.dir_d = False
				
				elif event.key == pygame.K_j: config.level_up_hp = False
				elif event.key == pygame.K_k: config.level_up_sp = False
				elif event.key == pygame.K_l: config.level_up = False
			
			elif event.type == pygame.MOUSEBUTTONDOWN:
				
				config.mbd = {'pos':event.pos, 'button':event.button, 'active':True}
			
			elif event.type == pygame.MOUSEBUTTONUP:
				
				config.mbd = {'pos':event.pos, 'button':event.button, 'active':False}
				
			elif event.type == pygame.MOUSEMOTION:
				
				config.mouse_pos = pygame.mouse.get_pos()
			
			# ~ elif event.type == pygame.VIDEORESIZE:
				# ~ config.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
