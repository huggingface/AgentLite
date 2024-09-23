#!/bin/bash
source ~/.bashrc
# Set the default directory path
DEFAULT_DIR="/admin/home/edward/work/agents/AgentBoard/agentboard/environment/WebShop"
ARGS="$@"

# Use the provided directory path or default to DEFAULT_DIR
echo $DIR_PATH
# cd $DIR_PATH
# conda init
# conda activate agentboard   
# pip list
# bash ./run_dev.sh
# Kill any dangling sessions
tmux kill-session -t webshop
tmux new-session -d -s webshop
tmux send-keys -t webshop "cd '$DEFAULT_DIR'" C-m C-l
tmux send-keys -t webshop "conda activate agentboard" C-m C-l
tmux send-keys -t webshop "bash ./run_dev.sh $ARGS" C-m C-l