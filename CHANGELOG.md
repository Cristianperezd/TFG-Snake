# Changelog

Versions follow [Semantic Versioning](https://semver.org/):

- **1.x** is the thesis project, cleaned up and made reproducible. Agent behaviour and results match the thesis.
- **2.x** will contain improvements beyond the thesis.

## [1.6.0] - 2026-11-28

Better visualization. Only the drawing changes: games, agents' decisions, observations, rewards and scores are the same as in 1.5.0 (the regression tests pass unchanged, and headless runs print exactly the same output).

### Added
- A side panel next to the board with the agent, score, length, game number, best score, average so far and FPS. The window is now 700×500; the board is still 25×25 cells.
- `snake-ai play --show-path`: draws the path the search agent plans to the apple and, lightly, the cells its last search expanded. The agents expose them in `SearchAgent.expanded` and `SearchAgent.planned_path()`, recorded without changing their decisions.
- Space pauses and resumes, and Esc quits like closing the window, in `snake-ai play` and in the `SnakeEnv` human window (`snake-ai evaluate`).
- A game-over message with the reason (collision, no path, step limit) between games, for `--game-over-delay` seconds (default 1.5; skipped with `--headless` and `--fps 0`). Also in `snake-ai evaluate`.
- `--record PATH` in `snake-ai play` and `snake-ai evaluate` saves the run as an animated GIF, with `--record-every N` and `--record-scale F` for smaller files. It also works without a window (`--headless`, `--no-render`). Needs Pillow, from the new `record` extra.
- `SnakeEnv.frame(overlay=None)` returns the current frame as an array in any render mode, and `SnakeEnv.hud` adds the episode statistics to its side panel.
- `docs/ppo-demo.gif`, the pretrained PPO agent playing.

### Changed
- New look: a dark checkerboard board, a snake whose body fades from head to tail with eyes facing where it moves, and a round apple. The drawing code is in `snake_ai/game/render.py` and is shared by the game and `SnakeEnv`; `Snake.draw` and `Food.draw` were removed.
- `SnakeEnv` renders with the same look. The `"human"` window adds the side panel; `"rgb_array"` frames still show only the board (500×500×3), and the new `SnakeEnv.frame()` returns the full frame, panel included.
- `docs/astar-demo.gif` was recorded again with `--record`, with the new look and `--show-path`.
- CI installs the `record` extra to run the recording tests.
- README: the Mermaid architecture diagram was replaced by an SVG diagram, with light and dark variants that follow the GitHub theme.

### Fixed
- In human play, driving the snake off the bottom or right edge of the board raised an `IndexError` instead of ending the game: the board was updated before checking the collision. The bug dates back to the thesis code; the search agents never leave the board, so their results are unchanged.

## [1.5.0] - 2026-11-27

### Added
- A pretrained PPO agent, `snake_ai/rl/pretrained/ppo_snake.zip` (~150 KB), trained with the thesis configuration (`snake-ai train --seed 0`, 5,109,760 steps). `snake-ai evaluate` uses it when no `MODEL` is given, so `pip install -e ".[rl]"` followed by `snake-ai evaluate` is enough to watch it play. Over 150 seeded episodes it scores 34.10 on average (1 – 70); see the README for the comparison with the thesis.
- `SnakeEnv(render_mode=None, max_episode_steps=None)`: render mode validated against `metadata["render_modes"]` (`"human"`, `"rgb_array"`) and optional truncation after `max_episode_steps` steps.
- `reset(seed=..., options=...)`: a seed also seeds Python's `random` module, which places the food, so seeded episodes are reproducible.
- `"rgb_array"` render mode: `render()` returns the frame as a 500×500×3 `uint8` array, without opening a window.
- The environment is registered with Gymnasium as `SnakeAI-v0` when `snake_ai.rl` is imported.
- Tests for the Gymnasium API (`gymnasium.utils.env_checker.check_env`, seeding, truncation, render modes, `gymnasium.make`) and for the pretrained model.

### Changed
- `snake-ai evaluate`: `MODEL` is optional. `--max-steps` uses the environment's truncation instead of breaking out of the loop, and `--seed` seeds the first `reset()`.
- The `"human"` window is opened on the first `render()` call instead of in `reset()`, and `close()` only closes the window.
- README: how to try the pretrained agent, how to train your own, the environment's API and the measured results.

### Fixed
- `SnakeEnv` did not follow the Gymnasium API: `reset()` did not accept `options` nor call `super().reset()`, there was no `metadata` and `render()` needed a window opened by `reset()`. Callers had to set `env.render_mode` after creating the environment.
- `snake-ai evaluate` failed with a traceback when the model file did not exist.

### Known issues
- Training in 10,000-step chunks (one checkpoint each) makes PPO run whole 2,048-step rollouts, so each chunk runs 10,240 steps and the default run does 5,109,760 steps instead of 4,990,000. Kept as in the thesis and documented.

The dynamics, observations and rewards are unchanged: the regression tests pass, and 2,000 random-action episodes (619,521 steps) give identical observations, rewards and scores with the 1.4.0 and 1.5.0 environments.

## [1.4.0] - 2026-11-27

### Added
- `pyproject.toml`: the project installs as the `snake-ai` package with `pip install -e .`. Optional extras: `rl` (Stable Baselines 3, TensorBoard) and `test` (pytest). The version is defined once, in `snake_ai.__version__`.
- A single `snake-ai` command with subcommands: `snake-ai play`, `snake-ai train` and `snake-ai evaluate MODEL`, with the same options as the old scripts. `python -m snake_ai` works too, and `snake-ai --version` prints the version.
- A clear error message when `train` or `evaluate` run without Stable Baselines 3 installed.
- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting, configured in `pyproject.toml` and checked in CI.
- Mermaid architecture diagram in the README.
- `.gitattributes` enforcing LF line endings.
- Python, license and Ruff badges in the README.
- Tests for the `snake-ai` entry point.

### Changed
- The modules moved from the repository root into the `snake_ai` package: `snake_ai.game` (`game`, `snake`, `food`, `constants`, `colors`), `snake_ai.search` (`node`, `search_agent`, `gbfs`, `astar`) and `snake_ai.rl` (`snake_env`, `train`, `evaluate`). `GBFSNode` and `AStarNode` now live in `gbfs.py` and `astar.py`.
- The code is formatted with Ruff (formatting only).
- CI installs the package with `pip install -e ".[test]"`.

### Removed
- `main.py`, `train_ppo.py` and `evaluate_ppo.py`: use `snake-ai play`, `snake-ai train` and `snake-ai evaluate`.
- `requirements.txt`, `requirements-test.txt` and `pytest.ini`, replaced by `pyproject.toml`.
- The `Documentation/` folder with the outdated PlantUML class diagram. The original is still available at [`v1.0.0`](https://github.com/Cristianperezd/TFG-Snake/tree/v1.0.0/Documentation).

Agent behaviour is unchanged: the regression tests pass, and `snake-ai play --games 50 --headless --seed 1` prints exactly the same scores as `python main.py --games 50 --headless --seed 1` in 1.3.0.

## [1.3.0] - 2026-11-27

### Added
- Command-line interface for `main.py`: `--agent {human,gbfs,astar}`, `--games`, `--fps`, `--seed`, `--headless` and `--max-steps`. It prints each game's score and why it ended, plus mean, min and max. `--games 50` reproduces the thesis evaluation.
- Command-line options for the PPO scripts: total timesteps, checkpoint frequency, run name, output folders and seed for training; checkpoint path, number of episodes, rendering on/off, seed and a step limit for evaluation.
- `tensorboard` in `requirements.txt` (the training script logs to TensorBoard).
- Tests for the command-line options and for how games end.

### Changed
- Renamed `checkenv.py` to `train_ppo.py` and `load_models.py` to `evaluate_ppo.py`. Their defaults match the previous hard-coded values (10,000-step checkpoints, ~5M steps, 50 evaluation episodes).
- `Game.step()` returns `True` when the game is over and stores the reason in `Game.end_reason`, instead of returning the score. `Game` takes `fps` and `render` arguments.
- The default frame rate (30 FPS) and the GBFS node limit (2,000) are defined in `constants.py`.

### Fixed
- The process exited as soon as the snake died or the window was closed, so only one game could be played per run.
- The game always wrapped the current state in an `AStarNode` when an agent replanned, also for GBFS. Each agent now uses its own node type. This does not change any search result: the root node is the only one in the queue when it is expanded, so its ordering is never used.
- A game where the agent found no path before eating anything looped forever, because a score of 0 meant "game still running".
- The PPO evaluation drew every frame twice.

The regression tests confirm that A\* games, GBFS searches and RL environment episodes are still identical to the thesis code.

## [1.2.0] - 2026-11-27

### Changed
- Removed the outdated `AStar.py`. The A\* used in the thesis experiments (`AStar_copy.py`, class `AStarCo`) is now `astar.py`, class `AStar`.
- Renamed modules to snake_case (`gbfs.py`, `snake_env.py`, …).
- Moved the logic shared by GBFS and A\* into a `SearchAgent` base class.
- Replaced the 560-colour palette module with the five colours in use.
- Removed dead code, debug prints and unused imports, and translated comments to English.

### Added
- Test suite (`pytest`) with regression tests against traces recorded from the thesis code, plus unit tests.
- GitHub Actions workflow running the tests on Python 3.10–3.13 for every push and pull request.

The regression tests confirm that A\* games, GBFS searches and RL environment episodes are identical before and after the cleanup.

## [1.1.0] - 2026-11-27

### Added
- README with thesis results, approach, usage and an A\* gameplay demo.
- `requirements.txt`.

### Fixed
- Food spawning crashed on Python 3.12+ (`random.randint()` with a float argument).

## [1.0.0] - 2023-07

Original submission of the Bachelor's Thesis (Universitat Autònoma de Barcelona).

[1.6.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Cristianperezd/TFG-Snake/tree/v1.0.0
