#!/bin/bash
# Builds JamerGamer for this Mac (first run takes a few minutes), then opens it.
cd "$(dirname "$0")" || exit 1
APP="dist/JamerGamer.app"
if [ ! -d "$APP" ]; then
    if ! python3 -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
        echo
        echo "Python 3 was not found. Install it from https://www.python.org/downloads/"
        echo "then double-click this file again."
        read -n 1 -s -r -p "Press any key to close..."
        exit 1
    fi
    [ -x .buildenv/bin/python ] || python3 -m venv .buildenv || exit 1
    if ! .buildenv/bin/python build.py; then
        read -n 1 -s -r -p "Build failed. Press any key to close..."
        exit 1
    fi
fi
open "$APP"
