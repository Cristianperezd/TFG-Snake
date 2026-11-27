# Changelog

Versions follow [Semantic Versioning](https://semver.org/):

- **1.x** is the thesis project, cleaned up and made reproducible. Agent behaviour and results match the thesis.
- **2.x** will contain improvements beyond the thesis.

## [1.3.0] - Unreleased

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

[1.3.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Cristianperezd/TFG-Snake/tree/v1.0.0
