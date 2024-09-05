#!/bin/bash

# Set the default directory path
DEFAULT_DIR="/fsx/lewis/git/AgentBoard/agentboard/environment/WebShop"

# Use the provided directory path or default to DEFAULT_DIR
DIR_PATH="${1:-$DEFAULT_DIR}"

# Kill any dangling sessions
tmux kill-session -t webshop
tmux new-session -d -s webshop
tmux send-keys -t webshop "cd '$DIR_PATH'" C-m C-l
tmux send-keys -t webshop "conda activate agentboard" C-m C-l
tmux send-keys -t webshop "bash ./run_dev.sh" C-m C-l