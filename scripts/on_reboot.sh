#!/usr/bin/env bash

set -u -o pipefail

# Run from pi user's crontab

# Redirect stderr and stdout to fff
# exec >/home/pi/fff

# echo "I'm run as $(whoami) - EUID: $EUID"
# echo "See the stderr mesg!" 2>&1

# cmd='tmux new-session -d -s my_session "sudo python3 /var/www/html/scripts/entry.py"'
# echo "$cmd"

# bash --init-file <(echo ". \"$HOME/.bashrc\"; $cmd")

# echo 'bash --init-file <(echo ". "$HOME/.bashrc"; sudo python3 /var/www/html/scripts/entry.py")'
# https://serverfault.com/a/586272/532952
# Don't believe quoting has to be like this, fairly arbitrary
# This way runs tmux session on reboot, runs commands AND even when the commands
# end the session keeps running
tmux new-session -d -s sesh 'bash --init-file <(echo ". "$HOME/.bashrc"; sudo python3 /var/www/html/scripts/entry.py")'

