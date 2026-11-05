#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ -f .venv/bin/python ]]; then
    python_path=.venv/bin/python
elif [[ -f .venv/Scripts/python.exe ]]; then
    python_path=.venv/Scripts/python.exe
else
    if command -v python3 >/dev/null 2>&1; then
        python3 -m venv .venv
    elif command -v python >/dev/null 2>&1; then
        python -m venv .venv
    elif command -v py >/dev/null 2>&1; then
        py -3 -m venv .venv
    else
        echo "Python was not found. Install Python and add it to PATH." >&2
        exit 1
    fi

    if [[ -f .venv/bin/python ]]; then
        python_path=.venv/bin/python
    else
        python_path=.venv/Scripts/python.exe
    fi
fi

"$python_path" -m pip install -r requirements-build.txt
mkdir -p build
"$python_path" -m PyInstaller --noconfirm --clean --onefile --console --name GithubUserActivity --specpath build cli.py

echo "Created dist/GithubUserActivity (on Windows: dist/GithubUserActivity.exe)"
