# Graph GA (Graph-based Genetic Algorithm)

## Algorithm Overview

Graph GA is an evolutionary algorithm that optimizes molecules by directly manipulating their graph structure (atoms as nodes, bonds as edges). Unlike SMILES-based approaches that operate on string representations, Graph GA performs crossover and mutation operations directly on RDKit molecule objects, preserving chemical validity more naturally. The algorithm loads the initial population from the reference SMILES file, with higher-scoring molecules having greater probability of being selected for reproduction. Through iterative cycles of fitness-based selection, graph-level crossover (combining subgraphs from two parent molecules), and mutation (adding/removing/modifying atoms and bonds), the population evolves toward molecules with better binding affinity. The reference SMILES file is critical as it provides the starting gene pool - the algorithm exclusively evolves these molecules rather than generating entirely new structures, making it particularly effective for optimizing within a chemically relevant neighborhood of known binders.

## Hyperparameters

**`population_size`** (default: `120`)
- Number of molecules maintained in the population at each generation
- Larger populations explore more diverse solutions simultaneously but require more oracle evaluations per generation
- Smaller populations converge faster but may get trapped in local optima
- Trade-off: Diversity and robustness vs. convergence speed and computational cost
- The top `population_size` molecules are selected from the reference SMILES file to initialize the population

**`offspring_size`** (default: `70`)
- Number of new offspring molecules generated per generation through crossover and mutation
- Controls the rate of exploration: higher values test more new variants per generation
- After generating offspring, the algorithm selects the best `population_size` molecules from the combined pool (parents + offspring) to form the next generation
- Trade-off: Exploration rate vs. computational cost per generation
- Typical ratio: offspring_size ≈ 0.5-0.7 × population_size maintains balance between preservation and exploration

**`mutation_rate`** (default: `0.067`)
- Probability that a mutation occurs to an offspring molecule after crossover
- Mutations include: adding/removing atoms, changing atom types, adding/removing bonds, changing bond types
- Lower rates (e.g., 0.01) make smaller, incremental changes suitable for fine-tuning
- Higher rates (e.g., 0.1-0.2) enable more radical structural exploration but may produce invalid molecules
- Default 0.067 (~6.7%) provides moderate structural diversity while maintaining chemical validity
- Note: This is per-molecule mutation probability, not per-atom like in some other algorithms
