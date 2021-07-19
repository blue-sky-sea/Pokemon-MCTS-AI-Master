#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math
import random
import numpy as np
from Game.engine.trainer import TrainerRandom
from Game.engine.trainerInput import TrainerInput
from threading import Thread
import time
# General imports
from random import randint
from Game.engine.attack import Attack
import copy 


def randomPolicy(state):
	"""isTerminal,whowin=state.isTerminal()
	while not isTerminal:
		try:
			action = random.choice(state.getPossibleActions())
		except IndexError:
			raise Exception("Non-terminal state has possible actions")
		state = state.takeAction(action)"""
	return state.getReward()

class State():
	def  __init__(self,pokemon1,pokemon2):
		self.Ally_pokemon = pokemon1
		self.Foe_pokemon =  pokemon2
	def getPossibleActions(self):
		#pp不足的也要，但是后面的计算不会击中，相当于miss
		possibleActions = []
		i=0
		j=0
		for move1 in self.Ally_pokemon._moves:
			i=i+1
			j=0
			for move2 in self.Foe_pokemon._moves:
				j=j+1
				mark=i*10+j
				#print(move1._name,move2._name,mark)
				possibleActions.append(Action(move1,1,move2,0,mark))#（1v1中target0是我，1是敌人）
		return possibleActions
	def isTerminal(self):
		"""
		检查是否有玩家获胜
		"""
		if self.Ally_pokemon.is_fainted():
			return True,-1#输了
		elif self.Foe_pokemon.is_fainted():
			return True,1#赢了
		else:
			return False,0

	def getReward(self):
		isTerminal,flag = self.isTerminal()
		#print("getReward-flag:",flag)
		return flag
	def takeAction(self,action):
		newstate = copy.deepcopy(self)
		#计算出完招后产生的局面
		#TODO
		##出招顺序可能不同，所以很难判断,所以我给出的解决方法是双方同时随机选择一个出招，然后计算结果(即游戏的一回合当作一步棋)
		live_trainers=[]

		order1=action.Ally_move.priority()*1000+self.Ally_pokemon.get_stat('speed')
		order2=action.Foe_move.priority()*1000+self.Foe_pokemon.get_stat('speed')

		#print("takeAction:",pokemontest._pokemonname,"hp:",pokemontest._health) 
		tr_sort=[]
		flag=0
		if(order1>order2):
			tr_sort=[self.Ally_pokemon,self.Foe_pokemon]
		if(order1<order2):
			tr_sort=[self.Foe_pokemon,self.Ally_pokemon]
			flag=1
		else:
			if(randint(0,1)): tr_sort=[self.Ally_pokemon,self.Foe_pokemon]
			else:
				tr_sort=[self.Foe_pokemon,self.Ally_pokemon]
				flag=1
		#flag==1,敌人先出招；flag==0，我先出招
		#print("出招顺序：",tr_sort[0]._pokemonname,tr_sort[1]._pokemonname)
		target=0
		for pokemon in tr_sort:
			isTerminal,f=self.isTerminal()
			if isTerminal==True: break
			if not pokemon.is_fainted(): # If fainted during this turn
				pk_enemy=None
				if(flag==0):
					move=action.Ally_move
					target=1
					#攻击的敌人
					pk_enemy = newstate.Foe_pokemon
					flag=flag+1
				elif(flag==1):
					move=action.Foe_move
					target=0
					#攻击的敌人
					flag=flag-1
					pk_enemy = newstate.Ally_pokemon
				print("mcts模拟：",move._name,target,"模拟攻击后——")
				#执行攻击命令，计算攻击效果
				attack = Attack(pokemon, pk_enemy, move)
				#print("模拟攻击后——",pk_enemy._pokemonname,"受到",attack.dmg)

		return newstate

class Action():
	def __init__(self, move1, target1,move2,target2,mark):
		self.Ally_move = move1
		self.Ally_target = target1
		self.Foe_move = move2
		self.Foe_target = target2
		self.mark=mark
	def databack():
		return self.Ally_move,self.Ally_target,self.Foe_move,self.Foe_target

class treeNode(object):
	def __init__(self,state,parent):
		self.parent = parent #当前节点的父节点
		self.children = {}#存action,以mark:action的字典形式存在

		self.state = state#即trianers集合
		self.isTerminal,flag= state.isTerminal() #代表当前的状态是否是终结态

		self.isFullyExpanded = self.isTerminal #节点是否完全扩展

		self.numVisits = 0 #节点被访问的次数
		self.totalReward = 0 #获取的奖励，如果我们定义1为胜利，0为失败，那么我们在上文中定义的3/4之类就可以表达为totalReward/numVisits


