#!/usr/bin/env bash
set -euo pipefail

cd /app/App 2>/dev/null || cd App
exec python -m streamlit run App.py --server.address 0.0.0.0 --server.port "${PORT:-8501}"
