'''
Class for a snake to be used for a pygame-based snake game.

----------------------
Author: Moritz Gruber
Date:   January 2020
----------------------
'''


import numpy as np
from copy import copy 

class Snake:
    def __init__(self, x=0, y=0):
        """Construct a snake."""

        # create directions (keys) and their corresponding opposites (values)
        self.directions = {'up':'down',
                           'down':'up',
                           'left':'right',
                           'right':'left'}

        # initialize body: initial position and direction
        self.body = [[int(x), int(y)]]  # the body consists of a list of [xpos,ypos]
        self.current_direction = np.random.choice(list(self.directions.keys()))
        
        # set cell size in pixels 
        self.cell_size = 10

    def change_direction(self, direction, return_copy=False):
        """Change direction of snake. If return_copy is True, the function will 
        create a copy of the snake, change its direction and return it without
        affecting the instance the function was called on."""

        if direction not in self.directions:
            raise ValueError(f'Wrong direction. Must be in {list(self.directions.keys())}.')
        
        is_opposite = direction == self.directions[self.current_direction]
        
        # only return a copy of the snake without affecting this instance (for bots)
        if return_copy:
            new_snake = copy(self)
            if not is_opposite:
                new_snake.current_direction = direction 
            return new_snake
        
        # change the direction if applicable
        if not is_opposite:
            self.current_direction = direction

    def move(self, has_eaten=False):
        """
        Move the snake based on the direction. This consists of 2 steps.
            Step 1. Add the new snake head to the body.
            Step 2. If the snake has not grown, delete the last cell.
        """

        # Step 1
        self.body.append(self.next_head_position()) 

        # Step 2
        if not has_eaten:       
            self.body.pop(0) 

    def next_head_position(self):
        """Computes new head position based on current position and direction."""
        
        new_head_cell = self.body[-1][:]  # slice here so as not to bind!!!

        if self.current_direction == 'left':
            new_head_cell[0] -= self.cell_size
        elif self.current_direction == 'down':
            new_head_cell[1] += self.cell_size
        elif self.current_direction == 'right':
            new_head_cell[0] += self.cell_size
        elif self.current_direction == 'up':
            new_head_cell[1] -= self.cell_size
        
        return new_head_cell