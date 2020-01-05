'''
Module that implements the snake game using pygame. 
You can play it using the WASD keys by running 

$ python snake_game.py 

A framework is provided to create your own player BOT.
Have a look at player.py and take it away!

Author: Moritz Gruber
Date: Jan 2020

------------------------------------------------------------------
TBD:
- keep track of the number of games and remember highscores, 
  implement returning the highscores and saving them to player
  attribute and then to pkl
- extend the framework to allow for the training of a genetic algo
    * need to be able to record thousands of bots and their scores
'''


import pygame
from snake import Snake
from player import HumanPlayer, SimplePlayer
from copy import copy
import numpy as np
from time import time 


class App:
    """This is the game itself."""

    def __init__(self):
        """Constructor for the game."""

        # Initialize game state
        self._running = True
        self._display_surf = None

        # Initialize key graphical parameters
        self.background = None
        self.window_size = 420, 500
        self.grid_size = self.xdim, self.ydim = 400, 400 
        self.margin_top = 90
        self.margin_left = self.margin_right = self.margin_bottom = 10
        self.cell_size = 10

        # Set player. This is where bot methods can be supplied. 
        self.player = SimplePlayer()

        # Initialize game parameters
        self.step_duration = 30  # step duration in ms
        
    def on_init(self):
        """Initial game setup."""
        
        # Initialize pygame (I have no idea what this does)
        pygame.init()
        print('Welcome to Le Serpent! Use WASD keys to play.')
        pygame.display.set_caption('Le Serpent')

        # Start a new game
        self._new_game()

        # Initialize graphical elements
        self._display_surf = pygame.display.set_mode(self.window_size, pygame.HWSURFACE)
        self.background = pygame.Surface(self.grid_size)
        self._running = True
        self.cell = pygame.Surface((self.snake.cell_size,self.snake.cell_size))
        self.cell_image = copy(self.cell)
        self.cell_image.fill((255,255,255))
        self.head_image = copy(self.cell)
        self.head_image.fill((255,0,0))
        self.food_image = copy(self.cell)
        self.food_image.fill((0,255,0))

        # Tell the on_execute method that everything is fine
        return True 

    def _new_game(self):
        """Routine to start a new game."""
        # Create and place snake
        xpos = np.random.randint(self.margin_left, self.grid_size[0]+self.margin_left-self.cell_size)
        ypos = np.random.randint(self.margin_top,  self.grid_size[0]+self.margin_top-self.cell_size)
        self.snake = Snake(round(xpos, -1), round(ypos, -1))  # round to nearest 10 (snake cell size)
        self.timer = time()
        self.score = {'food_eaten':0, 'mean steps per food':' '}
        self.will_die = False 
        self.iteration = 1
        self.mean_steps_per_food = '-'

        # Create and place food
        self._place_food()   
    
    def _place_food(self):
        """Place a food cell somewhere on the canvas, ensuring it does not spawn directly
        on the snake."""
        
        # Find a suitable position
        while True:
            # Generate random position within grid
            xpos = np.random.randint(self.margin_left, self.grid_size[0]+self.margin_left-10)
            ypos = np.random.randint(self.margin_top,  self.grid_size[0]+self.margin_top-10)
            new_food_pos = [round(xpos, -1), round(ypos, -1)]
            
            # Check if overlaps with the snake body
            if new_food_pos not in self.snake.body:
                self.food_pos = new_food_pos
                break

    def _check_will_eat(self):
        """Returns True if the snake head will land on a food cell in the next step and carries
        out appropriate actions."""

        if self.snake.next_head_position() == self.food_pos:
            # Place new food 
            self._place_food()
            
            # Update mean steps per food score
            self.mean_steps_per_food = round((self.iteration+1)/(self.score['food_eaten']+1),2)
            return True

        else:
            return False 
    
    def _check_death(self, snake=None):
        """Returns True if the snake dies in the next iteration."""
        
        # Select which snake to check
        if snake is not None:
            if not isinstance(snake, Snake):
                raise ValueError(f'snake needs to be Snake.snake, not {type(snake)}.')
            snake_to_check = snake
        else:
            snake_to_check = self.snake

        # Get next head position
        head_x, head_y = snake_to_check.next_head_position()
        
        # Check death criteria
        outside_bounds =  head_x >= self.grid_size[0]+self.margin_left or head_x < self.margin_left or \
                          head_y >= self.grid_size[0]+self.margin_top or head_y < self.margin_top
        eats_itself = [head_x, head_y] in snake_to_check.body  
        death = outside_bounds or eats_itself 
            
        return death 

    def _update_score(self):
        self.score['food_eaten'] = len(self.snake.body)-1 
        self.score['mean steps per food'] = self.mean_steps_per_food

    def on_event(self, event):
        """Captures keyboard events and executes the corresponding methods."""

        # quit the game
        if event.type == pygame.QUIT:
            print("Au revoir!")
            self._running = False
        
        # change direction
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.snake.change_direction('up')
            elif event.key == pygame.K_s:
                self.snake.change_direction('down')
            elif event.key == pygame.K_a:
                self.snake.change_direction('left')
            elif event.key == pygame.K_d:
                self.snake.change_direction('right')

    def on_loop(self):
        """This loop runs over and over while the game is running."""

        # Listen for player inputs and execute corresponding moves 
        try:
            tstart = time()

            self.player(App=self)  # refer to Player.__call__ to understand this

            if 1000*(time()-tstart) > (self.step_duration*0.75):
                print('Your bot takes dangerously long. Try making it faster or increasing the step duration.')

        except:
            print(f'There was a critical error in {self.player.bot_name}.\nExiting game.')
            self._running = False

        # Execute queued keystrokes
        for event in pygame.event.get():
            self.on_event(event)

        # If a new step was reached, check death and move to next step
        if 1000*(time()-self.timer) >= self.step_duration:
            
            # Check if death will occur
            self.will_die = self._check_death()
            
            # move to next iteration
            self.iteration += 1
            self.timer = time()
            self.snake.move(has_eaten=self._check_will_eat())
            
            # Check if death has occurred
            if self.will_die:
                print(f'You lost! You got {self.score["food_eaten"]} food with an average of {self.score["mean steps per food"]} steps per food.')
                pygame.time.wait(3000)
                self._new_game()
                return 

        # Update score 
        self._update_score()

    def on_render(self):
        """This method draws the goings on in the game backend onto the screen."""

        # Fill the display with black
        self._display_surf.fill((0,0,0))

        # Draw the title
        font = pygame.font.Font('freesansbold.ttf', 32)
        title_text = font.render('Le Serpent', True, (0,255,0))
        title_rect = title_text.get_rect() 
        title_rect.topleft = (self.margin_left, 10)
        self._display_surf.blit(title_text, title_rect) 

        # Draw the score
        score_str_all = [f'Food eaten: {self.score["food_eaten"]}', f'Mean steps per food:  {self.score["mean steps per food"]}']
        for idx, score_str in enumerate(score_str_all):
            score_text = pygame.font.Font('freesansbold.ttf', 14).render(score_str, True, (255,255,255))    
            score_rect = score_text.get_rect()
            score_rect.topleft = (self.margin_left,50+idx*20)        
            self._display_surf.blit(score_text, score_rect)

        # Draw the player name
        player_str = f'Player: {self.player.bot_name}'
        font = pygame.font.Font('freesansbold.ttf', 12)
        player_text = font.render(player_str[:40], True, (255,0,0))
        player_rect = player_text.get_rect() 
        player_rect.bottomleft = (210, 85)
        self._display_surf.blit(player_text, player_rect) 


        # Draw the border 
        pygame.draw.rect(self._display_surf,(255,255,255),pygame.Rect(self.margin_left, self.margin_top, self.grid_size[0], self.grid_size[1]), 2)

        # Draw the food
        if self.food_pos is not None:
            self._display_surf.blit(self.food_image,(self.food_pos))

        # Draw the snake
        for idx, cell in enumerate(self.snake.body):
            # if its the head (last cell in self.snake.body), make it red
            if idx == len(self.snake.body)-1:
                self._display_surf.blit(self.head_image,(cell[0],cell[1]))
            else:
                self._display_surf.blit(self.cell_image,(cell[0],cell[1]))
        
        # Make it happen
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        """Method that runs when the module is launched."""
        if self.on_init() == False:
            self._running = False
 
        while self._running:
            # Run the main loop
            self.on_loop()
            
            # Render the graphics
            self.on_render()

        # Pack up and leave
        self.on_cleanup()
            

if __name__ == "__main__" :
    the_game = App()
    the_game.on_execute()