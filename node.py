import pygame
from pygame.math import Vector2
import constants
from snake import Snake
from food import Food
import numpy as np



class Node:
    node_count = 0

    def __init__(self,board,snake: Snake,food: Food,parent = None):
        self.id = Node.node_count 
        Node.node_count += 1
        self.board = board
        self.snake = snake
        self.food = food
        self.h = self.calculate_h()
        self.parent = parent
        self.children = []
        
        self.ancestors = parent.ancestors[:] if parent else []  # Lista de ancestros del nodo actual
        if parent:
            self.ancestors.insert(0, parent.id)
        

        self.g = self.acumlate_g()
        self.cost = self.h + self.g
        """print('h: ', self.h)
        print('cost: ', self.cost)"""

    def acumlate_g(self):
            if self.parent is not None:
                 return self.parent.g + 1
            else:
                 return 1

    def calculate_h(self):
        head = self.snake.get_head()
        return abs(head.x - self.food.pos.x) + abs(head.y - self.food.pos.y)