class MCTS(Thread):
	def __init__(self,timeLimit=10000,
				iterationLimit=None,
				explorationConstant=1/math.sqrt(2),
				rolloutPolicy=randomPolicy,trainers=None):
		super().__init__()
		print("MCTSAI init success")

		newtrainers = copy.deepcopy(trainers)
		i=0
		self.Foe_action_flag=[0,0,0,0]#记录是否已知敌人的技能，已知为1，不知为0
		
		live_trainers = []

		for trainer in newtrainers:
			pokemontest=trainer.pokemon()
			print(pokemontest._pokemonname,"hp:",pokemontest._health) 
		print("###############################################")
		
		if timeLimit != None:
			if iterationLimit != None:
				raise ValueError("Cannot have both a time limit and an iteration limit")
			# time taken for each MCTS search in milliseconds
			self.timeLimit = timeLimit
			self.limitType = 'time'
		else:
			if iterationLimit == None:
				raise ValueError("Must have either a time limit or an iteration limit")
			# number of iterations of the search
			if iterationLimit < 1:
				raise ValueError("Iteration limit must be greater than one")
			self.searchLimit = iterationLimit
			self.limitType = 'iterations'
		self.explorationConstant = explorationConstant
		self.rollout = rolloutPolicy

	#从根结点往下走
	def select(self,  node, explorationValue):
		bestValue = float("-inf")
		bestNodes = []
		for child in node.children.values():
			nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
				2 * math.log(node.numVisits) / child.numVisits) # UCB公式
			print("子结点胜利估计:",child.totalReward / child.numVisits)
			if nodeValue > bestValue:
				bestValue = nodeValue
				bestNodes = [child]
			elif nodeValue == bestValue:
				bestNodes.append(child)

		return random.choice(bestNodes)  # 如果有多个节点值相等，从中随机选择一个。

	#state要实现的几个方法，getPossibleActions,takeAction
	def expand(self, node):
		isTerminal,whowin=node.state.isTerminal()
		if(isTerminal==True):
			return self.getBestChild(node, self.explorationConstant)
		else:
			actions=node.state.getPossibleActions()
			for action in actions:
				if action.mark not in node.children:
					newstate=node.state.takeAction(action)
					newNode = treeNode(newstate,node)
					node.children[action.mark] = newNode
					if len(actions) == len(node.children):
						#4个技能*4个技能即16种可能组合，children最多16个
						node.isFullyExpanded = True
					return newNode
		raise Exception("Should never reach here")

	def search(self, initialState):
		self.root = treeNode(initialState, None)#根据当前局面产生根节点
		if self.limitType == 'time':
			timeLimit = time.time() + self.timeLimit / 1000
			while time.time() < timeLimit:
				self.executeRound()#执行一轮模拟
		else:
			for i in range(self.searchLimit):
				self.executeRound()

		#时间结束，取最好的child返回action
		bestChild = self.getBestChild(self.root, 0)
		action = self.getAction(self.root, bestChild)
		#print("最好的结果：",action," *********MIZUKIYUTA********")
		for mark,node in self.root.children.items():
			move_index1=int(mark/10)-1
			move_index2=mark-(move_index1+1)*10-1
			#print(move_index1,move_index2)
			print("[", initialState.Ally_pokemon._moves[move_index1]._name,"-",
				 initialState.Foe_pokemon._moves[move_index2]._name,
				"]"," 总共访问了",node.numVisits,"次，reward为",node.totalReward)
		return action

	#模拟
	def executeRound(self):
		node = self.selectNode(self.root)#这里有问题，在terminal 的时候返回了None
		if(node is None):
			print("executeRound selectNode获得了一个None")
		else:
			print("executeRound select 正常")
			print("————————————————————————")

		reward = self.rollout(node.state)#...?
		self.backpropogate(node, reward)#回溯更新

	def selectNode(self, node):
		while not node.isTerminal:
			if node.isFullyExpanded:
				node = self.getBestChild(node, self.explorationConstant)
			else:
				return self.expand(node)#这里有问题，在terminal 的时候返回了None

		return node

	def backpropogate(self, node, reward):
		while node is not None:
			node.numVisits += 1
			node.totalReward += reward
			node = node.parent

	def getBestChild(self, node, explorationValue):
		bestValue = float("-inf")
		bestNodes = []
		for child in node.children.values():
			nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
				2 * math.log(node.numVisits) / child.numVisits)
			if nodeValue > bestValue:
				bestValue = nodeValue
				bestNodes = [child]
			elif nodeValue == bestValue:
				bestNodes.append(child)
		return random.choice(bestNodes)

	def getAction(self,root,bestChild):
		for action,node in root.children.items():
			if node is bestChild:
				return action

	def __str__(self):
		return "MCTS-AI-MIZUKIYUTA"

###
'''
		m = MCTS(timeLimit=30000,rolloutPolicy=weightPolicy)
		action = m.search(initialState=state)
'''
###

