"""Tests for the snake-ai entry point: subcommands, --version and packaging."""
import importlib.metadata
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import snake_ai
from snake_ai import cli

ROOT = Path(__file__).resolve().parent.parent


def run_command(*args):
    env = dict(os.environ, SDL_VIDEODRIVER='dummy')
    return subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=50)


def test_version_is_defined_once():
    try:
        installed = importlib.metadata.version('snake-ai')
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("snake-ai is not installed")
    assert installed == snake_ai.__version__


def test_version_option(capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(['--version'])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"snake-ai {snake_ai.__version__}"


def test_a_command_is_required():
    with pytest.raises(SystemExit) as exit_info:
        cli.parse_args([])
    assert exit_info.value.code == 2


def test_main_plays_and_returns_exit_code_0(capsys):
    assert cli.main(['play', '--headless', '--games', '1', '--max-steps', '50', '--seed', '1']) == 0
    assert "Games: 1  Mean:" in capsys.readouterr().out


def test_python_m_snake_ai_version():
    result = run_command(sys.executable, '-m', 'snake_ai', '--version')
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"snake-ai {snake_ai.__version__}"


def test_python_m_snake_ai_play():
    result = run_command(sys.executable, '-m', 'snake_ai', 'play', '--headless',
                         '--games', '1', '--max-steps', '50', '--seed', '1')
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("Game 1: score")
    assert "pygame" not in result.stdout  # the welcome banner stays hidden


def test_snake_ai_console_script():
    script = shutil.which('snake-ai', path=str(Path(sys.executable).parent))
    if script is None:
        pytest.skip("the snake-ai script is not installed")
    result = run_command(script, 'play', '--headless', '--games', '1', '--max-steps', '50')
    assert result.returncode == 0, result.stderr
    assert "Games: 1  Mean:" in result.stdout


def test_play_does_not_import_stable_baselines():
    code = ("import sys; from snake_ai import cli; "
            "cli.main(['play', '--headless', '--games', '1', '--max-steps', '20']); "
            "assert 'stable_baselines3' not in sys.modules and 'torch' not in sys.modules")
    result = run_command(sys.executable, '-c', code)
    assert result.returncode == 0, result.stderr
