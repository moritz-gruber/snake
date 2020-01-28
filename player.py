'''
A base class for snake player bots and several derived example players below.

----------------------
Author: Moritz Gruber
Date:   January 2020
----------------------
'''

import pygame 
import numpy as np
from time import time 
import operator
import NeuralNetwork as NN


class BasePlayer:

    """
    Parent class for snake player bots.
    Create a class that inherits from this one and modify the my_bot method.
    See examples below this class definition.
    """
    
    def __init__(self):
        """Constructs the Player."""
        self.permissible_actions = ('up', 'down', 'left', 'right', None)
        self.bot_name = 'template'
    
    def __repr__(self):
        """Repr method simply returns bot name."""
        return self.bot_name

    def __call__(self, App):
        """
        Make the class callable such that it can be stored directly to App.player.
        The Player instance will be called within the game loop.
        This function does 2 things.
            1. Call the Player.my_bot function to come up with an action based on some model.
            2. Trigger the corresponding keystrokes, e.g. "W" for "up".
        """

        # Call the my_bot method to determine an action based on the game state
        action = self.my_bot(App)

        # check the output
        
        if action not in self.permissible_actions:
            raise ValueError(f'Invalid action. Make sure it is in {self.permissible_actions}')
            
        # translate action into a keystroke to control the game
        self._generate_wasd_keystrokes(action)

        pygame.time.wait(20)

    def my_bot(self, App):
        """
        Function that implements the bot, i.e., the function that takes the game state as input
        and returns an action to be taken. The output must be either
        'up', 'down', 'left', 'right', or None.
        """

        # ------------------------------------------------------------------------------------
        # NOTE: you will need to overwrite this method when creating an inheriting class 
        # the code below is intended only for instructional purpuses 
        # see examples below this class definition
        # ------------------------------------------------------------------------------------

        ### get input from the App object

        # Most importantly, the snake itself.
        # check out the Snake class in snake.py to see the attributes you might want to use 
        # snake.current_direction and snake.body will be the most relevant 
        snake = App.snake 
        
        # food position
        food_pos = App.food_pos

        # grid corners: (top left, bottom left, top right, bottom right)
        grid_corners = ((App.margin_left, App.margin_top),\
                        (App.margin_left, App.margin_top+App.grid_size[1]), \
                        (App.margin_left+App.grid_size[0], App.margin_top), \
                        (App.margin_left+App.grid_size[0], App.margin_top+App.grid_size[1]))
        
        # the scores can be extracted from App.score

        # default: wait for human keystrokes by setting action to None 
        action = None

        return action 

    def _generate_wasd_keystrokes(self, action):
        """Tranforms the action provided into a keystroke to control the game."""

        if action is None:
            return

        actions_and_keystrokes = {'up':    ('w', pygame.K_w),
                                  'down':  ('s', pygame.K_s),
                                  'left':  ('a', pygame.K_a),
                                  'right': ('d', pygame.K_d)}
        
        # create the event based on the action 
        keypress = pygame.event.Event(pygame.KEYDOWN, unicode=actions_and_keystrokes[action][0],
                                     key=actions_and_keystrokes[action][1], mod=pygame.KMOD_NONE) 
        # add the event to the queue
        pygame.event.post(keypress) 

# -------------------------------------------------------------------------------
# ----------------------- write your own bots below -----------------------------
# -------------------------------------------------------------------------------

class HumanPlayer(BasePlayer):
    def __init__(self):
        super().__init__()
        self.bot_name = 'human'

    def my_bot(self, App): 
        """Returning none means the app only reacts to human-triggered keystrokes."""
        return None 


class RandomPlayer(BasePlayer):
    def __init__(self):
        super().__init__()
        self.bot_name = 'random'

    def my_bot(self, App):
        """This bot chooses a random command at every step."""
        return np.random.choice(self.permissible_actions)


