

import argparse
import os
import yaml
from molopt.gpbo import GPBO
from rdkit import RDLogger
from oracle import rnamigos2_oracle as tpp_rnamigos2_oracle

# Disable RDKit warnings for cleaner output
RDLogger.DisableLog('rdApp.warning')


if __name__ == '__main__':
    # ============================================================================
    # Parse Command-Line Arguments
    # ============================================================================
    parser = argparse.ArgumentParser(description='Run GP-BO optimization for RNA-ligand binding')
    parser.add_argument('--smi_file', type=str, default='inputs/ligands/robin_smiles.txt',
                        help='Path to SMILES file with starting molecules')
    parser.add_argument('--max_oracle_calls', type=int, default=10000,
                        help='Maximum number of oracle evaluations (default: 10000)')
    parser.add_argument('--output_dir', type=str, default='opt_results/gp_bo',
                        help='Directory to save results (default: opt_results/gp_bo)')
    parser.add_argument('--num_runs', type=int, default=1,
                        help='Number of independent runs (default: 1)')
    parser.add_argument('--n_jobs', type=int, default=-1,
                        help='Number of parallel jobs, -1 for all cores (default: -1)')
    parser.add_argument('--freq_log', type=int, default=100,
                        help='Logging frequency (default: 100)')
    parser.add_argument('--initial_population_size', type=int, default=340,
                        help='Initial population size for GP training (default: 340)')
    args = parser.parse_args()

    # ============================================================================
    # Initialize GP-BO Optimizer
    # ============================================================================
    optimizer = GPBO(
        smi_file=args.smi_file,
        n_jobs=args.n_jobs,
        max_oracle_calls=args.max_oracle_calls,
        freq_log=args.freq_log,
        output_dir=args.output_dir
    )

    # ============================================================================
    # Run Optimization
    # ============================================================================
    # Create config file if non-default initial_population_size is used
    if args.initial_population_size != 340:
        config_dict = {'initial_population_size': args.initial_population_size}
        os.makedirs('config', exist_ok=True)
        config_path = f'config/gp_bo_temp_{args.initial_population_size}.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f)
        optimizer.production(oracle=tpp_rnamigos2_oracle, config=config_path, num_runs=args.num_runs)
    else:
        # Use default config
        optimizer.production(oracle=tpp_rnamigos2_oracle, config=None, num_runs=args.num_runs)
