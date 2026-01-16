#!/bin/bash

# example_combined_objective.sh - Run RNA-ligand optimization with combined binding-similarity objective
# Usage: ./example_combined_objective.sh [num_runs] [experiment_name]
# Defaults: runs=1, experiment_name=auto_timestamp

# Parse arguments with defaults
NUM_RUNS=${1:-1}
EXP_NAME=${2:-$(date +%Y%m%d_%H%M%S)}

# Fixed parameters
POPULATION_SIZE=1000
MAX_CALLS=10000
SMI_FILE="inputs/ligands/robin_smiles.txt"
REFERENCE_FILE="inputs/ligands/diverse_molecules.txt"
SIMILARITY_WEIGHT=0.3
BINDING_WEIGHT=0.7

# Create timestamped parent directory for this experimental run
RESULTS_DIR="opt_results/run_combined_${EXP_NAME}"
LOGS_DIR="logs/run_combined_${EXP_NAME}"

mkdir -p "$RESULTS_DIR"
mkdir -p "$LOGS_DIR"

echo "=========================================="
echo "Combined Objective RNA-ligand optimization"
echo "=========================================="
echo "Configuration:"
echo "  Experiment Name: $EXP_NAME"
echo "  Population Size: $POPULATION_SIZE"
echo "  Max Oracle Calls: $MAX_CALLS"
echo "  Number of Runs: $NUM_RUNS"
echo "  SMILES File: $SMI_FILE"
echo "  Reference File: $REFERENCE_FILE"
echo "  Similarity Weight: $SIMILARITY_WEIGHT"
echo "  Binding Weight: $BINDING_WEIGHT"
echo "  Results Directory: $RESULTS_DIR"
echo "  Logs Directory: $LOGS_DIR"
echo "Started at: $(date)"
echo "=========================================="
echo ""

# Track overall start time
OVERALL_START=$(date +%s)

# Arrays to track experiment info
declare -a PIDS=()
declare -a NAMES=()
declare -a START_TIMES=()
declare -a RESULTS=()

# Function to run a single experiment in parallel
run_experiment_parallel() {
    local name=$1
    local command=$2
    local cuda_device=$3
    local logfile="${LOGS_DIR}/${name}.log"
    
    echo "[$(date +%H:%M:%S)] Starting: $name (CUDA: $cuda_device)"
    echo "  Command: $command"
    echo "  Log: $logfile"
    
    # Set CUDA device if specified
    if [ -n "$cuda_device" ]; then
        export CUDA_VISIBLE_DEVICES=$cuda_device
        command="CUDA_VISIBLE_DEVICES=$cuda_device $command"
    fi
    
    # Run in background and capture PID
    eval "$command" > "$logfile" 2>&1 &
    local pid=$!
    
    PIDS+=($pid)
    NAMES+=("$name")
    START_TIMES+=($(date +%s))
    
    echo "  PID: $pid"
    echo ""
}

# Function to wait for all experiments and collect results
wait_for_experiments() {
    echo "Waiting for all experiments to complete..."
    echo "You can monitor progress with: tail -f ${LOGS_DIR}/<method>.log"
    echo ""
    
    for i in "${!PIDS[@]}"; do
        local pid=${PIDS[$i]}
        local name=${NAMES[$i]}
        local start_time=${START_TIMES[$i]}
        
        echo "[$(date +%H:%M:%S)] Waiting for: $name (PID: $pid)"
        
        wait $pid
        local exit_code=$?
        
        local end_time=$(date +%s)
        local elapsed=$((end_time - start_time))
        local minutes=$((elapsed / 60))
        local seconds=$((elapsed % 60))
        
        if [ $exit_code -eq 0 ]; then
            echo "[$(date +%H:%M:%S)] ✓ Completed: $name (${minutes}m ${seconds}s)"
            RESULTS+=("✓ $name: ${minutes}m ${seconds}s")
        else
            echo "[$(date +%H:%M:%S)] ✗ Failed: $name (exit code: $exit_code)"
            RESULTS+=("✗ $name: FAILED (exit code: $exit_code)")
        fi
        echo ""
    done
}

# Calculate optimization budget for REINVENT
OPTIMIZATION_BUDGET=$((MAX_CALLS - POPULATION_SIZE))

# Run all experiments in parallel
echo "Running 4 experiments in parallel with combined objective..."
echo ""

