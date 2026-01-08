---
name: Implement run_gp_bo.py
overview: Create a GP-BO (Gaussian Process Bayesian Optimization) script following the structure of run_graphga.py, using the same oracle function and including detailed comments about all hyperparameters.
todos: []
---

# Implement run_gp_bo.py for GP-BO Optimization

## Overview

Create a new script `run_gp_bo.py` in the `rnamigos2_minimal/` directory that performs Gaussian Process Bayesian Optimization using the RNAmigos2 oracle function, following the same structure as [`rnamigos2_minimal/run_graphga.py`](rnamigos2_minimal/run_graphga.py).

## Implementation Details

### Structure

The script will follow the same pattern as the GraphGA implementation:

- Import `GPBO` from `molopt.gpbo` (found in [`mol-opt-rna/molopt/gpbo/__init__.py`](mol-opt-rna/molopt/gpbo/__init__.py))
- Import and use the same `rnamigos2_oracle` function from [`rnamigos2_minimal/oracle.py`](rnamigos2_minimal/oracle.py)
- Use similar constructor parameters (`smi_file`, `n_jobs`, `max_oracle_calls`, `freq_log`, `output_dir`)
- Call the `optimize()` method with oracle, patience, and seed
- Disable RDKit warnings for cleaner output

### GP-BO Algorithm Overview

The script will include a comprehensive comment section explaining how GP-BO works:

1. **Gaussian Process** - Surrogate model that predicts molecule scores and uncertainty
2. **Acquisition Function** - UCB (Upper Confidence Bound) balances exploration (high uncertainty) vs exploitation (high predicted score)
3. **Genetic Algorithm** - Optimizes the acquisition function to propose promising molecules
4. **Iterative Refinement** - GP is retrained with new data each iteration, improving predictions

### Hyperparameters to Document

Based on [`mol-opt-rna/molopt/gpbo/run.py`](mol-opt-rna/molopt/gpbo/run.py) (lines 88-118), [`mol-opt-rna/molopt/gpbo/hparams_default.yaml`](mol-opt-rna/molopt/gpbo/hparams_default.yaml), and [`mol-opt-rna/molopt/gpbo/mol_opt/run_bo_gp_exact_subset_ucb4.py`](mol-opt-rna/molopt/gpbo/mol_opt/run_bo_gp_exact_subset_ucb4.py), the script will document:

**1. Initial Population & GP Training Data Selection**

- `initial_population_size` (340): Starting molecules to evaluate before BO begins
- `n_train_gp_best` (2200): Top-scoring molecules kept in GP training set (for computational efficiency, prevents GP from training on all data)
- `n_train_gp_rand` (1350): Random molecules added to GP training (maintains diversity, prevents overfitting to top performers)

**2. Bayesian Optimization Control**

- `max_bo_iter` (10000): Maximum BO iterations
- `bo_batch_size` (1180): Molecules to evaluate per BO iteration (larger = more parallel evaluation but less adaptive)

**3. Genetic Algorithm Settings** (for optimizing acquisition function)

- `ga_max_generations` (60): Generations per BO iteration to find molecules with high acquisition values
- `ga_population_size` (820): Population size in GA
- `ga_offspring_size` (150): New molecules generated per generation
- `ga_mutation_rate` (0.01): Probability of mutation (1% per atom/bond)
- `ga_pool_num_best` (250): Top-scoring molecules used to seed GA (exploitation)
- `ga_pool_num_carryover` (250): High-acquisition molecules from previous BO iteration (warm-start)
- `max_ga_start_population_size` (1000): Maximum starting population for GA (padded with random molecules)

**4. Molecular Fingerprint Parameters**

- `fp_radius` (2): Morgan fingerprint radius (atom neighborhood size for molecular similarity)
- `fp_nbits` (4096): Fingerprint bit vector length (higher = more detailed, but more computational cost)

### Documentation Approach

Each hyperparameter section will include:

1. **Section header** explaining the category
2. **Inline comments** for each parameter with:

- What it controls
- How it affects the algorithm (exploration/exploitation, computational cost, etc.)
- Default value from `hparams_default.yaml`
- Key insights from the reference implementation

3. **Algorithm flow context** showing where each parameter is used in the BO loop