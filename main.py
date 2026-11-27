"""Run the A* agent and print score statistics."""
from astar import AStar
from astar_node import AStarNode
from game import Game

N_GAMES = 50


def play_game():
    game = Game()
    agent = AStar(AStarNode(game.board, game.snake, game.food))
    score = 0
    while score <= 0:
        score = game.step(agent)
    return score


if __name__ == '__main__':
    results = []
    for i in range(N_GAMES):
        score = play_game()
        results.append(score)
        print(f'Game {i + 1}: score {score}')

    print('Mean:', sum(results) / len(results))
    print('Min:', min(results))
    print('Max:', max(results))
