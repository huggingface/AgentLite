#!/bin/bash

# Set the default directory path
DEFAULT_DIR="/fsx/lewis/git/AgentBoard/agentboard/environment/WebShop"

# Use the provided directory path or default to DEFAULT_DIR
DIR_PATH="${1:-$DEFAULT_DIR}"

cd "$DIR_PATH"

tmux new-session -d -s webshop
tmux send-keys -t webshop "conda activate agentboard" C-m C-l
tmux send-keys -t webshop "bash ./run_dev.sh" C-m C-l