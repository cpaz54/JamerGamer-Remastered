"""JamerGamer - run with:  python main.py

Optional:  python main.py --step <id>   jump straight to a story step
           (intro, snake, pre_platformer, platformer, pre_rhythm, rhythm,
            pre_adventure, adventure, pre_doom, doom, finale, end)
"""
import argparse

from jamergamer.app import App
from jamergamer.story import INDEX


def main():
    parser = argparse.ArgumentParser(description="JamerGamer")
    parser.add_argument("--step", choices=list(INDEX), help="start at a specific story step")
    args = parser.parse_args()
    app = App(start_step=INDEX[args.step] if args.step else None)
    app.run()


if __name__ == "__main__":
    main()
