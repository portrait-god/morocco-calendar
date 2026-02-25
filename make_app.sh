#!/bin/bash
DIR=$(cd "$(dirname "$0")" && pwd)
start_script="$DIR/start.sh"

cat << 'EOF' > launch.applescript
set app_path to POSIX path of (path to me)
set script_path to do shell script "dirname '" & app_path & "'"
set full_path to script_path & "/start.sh"
do shell script "'" & full_path & "' > /dev/null 2>&1 &"
delay 1
open location "http://localhost:5055"
EOF

osacompile -o "Morocco Calendar.app" launch.applescript
rm launch.applescript
