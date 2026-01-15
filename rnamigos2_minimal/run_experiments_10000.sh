#!/bin/bash

# run_experiments_10000.sh - Run all RNA-ligand optimization methods sequentially
# Usage: ./run_experiments_10000.sh [initial_pop_size] [max_oracle_calls] [num_runs] [experiment_name]
# Defaults: initial_pop=10000, max_calls=20000, runs=1, experiment_name=auto_timestamp

# Parse arguments with defaults
INITIAL_POP=${1:-10000}
MAX_CALLS=${2:-20000}
NUM_RUNS=${3:-1}
EXP_NAME=${4:-$(date +%Y%m%d_%H%M%S)}

# Create timestamped parent directory for this experimental run
RESULTS_DIR="opt_results/run_${EXP_NAME}"
LOGS_DIR="logs/run_${EXP_NAME}"

mkdir -p "$RESULTS_DIR"
mkdir -p "$LOGS_DIR"

echo "=========================================="
echo "Sequential RNA-ligand optimization experiments"
echo "=========================================="
echo "Configuration:"
echo "  Experiment Name: $EXP_NAME"
echo "  Initial Population Size: $INITIAL_POP"
echo "  Max Oracle Calls: $MAX_CALLS"
echo "  Number of Runs: $NUM_RUNS"
echo "  Results Directory: $RESULTS_DIR"
echo "  Logs Directory: $LOGS_DIR"
echo "Started at: $(date)"
echo "=========================================="
echo ""

# Track overall start time
OVERALL_START=$(date +%s)

# Array to track experiment results
declare -a RESULTS=()

# Function to run a single experiment
run_experiment() {
    local name=$1
    local command=$2
    local logfile="${LOGS_DIR}/${name}.log"
    
    echo "[$(date +%H:%M:%S)] Starting: $name"
    echo "  Command: $command"
    echo "  Log: $logfile"
    
    local start_time=$(date +%s)
    
    eval "$command" > "$logfile" 2>&1
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
    
    return $exit_code
}

# Run experiments sequentially
echo "Running experiments..."
echo ""

# 1. Screening (baseline - evaluates molecules randomly)
run_experiment "screening" \
    "python run_screen.py --max_oracle_calls $MAX_CALLS --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/screening"

# 2. Graph GA (graph-based genetic algorithm)
run_experiment "graph_ga" \
    "python run_graphga.py --max_oracle_calls $MAX_CALLS --population_size $INITIAL_POP --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/graph_ga"

# 3. SMILES GA (SMILES-based genetic algorithm)
run_experiment "smiles_ga" \
    "python run_smiles_ga.py --max_oracle_calls $MAX_CALLS --population_size $INITIAL_POP --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/smiles_ga"

# 4. GP-BO (Gaussian Process Bayesian Optimization)
run_experiment "gp_bo" \
    "python run_gp_bo.py --max_oracle_calls $MAX_CALLS --initial_population_size $INITIAL_POP --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/gp_bo"

# 5. REINVENT (Reinforcement Learning)
run_experiment "reinvent" \
    "python run_reinvent.py --max_oracle_calls $MAX_CALLS --num_runs $NUM_RUNS --output_dir ${RESULTS_DIR}/reinvent"

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
echo "  Initial Population: $INITIAL_POP molecules"
echo "  Max Oracle Calls: $MAX_CALLS per method"
echo "  Number of Runs: $NUM_RUNS per method"
echo ""
echo "Expected Oracle Usage:"
echo "  - Screening: $MAX_CALLS calls (random evaluation)"
echo "  - Graph GA: ~$INITIAL_POP initial + $((MAX_CALLS - INITIAL_POP)) evolution"
echo "  - SMILES GA: ~$INITIAL_POP initial + $((MAX_CALLS - INITIAL_POP)) evolution"
echo "  - GP-BO: ~$INITIAL_POP initial + $((MAX_CALLS - INITIAL_POP)) optimization"
echo "  - REINVENT: $MAX_CALLS calls (generative, no initial pop)"
echo ""
echo "Output locations:"
echo "  - Results: $RESULTS_DIR/"
echo "  - Log files: $LOGS_DIR/"
echo ""
echo "Directory structure:"
echo "  $RESULTS_DIR/"
echo "    ├── screening/"
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
