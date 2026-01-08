"""
Gaussian Process Bayesian Optimization (GP-BO) for RNA-ligand binding optimization.

GP-BO Algorithm Overview:
-------------------------
1. Gaussian Process (GP): A probabilistic surrogate model that predicts molecule 
   scores AND uncertainty. Unlike simple models, GP provides confidence estimates.

2. Acquisition Function: Uses UCB (Upper Confidence Bound) to balance:
   - Exploitation: Optimizing molecules with high predicted scores
   - Exploration: Testing molecules with high uncertainty (could be hidden gems)

3. Genetic Algorithm: Optimizes the acquisition function to propose promising 
   molecules by evolving molecular structures through crossover and mutation.

4. Iterative Refinement: GP is retrained with new evaluated molecules each iteration,
   continuously improving predictions and focusing search on promising regions.

The algorithm maintains computational efficiency by training GP on a subset of data
(top performers + random samples) rather than all evaluated molecules.
"""

from molopt.gpbo import GPBO
from rdkit import RDLogger
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle

# Disable RDKit warnings for cleaner output
RDLogger.DisableLog('rdApp.warning')


# ============================================================================
# Initialize GP-BO Optimizer
# ============================================================================
optimizer = GPBO(
    smi_file='inputs/ligands/robin_smiles.txt',  # Starting molecules for optimization
    n_jobs=-1,                                     # Use all available CPU cores
    max_oracle_calls=1000,                         # Stop after 1000 oracle evaluations
    freq_log=100,                                  # Log progress every 100 evaluations
    output_dir='opt_results/gp_bo'                 # Directory to save results
)


# ============================================================================
# Hyperparameter Configuration
# ============================================================================
# These hyperparameters are set automatically by the GPBO class with defaults
# from mol-opt-rna/molopt/gpbo/hparams_default.yaml
# They are documented here for reference and understanding.

# --- 1. INITIAL POPULATION & GP TRAINING DATA SELECTION ---
# 
# initial_population_size: 340
#   - Number of starting molecules to evaluate before BO loop begins
#   - Provides initial data for training the GP surrogate model
#   - Larger = better initial GP, but more oracle calls before optimization
#
# n_train_gp_best: 2200
#   - Top-scoring molecules kept in GP training set
#   - For computational efficiency: prevents GP from training on ALL data
#   - Focuses GP on high-performing regions of chemical space
#   - Trade-off: Too small = underfitting, too large = computational cost
#
# n_train_gp_rand: 1350
#   - Random molecules added to GP training set (beyond the top performers)
#   - Maintains diversity in training data
#   - Prevents overfitting to only top performers
#   - Helps GP model the full landscape, not just peaks

# --- 2. BAYESIAN OPTIMIZATION CONTROL ---
#
# max_bo_iter: 10000
#   - Maximum number of BO iterations
#   - Each iteration: optimize acquisition function → evaluate batch → retrain GP
#   - Usually stops earlier when max_oracle_calls is reached
#
# bo_batch_size: 1180
#   - Number of molecules to evaluate per BO iteration
#   - Larger batch = more parallel evaluation, less frequent GP retraining
#   - Smaller batch = more adaptive, but slower due to frequent retraining
#   - Trade-off: parallelism vs. adaptivity

# --- 3. GENETIC ALGORITHM SETTINGS (for optimizing acquisition function) ---
# The GA is used WITHIN each BO iteration to find molecules with high acquisition values
#
# ga_max_generations: 60
#   - Number of GA generations per BO iteration
#   - More generations = better acquisition function optimization
#   - But diminishing returns after sufficient exploration
#
# ga_population_size: 820
#   - Number of molecules maintained in GA population
#   - Larger = more diversity, but more computational cost
#
# ga_offspring_size: 150
#   - New molecules generated per GA generation
#   - Controls how aggressively new structures are explored
#
# ga_mutation_rate: 0.01
#   - Probability of mutation per atom/bond (1%)
#   - Lower = incremental changes, higher = more radical exploration
#   - 0.01 balances local search with structural diversity
#
# ga_pool_num_best: 250
#   - Top-scoring molecules used to seed GA population
#   - Exploitation component: start from known good molecules
#
# ga_pool_num_carryover: 250
#   - High-acquisition molecules from previous BO iteration carried over
#   - Warm-start strategy: molecules that looked promising before
#   - May still have high acquisition after GP retraining
#
# max_ga_start_population_size: 1000
#   - Maximum starting population for GA
#   - Combines: best molecules + carryover + random padding
#   - Ensures diverse starting point for acquisition optimization

# --- 4. MOLECULAR FINGERPRINT PARAMETERS ---
# Fingerprints are used by GP to measure molecular similarity (kernel function)
#
# fp_radius: 2
#   - Morgan fingerprint radius (atom neighborhood size)
#   - Radius 2 = captures substructures up to 2 bonds away from each atom
#   - Standard choice balancing specificity and generalization
#
# fp_nbits: 4096
#   - Length of fingerprint bit vector
#   - Higher = more detailed representation, less collision
#   - But increases computational cost and memory
#   - 4096 is a common choice (vs. 1024 or 2048 for faster, 16384 for precise)


# ============================================================================
# Run Optimization
# ============================================================================
# patience: Number of iterations without improvement before stopping early
# seed: Random seed for reproducibility
optimizer.optimize(oracle=tpp_rnamigos2_oracle, patience=50, seed=0)
