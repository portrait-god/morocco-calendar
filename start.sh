#!/bin/bash
cd "$(dirname "$0")"
lsof -ti:5055 | xargs kill -9 2>/dev/null || true
pip3 install flask --quiet 2>/dev/null
python3 app.py
