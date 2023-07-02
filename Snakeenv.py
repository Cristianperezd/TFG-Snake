import gymnasium as gym
import sys



from gymnasium import spaces
from pygame.math import Vector2
import constants
from snake import Snake
from food import Food
import numpy as np
import pygame
from color_constants import colors





class SnakeEnv(gym.Env):
    def __init__(self):
        super(SnakeEnv, self).__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=4 , shape=(9,)  , dtype = np.float32)

        



    def step(self,action):




        if action == 0 and self.snake.direction != 'DOWN':
            self.snake.direction = 'UP'
        elif action == 1 and self.snake.direction != 'UP':
            self.snake.direction= 'DOWN' 
        elif action == 2 and self.snake.direction != 'RIGHT':
            self.snake.direction = 'LEFT' 
        elif action == 3 and self.snake.direction != 'LEFT':
            self.snake.direction = 'RIGHT' 

       
        self.snake.move()

      
        #Check collision with the food
        if self.food.detect_collision(self.snake) == False:
            self.snake.body.pop()
        else:
            self.score += 1
            self.reward += 10

           
           
        
        #Check collision with the snake with:
        # Borders
        # Itself
        if self.snake.check_collision() == True:
            self.done = True
            self.reward = -10
        else:
            self.update_board()

        self.info = {}


    

        self.observation = [
        int(self.food.pos.x < self.snake.head.x) ,  # food left
        int(self.food.pos.x > self.snake.head.x) ,  # food right
        int(self.food.pos.y < self.snake.head.y) ,  # food up
        int(self.food.pos.y > self.snake.head.y) ,  # food down
        action                                         ]

        self.observation.extend(self.check_safe_directions())

        self.observation = np.array(self.observation,dtype=np.float32)

        if self.render_mode == 'human':
            self.render()


        return self.observation, self.reward, self.done, False, self.info
    
    def reset(self, seed= None):
        self.snake = Snake()
        self.food = Food()
        self.w = constants.WIDTH
        self.h = constants.HEIGHT
        self.score = 0
        self.done = False


        self.reward = 0
        
        self.board = np.zeros((25,25),dtype=np.int8)

        self.board[int(self.food.pos.y/constants.BLOCK), int(self.food.pos.x/constants.BLOCK)] = 2
        
        self.update_board()
        self.info = {}

        """self.food.pos.x < self.snake.head.x # food left
        self.food.pos.x > self.snake.head.x # food right
        self.food.pos.y < self.snake.head.y  # food up
        self.food.pos.y > self.snake.head.y # food down"""
        #Always first direction is UP which is action 0
        
        self.observation = [
        int(self.food.pos.x < self.snake.head.x) ,  # food left
        int(self.food.pos.x > self.snake.head.x) ,  # food right
        int(self.food.pos.y < self.snake.head.y) ,  # food up
        int(self.food.pos.y > self.snake.head.y) ,  # food down
        0                                          #Always first direction is UP which is action 0
        ]
        self.observation.extend(self.check_safe_directions())

        self.observation = np.array(self.observation,dtype=np.float32)


        if self.render_mode == 'human':
            pygame.init()
            self.display = pygame.display.set_mode((self.w, self.h))
            self.clock = pygame.time.Clock()

            self.render()


        return self.observation, self.info


    def render(self, render_mode='human'):
        """Draw the game objects on the screen"""

        # Fill the display with a brown color
        self.display.fill(colors['brown'][0:3])

        # Draw the snake on the screen
        self.snake.draw(display=self.display)

        self.food.draw(display=self.display)

        pygame.draw.rect(self.display, colors['powderblue'][0:3], pygame.Rect(500, 0, constants.BLOCK, constants.BLOCK))


        """display_surface = pygame.display.get_surface()
        display_surface.blit(pygame.transform.flip(display_surface, True, False), dest = (0,0))"""
        # Update the display
        pygame.display.flip()
        self.clock.tick(60)

    def update_board(self):
        self.board = np.zeros((25,25),dtype=np.int8)
        self.board[int(self.food.pos.y/constants.BLOCK), int(self.food.pos.x/constants.BLOCK)] = 2
        for block in self.snake.body:
            self.board[int(block.y/constants.BLOCK), int(block.x/constants.BLOCK)] = 1

    def check_safe_directions(self):

        directions = ['UP','DOWN','LEFT','RIGHT']
        valids = []
        for direction in directions :
            valid = 1
            head = self.snake.get_head()
            if direction == 'UP':
                head = Vector2(head.x, head.y - constants.BLOCK)
            elif direction == 'DOWN':
                head = Vector2(head.x, head.y + constants.BLOCK)
            elif direction == 'LEFT':
                head = Vector2(head.x - constants.BLOCK, head.y)
            else:
                head = Vector2(head.x + constants.BLOCK, head.y)


            if head.x >= constants.WIDTH or head.x < 0 or head.y >= constants.HEIGHT or head.y < 0:
                valid = 0
            
            if head in self.snake.body[1:]:
                valid = 0

            valids.append(valid)

        return valids

    def close(self):
        pygame.quit()