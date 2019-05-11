#!/usr/bin/env bash

set -euf -o pipefail

# echo "Starting..."
# sleep 5
# echo "Done..."

tmux new-session -d -s ses "bash"

# tmux new-session -s session -d "bash -c \"sleep 2\""

# while [ 1 ]
# do
#     echo $$
#     echo "Still going"
#     sleep 1
# done &

# tmux detach

