
import json
import os

def save_data(player, verb=True):
	
	data_weapons = {}
	
	for name, weapon in player.weapons.items():
		data = {
			'lvl':   weapon.lvl,			# Weapon level
			'str_':  weapon.str,			# Weapon strenght
			'ammo':  weapon.ammo,			# Ammunition quantity
			'tps':   round(weapon.tps,2),	# Time per shot
			'dofs':  round(weapon.dofs,2),	# Duration of the shot = Range
			'speed': round(weapon.speed,2),	# Shot speed
			'acc':   weapon.accuracy,		# Shot accuracy
			'ps':    weapon.ps				# Piercing strike
		}
		
		data_weapons[name] = data
	
	data_player = {
		'hp':               player.hp,
		'sp':               player.sp,
		'hp_level':         player.hp_level,
		'sp_level':         player.sp_level,
		'money':            player.money,
		'weapons':          data_weapons,
		'speed':            round(player.speed,2),
		'dmg_hp':           player.dmg_hp,
		'resistant_dmg_hp': player.resistant_dmg_hp,
		'hp_time_recovery': round(player.hp_time_recovery,2),
		'sp_time_recovery': round(player.sp_time_recovery,2)
	}
	
	data_player = json.dumps(data_player, indent=4)		# Convierte Dict a JSON String
	
	with open('player.dat', 'w') as file_:
		file_.write(data_player)
		file_.close()
	
	if verb:
		print('\n\n')
		print(data_player)


def load_data(file_name='player.dat', verb=False):
	
	if os.path.isfile(file_name):
		
		with open(file_name, 'r') as file_:
			r = file_.read()
			data = json.loads(r)	# Convierte JSON String a Diccionario.
		
		return data