class SimplePlayer(BasePlayer):
    
    def __init__(self):
        super().__init__()
        self.bot_name = 'simpleBot'

    def my_bot(self, App):
        """This bot finds the quickest way to the food."""

        ### Get relevant info from game
        food_pos = App.food_pos
        head_pos = App.snake.body[-1]
        
        current_direction = App.snake.current_direction

        ### Find best direction
        directions = list(App.snake.directions.keys())

        # make dict to store direction evaluation: 
        # 1 - distance to food decreases
        # 2 - distance to food remains equal
        # 3 - distance to food grows
        # 4 - death or opposite to current direction

        direction_evaluation = {key: None for key in App.snake.directions.keys()}

        for proposed_choice in directions:

            # create a fictional snake that changes direction according to the choice    
            new_snake = App.snake.change_direction(proposed_choice, return_copy=True)
            
            # is the choice viable?
            will_die = App._check_death(snake=new_snake) 
            is_opposite = proposed_choice in new_snake.directions[current_direction]

            if will_die or is_opposite:
                direction_evaluation[proposed_choice] = 4
                continue 
            
            # are we getting closer to food?
            distance_delta = manhattan_distance(food_pos, head_pos) - manhattan_distance(food_pos, new_snake.next_head_position())

            # if we are, rate it 1 
            if distance_delta > 0:
                direction_evaluation[proposed_choice] = 1
            
            # if the distance remains equal, rate it 2 
            elif distance_delta == 0:
                direction_evaluation[proposed_choice] = 2

            # if we are getting further away, rate it 3 
            elif distance_delta < 0:
                direction_evaluation[proposed_choice] = 3
        
        # select choice with the lowest value
        best_choice = min(direction_evaluation.items(), key=operator.itemgetter(1))[0]
        return best_choice

def manhattan_distance(a,b):
    """Computes the manhattan distance between two points a and b given as lists or tuples."""
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def obstacle_distance(body,App):
        """Returns the distance in units App.grid_size to the closest obstacle in every direction"""
        head=body[-1]
        if len(body)==1:
            l_dist=(head[0]-App.margin_left)
            r_dist=(App.grid_size[0]+App.margin_left-head[0])
            u_dist=(head[1]-App.margin_top)
            d_dist=(App.margin_top+App.grid_size[1]-head[1])
            return l_dist/App.grid_size[0],r_dist/App.grid_size[0],u_dist/App.grid_size[1],d_dist/App.grid_size[1]
        

        body_obstacles_l=np.where((body[:-1][1]==head[1] & body[:-1][0]<head[0]),body)
        body_obstacles_r=np.where((body[:-1][1]==head[1] & body[:-1][0]>head[0]),body)
        body_obstacles_u=np.where((body[:-1][0]==head[0] & body[:-1][1]>head[1]),body)
        body_obstacles_d=np.where((body[:-1][0]==head[0] & body[:-1][1]<head[1]),body)

        l_dist=min(head[0]-App.margin_left,min(head[0]-body_obstacles_l))
        r_dist=min(App.grid_size[0]+App.margin_left-head[0],min(body_obstacles_r-head[0]))
        u_dist=min(head[1]-App.margin_top,min(head[1]-body_obstacles_u))
        d_dist=min(App.margin_top+App.grid_size[1]-head[1],min(body_obstacles_d-head[1]))

        return l_dist/App.grid_size[0],r_dist/App.grid_size[0],u_dist/App.grid_size[1],d_dist/App.grid_size[1]

class DarwinSnake(BasePlayer):

    def __init__(self,Net):
        super().__init__()
        self.bot_name = 'DarwinSnake'
        self.Net=Net
        self.last_action=0
        self.changes=-1

    def my_bot(self, App):
        snake = App.snake
        food_pos = App.food_pos
        body=snake.body
        l_dist,r_dist,u_dist,d_dist=obstacle_distance(body,App)
        food_pos_x=(food_pos[0]-App.margin_left)/App.grid_size[0]
        food_pos_y=(food_pos[1]-App.margin_top)/App.grid_size[1]
        head_x=(body[-1][0]-App.margin_left)/App.grid_size[0]
        head_y=(body[-1][1]-App.margin_top)/App.grid_size[1]
        ins=np.array([l_dist,r_dist,u_dist,d_dist,food_pos_x,food_pos_y,head_x,head_y])
        self.Net.input=ins
        #print("Inputs: "+str(ins))
        output=self.Net.forward()[-1]
        new_action=self.permissible_actions[np.argmax(output)]
        if self.last_action!=new_action:
            self.changes+=1
        self.last_action=new_action
        return new_action