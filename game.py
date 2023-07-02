import pygame
from pygame.math import Vector2
import constants
from snake import Snake
from food import Food
import numpy as np
from GBFS import GBFS
from node import Node
from AStarNode import AStarNode

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

        #0 for nothing
        #1 for snake
        #2 for food
        self.board = np.zeros((25,25),dtype=np.int8)

        self.board[int(self.food.pos.y/constants.BLOCK), int(self.food.pos.x/constants.BLOCK)] = 2
        
        self.update_board()
        
    def update_board(self):
        self.board = np.zeros((25,25),dtype=np.int8)
        self.board[int(self.food.pos.y/constants.BLOCK), int(self.food.pos.x/constants.BLOCK)] = 2
        for block in self.snake.body:
            self.board[int(block.y/constants.BLOCK), int(block.x/constants.BLOCK)] = 1

    def draw(self):
        """Draw the game objects on the screen"""

        # Fill the display with a brown color
        self.display.fill(colors['brown'][0:3])

        # Draw the snake on the screen
        self.snake.draw(display=self.display)

        self.food.draw(display=self.display)

        pygame.draw.rect(self.display, colors['powderblue'][0:3], pygame.Rect(500, 0, constants.BLOCK, constants.BLOCK))

        # Crear un objeto de fuente
        font = pygame.font.Font(None, 36)
        # Renderizar el texto de la puntuación
        score_text = font.render("Score: " + str(self.score), True, colors['white'])
        # Copiar el texto en la pantalla
        self.display.blit(score_text, (10, 10))
 

        pygame.display.flip()

    def step(self,gbfs = False,initial_state = None, greedybfs = None):
        """Update the game state for one frame"""

        # Process Pygame events
        for event in pygame.event.get():
            # Quit the game if the user closes the window
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if gbfs == False:
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
        
        if gbfs and greedybfs.state == 0:
            
            node_origin = AStarNode(self.board,self.snake,self.food)

            greedybfs.reset(node_origin)

            greedybfs.solution = greedybfs.search()


            if greedybfs.solution == 'END' or greedybfs.solution is None:
                return self.score
            greedybfs.solution.pop(0)
            greedybfs.state = 1
            i = len(greedybfs.solution)
            greedybfs.counter = 0
            #print(greedybfs.solution)


        if gbfs and greedybfs.state == 1:
            self.snake.direction = greedybfs.solution[greedybfs.counter]
            greedybfs.counter = greedybfs.counter + 1

        self.snake.move()

        #print(self.score)
        
        #print(self.food.pos.x/constants.BLOCK)
        """print(self.board)
        print(self.food.pos.x/constants.BLOCK, self.food.pos.y/constants.BLOCK)"""

        

        #Check collision with the food
        if self.food.detect_collision(self.snake) == False:
            self.snake.body.pop()
        else:
           self.score += 1
           if gbfs:
               greedybfs.state = 0
           
        self.update_board()
        #Check collision with the snake with:
        # Borders
        # Itself
        if self.snake.check_collision() == True:
            pygame.quit()
            quit()
            return self.score


        # Draw the game objects on the screen
        self.draw()

        # Control the frame rate of the game
        self.clock.tick(30)

        # Return a value to indicate the game should continue
        return 0
