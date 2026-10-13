"""JamerGamer - run with:  python main.py

Optional:  python main.py --step <id>   jump straight to a story step
           (intro, snake, pre_platformer, platformer, pre_rhythm, rhythm,
            pre_adventure, adventure, pre_doom, doom, finale, end)

The same file is the entry point for the browser build (see tools/build_web.py).
"""
import argparse
import asyncio

import pygame  # noqa: F401  (imported here so the browser build knows to load pygame)

from jamergamer.app import App
from jamergamer.story import INDEX


async def main():
    parser = argparse.ArgumentParser(description="JamerGamer")
    parser.add_argument("--step", choices=list(INDEX), help="start at a specific story step")
    args, _ = parser.parse_known_args()
    app = App(start_step=INDEX[args.step] if args.step else None)
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
