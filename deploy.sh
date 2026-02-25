#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🔄 Regenerating calendar data..."
python3 generate_calendar.py

echo "📦 Staging changes..."
git add .

# Only commit if there are changes
if git diff --cached --quiet; then
  echo "✅ Nothing new to commit."
else
  git commit -m "Automated update from AI Assistant"
fi

echo "🚀 Pushing to GitHub (force)..."
git push origin main --force

echo "✅ Done! Render will auto-deploy in ~60 seconds."

