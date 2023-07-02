
import pygame
from pygame.math import Vector2
import constants
from snake import Snake
from food import Food
import numpy as np
from node import Node
import heapq
import copy


class GBFSNode(Node):
    def __lt__(self, other):
        return self.h < other.h