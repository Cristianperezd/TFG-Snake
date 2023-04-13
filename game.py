import pygame
from pygame.math import Vector2
import constants
from snake import Snake
from food import Food

import os
import time
from color_constants import colors

pygame.init()

class Game:
    """Class to handle the game logic and rendering"""

    def __init__(self):
        """Initialize the game"""

        # Set the width and height of the game window
        self.w = constants.WIDTH
        self.h = constants.HEIGHT

        # Create a Pygame display surface
        self.display = pygame.display.set_mode((self.w, self.h))

        # Fill the display with a brown color
        self.display.fill(colors['brown'][0:3])

        # Create a Pygame clock object to control the frame rate
        self.clock = pygame.time.Clock()

        # Set the initial score to zero
        self.score = 0

        # Create a Snake object to represent the player
        self.snake = Snake()
        self.food = Food()

    def draw(self):
        """Draw the game objects on the screen"""

        # Fill the display with a brown color
        self.display.fill(colors['brown'][0:3])

        # Draw the snake on the screen
        self.snake.draw(display=self.display)

        self.food.draw(display=self.display)

        pygame.draw.rect(self.display, colors['powderblue'][0:3], pygame.Rect(500, 0, constants.BLOCK, constants.BLOCK))

        # Update the display
        pygame.display.flip()

    def step(self):
        """Update the game state for one frame"""

        # Process Pygame events
        for event in pygame.event.get():
            # Quit the game if the user closes the window
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Change the snake direction based on key input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != 'DOWN':
                    self.snake.direction = 'UP'
                elif event.key == pygame.K_DOWN and self.snake.direction != 'UP':
                    self.snake.direction = 'DOWN'
                elif event.key == pygame.K_LEFT and self.snake.direction != 'RIGHT':
                    self.snake.direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and self.snake.direction != 'LEFT':
                    self.snake.direction = 'RIGHT'

        # Move the snake

        self.snake.move()

        
        


        
        #Check collision with the food
        if self.food.detect_collision(self.snake) == False:
            self.snake.body.pop()
        else:
           self.score += 1

        #Check collision with the snake with:
        # Borders
        # Itself
        if self.snake.check_collision() == True:
            pygame.quit()
            quit()

        
        # Draw the game objects on the screen
        self.draw()

        # Control the frame rate of the game
        self.clock.tick(10)

        # Return a value to indicate the game should continue
        return 0
