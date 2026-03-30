#!/usr/bin/env bash
set -euo pipefail

cd App

if [ -x /opt/venv/bin/python ]; then
  PYTHON_BIN="/opt/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "Python runtime not found. Checked /opt/venv/bin/python, python3, and python." >&2
  exit 1
fi

exec "$PYTHON_BIN" -m streamlit run App.py --server.address 0.0.0.0 --server.port "${PORT:-8501}"
