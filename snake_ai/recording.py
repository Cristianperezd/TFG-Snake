"""Record games as animated GIFs (`--record PATH` in snake-ai play and evaluate).

Needs Pillow, from the `record` extra: pip install -e ".[record]". Frames are
kept in memory until the GIF is saved, so for long games record every few
frames (`--record-every`) or limit the game length (`--max-steps`).
"""

import zlib

import numpy as np
import pygame

# Browsers play GIF frames shorter than 20 ms much slower, so never go below it
MIN_FRAME_MS = 20

# How long the game-over frame stays in the GIF
GAME_OVER_MS = 1500


def add_arguments(parser):
    """Add --record, --record-every and --record-scale to a command's parser."""
    parser.add_argument(
        "--record",
        metavar="PATH",
        default=None,
        help="save the run as an animated GIF (needs the record extra)",
    )
    parser.add_argument(
        "--record-every",
        type=int,
        default=1,
        metavar="N",
        help="with --record, keep one frame out of N (default: %(default)s)",
    )
    parser.add_argument(
        "--record-scale",
        type=float,
        default=1.0,
        metavar="FACTOR",
        help="with --record, resize the frames, e.g. 0.6 (default: %(default)s)",
    )


def check_arguments(parser, args):
    if args.record_every < 1:
        parser.error("--record-every must be at least 1")
    if not 0 < args.record_scale <= 4:
        parser.error("--record-scale must be more than 0 and at most 4")


def from_arguments(args, fps):
    """A GifRecorder for the --record options, or None without --record."""
    if args.record is None:
        return None
    return GifRecorder(args.record, fps=fps, every=args.record_every, scale=args.record_scale)


def save(recorder):
    if recorder is not None:
        frames = recorder.save()
        print(f"Saved {frames} frames to {recorder.path}" if frames else "Nothing to record.")


def import_pillow():
    """Import and return Pillow's Image module, with a clear error if it is missing."""
    try:
        from PIL import Image
    except ImportError as error:
        raise SystemExit(
            'Recording GIFs needs Pillow. Install the record extra: pip install -e ".[record]"'
        ) from error
    return Image


class GifRecorder:
    """Collects frames and saves them as a looping GIF.

    Arguments:
        path: where to save the GIF.
        fps: frame rate of the game; sets how long each recorded frame lasts.
        every: keep one frame out of `every`, to make the file smaller.
        scale: resize the frames by this factor (e.g. 0.5), also to make it smaller.

    Frames are kept compressed in memory (the game's flat colours compress
    well) and share one palette in the GIF, so only the cells that change are
    stored for each frame.
    """

    def __init__(self, path, fps=30, every=1, scale=1.0):
        self.Image = import_pillow()
        self.path = path
        self.every = every
        self.scale = scale
        self.frame_ms = max(MIN_FRAME_MS, round(1000 * every / fps))
        self.frames = []  # zlib-compressed RGB bytes
        self.durations = []
        self.size = None
        self._seen = 0

    def add_frame(self, frame, hold_ms=None):
        """Add a frame: a pygame Surface or an HxWx3 uint8 array.

        Frames are subsampled with `every`; a frame with `hold_ms` (e.g. the
        game-over message) is always kept and shown for that long."""
        if hold_ms is None:
            self._seen += 1
            if (self._seen - 1) % self.every:
                return
        if isinstance(frame, pygame.Surface):
            size = frame.get_size()
            image = self.Image.frombytes("RGB", size, pygame.image.tobytes(frame, "RGB"))
        else:
            image = self.Image.fromarray(np.ascontiguousarray(frame, dtype=np.uint8), "RGB")
        if self.scale != 1:
            size = (round(image.width * self.scale), round(image.height * self.scale))
            image = image.resize(size, self.Image.Resampling.LANCZOS)
        if self.size is None:
            self.size = image.size
        elif image.size != self.size:
            raise ValueError(f"frame size {image.size} differs from the first one, {self.size}")
        self.frames.append(zlib.compress(image.tobytes(), 1))
        self.durations.append(hold_ms or self.frame_ms)

    def _image(self, index):
        return self.Image.frombytes("RGB", self.size, zlib.decompress(self.frames[index]))

    def _palette(self):
        """A 255-colour palette made from up to 16 frames spread over the recording."""
        step = max(1, len(self.frames) // 16)
        samples = [self._image(i) for i in range(0, len(self.frames), step)]
        sheet = self.Image.new("RGB", (self.size[0], self.size[1] * len(samples)))
        for row, sample in enumerate(samples):
            sheet.paste(sample, (0, row * self.size[1]))
        return sheet.quantize(colors=255, dither=self.Image.Dither.NONE)

    def save(self):
        """Write the GIF. Return the number of frames (0: nothing was written)."""
        if not self.frames:
            return 0
        palette = self._palette()
        frames = (
            self._image(i).quantize(palette=palette, dither=self.Image.Dither.NONE)
            for i in range(len(self.frames))
        )
        first = next(frames)
        first.save(
            self.path,
            save_all=True,
            append_images=frames,
            duration=self.durations,
            loop=0,
        )
        return len(self.frames)
