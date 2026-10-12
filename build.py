"""Build a shareable copy of JamerGamer for the computer this runs on.

    python build.py

Mac:     dist/JamerGamer-mac.zip      (contains JamerGamer.app)
Windows: dist/JamerGamer-windows.zip  (contains a JamerGamer folder with JamerGamer.exe)

PyInstaller can only build for the OS it runs on, so run this once on a Mac
and once on a Windows PC to get both versions.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "JamerGamer"


def run(*cmd):
    print(">", " ".join(cmd))
    subprocess.check_call(cmd, cwd=HERE)


def main():
    run(sys.executable, "-m", "pip", "install", "--upgrade", "pygame", "pyinstaller")
    sep = ";" if sys.platform == "win32" else ":"
    run(sys.executable, "-m", "PyInstaller", "main.py",
        "--name", NAME,
        "--windowed",                  # no terminal window
        "--onedir",
        "--noconfirm", "--clean",
        "--add-data", f"assets{sep}assets",
        "--osx-bundle-identifier", "com.jamergamer.game")

    dist = os.path.join(HERE, "dist")
    if sys.platform == "darwin":
        target, zip_name = f"{NAME}.app", f"{NAME}-mac"
        # ditto keeps the .app's symlinks and permissions intact, unlike a plain zip
        out = os.path.join(dist, zip_name + ".zip")
        if os.path.exists(out):
            os.remove(out)
        run("ditto", "-c", "-k", "--keepParent", os.path.join(dist, target), out)
    else:
        zip_name = f"{NAME}-windows"
        out = shutil.make_archive(os.path.join(dist, zip_name), "zip", dist, NAME)
    print(f"\nDone: {out}")


if __name__ == "__main__":
    main()
