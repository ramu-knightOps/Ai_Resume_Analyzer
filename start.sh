#!/usr/bin/env bash
set -euo pipefail

cd App
exec python -m streamlit run App.py --server.address 0.0.0.0 --server.port "${PORT:-8501}"
