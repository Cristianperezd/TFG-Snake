"""Build the browser version with pygbag, and optionally serve it.

    pip install pygbag==0.9.3
    python web/build.py            # build into build/snake-ai/build/web/
    python web/build.py --serve    # build, then serve it on http://localhost:8000

pygbag packs a folder with a main.py. This script puts web/main.py and the
`snake_ai` package in build/snake-ai/ and runs pygbag on it. `snake_ai.rl`
(the PPO agent, which needs PyTorch and Gymnasium) is left out: the browser
version does not use it. pygbag downloads its Python runtime from its CDN.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "build" / "snake-ai"
OUTPUT_DIR = APP_DIR / "build" / "web"

PYGBAG_OPTIONS = [
    "--app_name",
    "snake-ai",
    "--title",
    "Snake AI",
    # Start at once: the game has no sound, so it needs no click to unlock audio
    "--ume_block",
    "0",
]


def assemble():
    """Fill APP_DIR with main.py and the package, without the RL code or caches."""
    shutil.rmtree(APP_DIR, ignore_errors=True)
    APP_DIR.mkdir(parents=True)
    shutil.copy2(ROOT / "web" / "main.py", APP_DIR / "main.py")
    shutil.copytree(
        ROOT / "snake_ai",
        APP_DIR / "snake_ai",
        ignore=shutil.ignore_patterns("rl", "__pycache__", "*.pyc"),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--serve", action="store_true", help="serve the build on localhost:8000")
    args = parser.parse_args(argv)

    assemble()
    command = [sys.executable, "-m", "pygbag", *PYGBAG_OPTIONS]
    if not args.serve:
        command.append("--build")
    subprocess.run([*command, str(APP_DIR)], check=True)
    print(f"Built {OUTPUT_DIR / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
