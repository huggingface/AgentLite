#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:8
#SBATCH --partition=hopper-prod
#SBATCH --output=/fsx/h4/logs/%x-%j.out
#SBATCH --err=/fsx/h4/logs/%x-%j.err
#SBATCH --requeue
#SBATCH --mail-type=ALL 
#SBATCH --mail-user=lewis+hfc@huggingface.co

set -x -e
source ~/.bashrc
conda activate agentlite

MODEL_ID=$1

# Set the default directory path for AgentBoard
AGENTBOARD_DIR="/fsx/lewis/git/AgentBoard/agentboard/environment/WebShop"

# Start WebShop server in tmux session called `webshop`
./start_webshop_server.sh "$AGENTBOARD_DIR"

# Test it is up and running
sleep 10
curl -v http://127.0.0.1:3000/abc

# Start the vllm server in the background
NUM_GPUS=$(nvidia-smi --list-gpus | wc -l)
# Change output from /dev/null to vllm_server.log for debugging
nohup vllm serve $MODEL_ID --tensor-parallel-size $NUM_GPUS >vllm_server.log 2>&1 &

# Capture the process ID (PID) of the vllm server
VLLM_PID=$!

# Function to shut down the vllm server
function shutdown_server {
    echo "Shutting down the tmux and vLLM server..."
    tmux kill-session -t webshop
    kill $VLLM_PID
    wait $VLLM_PID
    echo "Server shut down."
}

# Trap interruption signals and call the shutdown function
trap shutdown_server SIGINT SIGTERM

# Function to check if the server is up by checking the /health endpoint
function check_server {
    curl -i http://0.0.0.0:8000/health 2>/dev/null | head -n 1 | grep "200 OK"
}

# Wait for the server to be available
echo "Waiting for the server to start..."
while ! check_server; do
    echo "vLLM server is not yet available. Checking again in 5 seconds..."
    sleep 5
done

echo "vLLM server is up and running."

# Run evaluation script
python evaluate_webshop.py --llm $MODEL_ID --agent_arch act

# TODO: compute success rate and push results to the Hub

# Stop the vllm server
shutdown_server

echo "Done!"