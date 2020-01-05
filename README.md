# snake
An implementation of snake in pygame including a framework for custom player bots. 

### Requirements
This code was tested on python 3.7.1 on MAC OS 10.14.5 using pygame 1.9.6.

## Description
The repo contains 3 files. 

* `snake.py` contains a class that describes the snake itself
* `player.py` contains a template class for players and some examples
* `snake-game.py` contains the actual game

To run the game, execute
```
$ python snake-game.py
```
By default, the code is set to human players. 
Different players can be supplied in the `App.__init__` method in `snake-game.py`. 

## How to create your own bot

1. Briefly familiarize yourself with the `Snake` class in `snake.py`
2. If you are new to pygame, try to understand some of its key principles (the loop, events, rendering) and how they are applied in `snake-game.py`
3. Go to `player.py`, read the code, create a class that interhits from `Player` and implement the `my_bot` method.
4. In `snake-game.py`, in `App.__init__` set `self.player` to an instance of your newly create player class. 
5. Launch the game and see how it performs! 

