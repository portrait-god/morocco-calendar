#!/bin/bash
# Double-click this file to launch the Morocco Content Calendar
cd "$(dirname "$0")"
pip3 install flask --quiet 2>/dev/null
echo ""
echo "🇲🇦  Opening Morocco Content Calendar..."
echo "   http://localhost:5055"
echo ""
open "http://localhost:5055" &
python3 app.py
