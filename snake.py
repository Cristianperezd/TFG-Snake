import pygame
from pygame.math import Vector2
import constants
from color_constants import colors






class Snake:
    """Class to handle the snake rendering and movement"""

    
    def __init__(self):
        """ Initializing the snake object """

        # Setting the initial direction of the snake
        self.direction = 'UP'
        
        # Setting the initial position of the snake's head
        self.head = Vector2(constants.WIDTH // 2, constants.HEIGHT // 2)
        
        # Setting the initial positions of the snake's body
        self.body = [self.head, Vector2(self.head.x, self.head.y - constants.BLOCK), Vector2(self.head.x, self.head.y - (2 * constants.BLOCK))]

    # Method to draw the snake on the display
    def draw(self, display):
        
        # Looping through each block of the snake's body
        for index, block in enumerate(self.body):
            if index == 0:
                # Drawing the head of the snake with a different color
                pygame.draw.rect(display, colors['chartreuse4'][0:3], pygame.Rect(block.x, block.y, constants.BLOCK, constants.BLOCK))
            else:
                # Drawing the rest of the snake's body
                pygame.draw.rect(display, colors['chartreuse1'][0:3], pygame.Rect(block.x, block.y, constants.BLOCK, constants.BLOCK))

    # Methods to move the snake in different directions
    def move_up(self):
        self.head = Vector2(self.head.x, self.head.y - constants.BLOCK)
        
    def move_down(self):
        self.head = Vector2(self.head.x, self.head.y + constants.BLOCK)
        
    def move_left(self):
        self.head = Vector2(self.head.x - constants.BLOCK, self.head.y)
        
    def move_right(self):
        self.head = Vector2(self.head.x + constants.BLOCK, self.head.y)

    # Method to move the snake based on its current direction
    def move(self):
        
        if self.direction == 'UP':
            self.move_up()
        elif self.direction == 'DOWN':
            self.move_down()
        elif self.direction == 'LEFT':
            self.move_left()
        elif self.direction == 'RIGHT':
            self.move_right()

        # Adding the new head to the beginning of the snake's body list
        self.body.insert(0, self.head)