#!/bin/bash
cd "$(dirname "$0")"

# Optional: Regenerate the JSON if the user wants to ensure data is fresh
# python3 generate_calendar.py

git add .
git commit -m "Automated update from AI Assistant"
git push origin main
