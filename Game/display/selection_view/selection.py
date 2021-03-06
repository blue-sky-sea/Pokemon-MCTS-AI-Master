#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Module that contains several classes related to the function of selecting from
the window.
Basically, Selection_Manager is the main class to generate the section for the
selection, and Selection_Display is a general class useful for the three types
of possible screens to show as selection, i.e Selection_Move, Selection_Target
and Selection_None

It contains the following class:

	Selection_Manager
    Selection_Display
    Selection_Move
    Selection_Target
    Selection_None
"""

# Local imports
from Configuration.settings import Directory, Display_Config, Select_Config
from Game.display.image import Image, Display
from Game.display.display_RL_info.moves_display import Move_Info
from .button import Button_Move, Button_Target, Button_Cancel
from .selector import Selector

__version__ = '0.7'
__author__  = 'Daniel Alcocer (daniel.alcocer@est.fib.upc.edu)'


"""
    Class to display the selection section and manage their mode,
    i.e. MODE_MOVE, MODE_TARGET and MODE_OFF.
"""
class Selection_Manager:
    def __init__(self,state):
        """
            Args:
                state ('dict of class:Pokemon'): A dictionary with all the
    											 information needed to display
                                                 the a battle.
    				Note: This dict have as key: "Ally_0","Ally_1","Foe_0" and
    					  "Foe_1" with the corresponding pokemon.
            Action:
                Create a manager of the modes of the action selection section
                of the window.
        """
        self.modes = {
          #技能的选择集合
          "MODE_MOVE":  Selection_Move(state["Ally_0"],state),
          #"MODE_TARGET":Selection_Target(state["Foe_0"],state["Foe_1"]),
          #技能施放的目标的选择集合
          "MODE_TARGET":Selection_Target(state["Foe_0"]),

          "MODE_OFF":   Selection_None()
        }
        self.change_mode('MODE_OFF')

    """
        Get the index of the button currently selected by the active sector.
		[0,3] buttons, [4] cancel. This function may also return None depending
		on the implementation of the class.
    """
    def get_selected(self):
        return self.active_mode.get_idx_selected()

    """
        Gets the index of the button clicked of the active selection.
		[0,3] buttons, [4] cancel or None if no button has been clicked.
		(tuple:('int','int') --> 'int')
    """
    def click_at(self, mouse):
        return self.active_mode.click_at(mouse)

    """
        Returns True if the current mode is 'name_mode', False otherwise.
		('str' --> 'bool')
    """
    def in_mode(self, name_mode):
        return self.mode == name_mode

    """
        Change to the 'name_mode' mode.
		('str' --> '')
    """
    def change_mode(self,name_mode):
        self.mode = name_mode
        self.active_mode = self.modes[name_mode]
        if name_mode != "MODE_OFF": self.selector = self.active_mode.selector
        self._visualize_items = [self.active_mode]

    """
    	Funcion to display the current selection section.
    """
    def display(self,SCREEN):
        self.active_mode.display(SCREEN)

"""
	General class to display the selection section.
"""
class Selection_Display(Display):
	def __init__(self, background_name, buttons):
		"""
			Args:
				background_name ('str'): The key in the Directory corresponding
				 						 to the name of the selection
										 background image file.
				buttons ('list of class:Button'): The buttons of this Selection.

			Action:
				Create an extension of the "Display" class to display the
				selection section of the game. Includes its own selector.
		"""
		height = Display_Config['BATTLE_SIZE'][1]+Display_Config['LOG_SIZE'][1]
		bg = Image(Directory[background_name],top_left_location=(0,height))
		visualize_items = [bg]
		self.buttons = buttons
		for button in self.buttons: visualize_items.append(button)
		
		if not 'EMPTY' in background_name:
			#创建一个选择器，用于显示选择（跳动的红色边框）
			self.selector = Selector(not 'TARGET' in background_name)
			visualize_items.append(self.selector)

		#下方技能/技能施放对象显示，根据传入的参数不同，显示不同的格式
		Display.__init__(self, visualize_items)

	"""
		Gets the index of the button currently selected. [0,3] buttons,
		[4] cancel. This function may also return None depending on the
		implementation of the class.
	"""
	def get_idx_selected(self):
		return self.selector.get_selection()

	"""
		Gets the index of the button clicked. [0,3] buttons, [4] cancel or None
		if no button has been clicked.
		(tuple:('int','int') --> 'int')
	"""
	def click_at(self, mouse):
		for i, button in enumerate(self.buttons):
			if button.point_inside(mouse): return i
		return None

"""
	Extended class from Selection_Display to display the move selection section.
"""
class Selection_Move(Selection_Display):
	def __init__(self, pokemon, state=None):
		"""
			Args:
				pokemon (class:'Pokemon'): The pokemon whose movements will be
										   shown.
				state ('dict of class:Pokemon'): A dictionary with all the
    											 information needed to display
                                                 the a battle.

			Action:
				Create an extension of the "Selection_Display" class to show
				the moves of 'pokemon'.
				用于显示口袋妖怪的技能，是Selection_Display的扩展
		"""
		moves = pokemon.moves()
		if Display_Config['SHOW_EFF']:
			buttons = []
			#types = [state['Foe_0'].types(),state['Foe_1'].types()]
			types = [state['Foe_0'].types()]
			for i in range(0,4):
				move = moves[i] if i<len(moves) else None
				mo_in = Move_Info('POS_MOVE_'+str(i), move)
				mo_in.set_type_enemies(types)
				buttons.append(mo_in)
		else:
			buttons = [
			    Button_Move('POS_MOVE_'+str(i), moves[i] if i<len(moves) else None)
			    for i in range(0,4)]
		Selection_Display.__init__(self,'SELECT_MOVE_FILE', buttons)

"""
	Extended class from Selection_Display to display the target selection
	section.
"""
class Selection_Target(Selection_Display):
	def __init__(self, target_0):
		"""
			Args:
				target_0 (class:'Pokemon'): The first enemy pokemon.
				target_1 (class:'Pokemon'): The second enemy pokemon.

			Action:
				Create an extension of the "Selection_Display" class to show
				the possible targets that can be attacked.
				用于显示技能施放的目标，是Selection_Display的扩展
		"""
		buttons = [ Button_Target('POS_MOVE_0', target_0),
					Button_Target('POS_MOVE_1', None),
		    		#Button_Target('POS_MOVE_1', target_1),
		    		Button_Target('POS_MOVE_2', None),
		    		Button_Target('POS_MOVE_3', None),
		    		Button_Cancel() ]
		Selection_Display.__init__(self, 'SELECT_TARGET_FILE', buttons)

"""
	Class extended from Selection_Display to display a void selection section.
"""
class Selection_None(Selection_Display):
	def __init__(self):
		"""
			Args: -

			Action:
				Create an extension of the "Selection_Display" class to not show
				any option / button, and not perform any action (i.e. keyboard
				or mouse). Just implement the functions to not rise the
				NotImplementedError.

			无可选择项显示的情况，防止rise错误提示
		"""
		Selection_Display.__init__(self,'SELECT_EMPTY_FILE', [])

	"""
		The reimplementation of the function to not do anything.
	"""
	def get_move_selected(self):
		return None

	"""
		The reimplementation of the function to not do anything.
	"""
	def click_at(self, mouse):
		return None
