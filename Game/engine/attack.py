#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Module that contains the Attack class.
This class is used to make an attack between two pokemons and it also hurts the
defender pokemon with the calcualted damage.

This module contains the following class:

	Attack

It also includes this function:

	with_prob_of
"""

# Local imports
from Configuration.settings import Attack_Config

# General imports
from random import randint, uniform
from math import floor
from copy import deepcopy as copy

__version__ = '1.0'
__author__  = 'Daniel Alcocer (daniel.alcocer@est.fib.upc.edu)'


"""
	Return True with a certain probability
"""
def with_prob_of(prob):
	"""
		Args:
			prob ('int'): The probability of True, value between (0,100).

		Return ('bool'):
			True with probability 'prob'.
			Note: With a 'prob' = 100 already exists a 1/100 probability of
				  False, only with 'prob' = None a True is always guaranteed.
	"""
	if prob == None: return True
	return uniform(0,100) < prob


"""
	Class to make an attack.
"""
class Attack:
	def __init__(self, poke_attacker, poke_defender, move):
		"""
			Args:
				poke_attacker (class:'Pokemon'): The Pokémon that makes the
												 attack.
				poke_defender (class:'Pokemon'): The Pokémon that receives the
												 attack.
				move (class:'Move'): The Move that the 'poke_attacker' uses in
									 the attack.

			Action:
				Create and execute the attack and save relevant information
				about it.
		"""
		self.poke_attacker = copy(poke_attacker)
		self.poke_defender = copy(poke_defender)
		self.move = move
        
		self.dmg = 0
		self.has_pp = move.can_use()
		if not self.has_pp: self.missed_attack = False
		else:
			self.missed_attack = not with_prob_of(move.accuracy()) \
								 or self.poke_defender.is_fainted()
			if not self.missed_attack:
				move.use()
				self.calc_damage(poke_attacker, poke_defender, move)
				#print(" 招式造成的的伤害为",end="")
				#print(self.dmg)
				poke_defender.hurt(self.dmg)

		self.poke_defender_after = copy(poke_defender)


	"""
		Calculate the damage of this attack.
	"""
	def calc_damage(self, poke_attacker, poke_defender, used_move):
		"""
			Args:
				poke_attacker (class:'Pokemon'): The Pokémon that makes the
												 attack.
				poke_defender (class:'Pokemon'): The Pokémon that receives the
												 attack.
				used_move (class:'Move'): The Move that the 'poke_attacker' uses
										   in the attack.

			Action:
				Calculate the damage of this attack and save relevant
				information about it.
				计算伤害，记录相关
		"""

		sp = 'special-' if used_move.damage_class() == 'special' else ''
		a = (0.2*poke_attacker.level()+1) * poke_attacker.get_stat(sp+'attack')
		a *= used_move.power()#(0.2*等级+1）*攻击力*技能power
		d = 25*poke_defender.get_stat(sp+'defense')#25*防御
		typeMove = used_move.type()
		self.efectivity = typeMove.multiplier(poke_defender.types())
		bonification  = typeMove.bonification(poke_attacker.types())
		#print("self.efectivity * bonification",self.efectivity , bonification)
		self.dmg = (a/d + 2) * self.efectivity * bonification#伤害为

		# Randoms factors
		"""if Attack_Config["USE_VARABILITY"]:
			varability = randint(85,100)
			self.dmg *=  (0.01*varability)"""
		self.is_critic = False
		"""if Attack_Config["USE_CRITIC"]:
			# Always at least 0.01% of not critic
			self.is_critic =  with_prob_of(used_move.prob_critic())
			if self.is_critic: self.dmg *= 1.5 #Gen VI"""

		self.dmg = floor(self.dmg)

