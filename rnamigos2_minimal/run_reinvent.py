"""
REINVENT (Reinforcement Learning for Molecular Design) for RNA-ligand binding optimization.

REINVENT Algorithm Overview:
----------------------------
REINVENT uses reinforcement learning to train a recurrent neural network (RNN) to 
generate molecules with desired properties. Unlike genetic algorithms or Bayesian 
optimization that start from existing molecules, REINVENT generates entirely new 
molecules from scratch by learning to write SMILES strings character by character.

Key Components:
1. RNN-based Generator: A sequence-to-sequence model that generates SMILES strings
   one character at a time, similar to language models generating text.

2. Prior and Agent Models:
   - Prior: Pre-trained RNN model that represents general valid chemistry
   - Agent: Copy of Prior that gets fine-tuned to generate molecules for the task
   - The Prior acts as a regularizer to keep Agent from generating invalid molecules

3. Reinforcement Learning (Policy Gradients):
   - Agent generates molecules → Oracle scores them → Agent learns to generate better ones
   - Uses policy gradient methods to optimize the probability of high-scoring molecules
   - Balances between exploring new molecules and exploiting known good ones

4. Augmented Likelihood:
   - Combines prior likelihood P(molecule|Prior) with oracle score
   - Formula: Augmented = Prior_likelihood + sigma * Score
   - This keeps Agent from deviating too far from valid chemistry
   - Sigma controls the trade-off: higher = focus on score, lower = stay conservative

5. Experience Replay:
   - Stores high-scoring molecules found during training
   - Periodically retrains on these stored examples
   - Prevents "catastrophic forgetting" where Agent forgets good solutions
   - Stabilizes training by mixing new samples with proven successes

Key Differences from Other Methods:
-----------------------------------
- vs. Genetic Algorithms (GraphGA/SMILES GA):
  * REINVENT is generative (creates new molecules) vs. GA is evolutionary (modifies existing)
  * REINVENT doesn't need starting molecules (though can use them)
  * REINVENT learns a model that improves over time vs. GA uses fixed operators
  
- vs. Bayesian Optimization (GP-BO):
  * REINVENT generates molecules directly vs. BO searches fingerprint space
  * REINVENT is more exploratory (can find very different molecules)
  * BO is more efficient for local optimization around known molecules

When to Use REINVENT:
- Need diverse, novel molecular structures
- Want to explore beyond the initial dataset
- Have enough oracle budget for training (typically 5000+ evaluations)
- Oracle is relatively fast (REINVENT needs many sequential evaluations)
"""

from molopt.reinvent import REINVENT
from rdkit import RDLogger
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle

# Disable RDKit warnings for cleaner output
RDLogger.DisableLog('rdApp.warning')


# ============================================================================
# Initialize REINVENT Optimizer
# ============================================================================
optimizer = REINVENT(
    smi_file="inputs/ligands/robin_smiles.txt",   # REINVENT generates from scratch, doesn't need starting molecules
                                           # Set to a file path if you want to seed the experience replay buffer
    n_jobs=1,                              # REINVENT uses sequential RNN generation (no parallelization)
    max_oracle_calls=1500,                 # Stop after 1000 oracle evaluations
    freq_log=100,                          # Log progress every 100 evaluations
    output_dir='opt_results/reinvent'      # Directory to save results
)


# ============================================================================
# Hyperparameter Configuration
# ============================================================================
# These hyperparameters are set automatically by the REINVENT class with defaults
# from mol-opt-rna/molopt/reinvent/hparams_default.yaml
# They are documented here for reference and understanding.

# --- 1. LEARNING PARAMETERS ---
# Controls how the Agent RNN learns from the reward signal
#
# learning_rate: 0.0005
#   - Learning rate for Adam optimizer training the Agent model
#   - Controls how quickly the Agent adapts to maximize oracle scores
#   - Too high (>0.001): Training becomes unstable, Agent may collapse
#   - Too low (<0.0001): Very slow convergence, may not reach good solutions in time
#   - Default 0.0005 is a sweet spot for most tasks
#   - The Agent is continuously updated, so this affects every training step

# --- 2. SAMPLING PARAMETERS ---
# Controls the batch size for molecule generation
#
# batch_size: 64
#   - Number of molecules generated and evaluated per training step
#   - Larger batch = more stable gradient estimates, but slower per-step
#   - Smaller batch = faster iteration, but noisier gradients
#   - Trade-offs:
#     * 32: Faster, good for quick experiments, noisier training
#     * 64: Standard choice, balanced speed and stability
#     * 128+: Very stable but slower, good for final runs
#   - Each batch costs N oracle calls, so affects total optimization time

# --- 3. REWARD SHAPING ---
# Controls exploration vs exploitation trade-off
#
# sigma: 500
#   - Weight for oracle score in the augmented likelihood
#   - Formula: Augmented_likelihood = Prior_likelihood + sigma * Oracle_score
#   - This is THE key hyperparameter for REINVENT's behavior
#   - Effects:
#     * sigma = 0: Agent stays identical to Prior (no optimization)
#     * sigma = 100-300: Conservative, stays close to valid chemistry
#     * sigma = 500-750: Balanced, standard for most tasks
#     * sigma = 1000+: Aggressive, maximizes score but risks invalid molecules
#   - Higher sigma = Agent focuses more on score, less on chemistry validity
#   - Lower sigma = Agent stays safer, explores less aggressively
#   - Tune this if: molecules are invalid (decrease) or not improving enough (increase)

# --- 4. TRAINING STABILITY ---
# Prevents catastrophic forgetting through experience replay
#
# experience_replay: 24
#   - Number of past high-scoring molecules resampled per training step
#   - How it works:
#     1. Agent generates batch_size new molecules
#     2. Also samples experience_replay old molecules from memory
#     3. Trains on both new + old molecules together
#   - Benefits:
#     * Prevents forgetting: Agent remembers good solutions found earlier
#     * Stabilizes training: Mix of new exploration + proven successes
#     * Improves sample efficiency: Reuses successful examples
#   - Values:
#     * 0: No replay (pure on-policy RL, can forget good solutions)
#     * 8-16: Light replay, more exploration-focused
#     * 24-32: Standard, good balance
#     * 50+: Heavy replay, more conservative, slower to explore
#   - Stored molecules are the best ones found so far


# ============================================================================
# Algorithm Details (for Advanced Users)
# ============================================================================
# 
# Training Loop:
# 1. Agent.sample(batch_size) → generates SMILES strings via RNN
# 2. Oracle(smiles) → evaluates generated molecules
# 3. Calculate augmented likelihood = prior_likelihood + sigma * score
# 4. Calculate loss = (augmented_likelihood - agent_likelihood)²
# 5. Add experience replay samples to loss
# 6. Backpropagate and update Agent weights
# 7. Store good molecules in experience buffer
# 8. Repeat until max_oracle_calls reached
#
# Early Stopping:
# - Monitors top 100 molecules' scores
# - If no improvement for 'patience' iterations → stop
# - Default patience=50 in optimize() call below
#
# Model Architecture:
# - 3-layer LSTM with 512 hidden units
# - Input: SMILES vocabulary (~50 characters)
# - Output: Next character probability distribution
# - Pre-trained on ~1M molecules from ChEMBL
# - Prior weights frozen, only Agent is trained


# ============================================================================
# Run Optimization
# ============================================================================
# patience: Number of iterations without improvement before stopping early (50 iterations)
# seed: Random seed for reproducibility (0)
# optimizer.optimize(oracle=tpp_rnamigos2_oracle, patience=50, seed=0)
optimizer.production(oracle=tpp_rnamigos2_oracle, config=None, num_runs=5)
