# /// script
# dependencies = [
#     "numpy",
# ]
# ///
"""Entry point of the browser version, built with pygbag (pygame in WebAssembly).

pygbag runs this file in the page. The loop has to give control back to the
browser every frame (`await asyncio.sleep(0)`), so all the logic is in
`snake_ai.browser.App`, which never blocks. Build it with `python web/build.py`.
"""

import asyncio

import numpy  # noqa: F401  (imported here so pygbag loads it before the game needs it)
import pygame

from snake_ai.browser import App


async def main():
    app = App()
    while True:
        for event in pygame.event.get():
            app.handle_event(event, pygame.time.get_ticks())
        app.update(pygame.time.get_ticks())
        await asyncio.sleep(0)  # Let the browser draw the frame and handle input


asyncio.run(main())
