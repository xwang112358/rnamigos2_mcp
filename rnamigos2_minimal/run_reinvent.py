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

import argparse
from molopt.reinvent import REINVENT
from rdkit import RDLogger
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle

# Disable RDKit warnings for cleaner output
RDLogger.DisableLog('rdApp.warning')


if __name__ == '__main__':
    # ============================================================================
    # Parse Command-Line Arguments
    # ============================================================================
    parser = argparse.ArgumentParser(description='Run REINVENT optimization for RNA-ligand binding')
    parser.add_argument('--smi_file', type=str, default='inputs/ligands/robin_smiles.txt',
                        help='Path to SMILES file to seed experience replay buffer')
    parser.add_argument('--max_oracle_calls', type=int, default=10000,
                        help='Maximum number of oracle evaluations (default: 10000)')
    parser.add_argument('--output_dir', type=str, default='opt_results/reinvent',
                        help='Directory to save results (default: opt_results/reinvent)')
    parser.add_argument('--num_runs', type=int, default=1,
                        help='Number of independent runs (default: 1)')
    parser.add_argument('--n_jobs', type=int, default=1,
                        help='Number of parallel jobs (REINVENT uses sequential generation, default: 1)')
    parser.add_argument('--freq_log', type=int, default=100,
                        help='Logging frequency (default: 100)')
    args = parser.parse_args()

    # ============================================================================
    # Initialize REINVENT Optimizer
    # ============================================================================
    optimizer = REINVENT(
        smi_file=args.smi_file,
        n_jobs=args.n_jobs,
        max_oracle_calls=args.max_oracle_calls,
        freq_log=args.freq_log,
        output_dir=args.output_dir
    )

    # ============================================================================
    # Run Optimization
    # ============================================================================
    optimizer.production(oracle=tpp_rnamigos2_oracle, config=None, num_runs=args.num_runs)
