#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Module that contains the Double_Battle class.
This class is the principal class to execute a battle in the game.

It contains the following class:

	Double_Battle
"""

# Local imports
from Configuration.settings import Sentence, Display_Config
from Game.display.window import Window
from AI.mcts import MCTS
from AI.mcts import State

from .core.pokemon import Pokemon
from .trainer import TrainerRandom
from .trainerInput import TrainerInput

from .attack import Attack
from Agent.agent_to_play import AgentPlay

from threading import Thread
import threading
import time

__version__ = '0.7'
__author__  = 'Daniel Alcocer (daniel.alcocer@est.fib.upc.edu)'


"""
	Class to make a double battle.
"""
class Single_Battle:
	def __init__(self, constructor_trainerA1 = TrainerInput,
					   constructor_trainerF1 = TrainerRandom,
					   pokemon_trainerA1 = None,
				   	   pokemon_trainerF1 = None,
				 	   base_level = 50,
					   varability_level = 50):
		"""
			Args:
				trainerA1 (class:'Trainer'): The allied trainer 1 (the user's
											 trainer).
				trainerF1 (class:'Trainer'): The enemy trainer 1.
				
				base_level ('int'): The base level of the pokemons if necessary
				  					to create them.
				varability_level ('int'): The varaiability of the base level of
										  the pokemons if necessary to create
										  them.

			Action:
				Create and execute the attack and save relevant information
				about it.
		"""
		#我的pokemon（随机生成）
		if pokemon_trainerA1==None:
			pokemon_trainerA1 = Pokemon.Random(base_level, varability_level)
		trainerA1 = constructor_trainerA1("Ally_0", pokemon_trainerA1)
		#对手的pokemon（随机生成）
		if pokemon_trainerF1==None:
			pokemon_trainerF1 = Pokemon.Random(base_level, varability_level)
		trainerF1 = constructor_trainerF1("Foe_0", pokemon_trainerF1)
		
		#self._trainers = [trainerA1,trainerA2,trainerF1,trainerF2]
		self._trainers = [trainerA1,trainerF1]
		#state存着2只pokemon的object，类型为字典
		self.state = {t.role: t.pokemon() for t in self._trainers}
		#print(self.state[0].)
		#self.state['use_agent'] = isinstance(trainerA2, AgentPlay)
		self.state['use_agent'] = False
		self.show_message = None
		self.n_turn = 0#回合计数器
		for t in self._trainers:
			#如t的类型是trainerInput，那么set_state就是初始化整个游戏界面
			t.set_state(self.state)

			if isinstance(t, TrainerInput):	
				self.show_message = t.show_message
				#print(self.show_message,"MIUZKIYUTA")

	"""
		Function to play the battle
	"""
	def play(self):
		print("-------------- NEW BATTLE --------------")
		#显示游戏界面
		self.show('START', *[t.pokemon().name() for t in self._trainers],\
					time=Display_Config['FIRST_TIME_STEP'])

		#每一回合判断是否游戏结束
		while not self.is_finished():
			print("--------------- NEW TURN: {} ---------------".format(self.n_turn))
			self.doTurn()
		print("------------- BATTLE ENDED -------------")
		self.show_result()


	"""
		Function to display a message
	"""
	#time是显示的时间，时间结束message消失
	def show(self, name, *args, time=Display_Config['TIME_STEP']):
		#显示战斗解说log
		text = Sentence[name].format(*args)#从json中取
		print(text) # To have a "log"
		if self.show_message != None: self.show_message(text,time)


	"""
		Function to display as a message the result of an attack
	"""
	def show_attack(self, attack):
		p = attack.poke_attacker
		if not p.is_fainted():
			eb = attack.poke_defender
			ea = attack.poke_defender_after
			name_p = p.name()
			name_e = eb.name()
			name_m = attack.move.name()
			self.show('USE_ATTACK', name_p, name_m, name_e)

			if eb.is_fainted(): self.show('TARGET_FAINTED', name_e)
			elif not attack.has_pp: self.show('NO_PP_LEFT', name_p, name_m)
			elif attack.missed_attack: self.show('MISS_ATTACK', name_p)
			else: # Show results of the attack
				if   attack.efectivity == 4: self.show('EFECTIVITY_x4')
				elif attack.efectivity == 2: self.show('EFECTIVITY_x2')
				elif attack.efectivity == 0.5: self.show('EFECTIVITY_x05')
				elif attack.efectivity == 0.25: self.show('EFECTIVITY_x025')
				elif attack.efectivity == 0: self.show('EFECTIVITY_x0')
				if attack.is_critic: self.show('CRITIC_ATTACK')
				if ea.is_fainted(): self.show('DEAD_POKEMON', name_e)

	"""
		Function to show the result of the battle if the battle is finished.
	"""
	def show_result(self):
		if self.is_finished:
			winners = [ tr.pokemon().name()
						for tr in self._trainers
						if not tr.pokemon().is_fainted()]
			if len(winners) == 2: self.show("WINNERS", *winners)
			if len(winners) == 1: self.show("WINNER", *winners)
			self.show("WIN" if self.winners() else "LOSE", \
						time=Display_Config['LAST_TIME_STEP'])

	"""
		Return True if the battle is finished, False otherwise.
		('' --> 'bool')
	"""
	def is_finished(self):
		fainteds = list(map(lambda tr:tr.pokemon().is_fainted(),self._trainers))
		#return (fainteds[0] and fainteds[1]) or (fainteds[2] and fainteds[3])
		return fainteds[0] or fainteds[1]

	"""
		Returns True if the battle is won by the Ally team, False if the battle
		is won by the Foe team, or None otherwise.
		('' --> 'bool')
	"""
	def winners(self):
		if self.is_finished:
			for tr in self._trainers:
				if not tr.pokemon().is_fainted(): return tr.is_ally()
		else: return None

	"""
		Function to obtain the priority of a trainer depending on the selected
		action and the speed of its pokemon.
		(class:'Trainer' --> 'int')
	"""
	def attack_order(self, trainer):
		pk = trainer.pokemon()		# When two moves have the same priority,
		move, _ = trainer.action()	# the users' Speed statistics will determine
		priority = move.priority()	# which one is performed first in a battle
		return priority*1000 + pk.get_stat('speed')

	def choiceActions(self):
			# choice actions
			live_trainers = []
			for trainer in self._trainers:
				if not trainer.pokemon().is_fainted():
					#选择出招，trainerInput类型(也就是我本人)会在面板中选择出招，
					#trainerRandom类型的（也就是随机玩家，在trainer.py中有定义）会随机选一个招式打向随机玩家（1v1中对手必定打向我本人）
					trainer.choice_action()
					live_trainers.append(trainer)

			#计算攻击顺序
			tr_sort = sorted(live_trainers, key=self.attack_order, reverse=True)
			self.last_attacks = {}

			# do actions
			for trainer in tr_sort:
				if self.is_finished(): break
				poke = trainer.pokemon()
				if not poke.is_fainted(): # If fainted during this turn
					move, target = trainer.action()

					#攻击的敌人
					pk_enemy = self._trainers[target].pokemon()
					#执行攻击命令，计算攻击效果
					attack = Attack(poke, pk_enemy, move)
					self.last_attacks[trainer.role]=attack
					#在控制台和面板上显示攻击
					self.show_attack(attack)
	"""
		Function to do a turn, i.e. Ask for an action (choice_action function)
		for each trainer, and execute the action in the corresponding order.
	"""
	def doTurn(self):
		if not self.is_finished():
			#回合计数器加1
			self.n_turn+=1

			#MCTS计算出招获胜概率，提供参考
			trainers=[]
			import copy 
			i=0
			for t in self._trainers:
				role="Ally_0"
				if(i==1):
					role="Foe_0"
				newtrainer=TrainerRandom(role, copy.deepcopy(t._pk))
				trainers.append(newtrainer)
				i=i+1
			
			mcts = MCTS(trainers=trainers)
			pokemon1=trainers[0]._pk
			pokemon2=trainers[1]._pk
			initialstate=State(pokemon1,pokemon2)
			#initialstate.getPossibleActions()
			action = mcts.search(initialState=initialstate)
			move_index=int(action/10)-1
			print("MIZUKIYUTA应该选择：",pokemon1._moves[move_index]._name)
			#t1.start()
			#TODO


			self.choiceActions()



