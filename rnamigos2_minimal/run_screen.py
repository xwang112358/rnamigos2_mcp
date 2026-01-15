import argparse
from molopt.graph_ga import GraphGA
from molopt.screening import Screening
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit import RDLogger
import numpy as np
from rnamigos.inference import do_inference_single

# Disable only warnings
RDLogger.DisableLog('rdApp.warning') 

# Define a RNAmigos2 oracle function that returns the dock score
residue_list = np.load('./inputs/residue_list/tpp.npy')
cif_path = './inputs/rna_targets/2gdi.cif'

def rnamigos2_oracle(smi):
    """Run RNAmigos2 inference for a single SMILES string"""
    score = do_inference_single(
        cif_path=cif_path,
        residue_list=residue_list,
        smiles=smi
    )
    return score


if __name__ == '__main__':
    # ============================================================================
    # Parse Command-Line Arguments
    # ============================================================================
    parser = argparse.ArgumentParser(description='Run Screening baseline for RNA-ligand binding')
    parser.add_argument('--smi_file', type=str, default='inputs/ligands/robin_smiles.txt',
                        help='Path to SMILES file with molecules to screen')
    parser.add_argument('--max_oracle_calls', type=int, default=10000,
                        help='Maximum number of oracle evaluations (default: 10000)')
    parser.add_argument('--output_dir', type=str, default='opt_results/screening',
                        help='Directory to save results (default: opt_results/screening)')
    parser.add_argument('--num_runs', type=int, default=1,
                        help='Number of independent runs (default: 1)')
    parser.add_argument('--n_jobs', type=int, default=-1,
                        help='Number of parallel jobs, -1 for all cores (default: -1)')
    parser.add_argument('--freq_log', type=int, default=100,
                        help='Logging frequency (default: 100)')
    args = parser.parse_args()

    # ============================================================================
    # Initialize Screening Optimizer
    # ============================================================================
    # Screening is a baseline optimizer that simply evaluates molecules from a 
    # provided library in random order (no actual optimization/generation).
    # Use this as a baseline to compare against generative methods.
    
    screening_optimizer = Screening(
        smi_file=args.smi_file,
        n_jobs=args.n_jobs,
        max_oracle_calls=args.max_oracle_calls,
        freq_log=args.freq_log,    
        output_dir=args.output_dir,
        log_results=True
    )

    # ============================================================================
    # Run Screening
    # ============================================================================
    screening_optimizer.production(oracle=rnamigos2_oracle, config=None, num_runs=args.num_runs)


