#!/bin/bash

# experiment.sh - Run all RNA-ligand optimization methods
# Executes 2 processes in parallel at a time, logging output to separate files

# Maximum number of parallel processes
MAX_PARALLEL=2

# List of Python scripts to run (script_name:display_name)
EXPERIMENTS=(
    "run_screen.py:screening"
    "run_graphga.py:graph_ga"
    "run_smiles_ga.py:smiles_ga"
    "run_gp_bo.py:gp_bo"
    "run_reinvent.py:reinvent"
)

# Create logs directory if it doesn't exist
mkdir -p logs

echo "=========================================="
echo "Starting RNA-ligand optimization experiments"
echo "Started at: $(date)"
echo "Total experiments: ${#EXPERIMENTS[@]}"
echo "Parallel processes: $MAX_PARALLEL"
echo "=========================================="
echo ""

# Function to run a single experiment
run_experiment() {
    local script=$1
    local name=$2
    local logfile="logs/${name}_$(date +%Y%m%d_%H%M%S).log"
    
    echo "[$(date +%H:%M:%S)] Starting: $name"
    echo "  Script: $script"
    echo "  Log: $logfile"
    
    python "$script" > "$logfile" 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "[$(date +%H:%M:%S)] ✓ Completed: $name"
    else
        echo "[$(date +%H:%M:%S)] ✗ Failed: $name (exit code: $exit_code)"
    fi
    echo ""
    
    return $exit_code
}

# Array to track running jobs
declare -a PIDS=()
declare -a NAMES=()

# Index for experiments queue
experiment_idx=0

# Function to start next experiment if available
start_next_experiment() {
    if [ $experiment_idx -lt ${#EXPERIMENTS[@]} ]; then
        local exp="${EXPERIMENTS[$experiment_idx]}"
        local script="${exp%%:*}"
        local name="${exp##*:}"
        
        # Start experiment in background
        run_experiment "$script" "$name" &
        local pid=$!
        
        # Track the PID and name
        PIDS+=($pid)
        NAMES+=($name)
        
        experiment_idx=$((experiment_idx + 1))
    fi
}

# Start initial batch of experiments
for ((i=0; i<$MAX_PARALLEL && i<${#EXPERIMENTS[@]}; i++)); do
    start_next_experiment
done

# Main loop: wait for jobs to finish and start new ones
while [ ${#PIDS[@]} -gt 0 ]; do
    # Check each running process
    for i in "${!PIDS[@]}"; do
        pid="${PIDS[$i]}"
        
        # Check if process is still running
        if ! kill -0 "$pid" 2>/dev/null; then
            # Process finished, remove from tracking
            unset 'PIDS[$i]'
            unset 'NAMES[$i]'
            
            # Start next experiment if available
            start_next_experiment
        fi
    done
    
    # Rebuild arrays to remove gaps
    PIDS=("${PIDS[@]}")
    NAMES=("${NAMES[@]}")
    
    # Small sleep to avoid busy waiting
    sleep 1
done

echo "=========================================="
echo "All experiments completed at: $(date)"
echo "=========================================="
echo ""
echo "Log files saved in: logs/"
echo "Results saved in: opt_results/"
echo ""
echo "Summary of log files:"
ls -lh logs/
