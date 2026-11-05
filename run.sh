#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$project_dir/.venv/bin/python" ]]; then
    exec "$project_dir/.venv/bin/python" "$project_dir/cli.py" "$@"
elif [[ -f "$project_dir/.venv/Scripts/python.exe" ]]; then
    exec "$project_dir/.venv/Scripts/python.exe" "$project_dir/cli.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$project_dir/cli.py" "$@"
elif command -v python >/dev/null 2>&1; then
    exec python "$project_dir/cli.py" "$@"
elif command -v py >/dev/null 2>&1; then
    exec py -3 "$project_dir/cli.py" "$@"
else
    echo "Python was not found. Install Python and add it to PATH." >&2
    exit 1
fi
