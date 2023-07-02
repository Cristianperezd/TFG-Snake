from game import Game
from GBFS import GBFS
from AStar import AStar

from AStar_copy import AStarCo

from node import Node
from GBFSNode import GBFSNode
from AStarNode import AStarNode



if __name__ == '__main__':
    """game = Game()
    
    # game loop

    
    mode = 1

    if mode == 0:
        initial_state = GBFSNode(game.board,game.snake,game.food)
        greedybfs = GBFS(initial_state)
        counter = 0
    else:
        initial_state = AStarNode(game.board,game.snake,game.food)
        greedybfs = AStar(initial_state)
        counter = 0
    while True:
        score = game.step(True,initial_state,greedybfs)
        if score > 0:
            print(score)
            exit()
"""
    """results = []
    for i in range(50):
        game = Game()
        initial_state = GBFSNode(game.board,game.snake,game.food)
        greedybfs = GBFS(initial_state)
        counter = 0
        score = 0
        while score <= 0 :
            score = game.step(True,initial_state,greedybfs)
        
        results.append(score)
        print('end game: ', i)"""
    
    """results = []
    for i in range(20):
        game = Game()
        initial_state = AStarNode(game.board,game.snake,game.food)
        greedybfs = AStar(initial_state)
        counter = 0
        score = 0
        while score <= 0 :
            score = game.step(True,initial_state,greedybfs)
        
        results.append(score)
        print('end game: ', i)"""
    results = []
    for i in range(50):
        game = Game()
        initial_state = AStarNode(game.board,game.snake,game.food)
        greedybfs = AStarCo(initial_state)
        counter = 0
        score = 0
        while score <= 0 :
            score = game.step(True,initial_state,greedybfs)
        
        results.append(score)
        print('end game: ', i)
        print('Score: ', score)

    # Media
    media = sum(results) / len(results)
    print("Media:", media)

    # Mínimo y máximo
    minimo = min(results)
    maximo = max(results)
    print("Mínimo:", minimo)
    print("Máximo:", maximo)

    

    



