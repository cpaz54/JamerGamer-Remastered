"""Build the browser version of JamerGamer with pygbag.

    python tools/build_web.py            # build into build/web
    python -m pygbag build/JamerGamer    # then test it at http://localhost:8000

Needs ffmpeg on PATH and `pip install pygbag==0.9.3`. GitHub Actions runs this on
every push to main and publishes build/web to GitHub Pages (.github/workflows/web.yml).
(Test with pygbag's own server: a plain static server on localhost makes the page
look for pygame on localhost instead of the pygbag CDN.) The game code is shared with the
desktop version; this script only assembles a web copy in build/JamerGamer:
  - leaves out assets the game never loads,
  - converts every .mp3/.wav to .ogg (what browsers play reliably; audio.py
    swaps the extension when running in the browser),
then runs pygbag, which writes build/web (index.html + JamerGamer.apk).
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "build", "JamerGamer")   # folder name = bundle name pygbag shows
OUT = os.path.join(ROOT, "build", "web")

SKIP_ASSETS = {
    os.path.join("common", "legacy"),
    os.path.join("adventure", "source", "sheets"),
    os.path.join("doom", "sound", "theme.mp3"),
}
AUDIO = (".mp3", ".wav")


def skipped(rel):
    return any(rel == s or rel.startswith(s + os.sep) for s in SKIP_ASSETS)


def vorbis_args():
    """libvorbis if this ffmpeg has it, else ffmpeg's built-in (stereo-only) Vorbis encoder."""
    encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    if "libvorbis" in encoders:
        return ["-c:a", "libvorbis", "-q:a", "3"]
    return ["-c:a", "vorbis", "-strict", "-2", "-ac", "2", "-b:a", "128k"]


def copy_assets():
    enc = vorbis_args()
    src_root = os.path.join(ROOT, "assets")
    for folder, dirs, files in os.walk(src_root):
        rel_dir = os.path.relpath(folder, src_root)
        dirs[:] = [d for d in dirs if not skipped(os.path.normpath(os.path.join(rel_dir, d)))]
        for name in files:
            rel = os.path.normpath(os.path.join(rel_dir, name))
            if skipped(rel) or name.startswith(".") or name == "desktop.ini":
                continue
            src = os.path.join(src_root, rel)
            dst = os.path.join(SRC, "assets", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if name.lower().endswith(AUDIO):
                dst = os.path.splitext(dst)[0] + ".ogg"
                subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", *enc, dst])
            else:
                shutil.copy2(src, dst)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg is required (macOS: brew install ffmpeg)")
    shutil.rmtree(SRC, ignore_errors=True)
    os.makedirs(SRC)
    shutil.copy2(os.path.join(ROOT, "main.py"), SRC)
    shutil.copytree(os.path.join(ROOT, "jamergamer"), os.path.join(SRC, "jamergamer"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("converting audio and copying assets...")
    copy_assets()

    subprocess.check_call([sys.executable, "-m", "pygbag", "--build", "--title", "JamerGamer", SRC])
    shutil.rmtree(OUT, ignore_errors=True)
    # the page loads the .tar.gz; the .apk copy is only used on itch.io
    shutil.copytree(os.path.join(SRC, "build", "web"), OUT, ignore=shutil.ignore_patterns("*.apk"))
    print(f"\nweb build: {OUT}")


if __name__ == "__main__":
    main()
