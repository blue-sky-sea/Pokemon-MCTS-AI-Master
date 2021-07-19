#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math
import random
import numpy as np

AVAILABLE_CHOICES = [1, -1, 2, -2]
AVAILABLE_CHOICE_NUMBER = len(AVAILABLE_CHOICES)
MAX_ROUND_NUMBER = 10

class Node(object):
	def __init__(self):
		self.parent = None
		self.children=[]
		self.visit_times=0
		self.quality_value = 0.0
		self.state=None
	def set_state(self,state):
		self.state = state
	def get_state(self):
		return self.state
	def set_parent(self,parent):
		self.parent = parent
	def get_parent(self):
		return self.parent
	def set_children(self,children):
		self.children = children
	def get_children(self):
		return self.children
  	def get_visit_times(self):
   		return self.visit_times
	def set_visit_times(self, times):
		self.visit_times = times
	def visit_times_add_one(self):
		self.visit_times +=1
	def get_quality_value(self):
		return self.quality_value
	def set_quality_value(self, value):
		self.quality_value = value
	def quality_value_add_n(self,n):
		self.quality_value +=n
	def is_all_expand(self):
		if len(self.children)==AVAILABLE_CHOICE_NUMBER
			return True
		else:
			return False
	def add_child(self,sub_node):
		sub_node.set_parent(self)
		self.children.append(sub_node)
	def __repr__(self):
		return "Node:{},Q/N:{}/{},state:{}".format(hash(self),self.quality_value,self,visit_times,self.state)

class State(object):#某游戏的状态，例如模拟一个数相加等于1的游戏
	def __init__(self):
		self.current_value=0.0#当前数
		self.current_round_index=0#第几轮
		self.cumulative_choices = []#选择过程记录
	def is_terminal(self):#判断游戏是否结束
		if self.current_round_index = MAX_ROUND_NUMBER-1
			return True
		else:
			return False
	def compute_reward(self):#当前得分，越接近1分值越高
		return -abs(1-self.current_value)
	def set_current_value(self,value):
		self.current_value=value
	def set_current_round_index(self,round):
		self.current_round_index=round
	def set_cumulative_choices(self,choices):
		self.cumulative_choices=choices
	def get_next_state_with_random_choice(self):#得到下个状态
		random_choice=random.choice([choice for choice in AVAILABLE_CHOICES])
		next_state=State()
		next_state.set_current_value(self.current_value+random_choice)
		next_state.set_current_round_index(self.current_round_index+1)
		next_state.set_cumulative_choices(self.cumulative_choices+[random_choice])
		return next_state
def monte_carlo_tree_search(node):#蒙特卡洛树搜索总函数
	computation_budget=1000
	for i in range(computation_budget):
		expend_node = tree_policy(node)
		reward = default_policy(expand_node)
		backup(expand_node,reward)
	best_next_node = best_child(node,False)
	return best_next_node
def best_chile(node,is_exploration):#若子节点都扩展完了，求UCB值最大的子节点
	best_score=-sys.maxize
	best_sub_node = None
	for sub_node in node.get_children():
		if is_exploration:
			C=1/math.sqrt(2.0)
		else:
			C=0.0
		left=sub_node.get_quality_value()/sub_node.get_visit_times()
		right=2.0*math.log(node.get_visit_times())/sub_node.get_visit_times()
		score=left+C*math.sqrt(right)
		if score>best_score:
			best_sub_node = sub_node
	return best_sub_node
def expand(node):#得到未扩展的子节点
	tried_sub_node_states= [sub_node.get_state() for sub_node in node.get_children()]
	new_state = node.get_state().get_next_state_with_random_choice()
	while new_state in tried_sub_node_states:
		new_state=node.get_state().get_next_state_with_random_choice()
	sub_node=Node()
	sub_node.set_state(new_state)
	node.add_child(sub_node)
	return sub_node
def tree_policy(node):#选择子节点的策略
	while node.get_state().is_terminal()==False:
		if node.is_all_expand():
			node=best_child(node,True)
		else:
			sub_node = expand(node)
			return sub_node
	return node
def defaut_policy(node):
	current_state = node.get_state()
	while current_state.is_terminal==False:
		current_state = current_state.get_next_state_with_random_choice()
	final_state_reward=current_state.compute_reward()
	return final_state_reward
def backup(node,reward):
	while node != None:
		node.visit_times_add_one()
		node.quality_value_add_n(reward)
		node = node.parent

