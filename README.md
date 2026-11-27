# Snake: Intelligent Agents

Bachelor's Thesis (TFG) in Computer Engineering, Universitat Autònoma de Barcelona, 2023.

A Snake game built from scratch with **Pygame**, used as a testbed to compare classic search agents (**Greedy Best-First Search** and **A\***) with a **reinforcement learning** agent (**PPO**, via Stable Baselines 3 on a custom Gymnasium environment).

<p align="center">
  <img src="docs/astar-demo.gif" alt="A* agent playing Snake" width="300">
</p>

> **Status:** this repository is being revisited. The original thesis submission is preserved under the tag [`tfg-original-2023`](../../tree/tfg-original-2023). The current work reviews what I built at the time and improves it step by step: documentation, reproducibility and code quality.

## Results

Each agent played 50 games on a 25×25 board. The score is the number of apples eaten. Search agents were limited to 2,000 expanded nodes per search.

| Agent | Mean score | Min – Max |
|---|---:|---:|
| **A\*** | **78.34** | 36 – 136 |
| GBFS | 42.94 | 23 – 72 |
| PPO, v2 (cumulative reward) | 20.90 | 3 – 42 |
| PPO, v1 (constant reward) | 11.54 | 1 – 33 |

Key takeaways:

- **A\* almost doubles GBFS.** The accumulated path cost, together with pruning of redundant paths, keeps A\* from getting lost before it reaches the node limit. Both agents can still die when an apple spawns in a position with no safe path.
- **Reward design mattered more than the algorithm.** With a constant +10 / −10 reward, PPO learned to eat once and then circle forever. Switching to a cumulative reward for each apple doubled the mean score.
- **RL did not beat search here.** The PPO agent sees a compact 9-value observation: relative food direction, current action, and whether each neighbouring cell is safe. It has no information about its own body beyond one step away, so it cannot plan long paths the way A\* does.

The full write-up (in Catalan) is available from the UAB repository: [Snake: Implementació d'agents intel·ligents](https://ddd.uab.cat/record/280737) ([PDF](https://ddd.uab.cat/pub/tfg/2022/tfg_1634657/Informe_Final_TFG.pdf)).

## How it works

**Game.** `Snake`, `Food` and `Game` implement the rules on a 500×500 px window with 20 px cells. `Game` keeps a 25×25 matrix of the board (empty / snake / food) so the agents can read the state.

**Search agents.** Each search runs from the current state to the next apple. It simulates moves on copies of the snake and returns the path, which the game then follows.

- `Node` stores the board, snake, food, the Manhattan-distance heuristic `h` and the path cost `g`.
- `GBFSNode` orders nodes by `h` only. `AStarNode` orders them by `g + h`.
- `AStar_copy.py` (`AStarCo`) is the final A\* used in the experiments. It keeps a per-cell best-cost matrix to discard redundant paths. `AStar.py` is an earlier version.

**Reinforcement learning.** `SnakeEnv` wraps the game as a Gymnasium environment:

- 4 discrete actions (up, down, left, right).
- A 9-value observation: food left/right/up/down, the last action, and whether moving up/down/left/right is safe.
- Reward of +10 for each apple, accumulated over the episode, and −10 on death.

PPO is trained with Stable Baselines 3 (`MlpPolicy`).

## Running it

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

| Command | What it does |
|---|---|
| `python main.py` | Opens the game window and lets the A\* agent play. |
| `python checkenv.py` | Trains a PPO agent. Checkpoints go to `models/` and TensorBoard logs to `logs/`. |
| `python load_models.py` | Loads a trained PPO checkpoint and plays 50 episodes. Edit `models_dir` to point to your own run. |

Trained models are not included in the repository.

## Project structure

```
├── game.py            # Game loop, rendering and board matrix
├── snake.py, food.py  # Game entities
├── node.py            # Search node (heuristic + path cost)
├── GBFS.py, GBFSNode.py
├── AStar_copy.py      # Final A* implementation (AStarCo)
├── AStar.py, AStarNode.py
├── Snakeenv.py        # Gymnasium environment for RL
├── checkenv.py        # PPO training script
├── load_models.py     # PPO evaluation script
├── main.py            # Runs the A* agent
└── Documentation/     # Class diagram
```

## Tech stack

Python · Pygame · NumPy · Gymnasium · Stable Baselines 3 (PPO)

## License

[MIT](LICENSE.txt)
