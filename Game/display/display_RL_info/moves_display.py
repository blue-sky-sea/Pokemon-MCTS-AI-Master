#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Module that contains the Moves_display class.
This class is the principal class to disply moves.

It contains the following classes:

	Moves_display
	Move_Info
"""

# Local imports
from Configuration.settings import Directory, Display_Config, Select_Config
from Game.display.image import Image, Display
from Game.display.selection_view.button import Button_Move
from Game.display.utils_display import scale, shift
from Game.display.font import Font

# 3rd party imports
from pygame import Rect, draw

__version__ = '0.5'
__author__  = 'Daniel Alcocer (daniel.alcocer@est.fib.upc.edu)'


"""
	Class to display information about moves.
"""
class Moves_display(Display):
	def __init__(self, state):
		"""
			Args:
				state ('dict of class:Pokemon'): A dictionary with all the
												 information needed to display
												 the a battle.

			Action:
				Create a display to show the moves of 'pokemon'.
		"""
		width, height = Display_Config['BATTLE_SIZE']
		height+= Display_Config['LOG_SIZE'][1]
		visualize_items = [Image(Directory['SELECT_MOVE_FILE'], (width,height))]
		#我方的pokemon
		pokemon = state['Ally_1']
		#types = [state['Foe_0'].types(),state['Foe_1'].types()]
		#敌人的属性
		types = [state['Foe_0'].types()]
		moves = pokemon.moves()
		for i in range(0,4):
			m_info = Move_Info('POS_MOVE_'+str(i), \
									moves[i] if i<len(moves) else None, width)
			m_info.set_type_enemies(types)
			visualize_items.append(m_info)
		Display.__init__(self, visualize_items)

"""
	Extended class from Button_Move to display more info of a move.
"""
class Move_Info(Button_Move):
	def __init__(self, position_name, move, vertical_shift = 0):
		"""
			Args:
				position_name ('str'): The key to obtain the position.
				move (class:'Move'): The move to be displayed by the button.
				vertical_shift ('int'): Vertical shift where display the button

			Action:
				Create an extencion of 'Button' to show relevant information
				abount 'move'.
		"""
		#显示技能的详细信息，包括伤害P、命中概率A、物理还是特殊攻击Ph.\Sp.
		
		Button_Move.__init__(self, position_name, move, vertical_shift)
		x,y = scale(shift(self.location_pre_scale, Select_Config['SHIFT_RECT_EFF']))
		width, height = scale(Select_Config['SIZE_RECT_EFF'])

		# Create rectangles
		# 创建放置技能的矩形
		width_1 = width/2
		self.bar_0 = Rect(x, y, width_1, height)
		self.bar_1 = Rect(x+width_1, y, width_1, height)
		y += height + scale([1,Select_Config['V_SPACE_RECTS']])[1]
		self.bar_2 = Rect(x, y, width, height)
		#Create text effectiveness
		text_shift = shift( Select_Config['SHIFT_RECT_EFF'],\
							Select_Config['SHIFT_TEXT_EFF'])
		self.text_0 = Font(self.location_pre_scale, text_shift)
		text_shift_1 = shift(text_shift,[Select_Config['SIZE_RECT_EFF'][0]/2,0])
		self.text_1 = Font(self.location_pre_scale, text_shift_1)
		#Create text info move
		aux = Select_Config['SIZE_RECT_EFF'][1] + Select_Config['V_SPACE_RECTS']
		text_shift_2 = shift(text_shift,[-Select_Config['SHIFT_TEXT_EFF'][0]/2,aux])
		self.text_2 = Font(self.location_pre_scale, text_shift_2)
		#Set text info move
		string_pattern = 'P: {pow}  A: {acc}  {tp}'

		#伤害
		pow = self.obj.power()
		#命中概率
		acc = self.obj.accuracy() if self.obj.accuracy() != None else '-'
		#攻击类型：物理攻击or特殊攻击
		dmg_class = ' Sp.' if self.obj.damage_class() == 'special' else 'Ph.'

		string = string_pattern.format(pow=pow,acc=acc,tp=dmg_class)
		#print(string,"$$$$1234")
		self.text_2.set_text(string)

	"""
		Set enemies types to calculate effectiveness
	"""
	def set_type_enemies(self,types):
		#技能下方显示技能的有效倍数
		effectiveness_0 = int(self.obj.type().multiplier(types[0])*100)
		#effectiveness_1 = int(self.obj.type().multiplier(types[1])*100)
		pattern = Select_Config['EFFECTIVENESS_TO_COLOR_PATTERN']
		self.color_name_0 = Select_Config[pattern.format(str(effectiveness_0))]
		#self.color_name_1 = Select_Config[pattern.format(str(effectiveness_1))]
		self.text_0.set_text('x'+str(float(effectiveness_0)/100.0))
		#self.text_1.set_text('x'+str(float(effectiveness_1)/100.0))

	"""
		Funcion to display this button.
	"""
	def display(self,SCREEN):
		Button_Move.display(self,SCREEN)
		draw.rect(SCREEN, Display_Config[self.color_name_0], self.bar_0)
		#draw.rect(SCREEN, Display_Config[self.color_name_1], self.bar_1)
		draw.rect(SCREEN, Display_Config['GRAY'], self.bar_2)
		self.text_0.display(SCREEN)
		self.text_1.display(SCREEN)
		self.text_2.display(SCREEN)
