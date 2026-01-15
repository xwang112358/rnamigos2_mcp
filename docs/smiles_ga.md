# SMILES GA (SMILES-based Genetic Algorithm)

## Algorithm Overview

SMILES GA is an evolutionary algorithm that operates on the grammatical structure of SMILES strings using a context-free grammar representation. Unlike Graph GA which manipulates molecules as graph objects, SMILES GA encodes molecules as fixed-length integer gene sequences using a context-free grammar (CFG) that captures SMILES syntax rules. The algorithm loads the initial population from the reference SMILES file, converting each molecule into a gene representation of length `gene_size` using the CFG production rules. Evolution proceeds through tournament selection (choosing parents with higher scores), single-point crossover between parent genes, and mutation (randomly changing grammar rule choices). The grammatical encoding ensures that most genetic operations produce syntactically valid SMILES strings, though semantic validity (whether it represents a real molecule) is still checked with RDKit. The reference SMILES file is essential as it provides the starting population of genes - molecules that are already chemically relevant to the task - which the algorithm refines through grammatical recombination rather than creating entirely new structures.

## Hyperparameters

**`gene_size`** (default: `200`)
- Fixed length of the integer gene array used to encode SMILES grammar production rules
- Each integer in the gene specifies which grammar rule to apply at each derivation step
- Controls the maximum complexity of molecules that can be represented
- Too small (<100): Cannot represent complex molecules, limits exploration to simple structures
- Too large (>300): Wastes memory, increases crossover/mutation search space, most production rules at the end are unused
- Default 200 allows for moderately complex drug-like molecules while maintaining computational efficiency
- Molecules are encoded by applying CFG production rules sequentially based on gene values
- If a molecule requires fewer than `gene_size` derivation steps, remaining gene positions are filled with random integers

**`population_size`** (default: `50`)
- Number of molecules (genes) maintained in the population at each generation
- Smaller than typical genetic algorithms due to the CFG encoding being more structured
- Larger populations (100+) explore more diverse grammar derivations but require more oracle evaluations per generation
- Smaller populations (20-30) converge faster but may get stuck in local optima of the grammar space
- Trade-off: Diversity in grammatical variations vs. convergence speed
- The initial population is created by encoding the first `population_size` molecules from the reference SMILES file

**`n_mutations`** (default: `500`)
- Number of mutation operations performed in each generation
- Mutations randomly change integer values in the gene, selecting different CFG production rules
- This is NOT mutation rate per gene - it's the total number of mutation operations per generation
- Higher values (1000+) allow more aggressive exploration of the grammar space but increase computation per generation
- Lower values (100-200) make smaller, more incremental changes to the population
- Each mutation:
  1. Selects a parent from the population via tournament selection
  2. Randomly changes one integer in the gene (one grammar rule choice)
  3. Decodes the mutated gene into a SMILES string
  4. Adds to candidate pool if valid
- With `n_mutations=500` and `population_size=50`, on average each population member undergoes ~10 mutation attempts per generation
