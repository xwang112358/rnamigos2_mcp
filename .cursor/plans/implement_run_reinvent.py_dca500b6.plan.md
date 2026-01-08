---
name: Implement run_reinvent.py
overview: Create a REINVENT (Reinforcement Learning for molecular design) script following the structure of run_graphga.py and run_gp_bo.py, using the same oracle function and including detailed comments about all hyperparameters.
todos: []
---

# Implement run_reinvent.py for Reinforcement Learning-based Molecular Optimization

## Overview

Create a new script `run_reinvent.py` in the `rnamigos2_minimal/` directory that performs reinforcement learning-based molecular generation and optimization using the RNAmigos2 oracle function, following the same structure as [`rnamigos2_minimal/run_graphga.py`](rnamigos2_minimal/run_graphga.py) and [`rnamigos2_minimal/run_gp_bo.py`](rnamigos2_minimal/run_gp_bo.py).

## Implementation Details

### Structure

The script will follow the same pattern as the GraphGA and GP-BO implementations:

- Import `REINVENT` from `molopt.reinvent` (found in [`mol-opt-rna/molopt/reinvent/__init__.py`](mol-opt-rna/molopt/reinvent/__init__.py))
- Import and use the same `rnamigos2_oracle` function from [`rnamigos2_minimal/oracle.py`](rnamigos2_minimal/oracle.py) (with dtype fix)
- Use similar constructor parameters (`smi_file`, `n_jobs`, `max_oracle_calls`, `freq_log`, `output_dir`)
- Call the `optimize()` method with oracle, patience, and seed
- Disable RDKit warnings for cleaner output

### REINVENT Algorithm Overview

The script will include a comprehensive comment section explaining how REINVENT works:

1. **RNN-based Generator** - Uses a recurrent neural network to generate SMILES strings character by character
2. **Prior and Agent Models** - Prior is a pre-trained model representing valid chemistry; Agent is fine-tuned for the task
3. **Reinforcement Learning** - Uses policy gradients to optimize the Agent to generate molecules with high scores
4. **Augmented Likelihood** - Combines prior likelihood (valid chemistry) with oracle scores to guide learning
5. **Experience Replay** - Stores and reuses high-scoring molecules to stabilize training

### Hyperparameters to Document

Based on [`mol-opt-rna/molopt/reinvent/run.py`](mol-opt-rna/molopt/reinvent/run.py) (lines 22-30), [`mol-opt-rna/molopt/reinvent/hparams_default.yaml`](mol-opt-rna/molopt/reinvent/hparams_default.yaml), and [`mol-opt-rna/molopt/gpbo/mol_opt/run_reinvent.py`](mol-opt-rna/molopt/gpbo/mol_opt/run_reinvent.py), the script will document:

**1. Learning Parameters**

- `learning_rate` (0.0005): Learning rate for Adam optimizer training the Agent
- Controls how fast the Agent adapts to the reward signal
- Too high = unstable training, too low = slow convergence

**2. Sampling Parameters**

- `batch_size` (64): Number of molecules generated and evaluated per training step
- Larger batch = more stable gradients but slower per-step
- Smaller batch = faster but noisier gradients

**3. Reward Shaping**

- `sigma` (500): Weight for the oracle score in the augmented likelihood
- Controls exploration vs exploitation trade-off
- Higher sigma = stronger focus on optimizing oracle score
- Lower sigma = more conservative, stays closer to valid chemistry (prior)

**4. Training Stability**

- `experience_replay` (24): Number of past high-scoring molecules resampled per step
- Prevents catastrophic forgetting of good solutions
- Stabilizes training by reusing successful examples
- 0 = no experience replay (pure on-policy learning)

### Key Differences from Other Methods

REINVENT is fundamentally different from GraphGA and GP-BO:

- **Generative**: Creates entirely new molecules from scratch (not from a starting pool)
- **Sequential**: Generates SMILES one character at a time using RNN
- **Online Learning**: Model improves continuously during optimization
- **No Starting Pool Required**: Unlike GA methods, doesn't need initial molecules (though can benefit from them)

### Documentation Approach

Each hyperparameter section will include:

1. **Algorithm overview** explaining REINVENT's RL approach
2. **Section header** explaining each parameter category
3. **Inline comments** for each parameter with:

- What it controls
- How it affects learning (exploration/exploitation, training stability)
- Default value from `hparams_default.yaml`
- Practical implications for different values

4. **Key differences** from GA and BO methods to help users understand when to use REINVENT