# 1. Graph GA (graph-based genetic algorithm) - default CUDA device
run_experiment_parallel "graph_ga" \
    "python run_graphga.py --use_combined_objective --smi_file $SMI_FILE --reference_file $REFERENCE_FILE --max_oracle_calls $MAX_CALLS --population_size $POPULATION_SIZE --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/graph_ga --similarity_weight $SIMILARITY_WEIGHT --binding_weight $BINDING_WEIGHT" \
    ""

# 2. SMILES GA (SMILES-based genetic algorithm) - default CUDA device
run_experiment_parallel "smiles_ga" \
    "python run_smiles_ga.py --use_combined_objective --smi_file $SMI_FILE --reference_file $REFERENCE_FILE --max_oracle_calls $MAX_CALLS --population_size $POPULATION_SIZE --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/smiles_ga --similarity_weight $SIMILARITY_WEIGHT --binding_weight $BINDING_WEIGHT" \
    ""

# 3. GP-BO (Gaussian Process Bayesian Optimization) - CUDA 0
run_experiment_parallel "gp_bo" \
    "python run_gp_bo.py --use_combined_objective --smi_file $SMI_FILE --reference_file $REFERENCE_FILE --max_oracle_calls $MAX_CALLS --initial_population_size $POPULATION_SIZE --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/gp_bo --similarity_weight $SIMILARITY_WEIGHT --binding_weight $BINDING_WEIGHT" \
    "0"

# 4. REINVENT (Reinforcement Learning) - CUDA 1
run_experiment_parallel "reinvent" \
    "python run_reinvent.py --use_combined_objective --smi_file $SMI_FILE --reference_file $REFERENCE_FILE --max_oracle_calls $OPTIMIZATION_BUDGET --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/reinvent --similarity_weight $SIMILARITY_WEIGHT --binding_weight $BINDING_WEIGHT" \
    "1"

# Wait for all experiments to complete
wait_for_experiments

# Calculate total elapsed time
OVERALL_END=$(date +%s)
TOTAL_ELAPSED=$((OVERALL_END - OVERALL_START))
TOTAL_MINUTES=$((TOTAL_ELAPSED / 60))
TOTAL_SECONDS=$((TOTAL_ELAPSED % 60))

# Print summary
echo "=========================================="
echo "All experiments completed!"
echo "Finished at: $(date)"
echo "Total time: ${TOTAL_MINUTES}m ${TOTAL_SECONDS}s"
echo "=========================================="
echo ""
echo "Experiment Results:"
for result in "${RESULTS[@]}"; do
    echo "  $result"
done
echo ""
echo "Configuration Summary:"
echo "  Execution Mode: Parallel (4 experiments simultaneously)"
echo "  Population Size: $POPULATION_SIZE molecules"
echo "  Max Oracle Calls: $MAX_CALLS"
echo "  Optimization Budget (REINVENT): $OPTIMIZATION_BUDGET oracle calls"
echo "  Number of Runs: $NUM_RUNS per method"
echo "  SMILES File (initial population): $SMI_FILE"
echo "  Reference File (similarity calc): $REFERENCE_FILE"
echo "  Combined Objective Weights:"
echo "    - Similarity: $SIMILARITY_WEIGHT"
echo "    - Binding: $BINDING_WEIGHT"
echo ""
echo "CUDA Device Assignment:"
echo "  - Graph GA: default"
echo "  - SMILES GA: default"
echo "  - GP-BO: CUDA 0"
echo "  - REINVENT: CUDA 1"
echo ""
echo "Oracle Usage:"
echo "  Methods WITH initial population:"
echo "    - Graph GA: $POPULATION_SIZE initial + evolution = $MAX_CALLS total"
echo "    - SMILES GA: $POPULATION_SIZE initial + evolution = $MAX_CALLS total"
echo "    - GP-BO: $POPULATION_SIZE initial + optimization = $MAX_CALLS total"
echo ""
echo "  Methods WITHOUT initial population:"
echo "    - REINVENT: $OPTIMIZATION_BUDGET calls (generative)"
echo ""
echo "Output locations:"
echo "  - Results: $RESULTS_DIR/"
echo "  - Log files: $LOGS_DIR/"
echo ""
echo "Directory structure:"
echo "  $RESULTS_DIR/"
echo "    ├── graph_ga/"
echo "    ├── smiles_ga/"
echo "    ├── gp_bo/"
echo "    └── reinvent/"
echo ""
echo "View logs with:"
echo "  tail -f ${LOGS_DIR}/<method>.log"
echo ""
echo "Compare with previous runs:"
echo "  ls -lh opt_results/"
echo ""
