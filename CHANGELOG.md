# Changelog

Versions follow [Semantic Versioning](https://semver.org/):

- **1.x** is the thesis project, cleaned up and made reproducible. Agent behaviour and results match the thesis.
- **2.x** will contain improvements beyond the thesis.

## [1.2.0] - Unreleased

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

[1.2.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.1.0...code-cleanup
[1.1.0]: https://github.com/Cristianperezd/TFG-Snake/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Cristianperezd/TFG-Snake/tree/v1.0.0
