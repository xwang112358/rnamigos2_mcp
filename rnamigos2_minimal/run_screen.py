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


# ============================================================================
# SCREENING OPTIMIZER EXAMPLE
# ============================================================================
# Screening is a baseline optimizer that simply evaluates molecules from a 
# provided library in random order (no actual optimization/generation).
# Use this as a baseline to compare against generative methods like GraphGA.
# - smi_file: Path to file containing SMILES strings to screen (one per line)
# - n_jobs: Number of parallel processes for evaluation
# - max_oracle_calls: Maximum number of molecules to evaluate before stopping
# - freq_log: How often (in oracle calls) to log progress
# - output_dir: Directory to save results and logs
# - log_results: Whether to save detailed results to disk

screening_optimizer = Screening(
    smi_file='inputs/ligands/robin_smiles.txt',
    n_jobs=-1,
    max_oracle_calls=1500,
    freq_log=100,    
    output_dir='opt_results/screening',
    log_results=True
)


# Run screening - it will randomly shuffle and evaluate molecules from the library
# screening_optimizer.optimize(
#     oracle=rnamigos2_oracle,  # Can be custom function or string like 'qed', 'sa', etc.
#     seed=1          # Random seed for reproducibility
# )

screening_optimizer.production(oracle=rnamigos2_oracle, config=None, num_runs=5)


