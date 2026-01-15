# GP-BO (Gaussian Process Bayesian Optimization)

## Algorithm Overview

GP-BO combines Gaussian Process regression with Bayesian optimization to efficiently search chemical space for high-scoring RNA-ligand binding molecules. The algorithm starts by evaluating an initial population from the reference SMILES file, then uses these molecules to train a Gaussian Process surrogate model that predicts both molecule scores and uncertainty. A genetic algorithm optimizes an acquisition function (Upper Confidence Bound) that balances exploiting high-predicted scores with exploring uncertain regions. The reference SMILES file serves as the starting pool for the initial population and as seed molecules for the genetic algorithm, anchoring the search in chemically relevant space while allowing exploration through crossover and mutation operations. The GP model is iteratively retrained with newly evaluated molecules, progressively refining its predictions and focusing the search on the most promising regions of chemical space.

## Hyperparameters

### Initial Population & GP Training Data Selection

**`initial_population_size`** (default: `340`)
- Number of starting molecules randomly selected from the reference SMILES file to evaluate before the Bayesian optimization loop begins
- Provides initial training data for the Gaussian Process surrogate model
- Larger values give the GP a better initial understanding of the chemical landscape but consume more oracle calls upfront
- Trade-off: Better initial GP model vs. more oracle budget spent before optimization starts

**`n_train_gp_best`** (default: `2200`)
- Number of top-scoring molecules retained in the GP training set
- For computational efficiency, prevents GP from training on all evaluated molecules
- Focuses the GP's attention on high-performing regions of chemical space
- Trade-off: Too small leads to underfitting, too large increases computational cost and training time

**`n_train_gp_rand`** (default: `1350`)
- Number of random molecules (beyond top performers) added to the GP training set
- Maintains diversity in training data to prevent overfitting to only peak regions
- Helps GP model the full chemical landscape, including valleys and plateaus
- Critical for exploration: ensures GP doesn't become overconfident in unexplored regions

### Bayesian Optimization Control

**`max_bo_iter`** (default: `10000`)
- Maximum number of Bayesian optimization iterations allowed
- Each iteration: optimize acquisition function → evaluate batch → retrain GP
- Usually stops earlier when `max_oracle_calls` budget is exhausted
- Sets an upper bound to prevent infinite loops in edge cases

**`bo_batch_size`** (default: `1180`)
- Number of molecules to evaluate per Bayesian optimization iteration
- Larger batches enable more parallel evaluation but reduce adaptivity (less frequent GP retraining)
- Smaller batches make the search more adaptive but slower due to frequent retraining overhead
- Trade-off: Parallelism and throughput vs. adaptive search and responsiveness

### Genetic Algorithm Settings

The genetic algorithm is used within each BO iteration to optimize the acquisition function and propose promising molecules.

**`ga_max_generations`** (default: `60`)
- Number of genetic algorithm generations run per BO iteration to optimize the acquisition function
- More generations allow better acquisition function optimization but with diminishing returns
- Each generation performs selection, crossover, and mutation to evolve molecules with high acquisition values

**`ga_population_size`** (default: `820`)
- Number of molecules maintained in the genetic algorithm population
- Larger populations explore more diverse molecular structures but increase computational cost
- Balances diversity exploration with computational efficiency

**`ga_offspring_size`** (default: `150`)
- Number of new molecules generated per genetic algorithm generation through crossover and mutation
- Controls how aggressively new molecular structures are explored each generation
- Higher values speed up exploration but may reduce selection pressure

**`ga_mutation_rate`** (default: `0.01`)
- Probability of mutation per atom/bond (1% chance)
- Lower rates (e.g., 0.001) produce incremental changes for local search
- Higher rates (e.g., 0.1) enable more radical structural exploration
- Default 0.01 balances local refinement with structural diversity

**`ga_pool_num_best`** (default: `250`)
- Number of top-scoring molecules (from all evaluated) used to seed the GA population
- Exploitation component: starts GA search from known good molecules
- Ensures GA doesn't waste time re-discovering already known high-performers

**`ga_pool_num_carryover`** (default: `250`)
- Number of high-acquisition molecules from the previous BO iteration carried over to the next
- Warm-start strategy: molecules that had high acquisition values before may still be promising after GP retraining
- Provides continuity between BO iterations and reduces redundant search

**`max_ga_start_population_size`** (default: `1000`)
- Maximum size of the starting population for the genetic algorithm
- Combines: top-scoring molecules + carryover molecules + random molecules as padding
- Ensures diverse starting point for acquisition function optimization
- Prevents GA from starting with an overly large or unmanageable population

### Molecular Fingerprint Parameters

Fingerprints are used by the Gaussian Process kernel to measure molecular similarity.

**`fp_radius`** (default: `2`)
- Radius for Morgan (circular) fingerprint generation
- Defines atom neighborhood size: radius 2 captures substructures up to 2 bonds away from each atom
- Radius 1: captures only immediate neighbors (too local)
- Radius 2: standard choice balancing specificity and generalization
- Radius 3+: captures larger substructures but may over-specify and reduce similarity between related molecules

**`fp_nbits`** (default: `4096`)
- Length of the fingerprint bit vector representation
- Higher values provide more detailed molecular representation with fewer hash collisions
- Common values: 1024 (fast, less precise), 2048 (balanced), 4096 (standard), 16384 (highly precise)
- Trade-off: Representational precision vs. computational cost and memory usage
