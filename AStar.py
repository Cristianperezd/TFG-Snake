
import pygame
from pygame.math import Vector2
import constants
from snake import Snake
from food import Food
import numpy as np
from node import Node
import heapq
import copy
from AStarNode import AStarNode



class AStar:

    def __init__(self,initial_node: AStarNode):
        self.initial_node = initial_node
        self.goal_node = initial_node.food.pos
        self.state = 0
        self.solution = None
        self.counter = 0

        self.exploration_matrix = np.full((25, 25), np.inf)
        self.exploration_matrix_ids = np.full((25, 25),-1, dtype=int)


    def search(self):
        queue = []
        heapq.heappush(queue, self.initial_node)
        visited = []
        explored = 0
        debug_list = []
        while queue:

            """if( explored == 2000 ):
                return 'END'"""
            node = heapq.heappop(queue)
            visited.append(tuple(node.board.flatten()))
            
            if self.is_goal(node):
                #self.goal_node = node
                return self.get_solution(node)
            children = self.expand(node,queue)

            for child in children:
                
                if tuple(child.board.flatten()) not in visited:
                    heapq.heappush(queue, child)
                else:
                    print('repetido')

                #explored = explored + 1
            

        return None
    
    def expand(self,node,queue):
        children = []
        directions = ['UP','DOWN','LEFT','RIGHT']
        for direction in directions :
            if self.is_valid_direction(node,direction):
                new_board,new_snake,new_food = self.simulate_move(node,direction)
                child_node = AStarNode(new_board,new_snake,new_food,node)
                head_pos = (
                    int(new_snake.get_head().y / constants.BLOCK),
                    int(new_snake.get_head().x / constants.BLOCK)
                )

                if self.exploration_matrix[head_pos] >= child_node.cost:
                    temp_queue = []

                    while queue:    
                        new_node = heapq.heappop(queue)
                        if self.exploration_matrix_ids[head_pos] not in new_node.ancestors:
                            temp_queue.append(new_node)
                    

                    # Restaurar los nodos en la heapq
                    for node_temp in temp_queue:
                        heapq.heappush(queue, node_temp)


                    self.exploration_matrix[head_pos] = child_node.cost
                    self.exploration_matrix_ids[head_pos] = child_node.id



                    children.append(child_node)
        return children

    def is_valid_direction(self,node,direction):

        head = node.snake.get_head()
        if direction == 'UP':
            head = Vector2(head.x, head.y - constants.BLOCK)
        elif direction == 'DOWN':
            head = Vector2(head.x, head.y + constants.BLOCK)
        elif direction == 'LEFT':
            head = Vector2(head.x - constants.BLOCK, head.y)
        else:
            head = Vector2(head.x + constants.BLOCK, head.y)
    

        if head.x >= constants.WIDTH or head.x < 0 or head.y >= constants.HEIGHT or head.y < 0:
            return False
        
        if head in node.snake.body[1:]:
            return False
        
        return True

    def simulate_move(self,node,direction):
        new_snake = copy.deepcopy(node.snake)
        new_snake.direction = direction
        new_snake.move()
        new_snake.body.pop()

        new_food = copy.deepcopy(node.food)
        new_board = np.zeros((25,25),dtype=np.int8)

        new_board[int(new_food.pos.y/constants.BLOCK), int(new_food.pos.x/constants.BLOCK)] = 2
        for block in new_snake.body:
            new_board[int(block.y/constants.BLOCK), int(block.x/constants.BLOCK)] = 1

        return new_board, new_snake, new_food
    def get_solution(self,node):
        solution = []
        while node is not None:
            solution.append(node.snake.direction)
            node = node.parent
        solution.reverse()

        return solution
    
    def is_goal(self,node):
        return node.snake.body[0] == node.food.pos