#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.10+ is required."; exit 1
fi
if [ ! -f .venv/bin/python ]; then
  echo "Setting up Paperlane. First installation requires Internet for Python packages..."
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
exec .venv/bin/python app.py
