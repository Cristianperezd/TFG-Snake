import pygame
from pygame.math import Vector2
import constants
from color_constants import colors
import random






class Food:
    """Class to handle the food rendering, generation and collision check"""

    def __init__(self):
        """ Initializing the snake object """
        self.pos = Vector2(constants.BLOCK,(random.randint(0,(constants.HEIGHT-constants.BLOCK)/constants.BLOCK)*constants.BLOCK))
        

    #Method to generate the new possible cordinates for the food
    def generate(self):
        x = random.randint(0,(constants.WIDTH-constants.BLOCK)/constants.BLOCK)
        y = random.randint(0,(constants.HEIGHT-constants.BLOCK)/constants.BLOCK)
        self.pos = Vector2(x*constants.BLOCK, y*constants.BLOCK)

    #Method to draw the food object in the screen 
    def draw(self,display):

        pygame.draw.rect(display, colors['orangered1'][0:3], pygame.Rect(self.pos.x, self.pos.y, constants.BLOCK, constants.BLOCK))

    #Method to check if the food is inside the snake body
    def inside_collision(self,snake,valid):
        
        if self.pos in snake.body:
            self.generate()
        else:
            valid = True
        
        return valid
    
    #Method to check if snake's head collisioned the food
    def detect_collision(self,snake):


        if snake.head == self.pos:

            self.generate()
            valid = False
            while valid == False:
                valid = self.inside_collision(snake,valid)
            return True
        else:
            return False
                

