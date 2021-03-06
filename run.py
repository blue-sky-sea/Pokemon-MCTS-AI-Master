#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Main exeutable file
"""

# Local imports
from Game.engine.double_battle import Double_Battle as Battle
from Game.engine.single_battle import Single_Battle as Single_Battle
from DataBase.generator_data_base import \
	generate_pokemons, generate_types, generate_moves

# General imports
import argparse

__version__ = '0.5'
__author__  = 'Daniel Alcocer (daniel.alcocer@est.fib.upc.edu)'


"""
Run this code to re-generate the information database of Types, Moves, and
Pokemons, and the image dataset of the pokemon sprites.
"""
def generate_data(args):
	"""
		Args:
			args: parse_args return.

		Action:
			This function call the action indicated in the parameter 'args'.
	"""
	print_name = not args.no_print_name
	start = args.start
	if  args.type or args.all:
		print('Generating types info...')
		generate_types(print_name = print_name)
	if  args.move or args.all:
		print('Generating moves info...')
		generate_moves(start_iteration = start, print_name = print_name)
	if  args.poke or args.all:
		print('Generating pokemons info...')
		generate_pokemons(start_iteration = start, print_name = print_name)
	if  not (args.poke or args.move or args.type or args.all):
		print(	'Specify that you want to generate: --type (-t), --move (-m),'
				' --poke (-p) or --all (-a)')

"""
Main function to execute this program
"""
def main(args):
	"""
		Args:
			args: parse_args return.

		Action:
			This function execute the action indicated in the parameter
			'args.action'.
	"""
	if args.action == 'generate_data': generate_data(args)
	elif args.action == 'play':
		print('Running a battle with a random ally...')
		#开始运行游戏（随机pokemon）
		#Battle在Game.engine.double_battle包中
		Battle(	base_level = args.base_level,
				varability_level = args.var_level).play()
	elif args.action == 'play_with_rand':
		print('Running a battle with a random ally...')
		#开始运行游戏（随机pokemon）
		#Battle在Game.engine.double_battle包中
		Single_Battle(	base_level = args.base_level,
				varability_level = args.var_level).play()
	else: # so do not load tensorflow always
		from Agent.agent_to_play import AgentPlay
		from Agent.model import Model

		model = Model(model_file=args.model_name, log_file=args.log_name)
		if args.action == 'train_model':
			print('Training model...')
			model.train()
			model.save(args.model_name)
			print('Finished')
		elif args.action == 'play_to_eval':
			print('Running a battle with an agent ally...')
			def constructor_agent(role, pokemon):
				return AgentPlay(role, pokemon, model)
			Battle( constructor_trainerA2 = constructor_agent,
					base_level = args.base_level,
					varability_level = args.var_level).play()
		elif args.action == 'eval_agent':
			print('Running random battles to eval an agent')
			print('Not implemeted evaluation yet. Running...')
			def constructor_agent(role, pokemon):
				return AgentPlay(role, pokemon, model)
			wins = 0
			for e in range(args.episodes):
				print('-------------- EPISODE: {}/{} --------------'.format(i,args.episodes))
				battle = Battle(constructor_trainerA2 = constructor_agent,
								base_level = args.base_level,
								varability_level = args.var_level)
				battle.play()
				wins+=battle.winners()
				# More prins por analize
			print('WINS: {}/{} = {}'.format(wins,args.episodes,wins/args.episodes))

		else: # Training actions
			from Game.engine.core.pokemon import Pokemon
			from Agent.agent_to_train import AgentTrain
			from Agent.environment import Environment

			def poke_rand(): return Pokemon.Random(args.base_level, args.var_level)
			agent = AgentTrain('Ally_1', poke_rand(), model)
			def constructor_agent(role, pokemon): return agent

			if args.action == 'play_to_train':
				from Game.engine.trainerInput import TrainerInput
				print('Running a battle to train an agent')
				constructor_trainerA1 = TrainerInput
			elif args.action == 'train_agent':
				from Game.engine.trainer import TrainerRandom
				print('Running random battles to train an agent')
				constructor_trainerA1 = TrainerRandom
			for i in range(args.episodes):
				print('-------------- EPISODE: {}/{} --------------'.format(i,args.episodes))
				Environment(constructor_trainerA1 = constructor_trainerA1,
							constructor_trainerA2 = constructor_agent,
							base_level = args.base_level,
							varability_level = args.var_level).play()
				agent.replay(poke_rand())
				agent.save_model()


if __name__ == '__main__':
	#主函数入口，从这里开始执行代码
	"""
		Main function of this funcionality.
	"""
	#可能的动作参数
	possible_actions = ['generate_data','play', 'play_with_rand', 'play_to_eval', \
					  	'play_to_train', 'eval_agent', 'train_agent', \
						'train_model']
	#本游戏名称与介绍
	program_name = 'Pokémon Game'
	desc =  '这是一个模拟口袋妖怪1v1对战的python程序，将会运用到MCTS算法构建AI '
	'''
	desc =  'This is a program to play a Double Battle Pokémon with an ally ' +\
			'Pokémon played by an artificial intelligence created with deep ' +\
			'reinforcement learning technics'
	'''

	#参数介绍，可通过python run.py -h 获取详细的参数介绍
	desc_actions = 'Argument to indicate the main action. --------------- ' +\
	' ______________________________________________________'+\
	'"generate_data": This action allows to rebuild information of type, move'+\
	' and/or pokemon from PokeAPI (https://pokeapi.co/). '+\
	' ------------------------------- ' +\
	' ______________________________________________________'+\
	'"play_with_rand": This action executes a battle with a random ally to ' +\
	'evaluate its correct performance. '+\
	' ----- ' +\
	' ______________________________________________________'+\
	'"play_to_eval": This action runs a battle with an agent as ally for the '+\
	'manual evaluation of the model. '+\
	' ______________________________________________________'+\
	'"play_to_train": Executa N battles in which the agent learns from each ' +\
	'of them by playing with the player. '+\
	' - ' +\
	' ______________________________________________________'+\
	'"eval_agent": Executes N battles played by a random and an agent to ' +\
	'evaluate the performance of the model. '+\
	' ______________________________________________________'+\
	'"train_agent": Executes N battles played by a random and an agent to ' +\
	'train the model. '+\
	' --------------------- ' +\
	' ______________________________________________________'+\
	'"train_model": Trains a model with saved information of other games.'
	#parser为参数集合
	parser = argparse.ArgumentParser(prog = program_name, description=desc)
	parser.add_argument('action', choices=possible_actions,
						default = 'play_to_eval', help=desc_actions)
	# Arguments for generate_data
	parser.add_argument('--type', '-t', action='store_true',
						help='Param for "generate_data" action. ' +\
						'Flag to generate type\'s info')
	parser.add_argument('--move', '-m', action='store_true',
                   		help='Param for "generate_data" action. ' +\
						'Flag to generate move\'s info')
	parser.add_argument('--poke', '-p', action='store_true',
                  		help='Param for "generate_data" action. ' +\
						'Flag to generate pokemon\'s info')
	parser.add_argument('--all' , '-a', action='store_true',
                   		help='Param for "generate_data" action. ' +\
						'Flag to generate all the information')
	parser.add_argument('--no_print_name' , action='store_true',
                   		help='Param for "generate_data" action. ' +\
						'Flag to not print the name of the data')
	parser.add_argument('--start' , '-s', type=int, default = 0,
                   		help='Param for "generate_data" action. ' +\
						'Number of the starter iteration')
	# Arguments for play
	parser.add_argument('--log_name' , '-log', default = None,
						help='Param for agent actions. ' +\
						'Name of the log file to use/create')
	parser.add_argument('--model_name' , '-model', default = None,
						help='Param for agent actions. ' +\
						'Name of the model to use/create')
	parser.add_argument('--episodes' , '-e', type = int, default = 5,
						help='Param for agent train actions. ' +\
						'Number of battles to play')
	parser.add_argument('--base_level' , '-bl', type = int, default = 50,
						help='Param for battle actions. ' +\
						'Base level of each pokemon')
	parser.add_argument('--var_level' , '-vl', type = int, default = 0,
						help='Param for battle actions. ' +\
						'Varability for pokemon\'s level (lvl = Base +/- Var)')
	#将参数传入main函数，执行程序
	main(parser.parse_args())
