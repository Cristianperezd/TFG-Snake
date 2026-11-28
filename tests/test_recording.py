"""Tests for recording games as GIFs (--record)."""

import sys

import numpy as np
import pygame
import pytest

from snake_ai import cli, recording

Image = pytest.importorskip("PIL.Image")


def gif_frames(path):
    with Image.open(path) as gif:
        assert gif.format == "GIF"
        durations = []
        for index in range(gif.n_frames):
            gif.seek(index)
            durations.append(gif.info["duration"])
        return gif.size, durations


def test_play_records_a_gif_without_changing_the_scores(tmp_path, capsys):
    path = tmp_path / "game.gif"
    argv = ["play", "--headless", "--seed", "1", "--max-steps", "40"]
    recorded = cli.play(cli.parse_args(argv + ["--record", str(path), "--record-every", "2"]))
    assert recorded == cli.play(cli.parse_args(argv))
    size, durations = gif_frames(path)
    assert size == (700, 500)
    # 40 frames, one in two, plus the game-over frame
    assert len(durations) == 20 + 1
    assert durations[0] == 60  # 2 frames at 30 FPS; GIFs store hundredths of a second
    assert durations[-1] == recording.GAME_OVER_MS
    assert f"Saved 21 frames to {path}" in capsys.readouterr().out


def test_record_scale_resizes_the_frames(tmp_path):
    path = tmp_path / "small.gif"
    argv = ["play", "--headless", "--seed", "2", "--max-steps", "5", "--show-path"]
    cli.play(cli.parse_args(argv + ["--record", str(path), "--record-scale", "0.5"]))
    size, durations = gif_frames(path)
    assert size == (350, 250)
    assert len(durations) == 5 + 1


def test_recorder_accepts_surfaces_and_arrays(tmp_path):
    path = tmp_path / "frames.gif"
    recorder = recording.GifRecorder(path, fps=60)
    surface = pygame.Surface((30, 20))
    surface.fill((255, 0, 0))
    recorder.add_frame(surface)
    frame = np.zeros((20, 30, 3), dtype=np.uint8)
    frame[:, :, 2] = 255
    recorder.add_frame(frame, hold_ms=500)
    assert recorder.save() == 2
    size, durations = gif_frames(path)
    assert size == (30, 20)
    assert durations == [recording.MIN_FRAME_MS, 500]  # 60 FPS is faster than GIFs allow
    with Image.open(path) as gif:
        assert gif.convert("RGB").getpixel((0, 0)) == (255, 0, 0)
        gif.seek(1)
        assert gif.convert("RGB").getpixel((0, 0)) == (0, 0, 255)


def test_nothing_is_written_without_frames(tmp_path):
    path = tmp_path / "empty.gif"
    assert recording.GifRecorder(path).save() == 0
    assert not path.exists()


@pytest.mark.parametrize("argv", [["--record-every", "0"], ["--record-scale", "0"]])
def test_rejects_invalid_record_options(argv):
    with pytest.raises(SystemExit):
        cli.parse_args(["play", "--record", "x.gif"] + argv)


def test_missing_pillow_is_reported(monkeypatch):
    monkeypatch.setitem(sys.modules, "PIL", None)
    with pytest.raises(SystemExit, match="record extra"):
        recording.GifRecorder("x.gif")


def test_evaluate_records_without_a_window(tmp_path):
    pytest.importorskip("stable_baselines3")  # Not installed on CI
    path = tmp_path / "ppo.gif"
    cli.main(
        ["evaluate", "--episodes", "1", "--no-render", "--seed", "0", "--max-steps", "30"]
        + ["--record", str(path)]
    )
    size, durations = gif_frames(path)
    assert size == (700, 500)
    assert len(durations) == 1 + 30 + 1  # reset, 30 steps, game over
